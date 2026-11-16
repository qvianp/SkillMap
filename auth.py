"""
SkillMap Authentication & Session Security Module
-------------------------------------------------
Handles registration, login, logout, profile updates, CSRF token verification,
and route authorization decorators using Werkzeug password hashing and Flask sessions.

AI Assistance Note:
Authentication decorators and CSRF verification helpers were built with AI
assistance and verified against OWASP session and input validation guidelines.
"""

import math
import re
import secrets
from functools import wraps
from typing import Callable
from urllib.parse import urlparse

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from database import execute_write, log_activity, query_all, query_one
from translations import SUPPORTED_LANGUAGES, t

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def is_https_request() -> bool:
    """Detect whether the current request arrived over HTTPS (directly or via proxy)."""
    if request.is_secure:
        return True
    forwarded_proto = (request.headers.get("X-Forwarded-Proto") or "").split(",")[0].strip().lower()
    if forwarded_proto == "https":
        return True
    forwarded_ssl = (request.headers.get("X-Forwarded-Ssl") or "").strip().lower()
    if forwarded_ssl == "on":
        return True
    return False


def set_language_cookie(response, lang: str) -> None:
    """Persist UI language preference cookie with iframe-safe attributes over HTTPS."""
    https = is_https_request()
    response.set_cookie(
        "skillmap_lang",
        lang,
        max_age=60 * 60 * 24 * 365,
        path="/",
        httponly=False,
        secure=https,
        samesite="None" if https else "Lax",
        partitioned=https,
    )


def _reset_session_preserving_lang() -> None:
    """Clear authentication session keys while retaining the active UI language."""
    saved_lang = session.get("lang")
    session.clear()
    if saved_lang in SUPPORTED_LANGUAGES:
        session["lang"] = saved_lang


def get_csrf_token() -> str:
    """Generate or retrieve a per-session CSRF token."""
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf() -> None:
    """Verify CSRF token for state-changing requests when CSRF is enabled."""
    if not current_app.config.get("WTF_CSRF_ENABLED", True):
        return
    session_token = session.get("_csrf_token")
    json_payload = request.get_json(silent=True)
    json_token = json_payload.get("csrf_token") if isinstance(json_payload, dict) else None
    submitted_token = (
        request.form.get("csrf_token")
        or request.headers.get("X-CSRFToken")
        or request.headers.get("X-CSRF-Token")
        or json_token
    )
    if (
        not isinstance(session_token, str)
        or not session_token
        or not submitted_token
        or not secrets.compare_digest(session_token, str(submitted_token))
    ):
        abort(400, description=t("flash.csrf_invalid"))


def load_logged_in_user() -> None:
    """Populate g.user from the authenticated Flask session before each request."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = query_one(
            """
            SELECT u.*, cp.title AS target_career_title, cp.slug AS target_career_slug
            FROM users u
            LEFT JOIN career_paths cp ON cp.id = u.target_career_id
            WHERE u.id = ?
            """,
            (user_id,),
        )
        if g.user is None:
            _reset_session_preserving_lang()


def login_required(view: Callable) -> Callable:
    """Protect routes from unauthenticated access."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            if request.path.startswith("/api/"):
                return {"error": t("api.auth_required")}, 401
            flash(t("flash.auth_required"), "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account with validated inputs and hashed password."""
    if g.user is not None:
        return redirect(url_for("main.dashboard"))

    careers = query_all("SELECT id, slug, title FROM career_paths ORDER BY title ASC")
    form_data = {"full_name": "", "email": "", "target_career_id": "", "weekly_goal_hours": "10"}

    if request.method == "POST":
        validate_csrf()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        target_career_raw = request.form.get("target_career_id", "").strip()
        weekly_goal_raw = request.form.get("weekly_goal_hours", "10").strip()

        form_data = {
            "full_name": full_name,
            "email": email,
            "target_career_id": target_career_raw,
            "weekly_goal_hours": weekly_goal_raw,
        }

        errors = []
        if len(full_name) < 2 or len(full_name) > 80:
            errors.append(t("flash.name_length"))
        if not EMAIL_REGEX.match(email):
            errors.append(t("flash.email_invalid"))
        if len(password) < 8:
            errors.append(t("flash.password_length"))
        if password != confirm_password:
            errors.append(t("flash.password_mismatch"))

        try:
            weekly_goal = float(weekly_goal_raw)
            if not math.isfinite(weekly_goal) or not (1 <= weekly_goal <= 100):
                errors.append(t("flash.weekly_goal_range"))
        except ValueError:
            weekly_goal = 10.0
            errors.append(t("flash.weekly_goal_number"))

        target_career_id = None
        if target_career_raw:
            if target_career_raw.isdigit():
                career_exists = query_one("SELECT id FROM career_paths WHERE id = ?", (int(target_career_raw),))
                if career_exists:
                    target_career_id = int(target_career_raw)
                else:
                    errors.append(t("flash.career_not_exist"))
            else:
                errors.append(t("flash.career_selection_invalid"))

        if not errors:
            existing = query_one("SELECT id FROM users WHERE email = ?", (email,))
            if existing:
                errors.append(t("flash.email_exists"))

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("auth/register.html", careers=careers, form_data=form_data), 400

        password_hash = generate_password_hash(password)
        user_id = execute_write(
            """
            INSERT INTO users (full_name, email, password_hash, target_career_id, weekly_goal_hours)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, password_hash, target_career_id, weekly_goal),
        )

        # If user selected a target career during registration, enroll them immediately
        if target_career_id is not None:
            from seed_data import enroll_user_in_career
            enroll_user_in_career(user_id, target_career_id)

        _reset_session_preserving_lang()
        session["user_id"] = user_id
        session.permanent = True
        log_activity(user_id, "account_created", "Created SkillMap learner account", target_career_id, 0.0)
        flash(t("flash.welcome_new", name=full_name), "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", careers=careers, form_data=form_data)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an existing user and establish a secure Flask session."""
    if g.user is not None:
        return redirect(url_for("main.dashboard"))

    email_value = ""
    if request.method == "POST":
        validate_csrf()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        email_value = email

        if not email or not password:
            flash(t("flash.login_required_fields"), "error")
            return render_template("auth/login.html", email_value=email_value), 400

        user = query_one("SELECT * FROM users WHERE email = ?", (email,))
        if user is None or not check_password_hash(user["password_hash"], password):
            flash(t("flash.login_invalid"), "error")
            return render_template("auth/login.html", email_value=email_value), 401

        _reset_session_preserving_lang()
        session["user_id"] = user["id"]
        session.permanent = True
        next_url = request.args.get("next", "").strip()
        parsed_next = urlparse(next_url)
        if next_url and next_url.startswith("/") and not next_url.startswith(("//", "/\\")) and not parsed_next.netloc:
            return redirect(next_url)
        flash(t("flash.login_success", name=user["full_name"]), "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html", email_value=email_value)


@auth_bp.route("/demo-login", methods=["POST"])
def demo_login():
    """Sign into the seeded demo learner account for immediate exploration."""
    validate_csrf()
    demo_user = query_one("SELECT id, full_name FROM users WHERE email = ?", ("alex.chen@skillmap.dev",))
    if not demo_user:
        flash(t("flash.demo_unavailable"), "warning")
        return redirect(url_for("auth.register"))

    _reset_session_preserving_lang()
    session["user_id"] = demo_user["id"]
    session.permanent = True
    flash(t("flash.demo_success"), "success")
    return redirect(url_for("main.dashboard"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Clear the current user session."""
    validate_csrf()
    _reset_session_preserving_lang()
    flash(t("flash.logout_success"), "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View and update user profile, learning target, weekly study goal, or password."""
    careers = query_all("SELECT id, slug, title FROM career_paths ORDER BY title ASC")

    if request.method == "POST":
        validate_csrf()
        action = request.form.get("action", "update_profile")

        if action == "update_profile":
            full_name = request.form.get("full_name", "").strip()
            bio = request.form.get("bio", "").strip()
            target_career_raw = request.form.get("target_career_id", "").strip()
            weekly_goal_raw = request.form.get("weekly_goal_hours", "10").strip()

            errors = []
            if len(full_name) < 2 or len(full_name) > 80:
                errors.append(t("flash.name_length"))
            if len(bio) > 500:
                errors.append(t("flash.bio_length"))

            try:
                weekly_goal = float(weekly_goal_raw)
                if not math.isfinite(weekly_goal) or not (1 <= weekly_goal <= 100):
                    errors.append(t("flash.weekly_goal_range"))
            except ValueError:
                weekly_goal = float(g.user["weekly_goal_hours"])
                errors.append(t("flash.weekly_goal_number"))

            target_career_id = None
            if target_career_raw:
                if target_career_raw.isdigit() and query_one("SELECT id FROM career_paths WHERE id = ?", (int(target_career_raw),)):
                    target_career_id = int(target_career_raw)
                else:
                    errors.append(t("flash.profile_career_invalid"))

            if errors:
                for err in errors:
                    flash(err, "error")
                return redirect(url_for("auth.profile"))

            execute_write(
                """
                UPDATE users
                SET full_name = ?, bio = ?, target_career_id = ?, weekly_goal_hours = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (full_name, bio, target_career_id, weekly_goal, g.user["id"]),
            )
            log_activity(g.user["id"], "profile_updated", "Updated profile settings and weekly study goal", target_career_id, 0.0)
            flash(t("flash.profile_saved"), "success")
            return redirect(url_for("auth.profile"))

        if action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            if not check_password_hash(g.user["password_hash"], current_pw):
                flash(t("flash.current_pw_wrong"), "error")
                return redirect(url_for("auth.profile"))
            if len(new_pw) < 8:
                flash(t("flash.new_pw_length"), "error")
                return redirect(url_for("auth.profile"))
            if new_pw != confirm_pw:
                flash(t("flash.new_pw_mismatch"), "error")
                return redirect(url_for("auth.profile"))

            execute_write(
                "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (generate_password_hash(new_pw), g.user["id"]),
            )
            log_activity(g.user["id"], "password_changed", "Updated account password", None, 0.0)
            flash(t("flash.pw_updated"), "success")
            return redirect(url_for("auth.profile"))

    stats = query_one(
        """
        SELECT
            (SELECT COUNT(*) FROM user_progress WHERE user_id = ? AND skill_id IS NULL AND is_active_path = 1) AS active_paths,
            (SELECT COUNT(*) FROM roadmap_tasks WHERE user_id = ? AND is_completed = 1) AS completed_tasks,
            (SELECT COUNT(*) FROM projects WHERE user_id = ?) AS total_projects,
            (SELECT COALESCE(SUM(hours_spent), 0) FROM activity_logs WHERE user_id = ?) AS total_hours
        """,
        (g.user["id"], g.user["id"], g.user["id"], g.user["id"]),
    )

    return render_template("auth/profile.html", careers=careers, stats=stats)
