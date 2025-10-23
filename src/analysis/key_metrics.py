import zipfile
from datetime import datetime
from config.db_config import get_connection
from project_manager import get_project_by_id
from src.analysis.activity_classifier import aggregate


def init_metrics_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_metrics(
            id SERIAL PRIMARY KEY,
            project_id INTEGER,
            activity_type TEXT,
            file_count INT,
            total_bytes BIGINT,
            contribution_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def read_zip(zip_path):
    files, sizes = [], {}
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            files.append(info.filename)
            sizes[info.filename] = info.file_size
    return files, sizes


def analyze_project(project_id):
    project = get_project_by_id(project_id)
    if not project:
        print("Project not found.")
        return
    files, sizes = read_zip(project["filepath"])
    agg = aggregate(files, sizes)
    save_metrics(project_id, agg)
    print_summary(project["filename"], agg)
    return agg


def save_metrics(pid, agg):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM project_metrics WHERE project_id=%s", (pid,))
    for t, v in agg.items():
        cur.execute("""
            INSERT INTO project_metrics
            (project_id, activity_type, file_count, total_bytes, contribution_score, created_at)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (pid, t, v["count"], v["bytes"], v["score"], datetime.utcnow()))
    conn.commit()
    cur.close()
    conn.close()


def print_summary(name, agg):
    print("\n----- Key Metrics for", name, "-----")
    print(f"{'Type':<12}{'Files':>8}{'Bytes':>12}{'Score':>14}")
    for t, v in sorted(agg.items(), key=lambda x: -x[1]["score"]):
        print(f"{t:<12}{v['count']:>8}{v['bytes']:>12}{v['score']:>14.2f}")
