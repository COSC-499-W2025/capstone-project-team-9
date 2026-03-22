from __future__ import annotations
from typing import Dict, Any, List, Tuple, Set, Optional
from datetime import datetime, date
from collections import defaultdict

from collaborative.identify_projects import _identify_authors_from_zip, _extract_common_names_from_filenames
from collaborative.identify_contributors import identify_contributors
from config.db_config import get_connection
from analysis.activity_classifier import aggregate as agg_by_activity
from parsing.file_contents_manager import get_zip_file, get_file_contents_by_upload_id
from database.user_preferences import get_user_git_username, get_user_collaboration
from account.user_manager import AuthManager


def get_project_contributor_name(uploaded_file_id: int) -> Optional[str]:
    """
    Fetch contributor_name from uploaded_files if present.
    Returns a trimmed name or None when not set.
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT contributor_name FROM uploaded_files WHERE id = %s;",
                (uploaded_file_id,),
            )
            row = cur.fetchone()
            if row and row[0]:
                name = str(row[0]).strip()
                return name if name else None
    except Exception:
        return None
    return None


def set_project_contributor_name(uploaded_file_id: int, contributor_name: str) -> bool:
    """
    Store contributor_name on uploaded_files for a project.
    Returns True on success, False on failure.
    """
    if uploaded_file_id <= 0:
        return False
    name = (contributor_name or "").strip()
    if not name:
        return False
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE uploaded_files
                SET contributor_name = %s
                WHERE id = %s;
                """,
                (name, uploaded_file_id),
            )
            conn.commit()
        return True
    except Exception:
        return False

def choose_author_from_zip(uploaded_file_id: int):
    """
    Calls _identify_authors_from_zip(uploaded_file_id),
    prints authors with numbered options,
    and adds an option to select ALL authors.
    """
    contributor_name = get_project_contributor_name(uploaded_file_id)
    if contributor_name:
        return contributor_name
    
    file_contents = get_file_contents_by_upload_id(uploaded_file_id)
    authors = _identify_authors_from_zip(uploaded_file_id) | _extract_common_names_from_filenames(file_contents)

    if not authors:
        return None

    # Get current user for git username lookup
    current_user = AuthManager.get_current_username()
    git_username = get_user_git_username(current_user) if current_user else None
    if git_username and git_username in authors:
        return git_username

    authors = sorted(list(authors))  # ordered for consistency

    print(f"\nDetected Authors for Project {uploaded_file_id}:")
    for idx, name in enumerate(authors, start=1):
        print(f"  {idx}. {name}")
    print(f"  {len(authors) + 1}. [Not a collaboarative project]")

    # get user choice
    while True:
        try:
            choice = int(input("\nSelect an option: "))

            # user selected all authors
            if choice == len(authors) + 1:
                print("\nYou selected: ALL authors")
                return None

            # user selected a specific author
            if 1 <= choice <= len(authors):
                selected = authors[choice - 1]
                set_project_contributor_name(uploaded_file_id, selected)
                return selected

            print(f"Please enter a number between 1 and {len(authors) + 1}.")
        except ValueError:
            print("Invalid input. Enter a number.")

def get_author_file_contributions_from_zip(project_id: int, author_name: str) -> Dict[str, Set[str]]:
    """
    For a given project_id and author_name, return all files that the author
    created, modified, or deleted, based on the Git history inside the uploaded ZIP.

    Return format:
        {
            "created": { "file1.py", "file2.txt", ... },
            "modified": { "file3.py", ... },
            "deleted": { "old_file.txt", ... }
        }

    If anything fails (no zip, no repo, author not found, etc.), returns
    empty sets for each category.
    """
    # Default empty structure
    empty_result: Dict[str, Set[str]] = {
        "created": set(),
        "modified": set(),
        "deleted": set(),
    }

    if project_id <= 0:
        return empty_result

    # Get the raw ZIP bytes from your storage/DB
    zip_data = get_zip_file(project_id)
    if not (zip_data and isinstance(zip_data, (bytes, bytearray))):
        # No usable zip attached to this project
        return empty_result

    ic = None
    try:
        ic = identify_contributors(zip_bytes=zip_data)
        repo_path = ic.extract_repo()
        if repo_path is None:
            return empty_result

        # Use your existing method on the class
        file_contribs = ic.get_file_contributions()
        if not file_contribs:
            return empty_result

        # Try exact match first
        author_contrib = file_contribs.get(author_name)

        # If not found, fall back to case-insensitive match
        if author_contrib is None:
            for author_key, contrib in file_contribs.items():
                if author_key.casefold() == author_name.casefold():
                    author_contrib = contrib
                    break

        if author_contrib is None:
            # Author not present in Git history
            return empty_result

        # Ensure we always return sets (not whatever internal type)
        return {
            "created": set(author_contrib.get("created", {}).get("files", set())),
            "modified": set(author_contrib.get("modified", {}).get("files", set())),
            "deleted": set(author_contrib.get("deleted", {}).get("files", set())),
        }

    except Exception:
        # If anything about the archive/repo fails, return empty
        return empty_result
    finally:
        if ic is not None:
            ic.cleanup()

def get_all_files_for_author_from_zip(project_id: int, author_name: str) -> Set[str]:
    contribs = get_author_file_contributions_from_zip(project_id, author_name)
    return contribs["created"] | contribs["modified"] | contribs["deleted"]

def fetch_records_from_db(project_id: int) -> List[Tuple[str, int, str, int]]:
    """
    Fetch file records for the given project_id from the file_contents table.
    Returns a list of tuples:
      (file_path: str, size_bytes: int, language: str, num_lines: int)

    Internally we may also fetch extra columns (e.g., timestamps),
    but they are not exposed in the returned tuple to keep the public
    contract simple and compatible with tests.  
    """
    
    with get_connection() as conn, conn.cursor() as cur:
        # Prefer line_count column when set (avoids loading file_content for LOC)
        cur.execute(
            """
            SELECT
              fc.file_path,
              COALESCE(fc.file_size, 0) AS size_bytes,
              COALESCE(fc.content_type, fc.file_extension, 'Unknown') AS language,
              fc.is_binary,
              fc.file_content,
              fc.line_count
            FROM file_contents fc
            WHERE fc.uploaded_file_id = %s
            ORDER BY fc.id;
            """,
            (project_id,),
        )
        rows = cur.fetchall()

    # results = []
    results: List[Tuple[str, int, str, int]] = []
    for row in rows:
        file_path = row[0]
        size_bytes = row[1]
        language = row[2]
        is_binary = row[3]
        file_content = row[4]
        line_count_col = row[5] if len(row) > 5 else None

        num_lines = 0
        if line_count_col is not None and line_count_col > 0:
            num_lines = int(line_count_col)
        elif not is_binary and file_content is not None:
            try:
                content_str = (
                    file_content.tobytes()
                    if hasattr(file_content, "tobytes")
                    else bytes(file_content)
                )
                text = content_str.decode("utf-8", errors="ignore")
                num_lines = text.count("\n") + (1 if text else 0)
            except Exception:
                try:
                    num_lines = content_str.count(b"\n") + (1 if content_str else 0)
                except Exception:
                    num_lines = 0

        results.append((str(file_path), int(size_bytes or 0), str(language or "Unknown"), int(num_lines)))

    current_user = AuthManager.get_current_username()
    if current_user and get_user_collaboration(current_user) and get_user_collaboration(current_user)[0]:
        author = choose_author_from_zip(project_id)
        user_files = get_all_files_for_author_from_zip(project_id, author)

        if len(user_files)>0:
            filtered_results = []
            for file_path, size_bytes, language, num_lines in results:
                keep = False
                # 1. Keep if file matches any suffix in user_files
                for suffix in user_files:
                    if file_path.endswith(suffix):
                        keep = True
                        break
                # 2. Keep if it is inside a .git folder
                if "/.git/" in file_path:
                    keep = True
                if keep:
                    filtered_results.append((file_path, size_bytes, language, num_lines))
            results = filtered_results
    return results



def aggregate_by_language(rows: List[Tuple[str, int, str, int]]) -> List[Dict[str, Any]]:
    """
    Aggregate file statistics by language.
    Returns a sorted list of dictionaries:
      [{"language": str, "files": int, "total_lines": int}, ...]
    """
    stats: Dict[str, Dict[str, int]] = {}
    for _, _, lang, lines in rows:
        bucket = stats.setdefault(lang, {"files": 0, "lines": 0})
        bucket["files"] += 1
        bucket["lines"] += int(lines or 0)

    return [
        {"language": lang, "files": v["files"], "total_lines": v["lines"]}
        for lang, v in sorted(stats.items(), key=lambda x: -x[1]["lines"])
    ]

def aggregate_by_activity(rows: List[Tuple[str, int, str, int]]) -> Dict[str, Any]:
    """
    Aggregate activity types using the existing activity_classifier.aggregate.
    """
    files = [r[0] for r in rows]
    sizes = {r[0]: int(r[1] or 0) for r in rows}
    return agg_by_activity(files, sizes)

def _add_activity_percentages(by_activity: Dict[str, Dict[str, Any]]) -> None:
    """
    For each activity type, add percentage fields based on overall totals.
    This gives a nicer breakdown of code vs docs vs media etc.
    """
    total_count = sum(v.get("count", 0) for v in by_activity.values())
    total_bytes = sum(v.get("bytes", 0) for v in by_activity.values())
    total_score = sum(float(v.get("score", 0.0)) for v in by_activity.values())

    for v in by_activity.values():
        count = v.get("count", 0)
        bytes_ = v.get("bytes", 0)
        score = float(v.get("score", 0.0))

        v["pct_count"] = (count / total_count * 100.0) if total_count else 0.0
        v["pct_bytes"] = (bytes_ / total_bytes * 100.0) if total_bytes else 0.0
        v["pct_score"] = (score / total_score * 100.0) if total_score else 0.0


def _fetch_activity_timestamps(project_id: int) -> List[datetime]:
    """
    Fetch timestamps related to this project.
    Prioritize using the earliest/latest timestamps of `file_contents.source_created_at` and `source_modified_at`.
    If neither is available, then fall back to `uploaded_files.created_at` or `last_modified_at`.

    This way:
    `Start` is closer to the earliest file time in the project (e.g., 2025/09/26 in JDK).
    `End` is closer to the latest file time in the project or the most recent analysis time.
    """
    timestamps: List[datetime] = []

    # 1) Look for file_contents's source_created_at / source_modified_at
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    MIN(COALESCE(source_created_at, source_modified_at)) AS start_ts,
                    MAX(COALESCE(source_modified_at, source_created_at)) AS end_ts
                FROM file_contents
                WHERE uploaded_file_id = %s
                  AND (source_created_at IS NOT NULL OR source_modified_at IS NOT NULL);
                """,
                (project_id,),
            )
            rows = cur.fetchall()
    except Exception:
        rows = []

    if rows:
        row = rows[0]
        start_ts = row[0] if len(row) >= 1 else None
        end_ts = row[1] if len(row) >= 2 else None

        for ts in (start_ts, end_ts):
            if isinstance(ts, datetime):
                timestamps.append(ts)
            elif isinstance(ts, date):
                timestamps.append(datetime.combine(ts, datetime.min.time()))

        # If we found any timestamps here, return them
        if timestamps:
            return timestamps

    # 2) Fallback：Use uploaded_files's created_at / last_modified_at
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT created_at, last_modified_at
                FROM uploaded_files
                WHERE id = %s;
                """,
                (project_id,),
            )
            rows = cur.fetchall()
    except Exception:
        rows = []

    for row in rows:
        if not row:
            continue
        # Safely extract created_at and last_modified_at
        if len(row) >= 1:
            created_at = row[0]
        else:
            created_at = None
        last_modified_at = row[1] if len(row) >= 2 else None

        for ts in (created_at, last_modified_at):
            if isinstance(ts, datetime):
                timestamps.append(ts)
            elif isinstance(ts, date):
                timestamps.append(datetime.combine(ts, datetime.min.time()))

    return timestamps


def _compute_timeline_metrics(timestamps: List[datetime]) -> Dict[str, Any]:
    """
    Given a list of timestamps, compute:
      - start
      - end
      - duration_days
      - active_days
    """
    if not timestamps:
        return {
            "start": None,
            "end": None,
            "duration_days": 0,
            "active_days": 0,
        }

    timestamps = sorted(timestamps)
    start = timestamps[0]
    end = timestamps[-1]
    duration_days = max((end.date() - start.date()).days, 0)
    active_days = len({t.date() for t in timestamps})

    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "duration_days": duration_days,
        "active_days": active_days,
    }

def analyze_project_from_db(project_id: int, silent: bool = False) -> Dict[str, Any]:
    """
    Analyze project metrics: language breakdown, activity type breakdown,
    totals, and simple timeline stats (Feature #10).
    
    Args:
        project_id: The project ID to analyze
        silent: If True, suppress printing of key metrics summary
    """
    rows = fetch_records_from_db(project_id)
    by_lang = aggregate_by_language(rows)
    by_activity = aggregate_by_activity(rows)

    # Extend activity metrics with percentages for frequency comparisons
    _add_activity_percentages(by_activity)

    totals_files = len(rows)
    totals_lines = sum(int(r[3] or 0) for r in rows)

    # Timeline / duration metrics
    timestamps = _fetch_activity_timestamps(project_id)
    timeline = _compute_timeline_metrics(timestamps)

    result: Dict[str, Any] = {
        "by_language": by_lang,
        "by_activity": by_activity,
        "totals": {
            "files": totals_files,
            "lines": totals_lines,
        },
        "timeline": timeline,  # new for Feature #10
    }
    
    if not silent:
        print_summary(f"project:{project_id}", result)

    # Update last_modified_at to now() for this project
    _touch_project_last_modified(project_id)

    return result

def print_summary(name: str, metrics: Dict[str, Any]) -> None:
    """
    Print formatted summary to terminal.
    """
    print(f"\n----- Key Metrics for {name} -----")

    # Timeline summary (project duration / active days)
    timeline = metrics.get("timeline") or {}
    start = timeline.get("start")
    end = timeline.get("end")
    duration_days = timeline.get("duration_days", 0)
    active_days = timeline.get("active_days", 0)

    print("\n== Timeline ==")
    print(f"Start date  : {start if start is not None else 'Unknown'}")
    print(f"End date    : {end if end is not None else 'Unknown'}")
    print(f"Duration    : {duration_days} day(s)")
    print(f"Active days : {active_days}")

    # Language summary
    print("\n== By Language ==")
    print(f"{'Language':<16}{'Files':>8}{'Lines':>12}")
    for r in metrics["by_language"]:
        print(f"{r['language']:<16}{r['files']:>8}{r['total_lines']:>12}")

    # Activity summary (with % score as frequency)
    print("\n== By Activity Type ==")
    print(f"{'Type':<12}{'Files':>8}{'Bytes':>12}{'Score':>14}{'%Score':>10}")
    for t, v in sorted(metrics["by_activity"].items(), key=lambda x: -x[1]["score"]):
        pct_score = float(v.get("pct_score", 0.0))
        print(
            f"{t:<12}{v['count']:>8}{v['bytes']:>12}"
            f"{v['score']:>14.2f}{pct_score:>10.1f}"
        )

    # Totals
    print(
        f"\nTotals: files={metrics['totals']['files']}, "
        f"lines={metrics['totals']['lines']}"
    )


# End of print_summary
def _touch_project_last_modified(project_id: int) -> None:
    """
    Update uploaded_files.last_modified_at to now() for this project.
    Record that we analyzed it just now.
    """
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE uploaded_files
                SET last_modified_at = CURRENT_TIMESTAMP
                WHERE id = %s;
                """,
                (project_id,),
            )
            conn.commit()
    except Exception as e:
        print(f"[WARN] Failed to update last_modified_at for project {project_id}: {e}")