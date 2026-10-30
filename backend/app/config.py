"""Application settings.

Development can use the documented local fallback key. Production must provide
SECRET_KEY through the hosting environment; real secrets must never be committed.
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ENV = os.environ.get("APP_ENV", "development").strip().lower()


class Config:
    APP_ENV = APP_ENV
    DEBUG = APP_ENV != "production"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-only-change-me"
    DATABASE = os.environ.get("DATABASE", str(REPO_ROOT / "database" / "timetable.db"))
