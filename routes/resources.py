"""
SkillMap Resource Library Routes
--------------------------------
Allows authenticated users to save, categorize, search, filter, complete,
edit, and delete personal learning resources, as well as bookmark curated
catalog resources into their personal library.

AI Assistance Note:
Filtering queries, URL validation, and resource CRUD endpoints were developed
and refined with AI assistance and verified by the author.
"""

from urllib.parse import urlparse

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from auth import login_required, validate_csrf
from database import execute_write, log_activity, query_all, query_one
from translations import t, t_career_field, t_resource_desc, t_resource_title

resources_bp = Blueprint("resources", __name__, url_prefix="/resources")

VALID_CATEGORIES = ("Documentation", "Course", "Book", "Video", "Article", "Tool", "Practice Lab")
VALID_DIFFICULTIES = ("Beginner", "Intermediate", "Advanced")


def _is_valid_http_url(url: str) -> bool:
    """Validate that a user-supplied URL uses http or https with a valid host."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


@resources_bp.route("/")
@login_required
def index():
    """List personal learning resources with live search and category/difficulty/status filters."""
    search = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()
    difficulty_filter = request.args.get("difficulty", "").strip()
    status_filter = request.args.get("status", "all").strip()

    sql = """
        SELECT r.*, cp.title AS career_title, cp.slug AS career_slug
        FROM resources r
        LEFT JOIN career_paths cp ON cp.id = r.career_path_id
        WHERE r.user_id = ?
    """
    params: list = [g.user["id"]]

    if category_filter in VALID_CATEGORIES:
        sql += " AND r.category = ?"
        params.append(category_filter)

    if difficulty_filter in VALID_DIFFICULTIES:
        sql += " AND r.difficulty = ?"
        params.append(difficulty_filter)

    if status_filter == "completed":
        sql += " AND r.is_completed = 1"
    elif status_filter == "unread":
        sql += " AND r.is_completed = 0"

    sql += " ORDER BY r.is_completed ASC, r.created_at DESC, r.id DESC"
    resources = query_all(sql, params)
    if search:
        term = search.lower()
        resources = [
            row
            for row in resources
            if term in row["title"].lower()
            or term in (row["description"] or "").lower()
            or term in (row["career_title"] or "").lower()
            or term in t_resource_title(row["title"]).lower()
            or term in t_resource_desc(row["title"], row["description"] or "").lower()
            or term in t_career_field(row["career_slug"], "title", row["career_title"] or "").lower()
        ]

    curated = query_all(
        """
        SELECT r.*, cp.title AS career_title, cp.slug AS career_slug
        FROM resources r
        LEFT JOIN career_paths cp ON cp.id = r.career_path_id
        WHERE r.user_id IS NULL
          AND r.url NOT IN (SELECT url FROM resources WHERE user_id = ?)
        ORDER BY
          CASE WHEN r.career_path_id IN (
              SELECT career_path_id FROM user_progress
              WHERE user_id = ? AND skill_id IS NULL AND is_active_path = 1
          ) THEN 0 ELSE 1 END,
          CASE WHEN r.career_path_id = ? THEN 0 ELSE 1 END,
          r.id ASC
        LIMIT 8
        """,
        (g.user["id"], g.user["id"], g.user["target_career_id"] or -1),
    )

    careers = query_all("SELECT id, slug, title FROM career_paths ORDER BY title ASC")
    counts = query_one(
        """
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END), 0) AS completed
        FROM resources
        WHERE user_id = ?
        """,
        (g.user["id"],),
    )

    return render_template(
        "resources/index.html",
        resources=resources,
        curated=curated,
        careers=careers,
        categories=VALID_CATEGORIES,
        difficulties=VALID_DIFFICULTIES,
        counts=counts,
        filters={
            "q": search,
            "category": category_filter,
            "difficulty": difficulty_filter,
            "status": status_filter,
        },
    )


@resources_bp.route("/add", methods=["POST"])
@login_required
def add_resource():
    """Create a new personal learning resource with URL and enum validation."""
    validate_csrf()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    url = request.form.get("url", "").strip()
    category = request.form.get("category", "Article").strip()
    difficulty = request.form.get("difficulty", "Beginner").strip()
    career_raw = request.form.get("career_path_id", "").strip()

    errors = []
    if len(title) < 2 or len(title) > 140:
        errors.append(t("resources.flash_title_len"))
    if not _is_valid_http_url(url):
        errors.append(t("resources.flash_url_invalid"))
    if category not in VALID_CATEGORIES:
        errors.append(t("resources.flash_cat_invalid"))
    if difficulty not in VALID_DIFFICULTIES:
        errors.append(t("resources.flash_diff_invalid"))

    career_path_id = None
    if career_raw:
        if career_raw.isdigit() and query_one("SELECT id FROM career_paths WHERE id = ?", (int(career_raw),)):
            career_path_id = int(career_raw)
        else:
            errors.append(t("resources.flash_career_invalid"))

    if errors:
        for err in errors:
            flash(err, "error")
        return redirect(url_for("resources.index"))

    execute_write(
        """
        INSERT INTO resources (user_id, career_path_id, title, description, url, category, difficulty, is_completed)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (g.user["id"], career_path_id, title, description, url, category, difficulty),
    )
    log_activity(g.user["id"], "resource_added", f"Saved resource: {title}", career_path_id, 0.0)
    flash(t("resources.flash_saved"), "success")
    return redirect(url_for("resources.index"))


@resources_bp.route("/save-curated/<int:resource_id>", methods=["POST"])
@login_required
def save_curated(resource_id: int):
    """Copy a system-curated resource into the user's personal Resource Library."""
    validate_csrf()
    curated = query_one("SELECT * FROM resources WHERE id = ? AND user_id IS NULL", (resource_id,))
    if curated is None:
        abort(404)

    duplicate = query_one(
        "SELECT id FROM resources WHERE user_id = ? AND url = ?",
        (g.user["id"], curated["url"]),
    )
    if duplicate:
        flash(t("resources.flash_already_saved"), "info")
        return redirect(url_for("resources.index"))

    execute_write(
        """
        INSERT INTO resources (user_id, career_path_id, title, description, url, category, difficulty, is_completed)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            g.user["id"],
            curated["career_path_id"],
            curated["title"],
            curated["description"],
            curated["url"],
            curated["category"],
            curated["difficulty"],
        ),
    )
    log_activity(g.user["id"], "resource_added", f"Bookmarked curated resource: {curated['title']}", curated["career_path_id"], 0.0)
    flash(t("resources.flash_added_curated", title=t_resource_title(curated["title"])), "success")
    return redirect(url_for("resources.index"))


@resources_bp.route("/<int:resource_id>/toggle", methods=["POST"])
@login_required
def toggle_resource(resource_id: int):
    """Toggle completed state on a user-owned resource."""
    validate_csrf()
    resource = query_one("SELECT * FROM resources WHERE id = ? AND user_id = ?", (resource_id, g.user["id"]))
    if resource is None:
        abort(404)

    new_state = 0 if resource["is_completed"] == 1 else 1
    execute_write(
        "UPDATE resources SET is_completed = ? WHERE id = ? AND user_id = ?",
        (new_state, resource_id, g.user["id"]),
    )
    if new_state == 1:
        log_activity(
            g.user["id"],
            "resource_completed",
            f"Completed resource: {resource['title']}",
            resource["career_path_id"],
            1.0,
        )
        flash(t("resources.flash_completed", title=t_resource_title(resource["title"])), "success")
    else:
        flash(t("resources.flash_unread", title=t_resource_title(resource["title"])), "info")
    return redirect(url_for("resources.index"))


@resources_bp.route("/<int:resource_id>/edit", methods=["POST"])
@login_required
def edit_resource(resource_id: int):
    """Edit an existing user-owned learning resource."""
    validate_csrf()
    resource = query_one("SELECT * FROM resources WHERE id = ? AND user_id = ?", (resource_id, g.user["id"]))
    if resource is None:
        abort(404)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    url = request.form.get("url", "").strip()
    category = request.form.get("category", resource["category"]).strip()
    difficulty = request.form.get("difficulty", resource["difficulty"]).strip()
    career_raw = request.form.get("career_path_id", "").strip()

    errors = []
    if len(title) < 2 or len(title) > 140:
        errors.append(t("resources.flash_title_len"))
    if not _is_valid_http_url(url):
        errors.append(t("resources.flash_url_invalid"))
    if category not in VALID_CATEGORIES:
        errors.append(t("resources.flash_cat_invalid"))
    if difficulty not in VALID_DIFFICULTIES:
        errors.append(t("resources.flash_diff_invalid"))

    career_path_id = None
    if career_raw:
        if career_raw.isdigit() and query_one("SELECT id FROM career_paths WHERE id = ?", (int(career_raw),)):
            career_path_id = int(career_raw)
        else:
            errors.append(t("resources.flash_career_invalid"))

    if errors:
        for err in errors:
            flash(err, "error")
        return redirect(url_for("resources.index"))

    execute_write(
        """
        UPDATE resources
        SET title = ?, description = ?, url = ?, category = ?, difficulty = ?, career_path_id = ?
        WHERE id = ? AND user_id = ?
        """,
        (title, description, url, category, difficulty, career_path_id, resource_id, g.user["id"]),
    )
    flash(t("resources.flash_updated", title=t_resource_title(title)), "success")
    return redirect(url_for("resources.index"))


@resources_bp.route("/<int:resource_id>/delete", methods=["POST"])
@login_required
def delete_resource(resource_id: int):
    """Remove a user-owned resource from the library."""
    validate_csrf()
    resource = query_one("SELECT id, title FROM resources WHERE id = ? AND user_id = ?", (resource_id, g.user["id"]))
    if resource is None:
        abort(404)

    execute_write("DELETE FROM resources WHERE id = ? AND user_id = ?", (resource_id, g.user["id"]))
    flash(t("resources.flash_removed", title=t_resource_title(resource["title"])), "success")
    return redirect(url_for("resources.index"))
