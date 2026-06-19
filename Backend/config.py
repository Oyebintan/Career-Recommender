import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY              = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/career_recommender",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG                   = os.environ.get("FLASK_DEBUG", "True") == "True"

    # Google OAuth  (optional — Google button hidden if not set)
    GOOGLE_CLIENT_ID        = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET    = os.environ.get("GOOGLE_CLIENT_SECRET")