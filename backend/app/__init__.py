"""Flask application factory."""
import os

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

    # Never allow the development fallback key to be used in production.
    # Tests may supply an explicit test_config, but production deployments must
    # provide SECRET_KEY in the hosting environment.
    if app.config.get("APP_ENV") == "production":
        production_secret = os.environ.get("SECRET_KEY")
        if not production_secret:
            raise RuntimeError("SECRET_KEY must be set in the environment when APP_ENV=production")
        app.config["SECRET_KEY"] = production_secret
        app.config["DEBUG"] = False

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
    return app
