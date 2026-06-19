from extensions import db


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True
    )
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    education_level = db.Column(db.String(80), nullable=False)
    course_of_study = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Profile id={self.id} user_id={self.user_id}>"