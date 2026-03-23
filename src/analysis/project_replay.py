"""Build replay timeline and interview talking points from project file metadata."""

from collections import defaultdict
from datetime import date
from typing import Any, Dict, List, Optional


CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".kt", ".swift",
}
DOC_EXTENSIONS = {".md", ".txt", ".rst", ".pdf", ".doc", ".docx"}
CONFIG_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env",
}


def _classify_file(file_path: str, file_extension: Optional[str]) -> str:
    path_lower = (file_path or "").lower()
    ext = (file_extension or "").lower()
    if "test" in path_lower:
        return "test"
    if "readme" in path_lower or "/docs/" in path_lower or ext in DOC_EXTENSIONS:
        return "doc"
    if ext in CONFIG_EXTENSIONS:
        return "config"
    if ext in CODE_EXTENSIONS:
        return "code"
    return "other"


def _to_iso_day(value: Any) -> Optional[str]:
    if value is None:
        return None
    if hasattr(value, "date"):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    as_text = str(value)
    return as_text[:10] if len(as_text) >= 10 else None


def build_project_replay(file_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a deterministic replay payload from file metadata.

    file_rows accepts dictionaries with:
      - file_path, file_extension, file_size
      - source_created_at or created_at timestamp-like value
    """
    grouped: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "new_files": 0,
            "tests_added": 0,
            "docs_added": 0,
            "config_added": 0,
            "code_files_added": 0,
            "bytes_added": 0,
            "evidence": [],
        }
    )

    for row in file_rows:
        event_day = _to_iso_day(row.get("source_created_at") or row.get("created_at"))
        if not event_day:
            continue

        file_path = row.get("file_path", "") or ""
        file_ext = row.get("file_extension", "") or ""
        category = _classify_file(file_path, file_ext)
        day_data = grouped[event_day]
        day_data["new_files"] += 1
        day_data["bytes_added"] += int(row.get("file_size") or 0)

        if category == "test":
            day_data["tests_added"] += 1
        elif category == "doc":
            day_data["docs_added"] += 1
        elif category == "config":
            day_data["config_added"] += 1
        elif category == "code":
            day_data["code_files_added"] += 1

        if len(day_data["evidence"]) < 3:
            day_data["evidence"].append(file_path)

    days = sorted(grouped.keys())
    if not days:
        return {
            "duration_days": 0,
            "events": [],
            "milestones": [],
            "interview_mode": {"talking_points": []},
        }

    events: List[Dict[str, Any]] = []
    for day in days:
        d = grouped[day]
        if d["tests_added"] >= max(2, d["new_files"] // 2):
            event_type = "quality"
            title = "Testing burst"
        elif d["docs_added"] >= max(2, d["new_files"] // 2):
            event_type = "polish"
            title = "Documentation and polish burst"
        elif d["code_files_added"] >= max(2, d["new_files"] // 2):
            event_type = "build"
            title = "Core build momentum"
        else:
            event_type = "structure"
            title = "Project structure evolved"

        events.append(
            {
                "t": day,
                "type": event_type,
                "title": title,
                "delta": {
                    "new_files": d["new_files"],
                    "tests_added": d["tests_added"],
                    "docs_added": d["docs_added"],
                    "code_files_added": d["code_files_added"],
                    "bytes_added": d["bytes_added"],
                },
                "evidence": d["evidence"],
            }
        )

    start_day = days[0]
    end_day = days[-1]
    duration_days = max(1, (date.fromisoformat(end_day) - date.fromisoformat(start_day)).days + 1)

    milestones = [
        {"label": "Kickoff", "t": start_day},
    ]
    if len(days) >= 3:
        milestones.append({"label": "Midpoint", "t": days[len(days) // 2]})
    milestones.append({"label": "Delivery", "t": end_day})

    highest_velocity = max(events, key=lambda e: e["delta"]["new_files"])
    quality_candidates = [e for e in events if e["delta"]["tests_added"] > 0]
    quality_event = max(quality_candidates, key=lambda e: e["delta"]["tests_added"]) if quality_candidates else None
    polish_candidates = [e for e in events if e["delta"]["docs_added"] > 0]
    polish_event = max(polish_candidates, key=lambda e: e["delta"]["docs_added"]) if polish_candidates else None

    talking_points = [
        {
            "title": "Highest delivery velocity",
            "insight": f"{highest_velocity['t']}: added {highest_velocity['delta']['new_files']} files in a single phase.",
            "evidence": highest_velocity["evidence"],
        }
    ]
    if quality_event:
        talking_points.append(
            {
                "title": "Quality investment moment",
                "insight": f"{quality_event['t']}: added {quality_event['delta']['tests_added']} test files during stabilization.",
                "evidence": quality_event["evidence"],
            }
        )
    if polish_event:
        talking_points.append(
            {
                "title": "Communication and polish push",
                "insight": f"{polish_event['t']}: documentation spike with {polish_event['delta']['docs_added']} doc files.",
                "evidence": polish_event["evidence"],
            }
        )

    return {
        "duration_days": duration_days,
        "events": events,
        "milestones": milestones,
        "interview_mode": {"talking_points": talking_points[:3]},
    }
