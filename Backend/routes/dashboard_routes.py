from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.assessment import Assessment
from models.recommendation import Recommendation

dashboard_bp = Blueprint("dashboard", __name__)


# ── Dashboard ─────────────────────────────────────────────────────
@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    assessments = Assessment.query.filter_by(
        user_id = current_user.id
    ).order_by(Assessment.created_at.desc()).all()

    history = []
    for assessment in assessments:
        top_rec = Recommendation.query.filter_by(
            assessment_id = assessment.id,
            rank          = 1,
        ).first()

        history.append({
            "assessment": assessment,
            "top_career": top_rec.career_name if top_rec else "N/A",
            "top_score":  top_rec.score        if top_rec else 0,
        })

    return render_template(
        "dashboard.html",
        history     = history,
        total_taken = len(assessments),
    )