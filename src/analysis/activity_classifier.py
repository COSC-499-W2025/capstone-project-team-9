from pathlib import PurePosixPath
from math import log

EXTENSION_MAP = {
    ".py": "code", ".java": "code", ".c": "code", ".cpp": "code",
    ".h": "code", ".js": "code", ".ts": "code",
    ".md": "doc", ".txt": "doc", ".pdf": "doc",
    ".csv": "data", ".json": "data", ".xlsx": "data",
    ".png": "media", ".jpg": "media", ".jpeg": "media",
    ".yaml": "config", ".yml": "config", ".ini": "config",
}

FOLDER_HINTS = {
    "src": "code", "scripts": "code", "tests": "code",
    "docs": "doc", "data": "data", "config": "config",
    "assets": "media"
}

WEIGHTS = {"code": 3, "doc": 1.5, "data": 2, "media": 1, "config": 1, "other": 1}


def classify_file(path: str) -> str:
    p = PurePosixPath(path)
    for part in p.parts:
        if part.lower() in FOLDER_HINTS:
            return FOLDER_HINTS[part.lower()]
    ext = p.suffix.lower()
    return EXTENSION_MAP.get(ext, "other")


def aggregate(files, sizes):
    result = {}
    for f in files:
        if f.endswith("/"):
            continue
        t = classify_file(f)
        size = int(sizes.get(f, 0))
        if t not in result:
            result[t] = {"count": 0, "bytes": 0, "score": 0.0}
        result[t]["count"] += 1
        result[t]["bytes"] += size
        result[t]["score"] += log(1 + size) * WEIGHTS.get(t, 1)
    return result
