from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from flask_login import login_required, current_user

from extensions import db
from models.profile import Profile

profile_bp = Blueprint("profile", __name__)


# ── Profile setup / edit ──────────────────────────────────────────
@profile_bp.route("/profile/setup", methods=["GET", "POST"])
@login_required
def setup():
    # Load existing profile if user already has one
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        age             = request.form.get("age", "").strip()
        gender          = request.form.get("gender", "").strip()
        education_level = request.form.get("education_level", "").strip()
        course_of_study = request.form.get("course_of_study", "").strip()

        # ── Validation ───────────────────────────────────────────
        if not all([age, gender, education_level, course_of_study]):
            flash("All fields are required.", "error")
            return render_template("profile_setup.html", profile=profile)

        if not age.isdigit() or not (10 <= int(age) <= 100):
            flash("Please enter a valid age.", "error")
            return render_template("profile_setup.html", profile=profile)

        # ── Create or update ─────────────────────────────────────
        if profile:
            profile.age             = int(age)
            profile.gender          = gender
            profile.education_level = education_level
            profile.course_of_study = course_of_study
        else:
            profile = Profile(
                user_id         = current_user.id,
                age             = int(age),
                gender          = gender,
                education_level = education_level,
                course_of_study = course_of_study,
            )
            db.session.add(profile)

        db.session.commit()
        flash("Profile saved successfully!", "success")
        return redirect(url_for("assessment.assessment"))

    return render_template("profile_setup.html", profile=profile)