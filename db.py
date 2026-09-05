"""Run a .sql file against funnel.db and return rows as dicts.

Deliberately tiny. All the analysis lives in the .sql files; this only opens
the database and hands back what the query returned.
"""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "funnel.db"
SQL_DIR = ROOT / "sql"


def run_query_file(name: str, db_path: Path = DB_PATH) -> list[dict]:
    if not db_path.exists():
        raise FileNotFoundError(f"{db_path} not found — run `python3 generate.py` first.")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute((SQL_DIR / name).read_text()).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]
