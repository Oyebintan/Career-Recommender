from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app
)
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, oauth
from models.user import User

auth_bp = Blueprint("auth", __name__)


# ── Landing ───────────────────────────────────────────────────────
@auth_bp.route("/")
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("landing.html")


# ── Register ──────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm]):
            flash("All fields are required.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome, {user.name}! Let's set up your profile.", "success")
        return redirect(url_for("profile.setup"))

    return render_template("register.html")


# ── Login ─────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        login_user(user)
        flash(f"Welcome back, {user.name}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard.dashboard"))

    return render_template("login.html")


# ── Logout ────────────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ── Google OAuth: redirect to Google ─────────────────────────────
@auth_bp.route("/auth/google")
def google_login():
    if not current_app.config.get("GOOGLE_CLIENT_ID"):
        flash("Google login is not configured.", "error")
        return redirect(url_for("auth.login"))
    
    redirect_uri = "https://lammyde-career-recommender.hf.space/auth/google/callback"
    print("GOOGLE CALLBACK URI:", redirect_uri)
    
    return oauth.google.authorize_redirect(redirect_uri)


# ── Google OAuth: callback from Google ───────────────────────────
@auth_bp.route("/auth/google/callback")
def google_callback():
    if not current_app.config.get("GOOGLE_CLIENT_ID"):
        return redirect(url_for("auth.login"))

    token     = oauth.google.authorize_access_token()
    user_info = token.get("userinfo", {})

    email     = user_info.get("email", "").lower()
    name      = user_info.get("name", "User")
    google_id = user_info.get("sub", "")

    if not email:
        flash("Could not retrieve email from Google.", "error")
        return redirect(url_for("auth.login"))

    # Find by Google ID first, then by email
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id          # link existing account
        else:
            user = User(name=name, email=email, google_id=google_id)
            db.session.add(user)

    db.session.commit()
    login_user(user)

    if not user.profile:
        flash(f"Welcome, {user.name}! Let's finish setting up your profile.", "success")
        return redirect(url_for("profile.setup"))

    flash(f"Welcome back, {user.name}!", "success")
    return redirect(url_for("dashboard.dashboard"))