"""
Run from the Backend/ directory:
    python tests/test_db_connection.py
"""
from app import app, db
from models import User

with app.app_context():
    if not User.query.filter_by(email="test@example.com").first():
        u = User(name="Test User", email="test@example.com")
        u.set_password("password123")
        db.session.add(u)
        db.session.commit()
        print("Created test user.")
    else:
        print("Test user already exists.")

    u = User.query.filter_by(email="test@example.com").first()
    print("User found:", u)
    print("Password check (correct):", u.check_password("password123"))
    print("Password check (wrong):", u.check_password("wrongpassword"))