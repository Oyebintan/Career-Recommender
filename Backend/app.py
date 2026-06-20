import os
import logging
import traceback
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, oauth

import models  # noqa: registers all models with SQLAlchemy metadata
from models.user import User

from routes.auth_routes       import auth_bp
from routes.profile_routes    import profile_bp
from routes.assessment_routes import assessment_bp
from routes.recommendation_routes import recommendation_bp
from routes.dashboard_routes  import dashboard_bp

from services.dataset_loader import DatasetLoader, DatasetLoaderError

# Print logs to stdout with level + timestamp. Most hosting platforms
# (Hugging Face Spaces, Render, Railway, etc.) capture stdout/stderr into
# their built-in log viewer automatically, so this is enough to see what
# actually broke instead of just a generic "Internal Server Error" page.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("career_recommender")


def create_app():
    # Fail fast and loud at startup if the datasets can't be found, rather
    # than letting individual pages silently render with empty data.
    try:
        DatasetLoader()
    except DatasetLoaderError as e:
        raise RuntimeError(
            f"Startup check failed — career datasets could not be located.\n{e}"
        ) from e

    # Point Flask at the Frontend folder for templates and static files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "..", "Frontend", "templates"),
        static_folder=os.path.join(base_dir, "..", "Frontend", "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    # Register Google OAuth provider (only when credentials are present)
    if app.config.get("GOOGLE_CLIENT_ID"):
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()

    # ── Error handlers ──────────────────────────────────────────────
    # Log the full traceback server-side (visible in your host's log
    # viewer) and show the visitor a branded, friendly page instead of
    # Werkzeug's bare "Internal Server Error" text dump.
    @app.errorhandler(500)
    def handle_500(e):
        logger.error("Unhandled 500 error:\n%s", traceback.format_exc())
        return render_template("error.html", code=500,
                                message="Something went wrong on our end."), 500

    @app.errorhandler(404)
    def handle_404(e):
        return render_template("error.html", code=404,
                                message="That page doesn't exist."), 404

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


import os

if __name__ == "__main__":
    # Strictly bind to Hugging Face's required network interface
    app.run(host="0.0.0.0", port=7860, debug=False)