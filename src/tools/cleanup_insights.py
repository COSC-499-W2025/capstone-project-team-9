from __future__ import annotations
import argparse
from typing import Tuple
from pathlib import Path
import sys

# allowed "python -m src.tools.cleanup_insights"
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.db_config import get_connection  # noqa: E402

# Handle optional import for different psycopg versions
try:
    from psycopg import errors as pg_errors  # psycopg v3
except Exception:  # pragma: no cover
    pg_errors = None

# Check if a table exists in the database
def _table_exists(cur, table_name: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (table_name,),
    )
    return cur.fetchone() is not None

# Delete insights and the uploaded file record for a specific project
def delete_insights(project_id: int) -> Tuple[int, int, int]:
    """
    Delete previously generated insights and the uploaded file itself for a project.

    Returns: (deleted_metrics, deleted_files, deleted_projects)
      - project_metrics: deleted by project_id
      - file_contents:  deleted by uploaded_file_id (FK -> uploaded_files.id == project_id)
      - uploaded_files: deleted by id
    """
    deleted_metrics = 0
    deleted_files = 0
    deleted_projects = 0

    with get_connection() as conn, conn.cursor() as cur:
        # Clean up project_metrics if the table exists
        try:
            if _table_exists(cur, "project_metrics"):
                cur.execute("DELETE FROM project_metrics WHERE project_id = %s;", (project_id,))
                deleted_metrics = cur.rowcount or 0
        except Exception as e:
            # Some setups may not have project_metrics table
            # If the error indicates undefined table, we ignore it
            if pg_errors and isinstance(e, getattr(pg_errors, "UndefinedTable", tuple())):
                deleted_metrics = 0
            else:
                # Re-raise unexpected exceptions
                raise

        # Clean up file_contents
        cur.execute("DELETE FROM file_contents WHERE uploaded_file_id = %s;", (project_id,))
        deleted_files = cur.rowcount or 0

        # Finally remove the uploaded_files record itself
        cur.execute("DELETE FROM uploaded_files WHERE id = %s;", (project_id,))
        deleted_projects = cur.rowcount or 0

        conn.commit()

    return deleted_metrics, deleted_files, deleted_projects


# Entry point for command-line execution
def main():
    ap = argparse.ArgumentParser(description="Delete previously generated insights and the uploaded file for a project.")
    ap.add_argument("--project-id", "-p", type=int, required=True, help="uploaded_files.id / project_id to clean")
    args = ap.parse_args()

    m, f, p = delete_insights(args.project_id)
    print(
        f"[CLEANUP] project_id={args.project_id} | "
        f"project_metrics deleted={m}, file_contents deleted={f}, uploaded_files deleted={p}"
    )


if __name__ == "__main__":
    main()
