"""
SkillMap Notes & Skill Assessments Routes
-----------------------------------------
Manages personal study notes per career path/skill and interactive skill
assessments (both graded multiple-choice quizzes and self-evaluations) that
identify weak skills needing further practice.

AI Assistance Note:
Quiz grading aggregation and latest-attempt weak-skill queries were refined
with AI assistance and tested by the author.
"""

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from auth import login_required, validate_csrf
from database import execute_write, log_activity, query_all, query_one
from translations import (
    t,
    t_assessment_feedback,
    t_assessment_title,
    t_note_content,
    t_note_title,
    t_question,
)

hub_bp = Blueprint("hub", __name__)

VALID_ASSESSMENT_TYPES = ("Quiz", "Self-Evaluation", "Practical")


@hub_bp.route("/notes")
@login_required
def notes_index():
    """List and filter personal study notes grouped by career path and skill."""
    career_filter = request.args.get("career_id", "").strip()
    search = request.args.get("q", "").strip()

    sql = """
        SELECT n.*, cp.title AS career_title, cp.slug AS career_slug, s.name AS skill_name
        FROM notes n
        JOIN career_paths cp ON cp.id = n.career_path_id
        LEFT JOIN skills s ON s.id = n.skill_id
        WHERE n.user_id = ?
    """
    params: list = [g.user["id"]]

    if career_filter.isdigit():
        sql += " AND n.career_path_id = ?"
        params.append(int(career_filter))

    sql += " ORDER BY n.updated_at DESC, n.id DESC"
    notes = query_all(sql, params)
    if search:
        term = search.lower()
        notes = [
            row
            for row in notes
            if term in row["title"].lower()
            or term in (row["content"] or "").lower()
            or term in t_note_title(row["title"]).lower()
            or term in t_note_content(row["title"], row["content"] or "").lower()
        ]
    careers = query_all("SELECT id, slug, title FROM career_paths ORDER BY title ASC")
    skills = query_all("SELECT id, career_path_id, name FROM skills ORDER BY career_path_id ASC, sort_order ASC")

    return render_template(
        "notes/index.html",
        notes=notes,
        careers=careers,
        skills=skills,
        filters={"career_id": career_filter, "q": search},
    )


@hub_bp.route("/notes/add", methods=["POST"])
@login_required
def add_note():
    """Create a new personal study note."""
    validate_csrf()
    career_raw = request.form.get("career_path_id", "").strip()
    skill_raw = request.form.get("skill_id", "").strip()
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not career_raw.isdigit() or not query_one("SELECT id FROM career_paths WHERE id = ?", (int(career_raw),)):
        flash(t("notes.flash_invalid_career"), "error")
        return redirect(url_for("hub.notes_index"))

    career_id = int(career_raw)
    if len(title) < 2 or len(title) > 140:
        flash(t("notes.flash_title_len"), "error")
        return redirect(url_for("hub.notes_index"))
    if len(content) < 3:
        flash(t("notes.flash_content_empty"), "error")
        return redirect(url_for("hub.notes_index"))

    skill_id = None
    if skill_raw.isdigit():
        skill_row = query_one(
            "SELECT id FROM skills WHERE id = ? AND career_path_id = ?",
            (int(skill_raw), career_id),
        )
        if skill_row:
            skill_id = skill_row["id"]

    execute_write(
        """
        INSERT INTO notes (user_id, career_path_id, skill_id, title, content)
        VALUES (?, ?, ?, ?, ?)
        """,
        (g.user["id"], career_id, skill_id, title, content),
    )
    log_activity(g.user["id"], "note_created", f"Added study note: {title}", career_id, 0.5)
    flash(t("notes.flash_saved"), "success")
    return redirect(url_for("hub.notes_index"))


@hub_bp.route("/notes/<int:note_id>/edit", methods=["POST"])
@login_required
def edit_note(note_id: int):
    """Edit an existing user-owned study note."""
    validate_csrf()
    note = query_one("SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, g.user["id"]))
    if note is None:
        abort(404)

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if len(title) < 2 or len(content) < 3:
        flash(t("notes.flash_edit_req"), "error")
        return redirect(url_for("hub.notes_index"))

    execute_write(
        "UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
        (title, content, note_id, g.user["id"]),
    )
    flash(t("notes.flash_updated"), "success")
    return redirect(url_for("hub.notes_index"))


@hub_bp.route("/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id: int):
    """Delete a user-owned study note."""
    validate_csrf()
    note = query_one("SELECT id, title FROM notes WHERE id = ? AND user_id = ?", (note_id, g.user["id"]))
    if note is None:
        abort(404)

    execute_write("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, g.user["id"]))
    flash(t("notes.flash_deleted", title=t_note_title(note["title"])), "success")
    return redirect(url_for("hub.notes_index"))


@hub_bp.route("/assessments")
@login_required
def assessments_index():
    """Display skill assessment history, interactive quiz launchers, and weak-skill insights."""
    assessments = query_all(
        """
        SELECT a.*, cp.title AS career_title, cp.slug AS career_slug, s.name AS skill_name
        FROM assessments a
        JOIN career_paths cp ON cp.id = a.career_path_id
        LEFT JOIN skills s ON s.id = a.skill_id
        WHERE a.user_id = ?
        ORDER BY a.taken_at DESC, a.id DESC
        """,
        (g.user["id"],),
    )

    weak_skills = query_all(
        """
        SELECT
            a.id,
            a.title,
            a.score,
            a.feedback,
            a.taken_at,
            cp.id AS career_path_id,
            cp.title AS career_title,
            cp.slug AS career_slug,
            s.id AS skill_id,
            s.name AS skill_name
        FROM assessments a
        JOIN career_paths cp ON cp.id = a.career_path_id
        LEFT JOIN skills s ON s.id = a.skill_id
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
        """,
        (g.user["id"],),
    )

    careers = query_all(
        """
        SELECT cp.*, COUNT(aq.id) AS question_count
        FROM career_paths cp
        LEFT JOIN assessment_questions aq ON aq.career_path_id = cp.id
        GROUP BY cp.id
        ORDER BY cp.id ASC
        """
    )
    skills = query_all("SELECT id, career_path_id, name FROM skills ORDER BY career_path_id ASC, sort_order ASC")

    summary = query_one(
        """
        SELECT
            COUNT(*) AS total,
            COALESCE(ROUND(AVG(score)), 0) AS avg_score
        FROM assessments
        WHERE user_id = ?
        """,
        (g.user["id"],),
    )
    summary_dict = {
        "total": int(summary["total"]) if summary else 0,
        "avg_score": int(summary["avg_score"]) if summary else 0,
        "needs_practice_count": len(weak_skills),
    }

    return render_template(
        "assessments/index.html",
        assessments=assessments,
        weak_skills=weak_skills,
        careers=careers,
        skills=skills,
        summary=summary_dict,
        assessment_types=VALID_ASSESSMENT_TYPES,
    )


@hub_bp.route("/assessments/take/<slug>", methods=["GET", "POST"])
@login_required
def take_quiz(slug: str):
    """Run an interactive graded assessment quiz for a career path."""
    career = query_one("SELECT * FROM career_paths WHERE slug = ?", (slug,))
    if career is None:
        abort(404)

    raw_questions = query_all(
        """
        SELECT aq.*, s.name AS skill_name
        FROM assessment_questions aq
        LEFT JOIN skills s ON s.id = aq.skill_id
        WHERE aq.career_path_id = ?
        ORDER BY aq.id ASC
        """,
        (career["id"],),
    )
    if not raw_questions:
        flash(t("assess.flash_no_questions"), "warning")
        return redirect(url_for("hub.assessments_index"))
    questions = [t_question(q) for q in raw_questions]

    if request.method == "POST":
        validate_csrf()
        total = len(questions)
        correct_count = 0
        results = []
        weak_skill_names = []
        primary_weak_skill_id = None

        saved_choices: dict[str, str] = {}
        per_skill_tally: dict[int, list[int]] = {}
        for q in questions:
            chosen = request.form.get(f"q_{q['id']}", "").strip().upper()
            saved_choices[str(q["id"])] = chosen
            is_correct = chosen == q["correct_option"]
            if is_correct:
                correct_count += 1
            else:
                if q["skill_name"] and q["skill_name"] not in weak_skill_names:
                    weak_skill_names.append(q["skill_name"])
                if primary_weak_skill_id is None and q["skill_id"]:
                    primary_weak_skill_id = q["skill_id"]

            if q["skill_id"]:
                tally = per_skill_tally.setdefault(int(q["skill_id"]), [0, 0])
                tally[0] += 1 if is_correct else 0
                tally[1] += 1

            results.append({
                "question": q,
                "chosen": chosen,
                "is_correct": is_correct,
            })

        # Update per-skill mastery once per skill using aggregated quiz accuracy
        for sid, (hits, q_total) in per_skill_tally.items():
            prog = query_one(
                "SELECT id, mastery_percent FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id = ?",
                (g.user["id"], career["id"], sid),
            )
            if prog:
                current_pct = int(prog["mastery_percent"])
                skill_quiz_pct = round((hits / q_total) * 100)
                new_pct = max(current_pct, 80) if skill_quiz_pct >= 70 else min(current_pct, 55)
                execute_write(
                    "UPDATE user_progress SET mastery_percent = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_pct, prog["id"]),
                )

        score = round((correct_count / total) * 100)
        needs_practice = 1 if score < 70 else 0
        if weak_skill_names:
            feedback = f"Focus next on: {', '.join(weak_skill_names)}."
        else:
            feedback = f"Excellent mastery across all {career['title']} core topics."

        target_skill_id = primary_weak_skill_id or questions[0]["skill_id"]
        execute_write(
            """
            INSERT INTO assessments
            (user_id, career_path_id, skill_id, title, assessment_type, score, total_questions, correct_answers, needs_practice, feedback)
            VALUES (?, ?, ?, ?, 'Quiz', ?, ?, ?, ?, ?)
            """,
            (
                g.user["id"],
                career["id"],
                target_skill_id,
                f"{career['title']} Competency Quiz",
                score,
                total,
                correct_count,
                needs_practice,
                feedback,
            ),
        )
        log_activity(
            g.user["id"],
            "assessment_taken",
            f"Completed {career['title']} Competency Quiz ({score}%)",
            career["id"],
            0.5,
        )

        session[f"last_quiz_{slug}"] = {
            "choices": saved_choices,
            "score": score,
            "correct_count": correct_count,
            "total": total,
            "needs_practice": needs_practice,
            "feedback": feedback,
        }

        return render_template(
            "assessments/take.html",
            career=career,
            questions=questions,
            submitted=True,
            score=score,
            correct_count=correct_count,
            total=total,
            needs_practice=needs_practice,
            feedback=t_assessment_feedback(feedback),
            results=results,
        )

    if request.args.get("view") == "result" and isinstance(session.get(f"last_quiz_{slug}"), dict):
        cached = session[f"last_quiz_{slug}"]
        saved_choices = cached.get("choices", {})
        results = [
            {
                "question": q,
                "chosen": saved_choices.get(str(q["id"]), ""),
                "is_correct": saved_choices.get(str(q["id"]), "") == q["correct_option"],
            }
            for q in questions
        ]
        return render_template(
            "assessments/take.html",
            career=career,
            questions=questions,
            submitted=True,
            score=cached.get("score", 0),
            correct_count=cached.get("correct_count", 0),
            total=cached.get("total", len(questions)),
            needs_practice=cached.get("needs_practice", 0),
            feedback=t_assessment_feedback(cached.get("feedback", "")),
            results=results,
        )

    return render_template(
        "assessments/take.html",
        career=career,
        questions=questions,
        submitted=False,
    )


@hub_bp.route("/assessments/add", methods=["POST"])
@login_required
def add_assessment():
    """Log a manual self-evaluation or practical skill assessment."""
    validate_csrf()
    career_raw = request.form.get("career_path_id", "").strip()
    skill_raw = request.form.get("skill_id", "").strip()
    title = request.form.get("title", "").strip()
    assessment_type = request.form.get("assessment_type", "Self-Evaluation").strip()
    score_raw = request.form.get("score", "0").strip()
    feedback = request.form.get("feedback", "").strip()

    if not career_raw.isdigit() or not query_one("SELECT id FROM career_paths WHERE id = ?", (int(career_raw),)):
        flash(t("assess.flash_invalid_career"), "error")
        return redirect(url_for("hub.assessments_index"))

    career_id = int(career_raw)
    if len(title) < 2 or len(title) > 140:
        flash(t("assess.flash_title_len"), "error")
        return redirect(url_for("hub.assessments_index"))

    if assessment_type not in VALID_ASSESSMENT_TYPES:
        assessment_type = "Self-Evaluation"

    try:
        score = max(0, min(100, int(score_raw)))
    except ValueError:
        flash(t("assess.flash_score_int"), "error")
        return redirect(url_for("hub.assessments_index"))

    skill_id = None
    if skill_raw.isdigit():
        skill_row = query_one(
            "SELECT id FROM skills WHERE id = ? AND career_path_id = ?",
            (int(skill_raw), career_id),
        )
        if skill_row:
            skill_id = skill_row["id"]

    needs_practice = 1 if score < 70 else 0
    if not feedback:
        feedback = "Flagged for extra practice (< 70%)." if needs_practice else "Meets competency benchmark."

    execute_write(
        """
        INSERT INTO assessments
        (user_id, career_path_id, skill_id, title, assessment_type, score, total_questions, correct_answers, needs_practice, feedback)
        VALUES (?, ?, ?, ?, ?, ?, 10, ?, ?, ?)
        """,
        (g.user["id"], career_id, skill_id, title, assessment_type, score, round(score / 10), needs_practice, feedback),
    )

    if skill_id is not None:
        prog = query_one(
            "SELECT id FROM user_progress WHERE user_id = ? AND career_path_id = ? AND skill_id = ?",
            (g.user["id"], career_id, skill_id),
        )
        if prog:
            execute_write(
                "UPDATE user_progress SET mastery_percent = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (score, prog["id"]),
            )
        else:
            execute_write(
                """
                INSERT INTO user_progress (user_id, career_path_id, skill_id, mastery_percent, hours_logged, is_active_path)
                VALUES (?, ?, ?, ?, 1.0, 1)
                """,
                (g.user["id"], career_id, skill_id, score),
            )

    log_activity(g.user["id"], "assessment_taken", f"Logged {assessment_type}: {title} ({score}%)", career_id, 0.5)
    flash(t("assess.flash_recorded"), "success")
    return redirect(url_for("hub.assessments_index"))


@hub_bp.route("/assessments/<int:assessment_id>/delete", methods=["POST"])
@login_required
def delete_assessment(assessment_id: int):
    """Delete a user-owned assessment record."""
    validate_csrf()
    row = query_one("SELECT id, title FROM assessments WHERE id = ? AND user_id = ?", (assessment_id, g.user["id"]))
    if row is None:
        abort(404)

    execute_write("DELETE FROM assessments WHERE id = ? AND user_id = ?", (assessment_id, g.user["id"]))
    flash(t("assess.flash_removed", title=t_assessment_title(row["title"])), "success")
    return redirect(url_for("hub.assessments_index"))
