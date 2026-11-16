"""
SkillMap Personalized Learning Roadmap Routes
---------------------------------------------
Allows learners to select an enrolled career path, view structured tasks by
level, add/edit/remove tasks, toggle completion, update per-skill mastery,
and manage personal learning goals and target dates.

AI Assistance Note:
Route handlers, skill-mastery recalculation, and input validation were refined
with AI assistance and reviewed by the author for CS50x submission.
"""

import math
from urllib.parse import urlparse

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from auth import login_required, validate_csrf
from database import execute_write, log_activity, query_all, query_one
from seed_data import enroll_user_in_career
from translations import t, t_career_field, t_skill_name, t_task_title

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/roadmap")

VALID_LEVELS = ("Beginner", "Intermediate", "Advanced")


def recalculate_skill_mastery(user_id: int, career_path_id: int, skill_id: int) -> None:
    """Sync skill mastery percentage based on completed roadmap tasks for that skill."""
    row = query_one(
        """
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END), 0) AS done,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN estimated_hours ELSE 0 END), 0) AS hours_done
        FROM roadmap_tasks
        WHERE user_id = ? AND career_path_id = ? AND skill_id = ?
        """,
        (user_id, career_path_id, skill_id),
    )
    if not row or int(row["total"]) == 0:
        return

    task_pct = round((int(row["done"]) / int(row["total"])) * 100)
    hours_done = round(float(row["hours_done"]), 1)

    existing = query_one(
        "SELECT id FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id = ?",
        (user_id, career_path_id, skill_id),
    )
    if existing:
        execute_write(
            """
            UPDATE user_progress
            SET mastery_percent = ?, hours_logged = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (task_pct, hours_done, existing["id"]),
        )
    else:
        execute_write(
            """
            INSERT INTO user_progress (user_id, career_path_id, skill_id, mastery_percent, hours_logged, is_active_path)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (user_id, career_path_id, skill_id, task_pct, hours_done),
        )


@roadmap_bp.route("/")
@login_required
def index():
    """Render the personalized roadmap workspace for the selected career path."""
    all_careers = query_all("SELECT * FROM career_paths ORDER BY id ASC")
    enrolled_careers = query_all(
        """
        SELECT cp.*, up.personal_goal, up.target_date
        FROM user_progress up
        JOIN career_paths cp ON cp.id = up.career_path_id
        WHERE up.user_id = ? AND up.skill_id IS NULL AND up.is_active_path = 1
        ORDER BY up.updated_at DESC
        """,
        (g.user["id"],),
    )

    requested_career_id = request.args.get("career_id", "").strip()
    level_filter = request.args.get("level", "").strip()
    status_filter = request.args.get("status", "all").strip()

    selected_career = None
    if requested_career_id.isdigit():
        selected_career = query_one("SELECT * FROM career_paths WHERE id = ?", (int(requested_career_id),))

    if selected_career is None and enrolled_careers:
        # Prefer user's target_career_id if enrolled, else first enrolled career
        target_id = g.user["target_career_id"]
        for c in enrolled_careers:
            if c["id"] == target_id:
                selected_career = c
                break
        if selected_career is None:
            selected_career = enrolled_careers[0]

    tasks = []
    skills_progress = []
    career_goal = None
    stats = {"total": 0, "completed": 0, "percent": 0, "total_hours": 0.0, "completed_hours": 0.0}

    if selected_career is not None:
        career_goal = query_one(
            """
            SELECT * FROM user_progress
            WHERE user_id = ? AND career_path_id = ? AND skill_id IS NULL
            """,
            (g.user["id"], selected_career["id"]),
        )

        # Ensure skill rows exist if user is enrolled
        skills_progress = query_all(
            """
            SELECT
                s.id,
                s.name,
                s.level,
                s.estimated_hours,
                COALESCE(up.mastery_percent, 0) AS mastery_percent,
                COALESCE(up.hours_logged, 0) AS hours_logged
            FROM skills s
            LEFT JOIN user_progress up
                ON up.skill_id = s.id AND up.user_id = ? AND up.career_path_id = s.career_path_id
            WHERE s.career_path_id = ?
            ORDER BY s.sort_order ASC
            """,
            (g.user["id"], selected_career["id"]),
        )

        all_tasks = query_all(
            """
            SELECT rt.*, s.name AS skill_name, s.description AS skill_eng_desc
            FROM roadmap_tasks rt
            LEFT JOIN skills s ON s.id = rt.skill_id
            WHERE rt.user_id = ? AND rt.career_path_id = ?
            ORDER BY rt.is_completed ASC,
                     CASE rt.level WHEN 'Beginner' THEN 1 WHEN 'Intermediate' THEN 2 ELSE 3 END,
                     rt.id ASC
            """,
            (g.user["id"], selected_career["id"]),
        )

        stats["total"] = len(all_tasks)
        stats["completed"] = sum(1 for t in all_tasks if t["is_completed"] == 1)
        stats["percent"] = round((stats["completed"] / stats["total"]) * 100) if stats["total"] > 0 else 0
        stats["total_hours"] = round(sum(float(t["estimated_hours"]) for t in all_tasks), 1)
        stats["completed_hours"] = round(
            sum(float(t["estimated_hours"]) for t in all_tasks if t["is_completed"] == 1), 1
        )

        tasks = list(all_tasks)
        if level_filter in VALID_LEVELS:
            tasks = [t for t in tasks if t["level"] == level_filter]
        if status_filter == "pending":
            tasks = [t for t in tasks if t["is_completed"] == 0]
        elif status_filter == "completed":
            tasks = [t for t in tasks if t["is_completed"] == 1]

    return render_template(
        "roadmap/index.html",
        all_careers=all_careers,
        enrolled_careers=enrolled_careers,
        selected_career=selected_career,
        career_goal=career_goal,
        skills_progress=skills_progress,
        tasks=tasks,
        stats=stats,
        level_filter=level_filter,
        status_filter=status_filter,
    )


@roadmap_bp.route("/select", methods=["POST"])
@login_required
def select_career():
    """Enroll in and switch to a chosen career path from the Roadmap selector."""
    validate_csrf()
    career_id_raw = request.form.get("career_path_id", "").strip()
    if not career_id_raw.isdigit():
        flash(t("roadmap.flash_choose_valid"), "error")
        return redirect(url_for("roadmap.index"))

    career_id = int(career_id_raw)
    career = query_one("SELECT id, slug, title FROM career_paths WHERE id = ?", (career_id,))
    if not career:
        flash(t("roadmap.flash_not_found"), "error")
        return redirect(url_for("roadmap.index"))

    enroll_user_in_career(g.user["id"], career_id)
    flash(t("roadmap.flash_loaded", title=t_career_field(career["slug"], "title", career["title"])), "success")
    return redirect(url_for("roadmap.index", career_id=career_id))


@roadmap_bp.route("/goal", methods=["POST"])
@login_required
def update_goal():
    """Update the user's personal learning goal and target date for a career path."""
    validate_csrf()
    career_id_raw = request.form.get("career_path_id", "").strip()
    personal_goal = request.form.get("personal_goal", "").strip()
    target_date = request.form.get("target_date", "").strip() or None

    if not career_id_raw.isdigit():
        flash(t("roadmap.flash_invalid_career"), "error")
        return redirect(url_for("roadmap.index"))

    career_id = int(career_id_raw)
    if len(personal_goal) < 3 or len(personal_goal) > 250:
        flash(t("roadmap.flash_goal_length"), "error")
        return redirect(url_for("roadmap.index", career_id=career_id))

    existing = query_one(
        "SELECT id FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id IS NULL",
        (g.user["id"], career_id),
    )
    if existing:
        execute_write(
            """
            UPDATE user_progress
            SET personal_goal = ?, target_date = ?, is_active_path = 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (personal_goal, target_date, existing["id"]),
        )
    else:
        execute_write(
            """
            INSERT INTO user_progress (user_id, career_path_id, skill_id, personal_goal, target_date, is_active_path)
            VALUES (?, ?, NULL, ?, ?, 1)
            """,
            (g.user["id"], career_id, personal_goal, target_date),
        )

    log_activity(g.user["id"], "goal_updated", f"Updated learning goal: {personal_goal}", career_id, 0.0)
    flash(t("roadmap.flash_goal_updated"), "success")
    return redirect(url_for("roadmap.index", career_id=career_id))


@roadmap_bp.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    """Add a custom learning task to the user's career roadmap."""
    validate_csrf()
    career_id_raw = request.form.get("career_path_id", "").strip()
    skill_id_raw = request.form.get("skill_id", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    level = request.form.get("level", "Beginner").strip()
    hours_raw = request.form.get("estimated_hours", "2").strip()
    due_date = request.form.get("due_date", "").strip() or None

    if not career_id_raw.isdigit() or not query_one("SELECT id FROM career_paths WHERE id = ?", (int(career_id_raw),)):
        flash(t("roadmap.flash_select_valid"), "error")
        return redirect(url_for("roadmap.index"))

    career_id = int(career_id_raw)
    if len(title) < 2 or len(title) > 140:
        flash(t("roadmap.flash_title_length"), "error")
        return redirect(url_for("roadmap.index", career_id=career_id))

    if level not in VALID_LEVELS:
        level = "Beginner"

    try:
        parsed_hours = float(hours_raw)
        estimated_hours = max(0.5, min(200.0, parsed_hours)) if math.isfinite(parsed_hours) else 2.0
    except ValueError:
        estimated_hours = 2.0

    skill_id = None
    if skill_id_raw.isdigit():
        skill_row = query_one(
            "SELECT id FROM skills WHERE id = ? AND career_path_id = ?",
            (int(skill_id_raw), career_id),
        )
        if skill_row:
            skill_id = skill_row["id"]

    execute_write(
        """
        INSERT INTO roadmap_tasks
        (user_id, career_path_id, skill_id, title, description, level, estimated_hours, is_completed, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
        """,
        (g.user["id"], career_id, skill_id, title, description, level, estimated_hours, due_date),
    )

    if skill_id is not None:
        recalculate_skill_mastery(g.user["id"], career_id, skill_id)

    log_activity(g.user["id"], "task_added", f"Added roadmap task: {title}", career_id, 0.0)
    flash(t("roadmap.flash_task_added"), "success")
    return redirect(url_for("roadmap.index", career_id=career_id))


@roadmap_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id: int):
    """Toggle completion status of a user-owned roadmap task."""
    validate_csrf()
    task = query_one(
        "SELECT * FROM roadmap_tasks WHERE id = ? AND user_id = ?",
        (task_id, g.user["id"]),
    )
    if task is None:
        abort(404)

    new_state = 0 if task["is_completed"] == 1 else 1
    display_task_title = t_task_title(task["title"])
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
        flash(t("roadmap.flash_task_completed", title=display_task_title), "success")
    else:
        execute_write(
            "UPDATE roadmap_tasks SET is_completed = 0, completed_at = NULL WHERE id = ? AND user_id = ?",
            (task_id, g.user["id"]),
        )
        flash(t("roadmap.flash_task_reopened", title=display_task_title), "info")

    if task["skill_id"] is not None:
        recalculate_skill_mastery(g.user["id"], task["career_path_id"], task["skill_id"])

    next_url = request.form.get("next", "").strip()
    if next_url and next_url.startswith("/") and not next_url.startswith(("//", "/\\")) and not urlparse(next_url).netloc:
        return redirect(next_url)

    return redirect(url_for("roadmap.index", career_id=task["career_path_id"]))


@roadmap_bp.route("/tasks/<int:task_id>/edit", methods=["POST"])
@login_required
def edit_task(task_id: int):
    """Edit an existing user-owned roadmap task."""
    validate_csrf()
    task = query_one(
        "SELECT * FROM roadmap_tasks WHERE id = ? AND user_id = ?",
        (task_id, g.user["id"]),
    )
    if task is None:
        abort(404)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    level = request.form.get("level", task["level"]).strip()
    hours_raw = request.form.get("estimated_hours", str(task["estimated_hours"])).strip()
    due_date = request.form.get("due_date", "").strip() or None
    skill_id_raw = request.form.get("skill_id", "").strip()

    if len(title) < 2 or len(title) > 140:
        flash(t("roadmap.flash_title_length"), "error")
        return redirect(url_for("roadmap.index", career_id=task["career_path_id"]))

    if level not in VALID_LEVELS:
        level = task["level"]

    try:
        parsed_hours = float(hours_raw)
        estimated_hours = max(0.5, min(200.0, parsed_hours)) if math.isfinite(parsed_hours) else float(task["estimated_hours"])
    except ValueError:
        estimated_hours = float(task["estimated_hours"])

    skill_id = None
    if skill_id_raw.isdigit():
        skill_row = query_one(
            "SELECT id FROM skills WHERE id = ? AND career_path_id = ?",
            (int(skill_id_raw), task["career_path_id"]),
        )
        if skill_row:
            skill_id = skill_row["id"]

    old_skill_id = task["skill_id"]
    execute_write(
        """
        UPDATE roadmap_tasks
        SET title = ?, description = ?, level = ?, estimated_hours = ?, due_date = ?, skill_id = ?
        WHERE id = ? AND user_id = ?
        """,
        (title, description, level, estimated_hours, due_date, skill_id, task_id, g.user["id"]),
    )

    if old_skill_id is not None:
        recalculate_skill_mastery(g.user["id"], task["career_path_id"], old_skill_id)
    if skill_id is not None and skill_id != old_skill_id:
        recalculate_skill_mastery(g.user["id"], task["career_path_id"], skill_id)

    flash(t("roadmap.flash_task_updated", title=title), "success")
    return redirect(url_for("roadmap.index", career_id=task["career_path_id"]))


@roadmap_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id: int):
    """Delete a user-owned roadmap task."""
    validate_csrf()
    task = query_one(
        "SELECT * FROM roadmap_tasks WHERE id = ? AND user_id = ?",
        (task_id, g.user["id"]),
    )
    if task is None:
        abort(404)

    execute_write("DELETE FROM roadmap_tasks WHERE id = ? AND user_id = ?", (task_id, g.user["id"]))
    if task["skill_id"] is not None:
        recalculate_skill_mastery(g.user["id"], task["career_path_id"], task["skill_id"])

    flash(t("roadmap.flash_task_removed", title=t_task_title(task["title"])), "success")
    return redirect(url_for("roadmap.index", career_id=task["career_path_id"]))


@roadmap_bp.route("/skills/<int:skill_id>/update", methods=["POST"])
@login_required
def update_skill_progress(skill_id: int):
    """Allow learners to adjust per-skill mastery percentage and logged study hours."""
    validate_csrf()
    skill = query_one("SELECT * FROM skills WHERE id = ?", (skill_id,))
    if skill is None:
        abort(404)

    try:
        mastery = max(0, min(100, int(request.form.get("mastery_percent", "0"))))
    except ValueError:
        mastery = 0

    try:
        parsed_hours = float(request.form.get("hours_logged", "0"))
        hours_logged = max(0.0, min(500.0, parsed_hours)) if math.isfinite(parsed_hours) else 0.0
    except ValueError:
        hours_logged = 0.0

    existing = query_one(
        "SELECT id, hours_logged FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id = ?",
        (g.user["id"], skill["career_path_id"], skill_id),
    )
    delta_hours = 0.0
    if existing:
        delta_hours = max(0.0, round(hours_logged - float(existing["hours_logged"]), 1))
        execute_write(
            """
            UPDATE user_progress
            SET mastery_percent = ?, hours_logged = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (mastery, hours_logged, existing["id"]),
        )
    else:
        delta_hours = hours_logged
        execute_write(
            """
            INSERT INTO user_progress (user_id, career_path_id, skill_id, mastery_percent, hours_logged, is_active_path)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (g.user["id"], skill["career_path_id"], skill_id, mastery, hours_logged),
        )

    log_activity(
        g.user["id"],
        "skill_updated",
        f"Updated {skill['name']} mastery to {mastery}%",
        skill["career_path_id"],
        delta_hours,
    )
    flash(t("roadmap.flash_skill_updated", name=t_skill_name(skill["name"]), pct=mastery), "success")
    return redirect(url_for("roadmap.index", career_id=skill["career_path_id"]))
