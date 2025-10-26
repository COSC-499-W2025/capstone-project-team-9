from typing import Dict, Any, List, Tuple
from src.config.db_config import get_connection
from src.analysis.activity_classifier import aggregate as agg_by_activity


def fetch_records_from_db(project_id: int) -> List[Tuple[str, int, str, int]]:
    sql = """
    SELECT
      path,
      COALESCE(size_bytes, octet_length(content)) AS size_bytes,
      COALESCE(language, 'Unknown') AS language,
      COALESCE(num_lines, (length(content) - length(replace(content, E'\n',''))) + 1) AS num_lines
    FROM file_contents
    WHERE project_id = %s;
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (project_id,))
        rows = cur.fetchall()
    return rows


def aggregate_by_language(rows: List[Tuple[str, int, str, int]]) -> List[Dict[str, Any]]:
    stats: Dict[str, Dict[str, int]] = {}
    for _, _, lang, lines in rows:
        bucket = stats.setdefault(lang, {"files": 0, "lines": 0})
        bucket["files"] += 1
        bucket["lines"] += int(lines or 0)
    return [
        {"language": k, "files": v["files"], "total_lines": v["lines"]}
        for k, v in sorted(stats.items(), key=lambda x: -x[1]["lines"])
    ]


def aggregate_by_activity(rows: List[Tuple[str, int, str, int]]) -> Dict[str, Any]:
    files = [r[0] for r in rows]
    sizes = {r[0]: int(r[1] or 0) for r in rows}
    return agg_by_activity(files, sizes)


def analyze_project_from_db(project_id: int) -> Dict[str, Any]:
    rows = fetch_records_from_db(project_id)
    by_lang = aggregate_by_language(rows)
    by_activity = aggregate_by_activity(rows)
    totals_files = len(rows)
    totals_lines = sum(int(r[3] or 0) for r in rows)

    result = {
        "by_language": by_lang,
        "by_activity": by_activity,
        "totals": {"files": totals_files, "lines": totals_lines},
    }
    print_summary(f"project:{project_id}", result)
    return result


def print_summary(name: str, metrics: Dict[str, Any]) -> None:
    print(f"\n----- Key Metrics for {name} -----")
    print("== By Language ==")
    print(f"{'Language':<16}{'Files':>8}{'Lines':>12}")
    for r in metrics["by_language"]:
        print(f"{r['language']:<16}{r['files']:>8}{r['total_lines']:>12}")

    print("\n== By Activity Type ==")
    print(f"{'Type':<12}{'Files':>8}{'Bytes':>12}{'Score':>14}")
    for t, v in sorted(metrics["by_activity"].items(), key=lambda x: -x[1]["score"]):
        print(f"{t:<12}{v['count']:>8}{v['bytes']:>12}{v['score']:>14.2f}")

    print(f"\nTotals: files={metrics['totals']['files']}, lines={metrics['totals']['lines']}")
