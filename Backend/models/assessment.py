from datetime import datetime, timezone

from extensions import db


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    answers = db.relationship(
        "AssessmentAnswer",
        backref="assessment",
        cascade="all, delete-orphan",
    )
    recommendations = db.relationship(
        "Recommendation",
        backref="assessment",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Assessment id={self.id} user_id={self.user_id}>"


class AssessmentAnswer(db.Model):
    __tablename__ = "assessment_answers"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessments.id"), nullable=False
    )
    question_id = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.Integer, nullable=False)  # Likert scale, 1-5

    def __repr__(self):
        return f"<AssessmentAnswer q{self.question_id}={self.answer}>"