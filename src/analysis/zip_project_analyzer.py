from __future__ import annotations

import json
import os
import re
import zipfile
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any, Dict, List, Tuple

from common.constants import LANGUAGE_EXTENSIONS, DOCUMENT_EXTENSIONS, DESIGN_EXTENSIONS


CONFIG_EXTENSIONS = {
    ".json",
    ".yml",
    ".yaml",
    ".xml",
    ".env",
    ".ini",
    ".toml",
    ".cfg",
    ".conf",
}

ENTRYPOINT_FILES = {
    "index.html",
    "index.js",
    "main.js",
    "app.js",
    "server.js",
    "index.ts",
    "main.ts",
    "app.ts",
    "server.ts",
    "main.py",
    "app.py",
    "server.py",
    "run.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "main.go",
    "main.rs",
    "main.c",
    "main.cpp",
    "main.java",
    "application.java",
    "program.cs",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}

DEPENDENCY_FILES = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "poetry.lock",
    "setup.py",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "cargo.toml",
    "composer.json",
    "gemfile",
}

DOC_DIRS = {"docs", "doc", "documentation"}
TEST_DIRS = {"tests", "test", "__tests__"}

EXCLUDED_PARTS = {
    "__macosx",
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}

BUILD_ARTIFACT_PARTS = {"dist", "build", "target", "out"}

README_PATTERN = re.compile(r"(^|/)(readme)(\.[^/]*)?$", re.IGNORECASE)
LICENSE_PATTERN = re.compile(r"(^|/)(license|copying)(\.[^/]*)?$", re.IGNORECASE)

TEST_FILE_PATTERNS = [
    re.compile(r"(^|/|\\)test_.+\.(py|js|ts|java|cs|rb|go|rs)$", re.IGNORECASE),
    re.compile(r"(^|/|\\).+_test\.(py|js|ts|java|cs|rb|go|rs)$", re.IGNORECASE),
    re.compile(r"\.(spec|test)\.(js|ts|jsx|tsx)$", re.IGNORECASE),
]

USAGE_PATTERNS = [
    ("usage", re.compile(r"\busage\b", re.IGNORECASE)),
    ("getting_started", re.compile(r"getting started", re.IGNORECASE)),
    ("installation", re.compile(r"\binstallation\b", re.IGNORECASE)),
    ("install", re.compile(r"\binstall\b", re.IGNORECASE)),
    ("quickstart", re.compile(r"\bquickstart\b", re.IGNORECASE)),
    ("how_to_run", re.compile(r"how to run", re.IGNORECASE)),
    ("run", re.compile(r"\brun\b", re.IGNORECASE)),
]

INCOMPLETE_PATTERNS = [
    ("todo", re.compile(r"\btodo\b", re.IGNORECASE)),
    ("fixme", re.compile(r"\bfixme\b", re.IGNORECASE)),
    ("wip", re.compile(r"\bwip\b", re.IGNORECASE)),
    ("work_in_progress", re.compile(r"work in progress", re.IGNORECASE)),
    ("not_working", re.compile(r"not working", re.IGNORECASE)),
    ("broken", re.compile(r"\bbroken\b", re.IGNORECASE)),
    ("incomplete", re.compile(r"\bincomplete\b", re.IGNORECASE)),
    ("unfinished", re.compile(r"\bunfinished\b", re.IGNORECASE)),
    ("coming_soon", re.compile(r"coming soon", re.IGNORECASE)),
    ("tbd", re.compile(r"\btbd\b", re.IGNORECASE)),
]


def _zip_timestamps(zip_path: str, indexed: Dict[str, zipfile.ZipInfo]) -> Dict[str, Any]:
    """Get zip file mtime (on disk) and earliest entry date inside zip."""
    out = {}
    try:
        out["zip_file_mtime"] = datetime.fromtimestamp(os.path.getmtime(zip_path)).isoformat() + "Z"
    except (OSError, ValueError):
        pass
    dates = []
    for info in indexed.values():
        if info.date_time and len(info.date_time) >= 6:
            y, mo, d, h, mi, s = info.date_time[:6]
            if 1980 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31:
                try:
                    dates.append(datetime(y, mo, d, h, mi, s).isoformat() + "Z")
                except ValueError:
                    pass
    if dates:
        out["zip_earliest_entry"] = min(dates)
    return out


def analyze_zip_project(zip_path: str, max_readme_bytes: int = 65536) -> Dict[str, Any]:
    """
    Analyze a zip archive and infer if it looks like a finished, working project.
    Uses local, heuristic signals only (no execution).
    """
    zip_path = os.path.abspath(zip_path)
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Not a valid zip archive: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        file_infos = [info for info in zf.infolist() if not info.is_dir()]
        if not file_infos:
            return _empty_result(zip_path, "empty_archive")

        normalized = [_normalize_zip_path(info.filename) for info in file_infos]
        common_root, rel_paths = _strip_common_root(normalized)

        indexed: Dict[str, zipfile.ZipInfo] = {}
        for info, rel_path in zip(file_infos, rel_paths):
            rel_path = rel_path.strip("/")
            if not rel_path:
                continue
            if rel_path in indexed:
                continue
            indexed[rel_path] = info

        signals, evidence, metrics = _analyze_paths(indexed, zf, max_readme_bytes)
        success = _score_success(signals, metrics, evidence)
        timestamps = _zip_timestamps(zip_path, indexed)

        return {
            "zip_path": zip_path,
            "project_name": _derive_project_name(zip_path, common_root),
            "root_prefix": common_root or "",
            "zip_file_mtime": timestamps.get("zip_file_mtime"),
            "zip_earliest_entry": timestamps.get("zip_earliest_entry"),
            "metrics": metrics,
            "signals": signals,
            "evidence": evidence,
            "success": success,
        }


def analyze_zip_projects_in_dir(base_dir: str, max_readme_bytes: int = 65536) -> List[Dict[str, Any]]:
    """
    Analyze every .zip file under a directory and return their success evaluations.
    """
    base_dir = os.path.abspath(base_dir)
    results: List[Dict[str, Any]] = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_PARTS]
        for filename in files:
            if filename.lower().endswith(".zip"):
                zip_path = os.path.join(root, filename)
                try:
                    results.append(analyze_zip_project(zip_path, max_readme_bytes=max_readme_bytes))
                except Exception as exc:
                    results.append(
                        {
                            "zip_path": zip_path,
                            "project_name": _derive_project_name(zip_path, None),
                            "root_prefix": "",
                            "metrics": {},
                            "signals": {},
                            "evidence": {},
                            "success": {
                                "status": "error",
                                "score": 0,
                                "confidence": 0.0,
                                "is_successful": False,
                                "reason": str(exc),
                            },
                        }
                    )
    return results


def _analyze_paths(
    indexed: Dict[str, zipfile.ZipInfo],
    zf: zipfile.ZipFile,
    max_readme_bytes: int,
) -> Tuple[Dict[str, bool], Dict[str, Any], Dict[str, Any]]:
    entrypoints: List[str] = []
    dependency_files: List[str] = []
    test_files: List[str] = []
    ci_files: List[str] = []
    readme_files: List[str] = []
    license_files: List[str] = []
    docs_files: List[str] = []
    build_artifacts: List[str] = []

    language_counts: Dict[str, int] = {}
    file_breakdown = {
        "code": 0,
        "documents": 0,
        "design": 0,
        "config": 0,
        "other": 0,
    }

    total_files = 0

    for rel_path, info in indexed.items():
        rel_path = rel_path.replace("\\", "/")
        parts = [p.lower() for p in PurePosixPath(rel_path).parts]
        if any(part in BUILD_ARTIFACT_PARTS for part in parts):
            build_artifacts.append(rel_path)
            continue
        if any(part in EXCLUDED_PARTS for part in parts):
            continue

        total_files += 1

        filename = PurePosixPath(rel_path).name
        filename_lower = filename.lower()
        path_lower = rel_path.lower()
        ext = PurePosixPath(filename).suffix.lower()

        if README_PATTERN.search(rel_path):
            readme_files.append(rel_path)
        if LICENSE_PATTERN.search(rel_path):
            license_files.append(rel_path)

        if filename_lower in ENTRYPOINT_FILES:
            entrypoints.append(rel_path)
        if filename_lower in DEPENDENCY_FILES:
            dependency_files.append(rel_path)
        if (
            "/.github/workflows/" in path_lower
            or path_lower.startswith(".github/workflows/")
            or path_lower.endswith(".circleci/config.yml")
            or path_lower.endswith(".gitlab-ci.yml")
            or path_lower.endswith("azure-pipelines.yml")
        ):
            ci_files.append(rel_path)

        if any(part in DOC_DIRS for part in parts):
            docs_files.append(rel_path)

        if any(part in TEST_DIRS for part in parts) or _matches_test_pattern(rel_path):
            test_files.append(rel_path)

        if ext in DOCUMENT_EXTENSIONS:
            file_breakdown["documents"] += 1
        elif ext in DESIGN_EXTENSIONS:
            file_breakdown["design"] += 1
        elif ext in CONFIG_EXTENSIONS or filename_lower in {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}:
            file_breakdown["config"] += 1
        elif ext in LANGUAGE_EXTENSIONS:
            file_breakdown["code"] += 1
        else:
            file_breakdown["other"] += 1

        if ext in LANGUAGE_EXTENSIONS:
            lang = LANGUAGE_EXTENSIONS[ext]
            language_counts[lang] = language_counts.get(lang, 0) + 1

    readme_path = _choose_primary_readme(readme_files)
    readme_text = _read_zip_text(zf, indexed.get(readme_path), max_readme_bytes) if readme_path else ""

    usage_hits = _match_text_patterns(readme_text, USAGE_PATTERNS)
    incomplete_hits = _match_text_patterns(readme_text, INCOMPLETE_PATTERNS)

    package_entrypoint, package_tests = _inspect_package_json(indexed, zf, max_readme_bytes)
    if package_entrypoint:
        entrypoints.append("package.json:scripts")
    if package_tests:
        test_files.append("package.json:scripts")

    entrypoints = sorted(set(entrypoints))
    dependency_files = sorted(set(dependency_files))
    test_files = sorted(set(test_files))
    ci_files = sorted(set(ci_files))
    docs_files = sorted(set(docs_files))
    build_artifacts = sorted(set(build_artifacts))

    signals = {
        "has_readme": bool(readme_path),
        "has_license": bool(license_files),
        "has_entrypoint": bool(entrypoints),
        "has_dependency_manifest": bool(dependency_files),
        "has_tests": bool(test_files),
        "has_ci": bool(ci_files),
        "has_docs": bool(docs_files) or bool(readme_path),
        "has_usage_instructions": bool(usage_hits),
        "has_incomplete_markers": bool(incomplete_hits),
        "has_code_files": file_breakdown["code"] > 0,
        "has_build_artifacts": bool(build_artifacts),
    }

    metrics = {
        "total_files": total_files,
        "file_breakdown": file_breakdown,
        "languages_detected": sorted(language_counts, key=language_counts.get, reverse=True),
        "language_counts": language_counts,
    }

    evidence = {
        "entrypoints": entrypoints,
        "dependency_manifests": dependency_files,
        "test_files": test_files,
        "ci_files": ci_files,
        "readme_file": readme_path,
        "license_files": sorted(set(license_files)),
        "docs_files": docs_files[:10],
        "usage_markers": usage_hits,
        "incomplete_markers": incomplete_hits,
        "build_artifacts": build_artifacts[:10],
    }

    return signals, evidence, metrics


def _score_success(signals: Dict[str, bool], metrics: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    score = 0

    if signals.get("has_entrypoint"):
        score += 25
    if signals.get("has_dependency_manifest"):
        score += 15
    if signals.get("has_readme"):
        score += 10
    if signals.get("has_usage_instructions"):
        score += 10
    if signals.get("has_tests"):
        score += 10
    if signals.get("has_ci"):
        score += 5
    if signals.get("has_license"):
        score += 5
    if signals.get("has_docs"):
        score += 5
    if signals.get("has_code_files"):
        score += 10

    is_static_site = "index.html" in {
        PurePosixPath(p).name.lower() for p in (evidence.get("entrypoints") or [])
    }
    if is_static_site and signals.get("has_entrypoint") and not signals.get("has_dependency_manifest"):
        score += 5

    if not signals.get("has_entrypoint"):
        score -= 15
    if not signals.get("has_code_files"):
        score -= 25
    if signals.get("has_incomplete_markers"):
        score -= 15

    score = max(0, min(100, score))

    signal_strength = sum(
        [
            signals.get("has_readme", False),
            signals.get("has_entrypoint", False),
            signals.get("has_dependency_manifest", False),
            signals.get("has_usage_instructions", False),
            signals.get("has_tests", False),
            signals.get("has_code_files", False),
        ]
    )
    confidence = round(min(1.0, signal_strength / 6.0), 2)

    if not signals.get("has_code_files"):
        status = "not_software"
    elif score >= 70 and signals.get("has_entrypoint"):
        status = "success"
    elif score >= 45:
        status = "partial"
    else:
        status = "incomplete"

    return {
        "status": status,
        "score": score,
        "confidence": confidence,
        "is_successful": status == "success",
    }


def _inspect_package_json(
    indexed: Dict[str, zipfile.ZipInfo],
    zf: zipfile.ZipFile,
    max_readme_bytes: int,
) -> Tuple[bool, bool]:
    package_paths = [p for p in indexed if PurePosixPath(p).name.lower() == "package.json"]
    if not package_paths:
        return False, False

    package_paths.sort(key=lambda p: len(PurePosixPath(p).parts))
    info = indexed.get(package_paths[0])
    text = _read_zip_text(zf, info, max_readme_bytes)
    if not text:
        return False, False

    try:
        data = json.loads(text)
    except Exception:
        return False, False

    scripts = data.get("scripts", {}) if isinstance(data, dict) else {}
    has_entrypoint = any(k in scripts for k in ("start", "dev", "build", "serve"))
    has_tests = "test" in scripts
    return has_entrypoint, has_tests


def _normalize_zip_path(name: str) -> str:
    return name.replace("\\", "/").lstrip("/")


def _strip_common_root(paths: List[str]) -> Tuple[str | None, List[str]]:
    if not paths:
        return None, []

    parts_list = [PurePosixPath(p).parts for p in paths if p]
    if not parts_list:
        return None, paths

    root = parts_list[0][0]
    if all(len(parts) > 1 and parts[0] == root for parts in parts_list):
        stripped = ["/".join(parts[1:]) for parts in parts_list]
        return root, stripped
    return None, paths


def _choose_primary_readme(readme_files: List[str]) -> str | None:
    if not readme_files:
        return None
    readme_files.sort(key=lambda p: (len(PurePosixPath(p).parts), p))
    return readme_files[0]


def _read_zip_text(zf: zipfile.ZipFile, info: zipfile.ZipInfo | None, max_bytes: int) -> str:
    if info is None:
        return ""
    try:
        with zf.open(info) as handle:
            data = handle.read(max_bytes + 1)
    except Exception:
        return ""
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _match_text_patterns(text: str, patterns: List[Tuple[str, re.Pattern]]) -> List[str]:
    if not text:
        return []
    hits = []
    for label, pattern in patterns:
        if pattern.search(text):
            hits.append(label)
    return hits


def _matches_test_pattern(path: str) -> bool:
    return any(pattern.search(path) for pattern in TEST_FILE_PATTERNS)


def _derive_project_name(zip_path: str, root_prefix: str | None) -> str:
    if root_prefix:
        return root_prefix
    base = os.path.basename(zip_path)
    return base[:-4] if base.lower().endswith(".zip") else base


def _empty_result(zip_path: str, status: str) -> Dict[str, Any]:
    return {
        "zip_path": zip_path,
        "project_name": _derive_project_name(zip_path, None),
        "root_prefix": "",
        "metrics": {},
        "signals": {},
        "evidence": {},
        "success": {
            "status": status,
            "score": 0,
            "confidence": 0.0,
            "is_successful": False,
        },
    }
