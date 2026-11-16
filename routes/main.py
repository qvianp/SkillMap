"""
SkillMap Main & Dashboard Routes
--------------------------------
Serves the landing entry page and the interactive SaaS Learning Dashboard.
All dashboard statistics, weekly activity series, skill mastery metrics, and
recent activity feeds are computed dynamically from SQLite records.

AI Assistance Note:
SQL aggregation queries for dashboard analytics were structured with AI
assistance and verified against real relational datasets.
"""

from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlparse

from flask import Blueprint, g, make_response, redirect, render_template, request, session, url_for

from auth import login_required, set_language_cookie, validate_csrf
from database import query_all, query_one
from translations import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, t_career_field, t_enum, t_skill_name, t_weekday_label

main_bp = Blueprint("main", __name__)


def compute_dashboard_data(user_id: int) -> dict[str, Any]:
    """Compute all dashboard metrics, chart series, and feeds from SQLite."""
    task_summary = query_one(
        """
        SELECT
            COUNT(*) AS total_tasks,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END), 0) AS completed_tasks,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN estimated_hours ELSE 0 END), 0) AS completed_task_hours
        FROM roadmap_tasks
        WHERE user_id = ?
        """,
        (user_id,),
    )

    total_tasks = int(task_summary["total_tasks"]) if task_summary else 0
    completed_tasks = int(task_summary["completed_tasks"]) if task_summary else 0
    overall_progress = round((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    active_paths = query_all(
        """
        SELECT
            cp.id,
            cp.slug,
            cp.title,
            cp.tagline,
            cp.estimated_hours,
            cp.accent_color,
            up.personal_goal,
            up.target_date,
            COUNT(rt.id) AS total_tasks,
            COALESCE(SUM(CASE WHEN rt.is_completed = 1 THEN 1 ELSE 0 END), 0) AS completed_tasks
        FROM user_progress up
        JOIN career_paths cp ON cp.id = up.career_path_id
        LEFT JOIN roadmap_tasks rt ON rt.user_id = up.user_id AND rt.career_path_id = up.career_path_id
        WHERE up.user_id = ? AND up.skill_id IS NULL AND up.is_active_path = 1
        GROUP BY cp.id, up.id
        ORDER BY up.updated_at DESC
        """,
        (user_id,),
    )

    active_paths_list = []
    for row in active_paths:
        t_total = int(row["total_tasks"])
        t_done = int(row["completed_tasks"])
        pct = round((t_done / t_total) * 100) if t_total > 0 else 0
        active_paths_list.append({
            "id": row["id"],
            "slug": row["slug"],
            "title": row["title"],
            "tagline": row["tagline"],
            "estimated_hours": row["estimated_hours"],
            "accent_color": row["accent_color"],
            "personal_goal": row["personal_goal"],
            "target_date": row["target_date"],
            "total_tasks": t_total,
            "completed_tasks": t_done,
            "progress_percent": pct,
        })

    # Weekly activity over the trailing 7 days (from activity_logs)
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)
    daily_rows = query_all(
        """
        SELECT
            DATE(created_at) AS activity_date,
            COALESCE(SUM(hours_spent), 0) AS hours_sum,
            COUNT(*) AS events_count
        FROM activity_logs
        WHERE user_id = ? AND DATE(created_at) >= ?
        GROUP BY DATE(created_at)
        """,
        (user_id, start_date.strftime("%Y-%m-%d")),
    )
    by_date = {row["activity_date"]: row for row in daily_rows}

    weekly_labels = []
    weekly_hours = []
    weekly_events = []
    total_week_hours = 0.0
    for offset in range(7):
        day = start_date + timedelta(days=offset)
        day_str = day.strftime("%Y-%m-%d")
        weekly_labels.append(t_weekday_label(day))
        row = by_date.get(day_str)
        hrs = round(float(row["hours_sum"]), 2) if row else 0.0
        evts = int(row["events_count"]) if row else 0
        weekly_hours.append(hrs)
        weekly_events.append(evts)
        total_week_hours += hrs

    # Skills progress (top 8 tracked skills ordered by mastery / active path)
    skill_rows = query_all(
        """
        SELECT
            s.id AS skill_id,
            s.name AS skill_name,
            s.level,
            cp.title AS career_title,
            cp.slug AS career_slug,
            up.mastery_percent,
            up.hours_logged
        FROM user_progress up
        JOIN skills s ON s.id = up.skill_id
        JOIN career_paths cp ON cp.id = up.career_path_id
        WHERE up.user_id = ? AND up.skill_id IS NOT NULL
        ORDER BY up.mastery_percent DESC, s.sort_order ASC
        LIMIT 8
        """,
        (user_id,),
    )

    skills_chart = {
        "labels": [t_skill_name(row["skill_name"]) for row in skill_rows],
        "values": [int(row["mastery_percent"]) for row in skill_rows],
        "levels": [t_enum("level", row["level"]) for row in skill_rows],
        "careers": [t_career_field(row["career_slug"], "title", row["career_title"]) for row in skill_rows],
    }

    # Resource, Project, Assessment, and Notes statistics
    resource_stats = query_one(
        """
        SELECT
            COUNT(*) AS total_resources,
            COALESCE(SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END), 0) AS completed_resources
        FROM resources
        WHERE user_id = ?
        """,
        (user_id,),
    )

    project_stats = query_one(
        """
        SELECT
            COUNT(*) AS total_projects,
            COALESCE(SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END), 0) AS completed_projects,
            COALESCE(ROUND(AVG(completion_percent)), 0) AS avg_completion
        FROM projects
        WHERE user_id = ?
        """,
        (user_id,),
    )

    assessment_stats = query_one(
        """
        SELECT
            COUNT(*) AS total_assessments,
            COALESCE(ROUND(AVG(score)), 0) AS avg_score
        FROM assessments
        WHERE user_id = ?
        """,
        (user_id,),
    )

    weak_skills = query_all(
        """
        SELECT
            a.id AS assessment_id,
            a.title AS assessment_title,
            a.title AS title,
            a.score,
            a.taken_at,
            s.id AS skill_id,
            s.name AS skill_name,
            cp.title AS career_title,
            cp.slug AS career_slug
        FROM assessments a
        LEFT JOIN skills s ON s.id = a.skill_id
        JOIN career_paths cp ON cp.id = a.career_path_id
        WHERE a.user_id = ?
          AND a.needs_practice = 1
          AND a.id = (
              SELECT a2.id
              FROM assessments a2
              WHERE a2.user_id = a.user_id
                AND a2.career_path_id = a.career_path_id
                AND (
                    (a.assessment_type = 'Quiz' AND a2.assessment_type = 'Quiz')
                    OR (
                        a.assessment_type != 'Quiz'
                        AND a2.assessment_type != 'Quiz'
                        AND COALESCE(a2.skill_id, 0) = COALESCE(a.skill_id, 0)
                    )
                )
              ORDER BY a2.taken_at DESC, a2.id DESC
              LIMIT 1
          )
        ORDER BY a.score ASC, a.taken_at DESC
        LIMIT 4
        """,
        (user_id,),
    )

    total_hours_row = query_one(
        "SELECT COALESCE(SUM(hours_spent), 0) AS total_hours FROM activity_logs WHERE user_id = ?",
        (user_id,),
    )
    notes_count_row = query_one(
        "SELECT COUNT(*) AS total_notes FROM notes WHERE user_id = ?",
        (user_id,),
    )

    recent_activities = query_all(
        """
        SELECT
            al.id,
            al.action_type,
            al.description,
            al.hours_spent,
            al.created_at,
            cp.title AS career_title,
            cp.slug AS career_slug
        FROM activity_logs al
        LEFT JOIN career_paths cp ON cp.id = al.career_path_id
        WHERE al.user_id = ?
        ORDER BY al.created_at DESC, al.id DESC
        LIMIT 8
        """,
        (user_id,),
    )

    upcoming_tasks = query_all(
        """
        SELECT
            rt.id,
            rt.title,
            rt.level,
            rt.estimated_hours,
            rt.due_date,
            cp.title AS career_title,
            cp.slug AS career_slug,
            s.name AS skill_name
        FROM roadmap_tasks rt
        JOIN career_paths cp ON cp.id = rt.career_path_id
        LEFT JOIN skills s ON s.id = rt.skill_id
        WHERE rt.user_id = ? AND rt.is_completed = 0
        ORDER BY CASE WHEN rt.due_date IS NULL OR rt.due_date = '' THEN 1 ELSE 0 END, rt.due_date ASC, rt.id ASC
        LIMIT 5
        """,
        (user_id,),
    )

    weekly_goal = float(g.user["weekly_goal_hours"]) if g.user else 10.0
    weekly_goal_pct = min(100, round((total_week_hours / weekly_goal) * 100)) if weekly_goal > 0 else 0

    return {
        "overall_progress": overall_progress,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "active_paths": active_paths_list,
        "active_paths_count": len(active_paths_list),
        "weekly_activity": {
            "labels": weekly_labels,
            "hours": weekly_hours,
            "events": weekly_events,
            "total_week_hours": round(total_week_hours, 1),
            "weekly_goal_hours": weekly_goal,
            "weekly_goal_pct": weekly_goal_pct,
        },
        "skills_chart": skills_chart,
        "skill_rows": [dict(r) for r in skill_rows],
        "stats": {
            "total_hours": round(float(total_hours_row["total_hours"]), 1) if total_hours_row else 0.0,
            "total_resources": int(resource_stats["total_resources"]) if resource_stats else 0,
            "completed_resources": int(resource_stats["completed_resources"]) if resource_stats else 0,
            "total_projects": int(project_stats["total_projects"]) if project_stats else 0,
            "completed_projects": int(project_stats["completed_projects"]) if project_stats else 0,
            "avg_project_completion": int(project_stats["avg_completion"]) if project_stats else 0,
            "total_assessments": int(assessment_stats["total_assessments"]) if assessment_stats else 0,
            "avg_assessment_score": int(assessment_stats["avg_score"]) if assessment_stats else 0,
            "total_notes": int(notes_count_row["total_notes"]) if notes_count_row else 0,
        },
        "weak_skills": [dict(r) for r in weak_skills],
        "recent_activities": [dict(r) for r in recent_activities],
        "upcoming_tasks": [dict(r) for r in upcoming_tasks],
    }


@main_bp.route("/")
def index():
    """Route authenticated users to Dashboard; unauthenticated visitors see the landing overview."""
    if g.user is not None:
        return redirect(url_for("main.dashboard"))

    careers = query_all(
        """
        SELECT cp.*, COUNT(s.id) AS skill_count
        FROM career_paths cp
        LEFT JOIN skills s ON s.career_path_id = cp.id
        GROUP BY cp.id
        ORDER BY cp.id ASC
        """
    )
    return render_template("landing.html", careers=careers)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Render the interactive learning dashboard backed by SQLite analytics."""
    dashboard_data = compute_dashboard_data(g.user["id"])
    return render_template("dashboard.html", data=dashboard_data)


@main_bp.route("/language/<lang_code>", methods=["POST"])
def switch_language(lang_code: str):
    """Non-JS fallback endpoint to persist language preference in session and cookie."""
    validate_csrf()
    chosen = lang_code if lang_code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    session["lang"] = chosen
    session.permanent = True

    next_url = request.form.get("next", "").strip()
    if not next_url and request.referrer:
        parsed_ref = urlparse(request.referrer)
        next_url = parsed_ref.path + (f"?{parsed_ref.query}" if parsed_ref.query else "")
    parsed_next = urlparse(next_url)
    target = (
        next_url
        if next_url and next_url.startswith("/") and not next_url.startswith(("//", "/\\")) and not parsed_next.netloc
        else url_for("main.index")
    )
    resp = make_response(redirect(target))
    set_language_cookie(resp, chosen)
    return resp
