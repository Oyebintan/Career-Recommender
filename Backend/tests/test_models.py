from extensions import db
from models.user import User


def test_set_password_hashes_and_check_password_verifies(app_context):
    user = User(name="Alice", email="alice@example.com")
    user.set_password("correct-horse")

    assert user.password_hash != "correct-horse"
    assert user.check_password("correct-horse") is True
    assert user.check_password("wrong-password") is False


def test_check_password_false_when_no_password_hash_set(app_context):
    # OAuth-only users have no password hash.
    user = User(name="OAuth Bob", email="bob@example.com", google_id="g-123")
    assert user.check_password("anything") is False


def test_email_uniqueness_enforced(app_context):
    u1 = User(name="A", email="dup@example.com")
    u1.set_password("password123")
    db.session.add(u1)
    db.session.commit()

    u2 = User(name="B", email="dup@example.com")
    u2.set_password("password456")
    db.session.add(u2)

    try:
        db.session.commit()
        assert False, "expected a uniqueness violation"
    except Exception:
        db.session.rollback()
