"""
SkillMap — Smart Learning & Career Platform
-------------------------------------------
Main Flask Application Factory and Runtime Entrypoint.

AI Assistance Note:
Application factory wiring, ProxyFix configuration, and environment-aware
session cookie handling were developed with AI assistance and reviewed by the author.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Type

# Ensure local vendored packages (.pylibs) are importable if system site-packages
# does not contain Flask (e.g., when running inside containerized previews).
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PYLIBS_DIR = os.path.join(BASE_DIR, ".pylibs")
if os.path.isdir(PYLIBS_DIR) and PYLIBS_DIR not in sys.path:
    sys.path.insert(0, PYLIBS_DIR)

from flask import Flask, g, jsonify, render_template, request
from flask.sessions import SecureCookieSessionInterface
from werkzeug.middleware.proxy_fix import ProxyFix

from auth import auth_bp, get_csrf_token, is_https_request, load_logged_in_user
from config import Config
from database import close_db, init_db
from routes import ALL_BLUEPRINTS
from seed_data import seed_catalog, seed_demo_user
from translations import (
    format_localized_datetime,
    get_client_i18n,
    get_lang,
    get_text_dir,
    load_language_preference,
    t,
    t_activity_desc,
    t_assessment_feedback,
    t_assessment_title,
    t_career_field,
    t_enum,
    t_goal,
    t_note_content,
    t_note_title,
    t_project_desc,
    t_project_name,
    t_question,
    t_rec_project_desc,
    t_rec_project_title,
    t_resource_desc,
    t_resource_title,
    t_skill_desc,
    t_skill_name,
    t_task_desc,
    t_task_title,
)


class AdaptiveSessionInterface(SecureCookieSessionInterface):
    """
    Use SameSite=None; Secure; Partitioned when accessed over HTTPS (such as
    proxied cloud previews inside cross-site iframes), while keeping SameSite=Lax
    on local http://127.0.0.1 so standard local browsers and test clients work cleanly.
    """

    def get_cookie_samesite(self, app: Flask) -> Optional[str]:
        if is_https_request():
            return "None"
        return app.config.get("SESSION_COOKIE_SAMESITE", "Lax")

    def get_cookie_secure(self, app: Flask) -> bool:
        if is_https_request():
            return True
        return bool(app.config.get("SESSION_COOKIE_SECURE", False))

    def get_cookie_partitioned(self, app: Flask) -> bool:
        if is_https_request():
            return True
        return bool(app.config.get("SESSION_COOKIE_PARTITIONED", False))


def create_app(config_class: Type[Config] = Config) -> Flask:
    """Create and configure a SkillMap Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.session_interface = AdaptiveSessionInterface()
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    app.teardown_appcontext(close_db)
    app.before_request(load_language_preference)
    app.before_request(load_logged_in_user)

    @app.after_request
    def apply_security_cache_headers(response):
        """Prevent HTTP/bfcache caching of dynamic responses carrying session CSRF tokens."""
        if not request.path.startswith("/static/"):
            response.headers.setdefault("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            response.headers.setdefault("Pragma", "no-cache")
        return response

    @app.template_filter("format_datetime")
    def format_datetime_filter(value) -> str:
        """Format SQLite timestamps into localized readable strings."""
        return format_localized_datetime(value)

    @app.context_processor
    def inject_globals():
        lang = get_lang()
        return {
            "csrf_token": get_csrf_token,
            "current_user": getattr(g, "user", None),
            "app_name": app.config.get("APP_NAME", "SkillMap"),
            "current_lang": lang,
            "text_dir": get_text_dir(lang),
            "client_i18n": get_client_i18n(lang),
            "t": t,
            "t_enum": t_enum,
            "t_career_field": t_career_field,
            "t_skill_name": t_skill_name,
            "t_skill_desc": t_skill_desc,
            "t_task_title": t_task_title,
            "t_task_desc": t_task_desc,
            "t_rec_project_title": t_rec_project_title,
            "t_rec_project_desc": t_rec_project_desc,
            "t_resource_title": t_resource_title,
            "t_resource_desc": t_resource_desc,
            "t_project_name": t_project_name,
            "t_project_desc": t_project_desc,
            "t_note_title": t_note_title,
            "t_note_content": t_note_content,
            "t_goal": t_goal,
            "t_question": t_question,
            "t_assessment_title": t_assessment_title,
            "t_assessment_feedback": t_assessment_feedback,
            "t_activity_desc": t_activity_desc,
        }

    # Register authentication and feature blueprints
    app.register_blueprint(auth_bp)
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    # Custom HTTP error handlers
    @app.errorhandler(400)
    def bad_request(error):
        desc = getattr(error, "description", None)
        if request.path.startswith("/api/"):
            return jsonify({"error": desc or t("api.bad_request")}), 400
        return render_template("errors/404.html", code=400, title=t("err.400_title"), message=desc or t("err.400_msg")), 400

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify({"error": t("api.not_found")}), 404
        return render_template("errors/404.html", code=404, title=t("err.404_title"), message=t("err.404_msg")), 404

    @app.errorhandler(500)
    def server_error(_error):
        if request.path.startswith("/api/"):
            return jsonify({"error": t("api.server_error")}), 500
        return render_template("errors/500.html"), 500

    # Initialize schema and seed catalog on startup (unless using an isolated :memory: test DB)
    if app.config["DATABASE_PATH"] != ":memory:":
        with app.app_context():
            init_db()
            seed_catalog()
            seed_demo_user()

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", os.environ.get("PORT", 5000)))
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
