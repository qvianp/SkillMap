"""
SkillMap Routes Package
-----------------------
Aggregates modular Flask blueprints for dashboard, career explorer,
personalized roadmaps, resource library, project tracker, notes & assessments,
and JSON API endpoints.

AI Assistance Note:
Blueprint organization was structured with AI assistance and reviewed by the author.
"""

from routes.main import main_bp
from routes.careers import careers_bp
from routes.roadmap import roadmap_bp
from routes.resources import resources_bp
from routes.projects import projects_bp
from routes.notes_assessments import hub_bp
from routes.api import api_bp

ALL_BLUEPRINTS = [
    main_bp,
    careers_bp,
    roadmap_bp,
    resources_bp,
    projects_bp,
    hub_bp,
    api_bp,
]
