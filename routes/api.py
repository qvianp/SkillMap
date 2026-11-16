"""
SkillMap JSON API Endpoints
---------------------------
Provides authenticated JSON endpoints for interactive UI updates, dashboard
chart datasets, and asynchronous task/resource/project toggles without losing
SQLite persistence or user-isolation guarantees.

AI Assistance Note:
JSON API endpoints and skill-progress response payloads were structured with
AI assistance and verified by automated tests.
"""

from flask import Blueprint, g, jsonify, make_response, request, session

from auth import login_required, set_language_cookie, validate_csrf
from database import execute_write, log_activity, query_one
from routes.main import compute_dashboard_data
from routes.roadmap import recalculate_skill_mastery
from translations import SUPPORTED_LANGUAGES, get_text_dir, t

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/language", methods=["POST"])
def api_set_language():
    """Persist language preference ('en' or 'fa') without refreshing the page."""
    validate_csrf()
    payload = request.get_json(silent=True) or {}
    lang = str(payload.get("lang") or request.form.get("lang") or "").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        return jsonify({"error": t("api.bad_request")}), 400

    session["lang"] = lang
    session.permanent = True
    response = make_response(jsonify({"lang": lang, "dir": get_text_dir(lang)}))
    set_language_cookie(response, lang)
    return response


@api_bp.route("/dashboard/stats", methods=["GET"])
@login_required
def dashboard_stats():
    """Return live dashboard analytics and Chart.js datasets computed from SQLite."""
    data = compute_dashboard_data(g.user["id"])
    return jsonify({
        "overall_progress": data["overall_progress"],
        "completed_tasks": data["completed_tasks"],
        "total_tasks": data["total_tasks"],
        "active_paths_count": data["active_paths_count"],
        "weekly_activity": data["weekly_activity"],
        "skills_chart": data["skills_chart"],
        "stats": data["stats"],
    })


@api_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def api_toggle_task(task_id: int):
    """Toggle a roadmap task via fetch() and return updated progress stats."""
    validate_csrf()
    task = query_one(
        "SELECT * FROM roadmap_tasks WHERE id = ? AND user_id = ?",
        (task_id, g.user["id"]),
    )
    if task is None:
        return jsonify({"error": t("api.task_not_found")}), 404

    new_state = 0 if task["is_completed"] == 1 else 1
    if new_state == 1:
        execute_write(
            "UPDATE roadmap_tasks SET is_completed = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
            (task_id, g.user["id"]),
        )
        log_activity(
            g.user["id"],
            "task_completed",
            f"Completed task: {task['title']}",
            task["career_path_id"],
            float(task["estimated_hours"]),
        )
    else:
        execute_write(
            "UPDATE roadmap_tasks SET is_completed = 0, completed_at = NULL WHERE id = ? AND user_id = ?",
            (task_id, g.user["id"]),
        )

    if task["skill_id"] is not None:
        recalculate_skill_mastery(g.user["id"], task["career_path_id"], task["skill_id"])

    summary = query_one(
        """
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END), 0) AS completed,
            COALESCE(SUM(estimated_hours), 0) AS total_hours,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN estimated_hours ELSE 0 END), 0) AS completed_hours
        FROM roadmap_tasks
        WHERE user_id = ? AND career_path_id = ?
        """,
        (g.user["id"], task["career_path_id"]),
    )
    total = int(summary["total"]) if summary else 0
    completed = int(summary["completed"]) if summary else 0
    percent = round((completed / total) * 100) if total > 0 else 0
    total_hours = round(float(summary["total_hours"]), 1) if summary else 0.0
    completed_hours = round(float(summary["completed_hours"]), 1) if summary else 0.0

    skill_mastery = None
    skill_hours = None
    if task["skill_id"] is not None:
        skill_row = query_one(
            "SELECT mastery_percent, hours_logged FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id = ?",
            (g.user["id"], task["career_path_id"], task["skill_id"]),
        )
        if skill_row:
            skill_mastery = int(skill_row["mastery_percent"])
            skill_hours = round(float(skill_row["hours_logged"]), 1)

    return jsonify({
        "task_id": task_id,
        "is_completed": bool(new_state),
        "career_total": total,
        "career_completed": completed,
        "career_percent": percent,
        "total_hours": total_hours,
        "completed_hours": completed_hours,
        "skill_id": task["skill_id"],
        "skill_mastery": skill_mastery,
        "skill_hours": skill_hours,
    })


@api_bp.route("/resources/<int:resource_id>/toggle", methods=["POST"])
@login_required
def api_toggle_resource(resource_id: int):
    """Toggle a resource's completion state via fetch()."""
    validate_csrf()
    resource = query_one(
        "SELECT * FROM resources WHERE id = ? AND user_id = ?",
        (resource_id, g.user["id"]),
    )
    if resource is None:
        return jsonify({"error": t("api.resource_not_found")}), 404

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

    return jsonify({"resource_id": resource_id, "is_completed": bool(new_state)})


@api_bp.route("/projects/<int:project_id>/progress", methods=["POST"])
@login_required
def api_update_project_progress(project_id: int):
    """Update a project's completion percentage via fetch()."""
    validate_csrf()
    project = query_one(
        "SELECT * FROM projects WHERE id = ? AND user_id = ?",
        (project_id, g.user["id"]),
    )
    if project is None:
        return jsonify({"error": t("api.project_not_found")}), 404

    payload = request.get_json(silent=True) or {}
    try:
        pct = max(0, min(100, int(payload.get("completion_percent", project["completion_percent"]))))
    except (TypeError, ValueError):
        return jsonify({"error": t("api.invalid_pct")}), 400

    new_status = project["status"]
    if pct == 100:
        new_status = "Completed"
    elif pct > 0 and new_status == "Planned":
        new_status = "In Progress"

    execute_write(
        """
        UPDATE projects
        SET completion_percent = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (pct, new_status, project_id, g.user["id"]),
    )
    log_activity(
        g.user["id"],
        "project_updated",
        f"Updated {project['name']} to {pct}%",
        project["career_path_id"],
        0.5,
    )

    return jsonify({"project_id": project_id, "completion_percent": pct, "status": new_status})
