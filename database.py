"""
SkillMap SQLite Database Layer
------------------------------
Manages SQLite connections, normalized schema creation, foreign key enforcement,
and helper functions for parameterized queries.

AI Assistance Note:
Schema normalization and SQLite connection lifecycle helpers were developed
with AI assistance and audited for SQL injection safety and referential integrity.
"""

import os
import sqlite3
from typing import Any, Iterable, Optional

from flask import current_app, g


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    bio TEXT NOT NULL DEFAULT '',
    target_career_id INTEGER REFERENCES career_paths(id) ON DELETE SET NULL,
    weekly_goal_hours REAL NOT NULL DEFAULT 10.0 CHECK (weekly_goal_hours >= 1 AND weekly_goal_hours <= 100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS career_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL UNIQUE,
    tagline TEXT NOT NULL,
    description TEXT NOT NULL,
    estimated_hours INTEGER NOT NULL CHECK (estimated_hours > 0),
    estimated_months INTEGER NOT NULL CHECK (estimated_months > 0),
    difficulty_summary TEXT NOT NULL,
    icon_name TEXT NOT NULL DEFAULT 'compass',
    accent_color TEXT NOT NULL DEFAULT '#4338CA',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_path_id INTEGER NOT NULL REFERENCES career_paths(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('Beginner', 'Intermediate', 'Advanced')),
    description TEXT NOT NULL,
    estimated_hours INTEGER NOT NULL DEFAULT 20 CHECK (estimated_hours > 0),
    sort_order INTEGER NOT NULL DEFAULT 0,
    UNIQUE (career_path_id, name)
);

CREATE TABLE IF NOT EXISTS career_recommended_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_path_id INTEGER NOT NULL REFERENCES career_paths(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('Beginner', 'Intermediate', 'Advanced')),
    description TEXT NOT NULL,
    tech_stack TEXT NOT NULL,
    estimated_hours INTEGER NOT NULL DEFAULT 15 CHECK (estimated_hours > 0)
);

CREATE TABLE IF NOT EXISTS roadmap_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_path_id INTEGER NOT NULL REFERENCES career_paths(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    level TEXT NOT NULL DEFAULT 'Beginner' CHECK (level IN ('Beginner', 'Intermediate', 'Advanced')),
    estimated_hours REAL NOT NULL DEFAULT 2.0 CHECK (estimated_hours >= 0),
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK (is_completed IN (0, 1)),
    due_date TEXT,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_path_id INTEGER NOT NULL REFERENCES career_paths(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    mastery_percent INTEGER NOT NULL DEFAULT 0 CHECK (mastery_percent >= 0 AND mastery_percent <= 100),
    hours_logged REAL NOT NULL DEFAULT 0.0 CHECK (hours_logged >= 0),
    personal_goal TEXT NOT NULL DEFAULT '',
    target_date TEXT,
    is_active_path INTEGER NOT NULL DEFAULT 1 CHECK (is_active_path IN (0, 1)),
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_career_goal
    ON user_progress(user_id, career_path_id)
    WHERE skill_id IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_skill_prog
    ON user_progress(user_id, career_path_id, skill_id)
    WHERE skill_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    career_path_id INTEGER REFERENCES career_paths(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Documentation', 'Course', 'Book', 'Video', 'Article', 'Tool', 'Practice Lab')),
    difficulty TEXT NOT NULL DEFAULT 'Beginner' CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK (is_completed IN (0, 1)),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_path_id INTEGER REFERENCES career_paths(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tech_stack TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Planned' CHECK (status IN ('Planned', 'In Progress', 'Completed', 'On Hold')),
    github_url TEXT NOT NULL DEFAULT '',
    completion_percent INTEGER NOT NULL DEFAULT 0 CHECK (completion_percent >= 0 AND completion_percent <= 100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_path_id INTEGER NOT NULL REFERENCES career_paths(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assessment_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_path_id INTEGER NOT NULL REFERENCES career_paths(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL CHECK (correct_option IN ('A', 'B', 'C', 'D')),
    explanation TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'Beginner' CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced'))
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_path_id INTEGER NOT NULL REFERENCES career_paths(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    assessment_type TEXT NOT NULL DEFAULT 'Quiz' CHECK (assessment_type IN ('Quiz', 'Self-Evaluation', 'Practical')),
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    total_questions INTEGER NOT NULL DEFAULT 5 CHECK (total_questions >= 1),
    correct_answers INTEGER NOT NULL DEFAULT 0 CHECK (correct_answers >= 0),
    needs_practice INTEGER NOT NULL DEFAULT 0 CHECK (needs_practice IN (0, 1)),
    feedback TEXT NOT NULL DEFAULT '',
    taken_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_path_id INTEGER REFERENCES career_paths(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    hours_spent REAL NOT NULL DEFAULT 0.0 CHECK (hours_spent >= 0),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_roadmap_user_career ON roadmap_tasks(user_id, career_path_id);
CREATE INDEX IF NOT EXISTS idx_resources_user ON resources(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_user_career ON notes(user_id, career_path_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user ON assessments(user_id, career_path_id);
CREATE INDEX IF NOT EXISTS idx_activity_user_date ON activity_logs(user_id, created_at);
"""


def get_db() -> sqlite3.Connection:
    """Open (or reuse) a request-scoped SQLite connection with foreign keys enabled."""
    if "db" not in g:
        db_path = current_app.config["DATABASE_PATH"]
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn
    return g.db


def close_db(_error: Optional[BaseException] = None) -> None:
    """Close the request-scoped SQLite connection at teardown."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(conn: Optional[sqlite3.Connection] = None) -> None:
    """Create all database tables and indexes if they do not exist."""
    db = conn or get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()


def query_all(sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
    """Execute a parameterized SELECT query and return all matching rows."""
    return get_db().execute(sql, tuple(params)).fetchall()


def query_one(sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
    """Execute a parameterized SELECT query and return the first row or None."""
    return get_db().execute(sql, tuple(params)).fetchone()


def execute_write(sql: str, params: Iterable[Any] = ()) -> int:
    """Execute a parameterized INSERT/UPDATE/DELETE statement and return lastrowid."""
    db = get_db()
    cursor = db.execute(sql, tuple(params))
    db.commit()
    return cursor.lastrowid


def log_activity(
    user_id: int,
    action_type: str,
    description: str,
    career_path_id: Optional[int] = None,
    hours_spent: float = 0.0,
) -> None:
    """Record a timestamped learning activity for dashboard metrics and recent feeds."""
    execute_write(
        """
        INSERT INTO activity_logs (user_id, career_path_id, action_type, description, hours_spent)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, career_path_id, action_type, description, max(0.0, float(hours_spent))),
    )
