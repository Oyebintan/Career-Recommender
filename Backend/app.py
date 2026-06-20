import os
from flask import Flask
from config import Config
from extensions import db, login_manager, oauth

import models  # noqa: registers all models with SQLAlchemy metadata
from models.user import User

from routes.auth_routes       import auth_bp
from routes.profile_routes    import profile_bp
from routes.assessment_routes import assessment_bp
from routes.recommendation_routes import recommendation_bp
from routes.dashboard_routes  import dashboard_bp


def create_app():
    # Point Flask at the Frontend folder for templates and static files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "..", "Frontend", "templates"),
        static_folder=os.path.join(base_dir, "..", "Frontend", "static"),
        static_url_path="/static",
    )

    # --- NEW HTTPS ENFORCER ---
    class ForceHTTPS(object):
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            # Violently force Flask to recognize the connection as secure
            environ['wsgi.url_scheme'] = 'https'
            return self.app(environ, start_response)

    app.wsgi_app = ForceHTTPS(app.wsgi_app)

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

    return app

app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    # Strictly bind to Hugging Face's required network interface
    app.run(host="0.0.0.0", port=7860, debug=False)

    def __call__(self, environ, start_response):
        # Violently force Flask to recognize the connection as secure
        environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)

app.wsgi_app = ForceHTTPS(app.wsgi_app)
# --------------------------

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

app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


import os

if __name__ == "__main__":
    # Strictly bind to Hugging Face's required network interface
    app.run(host="0.0.0.0", port=7860, debug=False)