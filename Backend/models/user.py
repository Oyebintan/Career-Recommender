from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)   # nullable for OAuth users
    google_id     = db.Column(db.String(120), unique=True, nullable=True, index=True)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    profile = db.relationship(
        "Profile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    assessments = db.relationship(
        "Assessment", backref="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"