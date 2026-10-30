"""Deployment safety checks for Ticket 12."""
import pytest

from app import create_app


def test_production_requires_secret_key(monkeypatch, db_path):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        create_app({"TESTING": True, "DATABASE": str(db_path), "APP_ENV": "production"})


def test_production_starts_with_environment_secret(monkeypatch, db_path):
    monkeypatch.setenv("SECRET_KEY", "test-production-secret")
    app = create_app({"TESTING": True, "DATABASE": str(db_path), "APP_ENV": "production"})
    assert app.config["SECRET_KEY"] == "test-production-secret"
    assert app.config["DEBUG"] is False


def test_development_has_debug_enabled_by_default():
    from app.config import Config

    assert Config.APP_ENV in {"development", "test"}
    assert Config.DEBUG is True
