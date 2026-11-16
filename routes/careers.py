"""
SkillMap Career Explorer Routes
-------------------------------
Displays the six curated technology career paths, searchable/filterable overview,
detailed skill breakdowns (Beginner, Intermediate, Advanced), recommended projects,
curated learning resources, and one-click roadmap enrollment.

AI Assistance Note:
Career catalog query aggregation and enrollment handlers were written with AI
assistance and reviewed by the author.
"""

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from auth import login_required, validate_csrf
from database import query_all, query_one
from seed_data import enroll_user_in_career
from translations import t, t_career_field

careers_bp = Blueprint("careers", __name__, url_prefix="/careers")


@careers_bp.route("/")
def index():
    """List all career paths with skill counts, estimated hours, and enrollment status."""
    search = request.args.get("q", "").strip().lower()
    careers = query_all(
        """
        SELECT
            cp.*,
            COUNT(DISTINCT s.id) AS skill_count,
            COUNT(DISTINCT crp.id) AS project_count,
            COUNT(DISTINCT r.id) AS resource_count
        FROM career_paths cp
        LEFT JOIN skills s ON s.career_path_id = cp.id
        LEFT JOIN career_recommended_projects crp ON crp.career_path_id = cp.id
        LEFT JOIN resources r ON r.career_path_id = cp.id AND r.user_id IS NULL
        GROUP BY cp.id
        ORDER BY cp.id ASC
        """
    )

    if search:
        careers = [
            c for c in careers
            if search in c["title"].lower()
            or search in c["tagline"].lower()
            or search in c["description"].lower()
            or search in t_career_field(c["slug"], "title", c["title"]).lower()
            or search in t_career_field(c["slug"], "tagline", c["tagline"]).lower()
            or search in t_career_field(c["slug"], "description", c["description"]).lower()
        ]

    enrolled_ids = set()
    if g.user is not None:
        enrolled_rows = query_all(
            "SELECT career_path_id FROM user_progress WHERE user_id = ? AND skill_id IS NULL AND is_active_path = 1",
            (g.user["id"],),
        )
        enrolled_ids = {r["career_path_id"] for r in enrolled_rows}

    return render_template(
        "careers/index.html",
        careers=careers,
        enrolled_ids=enrolled_ids,
        search=request.args.get("q", "").strip(),
    )


@careers_bp.route("/<slug>")
def detail(slug: str):
    """Display full curriculum details for a specific career path."""
    career = query_one("SELECT * FROM career_paths WHERE slug = ?", (slug,))
    if career is None:
        abort(404)

    skills = query_all(
        "SELECT * FROM skills WHERE career_path_id = ? ORDER BY sort_order ASC",
        (career["id"],),
    )

    skills_by_level = {"Beginner": [], "Intermediate": [], "Advanced": []}
    for skill in skills:
        skills_by_level.setdefault(skill["level"], []).append(skill)

    recommended_projects = query_all(
        "SELECT * FROM career_recommended_projects WHERE career_path_id = ? ORDER BY id ASC",
        (career["id"],),
    )
    curated_resources = query_all(
        "SELECT * FROM resources WHERE career_path_id = ? AND user_id IS NULL ORDER BY id ASC",
        (career["id"],),
    )

    is_enrolled = False
    if g.user is not None:
        enrolled = query_one(
            """
            SELECT id FROM user_progress
            WHERE user_id = ? AND career_path_id = ? AND skill_id IS NULL AND is_active_path = 1
            """,
            (g.user["id"], career["id"]),
        )
        is_enrolled = enrolled is not None

    return render_template(
        "careers/detail.html",
        career=career,
        skills_by_level=skills_by_level,
        recommended_projects=recommended_projects,
        curated_resources=curated_resources,
        is_enrolled=is_enrolled,
    )


@careers_bp.route("/<slug>/enroll", methods=["POST"])
@login_required
def enroll(slug: str):
    """Enroll the authenticated user in a career path and initialize their roadmap."""
    validate_csrf()
    career = query_one("SELECT id, title, slug FROM career_paths WHERE slug = ?", (slug,))
    if career is None:
        abort(404)

    personal_goal = request.form.get("personal_goal", "").strip()
    target_date = request.form.get("target_date", "").strip() or None

    newly_enrolled = enroll_user_in_career(
        g.user["id"],
        career["id"],
        personal_goal=personal_goal or None,
        target_date=target_date,
    )

    localized_title = t_career_field(career["slug"], "title", career["title"])
    if newly_enrolled:
        flash(t("careers.enrolled_flash", title=localized_title), "success")
    else:
        flash(t("careers.switched_flash", title=localized_title), "success")

    return redirect(url_for("roadmap.index", career_id=career["id"]))
