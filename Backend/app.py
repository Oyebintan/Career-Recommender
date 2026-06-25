import os
import logging
import traceback
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, oauth

import models  # noqa: registers all models with SQLAlchemy metadata
from models.user import User

from routes.auth_routes            import auth_bp
from routes.profile_routes         import profile_bp
from routes.assessment_routes      import assessment_bp
from routes.recommendation_routes  import recommendation_bp
from routes.dashboard_routes       import dashboard_bp

from services.dataset_loader import DatasetLoader, DatasetLoaderError

# Logs go to stdout — Hugging Face Spaces captures this automatically
# in the Space's Logs tab, so any 500 error will show the full traceback.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("career_recommender")


def create_app():
    # Fail loudly at startup if datasets can't be found,
    # instead of silently serving a broken assessment page.
    try:
        DatasetLoader()
        logger.info("Dataset loader OK — datasets/custom found.")
    except DatasetLoaderError as exc:
        raise RuntimeError(
            "Startup aborted — could not locate career datasets.\n" + str(exc)
        ) from exc

    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "..", "Frontend", "templates"),
        static_folder=os.path.join(base_dir, "..", "Frontend", "static"),
        static_url_path="/static",
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    if app.config.get("GOOGLE_CLIENT_ID"):
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()

    # ── Friendly error pages ──────────────────────────────────────
    @app.errorhandler(500)
    def handle_500(e):
        logger.error("500 Internal Server Error:\n%s", traceback.format_exc())
        return render_template(
            "error.html", code=500,
            message="Something went wrong on our end. We're on it."
        ), 500

    @app.errorhandler(404)
    def handle_404(e):
        return render_template(
            "error.html", code=404,
            message="That page doesn't exist."
        ), 404

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    if os.environ.get("PORT"):
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        app.run(debug=app.config.get("DEBUG", True))