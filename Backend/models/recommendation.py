from extensions import db


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessments.id"), nullable=False
    )
    career_name = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)
    rank = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Recommendation {self.career_name!r} rank={self.rank}>"