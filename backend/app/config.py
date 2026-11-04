"""Settings. Override with environment variables in production (Ticket 12)."""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class Config:
    # TODO (Ticket 12): set SECRET_KEY in the hosting environment. Never commit a real key.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DATABASE = os.environ.get("DATABASE", str(REPO_ROOT / "database" / "timetable.db"))

    # Session cookie (Ticket 5): scripts cannot read it, and other sites cannot send it with a
    # cross-site POST. Set COOKIE_SECURE=1 when the site is served over HTTPS.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE") == "1"
