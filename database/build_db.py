#!/usr/bin/env python3
"""
Build the timetable database from scratch in ONE command (Ticket 8).

    python database/build_db.py                 # -> database/timetable.db
    python database/build_db.py --db my.db      # custom path
    python database/build_db.py --no-seed       # schema only
    python database/build_db.py --no-sample     # skip the sample timetable

What it does
  1. deletes the old DB file (so a build is always fresh)
  2. applies every file in database/migrations/ in order  (001_*.sql, 002_*.sql ...)
  3. applies reference seeds, the sample timetable, and DEV-ONLY users
  4. records applied migrations in schema_migrations

Requires: Python 3.9+, and `werkzeug` (already installed with Flask) for
password hashing so the hashes work with the Flask login in Ticket 5.
"""
import argparse
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MIGRATIONS = HERE / "migrations"
SEEDS = HERE / "seeds"
DEFAULT_DB = HERE / "timetable.db"

# DEV ONLY. Never use these credentials outside local development.
DEV_PASSWORD = "ChangeMe123!"


def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def apply_migrations(con: sqlite3.Connection) -> None:
    con.execute(
        """CREATE TABLE IF NOT EXISTS schema_migrations (
               filename   TEXT PRIMARY KEY,
               applied_at TEXT NOT NULL DEFAULT (datetime('now'))
           )"""
    )
    done = {r[0] for r in con.execute("SELECT filename FROM schema_migrations")}
    for f in sorted(MIGRATIONS.glob("*.sql")):
        if f.name in done:
            continue
        con.executescript(f.read_text(encoding="utf-8"))
        con.execute("INSERT INTO schema_migrations (filename) VALUES (?)", (f.name,))
        con.commit()
        print(f"  migration applied: {f.name}")


def apply_seed(con: sqlite3.Connection, filename: str) -> None:
    con.executescript((SEEDS / filename).read_text(encoding="utf-8"))
    con.commit()
    print(f"  seed applied:      {filename}")


def seed_dev_users(con: sqlite3.Connection) -> None:
    try:
        from werkzeug.security import generate_password_hash
    except ImportError:
        print("  (skipped dev users: install werkzeug / Flask first)")
        return
    h = generate_password_hash(DEV_PASSWORD)
    con.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
        ("admin", h),
    )
    con.execute(
        "INSERT INTO users (username, password_hash, role, lecturer_id) "
        "SELECT 'bukasa', ?, 'lecturer', id FROM lecturers WHERE name = 'Bukasa'",
        (h,),
    )
    con.execute(
        "INSERT INTO users (username, password_hash, role, group_id) "
        "SELECT 'student_bsc1', ?, 'student', id FROM student_groups WHERE name = 'BSC1-G1'",
        (h,),
    )
    con.commit()
    print(f"  dev users created: admin, bukasa (lecturer), student_bsc1  [password: {DEV_PASSWORD}]")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the timetable database.")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--no-seed", action="store_true", help="schema only")
    ap.add_argument("--no-sample", action="store_true", help="skip the sample timetable")
    args = ap.parse_args()

    if args.db.exists():
        args.db.unlink()
    print(f"Building {args.db}")

    con = connect(args.db)
    try:
        apply_migrations(con)
        if not args.no_seed:
            apply_seed(con, "001_reference_data.sql")
            if not args.no_sample:
                apply_seed(con, "002_sample_timetable_bsc1_g1.sql")
            seed_dev_users(con)
    except sqlite3.Error as e:
        print(f"BUILD FAILED: {e}", file=sys.stderr)
        return 1
    finally:
        con.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
