"""Settings. Override with environment variables in production (Ticket 12)."""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class Config:
    # TODO (Ticket 12): set SECRET_KEY in the hosting environment. Never commit a real key.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DATABASE = os.environ.get("DATABASE", str(REPO_ROOT / "database" / "timetable.db"))
