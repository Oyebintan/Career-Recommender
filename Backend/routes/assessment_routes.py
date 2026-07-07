from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from flask_login import login_required, current_user

from extensions import db
from models.assessment import Assessment, AssessmentAnswer
from models.recommendation import Recommendation
from services.dataset_loader import DatasetLoader
from services.recommendation_service import RecommendationService

assessment_bp = Blueprint("assessment", __name__)

_loader = DatasetLoader()
_engine = RecommendationService()


# ── Show assessment form ──────────────────────────────────────────
@assessment_bp.route("/assessment")
@login_required
def assessment():
    questions_df = _loader.load_assessment_questions()

    questions  = questions_df.to_dict(orient="records")
    categories = questions_df["category"].unique().tolist()

    return render_template(
        "assessment.html",
        questions=questions,
        categories=categories,
        total=len(questions),
    )


# ── Submit assessment answers ─────────────────────────────────────
@assessment_bp.route("/assessment/submit", methods=["POST"])
@login_required
def submit():
    questions_df = _loader.load_assessment_questions()
    question_ids = questions_df["question_id"].tolist()

    answers = {}
    for qid in question_ids:
        raw = request.form.get(f"q_{qid}")
        if raw is None:
            flash("Please answer all questions before submitting.", "error")
            return redirect(url_for("assessment.assessment"))
        try:
            value = int(raw)
            if value not in range(1, 6):
                raise ValueError
        except ValueError:
            flash("Invalid answer detected. Please try again.", "error")
            return redirect(url_for("assessment.assessment"))
        answers[qid] = value

    new_assessment = Assessment(user_id=current_user.id)
    db.session.add(new_assessment)
    db.session.flush()

    for qid, value in answers.items():
        db.session.add(AssessmentAnswer(
            assessment_id = new_assessment.id,
            question_id   = qid,
            answer        = value,
        ))

    top_careers = _engine.get_top_careers(answers, top_n=3)

    for rank, (career_name, score) in enumerate(top_careers, start=1):
        db.session.add(Recommendation(
            assessment_id = new_assessment.id,
            career_name   = career_name,
            score         = score,
            rank          = rank,
        ))

    db.session.commit()

    return redirect(url_for(
        "recommendation.results",
        assessment_id=new_assessment.id
    ))


# ── Review (legacy) → redirect straight to results ────────────────
# The assessment flow now goes directly from submission to the results
# page (see submit() above), matching the documented user journey. This
# route is kept only so any previously-shared /assessment/review links
# still resolve instead of 404-ing.
@assessment_bp.route("/assessment/review/<int:assessment_id>")
@login_required
def review(assessment_id):
    return redirect(url_for(
        "recommendation.results",
        assessment_id=assessment_id
    ))