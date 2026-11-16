"""
SkillMap Configuration Module
-----------------------------
Centralized configuration for development, production, and automated testing.

AI Assistance Note:
Structured configuration patterns and environment-aware cookie settings were
developed with AI assistance and reviewed for CS50x engineering standards.
"""

import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


def _get_or_create_secret_key() -> str:
    """Return environment SECRET_KEY or persist a local instance secret."""
    env_key = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET")
    if env_key:
        return env_key

    os.makedirs(INSTANCE_DIR, exist_ok=True)
    key_file = os.path.join(INSTANCE_DIR, ".secret_key")
    if os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8") as fh:
            stored = fh.read().strip()
            if stored:
                return stored

    generated = secrets.token_hex(32)
    with open(key_file, "w", encoding="utf-8") as fh:
        fh.write(generated)
    return generated


class Config:
    """Base configuration used by the SkillMap Flask application."""

    SECRET_KEY = _get_or_create_secret_key()
    DATABASE_PATH = os.environ.get(
        "SKILLMAP_DB_PATH",
        os.path.join(INSTANCE_DIR, "skillmap.db"),
    )
    SESSION_COOKIE_NAME = "skillmap_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # 7 days
    APP_NAME = "SkillMap"
    WTF_CSRF_ENABLED = True


class TestConfig(Config):
    """Isolated configuration for automated unit and integration tests."""

    TESTING = True
    SECRET_KEY = "test-secret-key-not-for-production"
    DATABASE_PATH = ":memory:"
    WTF_CSRF_ENABLED = False
