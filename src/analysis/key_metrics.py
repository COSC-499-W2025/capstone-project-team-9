from __future__ import annotations
from typing import Dict, Any, List, Tuple
from config.db_config import get_connection
from analysis.activity_classifier import aggregate as agg_by_activity


def fetch_records_from_db(project_id: int) -> List[Tuple[str, int, str, int]]:
    """
    Fetch file records for the given project_id from the file_contents table.
    Returns a list of tuples:
      (file_path: str, size_bytes: int, language: str, num_lines: int)
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              fc.file_path,
              COALESCE(fc.file_size, 0) AS size_bytes,
              COALESCE(fc.content_type, fc.file_extension, 'Unknown') AS language,
              COALESCE(
                  (length(fc.file_content) - length(replace(fc.file_content, E'\n','')) + 1),
                  0
              ) AS num_lines
            FROM file_contents fc
            WHERE fc.uploaded_file_id = %s
            ORDER BY fc.id;
            """,
            (project_id,),
        )
        rows = cur.fetchall()

    return [(str(r[0]), int(r[1] or 0), str(r[2] or "Unknown"), int(r[3] or 0)) for r in rows]



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

def analyze_project_from_db(project_id: int) -> Dict[str, Any]:
    """
    Analyze project metrics: language breakdown, activity type breakdown, totals.
    """
    rows = fetch_records_from_db(project_id)
    by_lang = aggregate_by_language(rows)
    by_activity = aggregate_by_activity(rows)
    totals_files = len(rows)
    totals_lines = sum(int(r[3] or 0) for r in rows)

    result: Dict[str, Any] = {
        "by_language": by_lang,
        "by_activity": by_activity,
        "totals": {"files": totals_files, "lines": totals_lines},
    }
    print_summary(f"project:{project_id}", result)
    return result

def print_summary(name: str, metrics: Dict[str, Any]) -> None:
    """
    Print formatted summary to terminal.
    """
    print(f"\n----- Key Metrics for {name} -----")

    # Language summary
    print("== By Language ==")
    print(f"{'Language':<16}{'Files':>8}{'Lines':>12}")
    for r in metrics["by_language"]:
        print(f"{r['language']:<16}{r['files']:>8}{r['total_lines']:>12}")

    # Activity summary
    print("\n== By Activity Type ==")
    print(f"{'Type':<12}{'Files':>8}{'Bytes':>12}{'Score':>14}")
    for t, v in sorted(metrics["by_activity"].items(), key=lambda x: -x[1]["score"]):
        print(f"{t:<12}{v['count']:>8}{v['bytes']:>12}{v['score']:>14.2f}")

    # Totals
    print(f"\nTotals: files={metrics['totals']['files']}, lines={metrics['totals']['lines']}")
