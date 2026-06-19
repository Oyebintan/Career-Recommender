from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models.assessment import Assessment
from models.recommendation import Recommendation
from services.dataset_loader import DatasetLoader
from services.skill_gap_service import SkillGapService

recommendation_bp = Blueprint("recommendation", __name__)

_loader  = DatasetLoader()
_gap_svc = SkillGapService()


# ── Career results page ───────────────────────────────────────────
@recommendation_bp.route("/results/<int:assessment_id>")
@login_required
def results(assessment_id):
    assessment = Assessment.query.filter_by(
        id      = assessment_id,
        user_id = current_user.id,
    ).first_or_404()

    recommendations = Recommendation.query.filter_by(
        assessment_id = assessment_id
    ).order_by(Recommendation.rank).all()

    descriptions_df = _loader.load_career_descriptions()
    desc_map = {
        row["career_name"]: row
        for _, row in descriptions_df.iterrows()
    }

    career_cards = []
    for rec in recommendations:
        info = desc_map.get(rec.career_name, {})
        career_cards.append({
            "rank":                  rec.rank,
            "career_name":           rec.career_name,
            "score":                 rec.score,
            "description":           info.get("description", "N/A"),
            "salary_range":          info.get("salary_range", "N/A"),
            "education_requirement": info.get("education_requirement", "N/A"),
        })

    return render_template(
        "career_results.html",
        assessment   = assessment,
        career_cards = career_cards,
    )


# ── Career detail page ────────────────────────────────────────────
@recommendation_bp.route("/career/<career_name>")
@login_required
def career_detail(career_name):
    descriptions_df = _loader.load_career_descriptions()
    profiles_df     = _loader.load_career_profiles()

    desc_row = descriptions_df[
        descriptions_df["career_name"] == career_name
    ]
    prof_row = profiles_df[
        profiles_df["career_name"] == career_name
    ]

    if desc_row.empty:
        flash(f'Career "{career_name}" not found.', "error")
        return redirect(url_for("dashboard.dashboard"))

    career = desc_row.iloc[0].to_dict()
    career["domain"] = (
        prof_row.iloc[0]["domain"] if not prof_row.empty else "N/A"
    )

    skills_df = _loader.load_career_skills()
    skills = skills_df[
        skills_df["career_name"] == career_name
    ]["skill"].tolist()

    return render_template(
        "career_details.html",
        career = career,
        skills = skills,
    )


# ── Skill gap page ────────────────────────────────────────────────
@recommendation_bp.route(
    "/skill-gap/<int:assessment_id>/<career_name>",
    methods=["GET", "POST"]
)
@login_required
def skill_gap(assessment_id, career_name):
    Assessment.query.filter_by(
        id      = assessment_id,
        user_id = current_user.id,
    ).first_or_404()

    gap_result = None

    if request.method == "POST":
        raw_skills  = request.form.get("user_skills", "")
        user_skills = [
            s.strip() for s in raw_skills.split(",") if s.strip()
        ]

        if not user_skills:
            flash("Please enter at least one skill.", "error")
        else:
            gap_result = _gap_svc.analyze_skill_gap(
                career_name, user_skills
            )

    return render_template(
        "skill_gap.html",
        career_name   = career_name,
        assessment_id = assessment_id,
        gap_result    = gap_result,
    )