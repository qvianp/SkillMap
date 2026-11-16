"""
SkillMap Project Tracker Routes
-------------------------------
Enables learners to create, edit, filter, update completion percentage,
and delete personal portfolio projects linked to career paths and GitHub repos.

AI Assistance Note:
Project CRUD endpoints and status/completion synchronization were developed and
reviewed with AI assistance for CS50x academic honesty compliance.
"""

from urllib.parse import urlparse

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from auth import login_required, validate_csrf
from database import execute_write, log_activity, query_all, query_one
from translations import t, t_project_desc, t_project_name

projects_bp = Blueprint("projects", __name__, url_prefix="/projects")

VALID_STATUSES = ("Planned", "In Progress", "Completed", "On Hold")


def _is_valid_optional_url(url: str) -> bool:
    """Validate an optional GitHub repository URL."""
    if not url:
        return True
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


@projects_bp.route("/")
@login_required
def index():
    """Display the user's personal project portfolio tracker with status filtering."""
    status_filter = request.args.get("status", "all").strip()
    search = request.args.get("q", "").strip()

    sql = """
        SELECT p.*, cp.title AS career_title, cp.slug AS career_slug
        FROM projects p
        LEFT JOIN career_paths cp ON cp.id = p.career_path_id
        WHERE p.user_id = ?
    """
    params: list = [g.user["id"]]

    if status_filter in VALID_STATUSES:
        sql += " AND p.status = ?"
        params.append(status_filter)

    sql += " ORDER BY CASE p.status WHEN 'In Progress' THEN 1 WHEN 'Planned' THEN 2 WHEN 'On Hold' THEN 3 ELSE 4 END, p.updated_at DESC"
    projects = query_all(sql, params)
    if search:
        term = search.lower()
        projects = [
            row
            for row in projects
            if term in row["name"].lower()
            or term in (row["tech_stack"] or "").lower()
            or term in (row["description"] or "").lower()
            or term in t_project_name(row["name"]).lower()
            or term in t_project_desc(row["name"], row["description"] or "").lower()
        ]
    careers = query_all("SELECT id, slug, title FROM career_paths ORDER BY title ASC")

    summary = query_one(
        """
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END), 0) AS completed,
            COALESCE(SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END), 0) AS in_progress,
            COALESCE(ROUND(AVG(completion_percent)), 0) AS avg_completion
        FROM projects
        WHERE user_id = ?
        """,
        (g.user["id"],),
    )

    return render_template(
        "projects/index.html",
        projects=projects,
        careers=careers,
        statuses=VALID_STATUSES,
        summary=summary,
        filters={"status": status_filter, "q": search},
    )


@projects_bp.route("/add", methods=["POST"])
@login_required
def add_project():
    """Create a new personal portfolio project."""
    validate_csrf()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    tech_stack = request.form.get("tech_stack", "").strip()
    status = request.form.get("status", "Planned").strip()
    github_url = request.form.get("github_url", "").strip()
    completion_raw = request.form.get("completion_percent", "0").strip()
    career_raw = request.form.get("career_path_id", "").strip()

    errors = []
    if len(name) < 2 or len(name) > 120:
        errors.append(t("projects.flash_name_len"))
    if len(tech_stack) < 2 or len(tech_stack) > 160:
        errors.append(t("projects.flash_stack_req"))
    if status not in VALID_STATUSES:
        errors.append(t("projects.flash_status_invalid"))
    if not _is_valid_optional_url(github_url):
        errors.append(t("projects.flash_github_invalid"))

    try:
        completion_percent = max(0, min(100, int(completion_raw)))
    except ValueError:
        completion_percent = 0
        errors.append(t("projects.flash_pct_invalid"))

    if status == "Completed":
        completion_percent = 100

    career_path_id = None
    if career_raw:
        if career_raw.isdigit() and query_one("SELECT id FROM career_paths WHERE id = ?", (int(career_raw),)):
            career_path_id = int(career_raw)
        else:
            errors.append(t("projects.flash_career_invalid"))

    if errors:
        for err in errors:
            flash(err, "error")
        return redirect(url_for("projects.index"))

    execute_write(
        """
        INSERT INTO projects
        (user_id, career_path_id, name, description, tech_stack, status, github_url, completion_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (g.user["id"], career_path_id, name, description, tech_stack, status, github_url, completion_percent),
    )
    log_activity(g.user["id"], "project_created", f"Created project: {name}", career_path_id, 0.5)
    flash(t("projects.flash_created", name=t_project_name(name)), "success")
    return redirect(url_for("projects.index"))


@projects_bp.route("/<int:project_id>/update", methods=["POST"])
@login_required
def update_project(project_id: int):
    """Update project status, completion percentage, or details."""
    validate_csrf()
    project = query_one("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, g.user["id"]))
    if project is None:
        abort(404)

    name = request.form.get("name", project["name"]).strip()
    description = request.form.get("description", project["description"]).strip()
    tech_stack = request.form.get("tech_stack", project["tech_stack"]).strip()
    status = request.form.get("status", project["status"]).strip()
    github_url = request.form.get("github_url", project["github_url"]).strip()
    completion_raw = request.form.get("completion_percent", str(project["completion_percent"])).strip()
    career_raw = request.form.get("career_path_id", "").strip()

    if (
        len(name) < 2
        or len(name) > 120
        or len(tech_stack) < 2
        or len(tech_stack) > 160
        or status not in VALID_STATUSES
        or not _is_valid_optional_url(github_url)
    ):
        flash(t("projects.flash_update_verify"), "error")
        return redirect(url_for("projects.index"))

    career_path_id = project["career_path_id"]
    if "career_path_id" in request.form:
        if not career_raw:
            career_path_id = None
        elif career_raw.isdigit() and query_one("SELECT id FROM career_paths WHERE id = ?", (int(career_raw),)):
            career_path_id = int(career_raw)

    try:
        completion_percent = max(0, min(100, int(completion_raw)))
    except ValueError:
        completion_percent = int(project["completion_percent"])

    if status == "Completed":
        completion_percent = 100
    elif completion_percent == 100 and status != "Completed":
        status = "Completed"

    execute_write(
        """
        UPDATE projects
        SET name = ?, description = ?, tech_stack = ?, status = ?, github_url = ?, completion_percent = ?, career_path_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (name, description, tech_stack, status, github_url, completion_percent, career_path_id, project_id, g.user["id"]),
    )
    log_activity(
        g.user["id"],
        "project_updated",
        f"Updated {name} ({status}, {completion_percent}%)",
        career_path_id,
        1.0,
    )
    flash(t("projects.flash_updated", name=t_project_name(name)), "success")
    return redirect(url_for("projects.index"))


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id: int):
    """Delete a user-owned project."""
    validate_csrf()
    project = query_one("SELECT id, name FROM projects WHERE id = ? AND user_id = ?", (project_id, g.user["id"]))
    if project is None:
        abort(404)

    execute_write("DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, g.user["id"]))
    flash(t("projects.flash_deleted", name=t_project_name(project["name"])), "success")
    return redirect(url_for("projects.index"))
