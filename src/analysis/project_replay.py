"""Build replay timeline and interview talking points from project file metadata."""

import json
import re
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


def _format_date(iso_day: str) -> str:
    try:
        d = date.fromisoformat(iso_day)
        return d.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return iso_day


def _build_human_event_title(d: Dict[str, Any], day: str) -> str:
    """Build a human-readable one-line summary for a single day's activity."""
    parts = []
    n = d.get("new_files", 0)
    code = d.get("code_files_added", 0)
    tests = d.get("tests_added", 0)
    docs = d.get("docs_added", 0)
    config = d.get("config_added", 0)

    if code:
        parts.append(f"{code} source file{'s' if code != 1 else ''}")
    if tests:
        parts.append(f"{tests} test{'s' if tests != 1 else ''}")
    if docs:
        parts.append(f"{docs} doc{'s' if docs != 1 else ''}")
    if config and not parts:
        parts.append(f"{config} config file{'s' if config != 1 else ''}")
    elif config:
        parts.append(f"{config} config")

    if not parts:
        parts.append(f"{n} file{'s' if n != 1 else ''}")

    return ", ".join(parts)


def _build_project_narrative(
    events: List[Dict[str, Any]],
    duration_days: int,
    total_files: int,
) -> str:
    """Build a 1–2 sentence narrative of the full project build."""
    if not events:
        return "No build activity recorded yet."

    n_active = len(events)
    if duration_days <= 1 and n_active == 1:
        d = events[0]["delta"]
        return f"Single day build: shipped {d['new_files']} files — {_build_human_event_title(d, events[0]['t'])}."

    # Find phases: early (first third), middle, late (last third)
    third = max(1, len(events) // 3)
    early = events[:third]
    mid = events[third : 2 * third]
    late = events[2 * third :]

    def sum_files(e_list: List[Dict[str, Any]]) -> int:
        return sum(e["delta"].get("new_files", 0) for e in e_list)

    def sum_tests(e_list: List[Dict[str, Any]]) -> int:
        return sum(e["delta"].get("tests_added", 0) for e in e_list)

    def sum_docs(e_list: List[Dict[str, Any]]) -> int:
        return sum(e["delta"].get("docs_added", 0) for e in e_list)

    early_files = sum_files(early)
    mid_files = sum_files(mid)
    late_files = sum_files(late)
    total_tests = sum_tests(events)
    total_docs = sum_docs(events)

    phrases = []
    phrases.append(f"Over {duration_days} days you shipped {total_files} files across {n_active} active days.")

    if early_files > mid_files + late_files:
        phrases.append("Strongest momentum was early — got the core in place fast.")
    elif late_files > early_files:
        phrases.append("Ramped up toward the end as you closed out features.")
    else:
        phrases.append("Steady pace throughout.")

    if total_tests > 0:
        test_frac = total_tests / total_files
        if test_frac >= 0.2:
            phrases.append("You invested in tests along the way.")
        else:
            phrases.append("Tests were part of the mix.")
    if total_docs > 0:
        phrases.append("Added documentation where it mattered.")

    return " ".join(phrases)


def _build_talking_points(
    events: List[Dict[str, Any]],
    duration_days: int,
    total_files: int,
) -> List[Dict[str, Any]]:
    """Build 5–7 interview-ready talking points with suggested phrasing."""
    points: List[Dict[str, Any]] = []

    if not events:
        return points

    highest_velocity = max(events, key=lambda e: e["delta"]["new_files"])
    quality_events = [e for e in events if e["delta"].get("tests_added", 0) > 0]
    polish_events = [e for e in events if e["delta"].get("docs_added", 0) > 0]
    code_heavy = [e for e in events if e["delta"].get("code_files_added", 0) >= 2]

    total_tests = sum(e["delta"].get("tests_added", 0) for e in events)
    total_docs = sum(e["delta"].get("docs_added", 0) for e in events)

    points.append({
        "question": "What was your most productive day on this project?",
        "insight": f"On {_format_date(highest_velocity['t'])}, you shipped {highest_velocity['delta']['new_files']} files.",
        "suggested_phrase": f"\"That day I was in flow — got {_build_human_event_title(highest_velocity['delta'], highest_velocity['t'])} in place.\"",
        "evidence": highest_velocity.get("evidence", []),
    })

    if quality_events:
        best = max(quality_events, key=lambda e: e["delta"]["tests_added"])
        points.append({
            "question": "Tell me about a time you balanced speed with quality.",
            "insight": f"On {_format_date(best['t'])}, you added {best['delta']['tests_added']} test files.",
            "suggested_phrase": "\"I made sure we had test coverage before moving on — it caught bugs early and gave me confidence to refactor.\"",
            "evidence": best.get("evidence", []),
        })

    if polish_events:
        best = max(polish_events, key=lambda e: e["delta"]["docs_added"])
        points.append({
            "question": "How do you approach documentation?",
            "insight": f"On {_format_date(best['t'])}, you added {best['delta']['docs_added']} doc files.",
            "suggested_phrase": "\"I believe good docs help the next person — and future me. I made time for a README and setup guide.\"",
            "evidence": best.get("evidence", []),
        })

    if len(events) >= 3 and duration_days >= 3:
        points.append({
            "question": "How did you structure your work over time?",
            "insight": f"Active across {len(events)} days over {duration_days} total.",
            "suggested_phrase": "\"I spread the work over time — core first, then tests and docs as things solidified.\"",
            "evidence": [],
        })

    if code_heavy and total_files >= 5:
        points.append({
            "question": "What does your development process look like?",
            "insight": f"Shipped {total_files} files with a mix of source, tests, and docs.",
            "suggested_phrase": "\"I like to iterate — get something working, then add tests and clean up. This project followed that pattern.\"",
            "evidence": [],
        })

    if total_tests > 0 and total_docs > 0:
        points.append({
            "question": "How do you know when a feature is done?",
            "insight": f"You added {total_tests} test files and {total_docs} doc files.",
            "suggested_phrase": "\"For me, done means it works, it’s tested, and the next person can understand it.\"",
            "evidence": [],
        })

    return points[:7]


def build_project_replay(file_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a deterministic replay payload from file metadata.
    Includes full-duration narrative and interview-ready talking points.

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
            "project_narrative": "No build activity recorded yet.",
            "interview_mode": {"talking_points": []},
        }

    events: List[Dict[str, Any]] = []
    for day in days:
        d = grouped[day]
        title = _build_human_event_title(d, day)
        event_type = "structure"
        if d["tests_added"] >= max(2, d["new_files"] // 2):
            event_type = "quality"
        elif d["docs_added"] >= max(2, d["new_files"] // 2):
            event_type = "polish"
        elif d["code_files_added"] >= max(2, d["new_files"] // 2):
            event_type = "build"

        events.append(
            {
                "t": day,
                "t_formatted": _format_date(day),
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
    total_files = sum(d["new_files"] for d in grouped.values())

    milestones = [
        {"label": "Kickoff", "t": start_day, "t_formatted": _format_date(start_day)},
    ]
    if len(days) >= 3:
        mid_day = days[len(days) // 2]
        milestones.append({"label": "Midpoint", "t": mid_day, "t_formatted": _format_date(mid_day)})
    milestones.append({"label": "Delivery", "t": end_day, "t_formatted": _format_date(end_day)})

    project_narrative = _build_project_narrative(events, duration_days, total_files)
    talking_points = _build_talking_points(events, duration_days, total_files)

    return {
        "duration_days": duration_days,
        "total_files": total_files,
        "events": events,
        "milestones": milestones,
        "project_narrative": project_narrative,
        "interview_mode": {"talking_points": talking_points},
    }


def enrich_replay_with_ai(
    replay: Dict[str, Any],
    project_name: str = "Project",
) -> Dict[str, Any]:
    """
    Use Gemini to enrich the replay with a richer narrative and interview points.
    Falls back to the original replay if AI fails.
    """
    try:
        from external_services.gemini_client import generate_text
    except Exception:
        return replay

    prompt = f"""You are helping someone prepare for job interviews. They built a software project and we have a build timeline.

Project name: {project_name}
Duration: {replay.get('duration_days', 0)} days
Total files: {replay.get('total_files', 0)}

Timeline (each day's activity):
{json.dumps([{"date": e.get("t"), "title": e.get("title"), "delta": e.get("delta", {})} for e in replay.get("events", [])[:20]], indent=2)}

Current summary: {replay.get('project_narrative', '')}

Respond with valid JSON only, no markdown:
{{
  "project_narrative": "1–2 sentences that tell the story of this build in plain language. Emphasize what a hiring manager would care about: delivery pace, quality focus, documentation.",
  "talking_points": [
    {{
      "question": "Interview question this addresses",
      "insight": "One line of context from the data",
      "suggested_phrase": "Exact phrase they could say out loud, in quotes"
    }}
  ]
}}

Give 5–7 talking_points. Each suggested_phrase should be something a real person could say in an interview — natural, confident, not robotic."""

    try:
        response = generate_text(
            prompt,
            system_instruction="You output only valid JSON. No markdown, no code fences.",
            temperature=0.3,
        )
        text = response.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)

        narrative = data.get("project_narrative") or replay.get("project_narrative", "")
        raw_points = data.get("talking_points") or []

        talking_points = []
        for p in raw_points[:7]:
            talking_points.append({
                "question": p.get("question", ""),
                "insight": p.get("insight", ""),
                "suggested_phrase": p.get("suggested_phrase", ""),
                "evidence": p.get("evidence", []),
            })

        return {
            **replay,
            "project_narrative": narrative,
            "interview_mode": {"talking_points": talking_points},
            "ai_enriched": True,
        }
    except Exception:
        return replay
