from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
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
    questions    = questions_df.to_dict(orient="records")

    # Defensive guard: if the dataset ever comes back empty (a hosting
    # path hiccup, a corrupted CSV, etc.) show a clear message instead
    # of silently rendering a broken "Step 1 of 0" page with a dead
    # Next button.
    if not questions:
        flash(
            "We couldn't load the assessment questions right now. "
            "Please try again in a moment.",
            "error",
        )
        return redirect(url_for("dashboard.dashboard"))

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
    session["last_assessment_id"] = new_assessment.id

    return redirect(url_for(
        "assessment.review",
        assessment_id=new_assessment.id
    ))


# ── Review page ───────────────────────────────────────────────────
@assessment_bp.route("/assessment/review/<int:assessment_id>")
@login_required
def review(assessment_id):
    record = Assessment.query.filter_by(
        id      = assessment_id,
        user_id = current_user.id
    ).first_or_404()

    questions_df  = _loader.load_assessment_questions()
    questions_map = {
        row["question_id"]: row["question"]
        for _, row in questions_df.iterrows()
    }

    answers = AssessmentAnswer.query.filter_by(
        assessment_id=assessment_id
    ).all()

    answer_display = [
        {
            "question": questions_map.get(a.question_id, "Unknown"),
            "answer":   a.answer,
            "label":    _likert_label(a.answer),
        }
        for a in answers
    ]

    return render_template(
        "assessment_review.html",
        assessment = record,
        answers    = answer_display,
        total      = len(answer_display),
    )


def _likert_label(value: int) -> str:
    return {
        1: "Strongly Disagree",
        2: "Disagree",
        3: "Neutral",
        4: "Agree",
        5: "Strongly Agree",
    }.get(value, "Unknown")