"""
Confirms the full Flask → SQLAlchemy → PostgreSQL round-trip works.

Run from Backend/ with the virtual environment active:
    python tests/test_db_connection.py

Requires a real DATABASE_URL in your .env file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app, db
from models import User

with app.app_context():

    existing = User.query.filter_by(email="dbtest@careerrecommender.test").first()

    if not existing:
        user = User(name="DB Test User", email="dbtest@careerrecommender.test")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        print("Created test user.")
    else:
        user = existing
        print("Test user already exists.")

    fetched = User.query.filter_by(email="dbtest@careerrecommender.test").first()

    assert fetched is not None,            "FAIL: User not found after insert"
    assert fetched.name == "DB Test User", "FAIL: Name mismatch"
    assert fetched.check_password("testpassword123"), "FAIL: Password check failed"
    assert not fetched.check_password("wrongpassword"), "FAIL: Wrong password passed"

    print(f"User:            {fetched}")
    print(f"Password valid:  {fetched.check_password('testpassword123')}")
    print(f"Wrong password:  {fetched.check_password('wrongpassword')}")
    print()
    print("ALL DATABASE CHECKS PASSED")