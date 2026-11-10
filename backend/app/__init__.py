"""Flask application factory."""
import sqlite3

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from . import auth, db
from .config import REPO_ROOT, Config
from .routes import crud, timetable


def create_app(test_config: dict | None = None) -> Flask:
    # Serve the frontend/ folder at the site root so pages and API share one origin
    # (no CORS needed): http://127.0.0.1:5000/login.html
    app = Flask(
        __name__,
        static_folder=str(REPO_ROOT / "frontend"),
        static_url_path="",
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(crud.bp)
    app.register_blueprint(timetable.bp)

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    # Ticket 6: a broken database rule (clash, duplicate, missing reference) is a 409 with a
    # reason, never a 500 page.
    @app.errorhandler(sqlite3.IntegrityError)
    def handle_integrity_error(exc):
        try:
            db.get_db().rollback()
        except Exception:  # nothing to roll back
            pass
        return jsonify(error=str(exc)), 409

    # Ticket 6: the API contract says every API error is {"error": "..."}.
    # Only /api/ paths are changed; the frontend's own pages keep Flask's normal error pages.
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        if request.path.startswith("/api/"):
            return jsonify(error=exc.description), exc.code
        return exc

    # TODO (Ticket 12): decide how the frontend is hosted in production (see docs/deployment.md).
    return app
