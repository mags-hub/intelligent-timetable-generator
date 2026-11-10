"""Shared pytest fixtures."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))              # makes `scheduling` importable
sys.path.insert(0, str(ROOT / "backend"))  # makes `app` importable


@pytest.fixture()
def db_path(tmp_path):
    """A fresh seeded database, unique to each test."""
    path = tmp_path / "test.db"
    subprocess.run(
        [sys.executable, str(ROOT / "database" / "build_db.py"), "--db", str(path)],
        check=True,
        capture_output=True,
    )
    return path


@pytest.fixture()
def app(db_path):
    from app import create_app
    return create_app({"TESTING": True, "DATABASE": str(db_path), "SECRET_KEY": "test"})


@pytest.fixture()
def client(app):
    return app.test_client()
