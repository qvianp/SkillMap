"""
SkillMap Database Initialization Script
---------------------------------------
Standalone CLI script to initialize or reset the SQLite database schema,
seed the six technology career paths, and populate the demo learner account.

Usage:
    python3 init_db.py
    python3 init_db.py --reset

AI Assistance Note:
CLI database reset workflow was structured with AI assistance and verified by the author.
"""

import argparse
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PYLIBS_DIR = os.path.join(BASE_DIR, ".pylibs")
if os.path.isdir(PYLIBS_DIR) and PYLIBS_DIR not in sys.path:
    sys.path.insert(0, PYLIBS_DIR)

from app import create_app
from config import Config
from database import init_db
from seed_data import seed_catalog, seed_demo_user


def initialize_database(reset: bool = False) -> None:
    """Initialize SQLite schema and seed data."""
    db_path = Config.DATABASE_PATH
    if reset and db_path != ":memory:" and os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")

    app = create_app()
    with app.app_context():
        init_db()
        seed_catalog()
        seed_demo_user()
    print(f"SkillMap database initialized successfully at {db_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize SkillMap SQLite database.")
    parser.add_argument("--reset", action="store_true", help="Delete and recreate the SQLite database.")
    args = parser.parse_args()
    initialize_database(reset=args.reset)
