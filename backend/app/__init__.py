"""Flask application factory."""
from flask import Flask, jsonify

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

    # TODO (Ticket 6): turn sqlite3.IntegrityError into a JSON 409 error handler, so a clash
    #                  attempt returns {"error": "..."} instead of a 500 page.
    # TODO (Ticket 12): decide how the frontend is hosted in production (see docs/deployment.md).
    return app
