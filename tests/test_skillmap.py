"""
SkillMap Automated Test Suite
-----------------------------
Tests database schema integrity, authentication and password hashing,
user-record authorization boundaries, career enrollment, roadmap CRUD,
resource library, project tracker, study notes, interactive assessments,
and SQLite-computed dashboard analytics.

Run with:
    python3 -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYLIBS_DIR = os.path.join(BASE_DIR, ".pylibs")
if os.path.isdir(PYLIBS_DIR) and PYLIBS_DIR not in sys.path:
    sys.path.insert(0, PYLIBS_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from config import Config
from database import get_db, init_db
from seed_data import seed_catalog


class SkillMapTestCase(unittest.TestCase):
    """End-to-end integration tests backed by an isolated temporary SQLite database."""

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(prefix="skillmap_test_", suffix=".db")

        class LocalTestConfig(Config):
            TESTING = True
            SECRET_KEY = "unit-test-secret"
            DATABASE_PATH = self.db_path
            WTF_CSRF_ENABLED = False

        self.app = create_app(LocalTestConfig)
        with self.app.app_context():
            init_db()
            seed_catalog()

        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _register_user(self, name="Alice Test", email="alice@example.com", password="Password123!"):
        return self.client.post(
            "/register",
            data={
                "full_name": name,
                "email": email,
                "password": password,
                "confirm_password": password,
                "weekly_goal_hours": "12",
            },
            follow_redirects=True,
        )

    def _login_user(self, email="alice@example.com", password="Password123!"):
        return self.client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def test_schema_and_catalog_seed(self):
        """Verify all 10 core tables and 6 career paths exist in SQLite."""
        required_tables = {
            "users",
            "career_paths",
            "skills",
            "roadmap_tasks",
            "user_progress",
            "resources",
            "projects",
            "notes",
            "assessments",
            "activity_logs",
        }
        with self.app.app_context():
            db = get_db()
            rows = db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            table_names = {r["name"] for r in rows}
            self.assertTrue(required_tables.issubset(table_names))

            careers = db.execute("SELECT slug FROM career_paths").fetchall()
            self.assertEqual(len(careers), 6)

    def test_registration_password_hashing_and_login(self):
        """Verify user registration stores salted password hash and supports login/logout."""
        resp = self._register_user()
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Welcome back, Alice Test", resp.data)

        with self.app.app_context():
            user = get_db().execute("SELECT * FROM users WHERE email = ?", ("alice@example.com",)).fetchone()
            self.assertIsNotNone(user)
            self.assertNotEqual(user["password_hash"], "Password123!")
            self.assertTrue(user["password_hash"].startswith("scrypt:") or user["password_hash"].startswith("pbkdf2:"))

        # Logout and test invalid vs valid login
        self.client.post("/logout", follow_redirects=True)
        bad_login = self._login_user(password="WrongPass!")
        self.assertEqual(bad_login.status_code, 401)

        good_login = self._login_user()
        self.assertEqual(good_login.status_code, 200)
        self.assertIn(b"Welcome back, Alice Test", good_login.data)

    def test_career_enrollment_and_roadmap_crud(self):
        """Verify enrolling in a career path generates tasks and supports toggle/add/delete."""
        self._register_user()

        enroll_resp = self.client.post("/careers/backend-development/enroll", follow_redirects=True)
        self.assertEqual(enroll_resp.status_code, 200)
        self.assertIn(b"Backend Development", enroll_resp.data)

        with self.app.app_context():
            user = get_db().execute("SELECT id FROM users WHERE email = 'alice@example.com'").fetchone()
            career = get_db().execute("SELECT id FROM career_paths WHERE slug = 'backend-development'").fetchone()
            tasks = get_db().execute(
                "SELECT * FROM roadmap_tasks WHERE user_id = ? AND career_path_id = ?",
                (user["id"], career["id"]),
            ).fetchall()
            self.assertGreaterEqual(len(tasks), 6)
            first_task_id = tasks[0]["id"]

        # Toggle first task via JSON API
        toggle_resp = self.client.post(f"/api/tasks/{first_task_id}/toggle")
        self.assertEqual(toggle_resp.status_code, 200)
        payload = toggle_resp.get_json()
        self.assertTrue(payload["is_completed"])
        self.assertEqual(payload["career_completed"], 1)

        # Add a custom task
        add_resp = self.client.post(
            "/roadmap/tasks/add",
            data={
                "career_path_id": str(career["id"]),
                "title": "Benchmark SQLite Indexes",
                "level": "Intermediate",
                "estimated_hours": "3.5",
            },
            follow_redirects=True,
        )
        self.assertEqual(add_resp.status_code, 200)
        self.assertIn(b"Benchmark SQLite Indexes", add_resp.data)

        # Edit the custom task and verify persistence
        with self.app.app_context():
            custom_task = get_db().execute(
                "SELECT id FROM roadmap_tasks WHERE user_id = ? AND title = ?",
                (user["id"], "Benchmark SQLite Indexes"),
            ).fetchone()
            self.assertIsNotNone(custom_task)
            custom_task_id = custom_task["id"]

        edit_task_resp = self.client.post(
            f"/roadmap/tasks/{custom_task_id}/edit",
            data={
                "title": "Benchmark SQLite Composite Indexes",
                "level": "Advanced",
                "estimated_hours": "4.5",
                "description": "Compare EXPLAIN QUERY PLAN outputs.",
            },
            follow_redirects=True,
        )
        self.assertEqual(edit_task_resp.status_code, 200)
        self.assertIn(b"Benchmark SQLite Composite Indexes", edit_task_resp.data)

        # Toggle task with safe local `next` redirect vs blocked external `next`
        safe_toggle = self.client.post(
            f"/roadmap/tasks/{custom_task_id}/toggle",
            data={"next": "/dashboard"},
            follow_redirects=False,
        )
        self.assertEqual(safe_toggle.status_code, 302)
        self.assertTrue(safe_toggle.headers["Location"].endswith("/dashboard"))

        unsafe_toggle = self.client.post(
            f"/roadmap/tasks/{custom_task_id}/toggle",
            data={"next": "https://evil.example/phish"},
            follow_redirects=False,
        )
        self.assertEqual(unsafe_toggle.status_code, 302)
        self.assertNotIn("evil.example", unsafe_toggle.headers["Location"])

        # Verify dashboard calculates completed tasks from DB
        stats_resp = self.client.get("/api/dashboard/stats")
        self.assertEqual(stats_resp.status_code, 200)
        stats_json = stats_resp.get_json()
        self.assertEqual(stats_json["completed_tasks"], 1)
        self.assertEqual(stats_json["active_paths_count"], 1)

    def test_resources_projects_notes_and_assessments(self):
        """Verify CRUD across Resources, Projects, Notes, and Quiz Grading."""
        self._register_user()

        # 1. Resource validation, creation & editing
        bad_res = self.client.post(
            "/resources/add",
            data={"title": "Bad JS URL", "url": "javascript:alert(1)", "category": "Article", "difficulty": "Beginner"},
            follow_redirects=True,
        )
        self.assertIn(b"valid URL", bad_res.data)

        good_res = self.client.post(
            "/resources/add",
            data={
                "title": "Flask Testing Docs",
                "url": "https://flask.palletsprojects.com/en/latest/testing/",
                "category": "Documentation",
                "difficulty": "Intermediate",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Flask Testing Docs", good_res.data)

        with self.app.app_context():
            res_row = get_db().execute("SELECT id FROM resources WHERE title = 'Flask Testing Docs'").fetchone()
            self.assertIsNotNone(res_row)
            res_id = res_row["id"]

        edit_res = self.client.post(
            f"/resources/{res_id}/edit",
            data={
                "title": "Flask Automated Testing Guide",
                "url": "https://flask.palletsprojects.com/en/latest/testing/",
                "category": "Documentation",
                "difficulty": "Advanced",
                "description": "Updated reference guide.",
            },
            follow_redirects=True,
        )
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(b"Flask Automated Testing Guide", edit_res.data)

        # 2. Project creation & update including career_path_id
        proj_resp = self.client.post(
            "/projects/add",
            data={
                "name": "SkillMap Portfolio API",
                "tech_stack": "Python, Flask, SQLite",
                "status": "In Progress",
                "completion_percent": "45",
                "github_url": "https://github.com/example/skillmap-api",
            },
            follow_redirects=True,
        )
        self.assertIn(b"SkillMap Portfolio API", proj_resp.data)

        with self.app.app_context():
            proj_row = get_db().execute("SELECT id FROM projects WHERE name = 'SkillMap Portfolio API'").fetchone()
            career = get_db().execute("SELECT id FROM career_paths WHERE slug = 'cybersecurity'").fetchone()
            questions = get_db().execute(
                "SELECT id, correct_option FROM assessment_questions WHERE career_path_id = ?",
                (career["id"],),
            ).fetchall()

        update_proj = self.client.post(
            f"/projects/{proj_row['id']}/update",
            data={
                "name": "SkillMap Portfolio API v2",
                "tech_stack": "Python, Flask, SQLite, Chart.js",
                "status": "Completed",
                "completion_percent": "100",
                "career_path_id": str(career["id"]),
                "github_url": "https://github.com/example/skillmap-api",
            },
            follow_redirects=True,
        )
        self.assertEqual(update_proj.status_code, 200)
        self.assertIn(b"SkillMap Portfolio API v2", update_proj.data)
        self.assertIn(b"Cybersecurity", update_proj.data)

        # 3. Study note creation
        note_resp = self.client.post(
            "/notes/add",
            data={
                "career_path_id": str(career["id"]),
                "title": "OWASP Prepared Statements",
                "content": "Always bind SQL parameters with ? placeholders.",
            },
            follow_redirects=True,
        )
        self.assertIn(b"OWASP Prepared Statements", note_resp.data)

        # 4. Interactive Quiz Grading with deliberate misses to verify weak-skill detection (<70%)
        quiz_answers = {}
        for idx, q in enumerate(questions):
            # Answer only 1 out of 5 correctly (20% score -> needs_practice = 1)
            if idx == 0:
                quiz_answers[f"q_{q['id']}"] = q["correct_option"]
            else:
                wrong = "A" if q["correct_option"] != "A" else "B"
                quiz_answers[f"q_{q['id']}"] = wrong

        quiz_resp = self.client.post("/assessments/take/cybersecurity", data=quiz_answers)
        self.assertEqual(quiz_resp.status_code, 200)
        self.assertIn(b"Needs Practice", quiz_resp.data)
        self.assertIn(b"20%", quiz_resp.data)

        # Verify weak skill appears on Assessments page before retake
        assess_before = self.client.get("/assessments")
        self.assertIn(b"Skills Needing More Practice", assess_before.data)

        # Retake with 100% correct answers and verify weak-skill banner clears for the latest attempt
        passing_answers = {f"q_{q['id']}": q["correct_option"] for q in questions}
        pass_resp = self.client.post("/assessments/take/cybersecurity", data=passing_answers)
        self.assertEqual(pass_resp.status_code, 200)
        self.assertIn(b"Proficient", pass_resp.data)
        self.assertIn(b"100%", pass_resp.data)

        assess_after = self.client.get("/assessments")
        self.assertNotIn(b"Skills Needing More Practice", assess_after.data)

    def test_user_record_isolation(self):
        """Ensure User B cannot access, toggle, or delete records owned by User A."""
        # User A creates a project
        self._register_user(name="User A", email="usera@example.com")
        self.client.post(
            "/projects/add",
            data={"name": "Private Project A", "tech_stack": "Python", "status": "Planned", "completion_percent": "0"},
            follow_redirects=True,
        )
        with self.app.app_context():
            proj_a = get_db().execute("SELECT id FROM projects WHERE name = 'Private Project A'").fetchone()
            self.assertIsNotNone(proj_a)
            proj_a_id = proj_a["id"]

        self.client.post("/logout", follow_redirects=True)

        # User B registers and attempts to delete or update User A's project
        self._register_user(name="User B", email="userb@example.com")
        del_resp = self.client.post(f"/projects/{proj_a_id}/delete")
        self.assertEqual(del_resp.status_code, 404)

        api_resp = self.client.post(f"/api/projects/{proj_a_id}/progress", json={"completion_percent": 99})
        self.assertEqual(api_resp.status_code, 404)

        # Confirm User A's project remained untouched
        with self.app.app_context():
            still_there = get_db().execute("SELECT completion_percent FROM projects WHERE id = ?", (proj_a_id,)).fetchone()
            self.assertIsNotNone(still_there)
            self.assertEqual(still_there["completion_percent"], 0)

    def test_bilingual_persian_and_rtl_switching(self):
        """Verify EN/FA language switching, RTL layout attributes, persistence across auth, and localized views."""
        # 1. Default landing is English LTR
        landing_en = self.client.get("/")
        self.assertEqual(landing_en.status_code, 200)
        self.assertIn(b'<html lang="en" dir="ltr">', landing_en.data)
        self.assertIn(b"Smart Learning &amp; Career Platform", landing_en.data)

        # 2. Switch to Persian via zero-refresh JSON API
        switch_res = self.client.post("/api/language", json={"lang": "fa"})
        self.assertEqual(switch_res.status_code, 200)
        switch_payload = switch_res.get_json()
        self.assertEqual(switch_payload["lang"], "fa")
        self.assertEqual(switch_payload["dir"], "rtl")
        self.assertIn("skillmap_lang=fa", switch_res.headers.get("Set-Cookie", ""))

        # Invalid language code rejected cleanly
        bad_lang = self.client.post("/api/language", json={"lang": "fr"})
        self.assertEqual(bad_lang.status_code, 400)

        # 3. Public views now render Persian + RTL + Vazirmatn font
        landing_fa = self.client.get("/")
        self.assertEqual(landing_fa.status_code, 200)
        self.assertIn(b'<html lang="fa" dir="rtl">', landing_fa.data)
        self.assertIn(b"Vazirmatn", landing_fa.data)
        self.assertIn("نقشه راه".encode("utf-8"), landing_fa.data)

        # Persian career search finds translated career while preserving tech terms
        careers_fa = self.client.get("/careers/?q=بک")
        self.assertEqual(careers_fa.status_code, 200)
        self.assertIn("توسعه بک‌اند".encode("utf-8"), careers_fa.data)

        detail_fa = self.client.get("/careers/backend-development")
        self.assertEqual(detail_fa.status_code, 200)
        self.assertIn("Python".encode("utf-8"), detail_fa.data)
        self.assertIn("سطح مبتدی".encode("utf-8"), detail_fa.data)

        # 4. Register user and verify language preference survives session reset on login/register/logout
        reg_resp = self._register_user(name="Sara Dev", email="sara@example.com")
        self.assertEqual(reg_resp.status_code, 200)
        self.assertIn(b'<html lang="fa" dir="rtl">', reg_resp.data)
        self.assertIn("داشبورد یادگیری".encode("utf-8"), reg_resp.data)

        self.client.post("/careers/backend-development/enroll", follow_redirects=True)

        # Verify all authenticated workspace routes in Persian RTL
        for path in ("/dashboard", "/roadmap/", "/resources/", "/projects/", "/notes", "/assessments", "/assessments/take/cybersecurity", "/profile"):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, f"Expected 200 on {path}")
            self.assertIn(b'<html lang="fa" dir="rtl">', resp.data, f"Missing RTL header on {path}")

        # Verify localized Persian validation flash message
        bad_res = self.client.post(
            "/resources/add",
            data={"title": "Bad", "url": "javascript:alert(1)", "category": "Article", "difficulty": "Beginner"},
            follow_redirects=True,
        )
        self.assertIn("نشانی معتبر".encode("utf-8"), bad_res.data)

        # 5. Logout preserves language preference, and fallback POST /language/en switches back to LTR
        logout_resp = self.client.post("/logout", follow_redirects=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertIn(b'<html lang="fa" dir="rtl">', logout_resp.data)

        en_back = self.client.post("/language/en", data={"next": "/login"}, follow_redirects=True)
        self.assertEqual(en_back.status_code, 200)
        self.assertIn(b'<html lang="en" dir="ltr">', en_back.data)
        self.assertIn(b"Sign in to SkillMap", en_back.data)


class SkillMapCsrfTestCase(unittest.TestCase):
    """Verify real CSRF protection, session cookies, and EN/FA language switching end-to-end."""

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(prefix="skillmap_csrf_test_", suffix=".db")

        class CsrfEnabledConfig(Config):
            TESTING = True
            SECRET_KEY = "csrf-unit-test-secret"
            DATABASE_PATH = self.db_path
            WTF_CSRF_ENABLED = True

        self.app = create_app(CsrfEnabledConfig)
        with self.app.app_context():
            init_db()
            seed_catalog()
            from seed_data import seed_demo_user
            seed_demo_user()

        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    @staticmethod
    def _extract_csrf(html_bytes: bytes) -> str:
        import re
        match = re.search(rb'<meta name="csrf-token" content="([^"]+)"', html_bytes)
        if not match:
            raise AssertionError("Missing csrf-token meta tag in response")
        return match.group(1).decode("utf-8")

    def test_csrf_enforced_and_unauthenticated_language_switching(self):
        """CSRF validation must reject missing/bad tokens and allow valid unauthenticated EN <-> FA switches."""
        landing = self.client.get("/")
        self.assertEqual(landing.status_code, 200)
        self.assertIn("no-store", landing.headers.get("Cache-Control", ""))
        csrf_token = self._extract_csrf(landing.data)

        # Missing or invalid CSRF token must return 400
        missing_csrf = self.client.post("/api/language", json={"lang": "fa"})
        self.assertEqual(missing_csrf.status_code, 400)

        bad_csrf = self.client.post(
            "/language/fa",
            data={"csrf_token": "wrong-token", "next": "/"},
        )
        self.assertEqual(bad_csrf.status_code, 400)

        # Valid X-CSRFToken header switches EN -> FA
        to_fa = self.client.post(
            "/api/language",
            json={"lang": "fa"},
            headers={"X-CSRFToken": csrf_token},
        )
        self.assertEqual(to_fa.status_code, 200)
        self.assertEqual(to_fa.get_json(), {"lang": "fa", "dir": "rtl"})
        lang_cookies = [c for c in to_fa.headers.getlist("Set-Cookie") if c.startswith("skillmap_lang=")]
        self.assertTrue(lang_cookies and "SameSite=Lax" in lang_cookies[0])

        # Persists across page navigation and refresh
        careers_fa = self.client.get("/careers/")
        self.assertEqual(careers_fa.status_code, 200)
        self.assertIn(b'<html lang="fa" dir="rtl">', careers_fa.data)

        # Valid form POST switches FA -> EN
        to_en = self.client.post(
            "/language/en",
            data={"csrf_token": csrf_token, "next": "/careers/"},
            follow_redirects=True,
        )
        self.assertEqual(to_en.status_code, 200)
        self.assertIn(b'<html lang="en" dir="ltr">', to_en.data)

    def test_authenticated_language_switching_and_https_partitioned_cookies(self):
        """Verify authenticated EN <-> FA switching with CSRF and HTTPS iframe-safe Partitioned cookies."""
        https_headers = {"X-Forwarded-Proto": "https"}
        login_page = self.client.get("/login", headers=https_headers)
        self.assertEqual(login_page.status_code, 200)

        session_cookies = [c for c in login_page.headers.getlist("Set-Cookie") if c.startswith("skillmap_session=")]
        self.assertTrue(session_cookies)
        self.assertIn("SameSite=None", session_cookies[0])
        self.assertIn("Secure", session_cookies[0])
        self.assertIn("Partitioned", session_cookies[0])

        csrf_token = self._extract_csrf(login_page.data)
        demo_resp = self.client.post(
            "/demo-login",
            data={"csrf_token": csrf_token},
            headers=https_headers,
            follow_redirects=True,
        )
        self.assertEqual(demo_resp.status_code, 200)
        self.assertIn(b'<html lang="en" dir="ltr">', demo_resp.data)

        # Demo login resets session -> must use fresh CSRF token from dashboard
        dash_csrf = self._extract_csrf(demo_resp.data)

        # Switch EN -> FA over HTTPS proxy headers
        to_fa = self.client.post(
            "/api/language",
            json={"lang": "fa", "csrf_token": dash_csrf},
            headers={"X-CSRFToken": dash_csrf, **https_headers},
        )
        self.assertEqual(to_fa.status_code, 200)
        lang_cookies = [c for c in to_fa.headers.getlist("Set-Cookie") if c.startswith("skillmap_lang=")]
        self.assertTrue(lang_cookies)
        self.assertIn("SameSite=None", lang_cookies[0])
        self.assertIn("Secure", lang_cookies[0])
        self.assertIn("Partitioned", lang_cookies[0])

        # Persists across authenticated navigation
        roadmap_fa = self.client.get("/roadmap/", headers=https_headers)
        self.assertEqual(roadmap_fa.status_code, 200)
        self.assertIn(b'<html lang="fa" dir="rtl">', roadmap_fa.data)

        # Switch FA -> EN while authenticated
        to_en = self.client.post(
            "/api/language",
            json={"lang": "en", "csrf_token": dash_csrf},
            headers={"X-CSRFToken": dash_csrf, **https_headers},
        )
        self.assertEqual(to_en.status_code, 200)
        dash_en = self.client.get("/dashboard", headers=https_headers)
        self.assertEqual(dash_en.status_code, 200)
        self.assertIn(b'<html lang="en" dir="ltr">', dash_en.data)

    def test_password_visibility_toggles_rendered(self):
        """All password inputs on login, register, and profile pages render accessible eye toggles."""
        login_html = self.client.get("/login").data
        self.assertIn(b'data-password-toggle="login-password"', login_html)
        self.assertIn(b'aria-label="Show password"', login_html)

        reg_html = self.client.get("/register").data
        self.assertIn(b'data-password-toggle="reg-password"', reg_html)
        self.assertIn(b'data-password-toggle="reg-confirm"', reg_html)

        csrf = self._extract_csrf(login_html)
        self.client.post("/api/language", json={"lang": "fa"}, headers={"X-CSRFToken": csrf})
        reg_fa = self.client.get("/register").data
        self.assertIn("نمایش رمز عبور".encode("utf-8"), reg_fa)

        self.client.post("/demo-login", data={"csrf_token": csrf}, follow_redirects=True)
        profile_html = self.client.get("/profile").data
        self.assertIn(b'data-password-toggle="pw-current"', profile_html)
        self.assertIn(b'data-password-toggle="pw-new"', profile_html)
        self.assertIn(b'data-password-toggle="pw-confirm"', profile_html)


if __name__ == "__main__":
    unittest.main()
