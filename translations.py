"""
SkillMap Centralized Internationalization (i18n) Module
-------------------------------------------------------
Single source of truth for English (en / LTR) and Persian (fa / RTL)
UI strings, form labels, validation errors, flash messages, enum values,
dashboard chart labels, and dynamic catalog/domain translations.
"""

import re
from datetime import datetime
from typing import Any, Optional

from flask import g, has_request_context, request, session

SUPPORTED_LANGUAGES = ("en", "fa")
DEFAULT_LANGUAGE = "en"


def get_lang() -> str:
    """Resolve the active language from request context, session, or cookie."""
    if has_request_context():
        cached = getattr(g, "lang", None)
        if cached in SUPPORTED_LANGUAGES:
            return cached
        sess_lang = session.get("lang")
        if sess_lang in SUPPORTED_LANGUAGES:
            return sess_lang
        cookie_lang = request.cookies.get("skillmap_lang")
        if cookie_lang in SUPPORTED_LANGUAGES:
            return cookie_lang
    return DEFAULT_LANGUAGE


def get_text_dir(lang: Optional[str] = None) -> str:
    """Return 'rtl' for Persian and 'ltr' for English."""
    active = lang or get_lang()
    return "rtl" if active == "fa" else "ltr"


def load_language_preference() -> None:
    """Populate g.lang and g.text_dir before handling each request."""
    lang = DEFAULT_LANGUAGE
    sess_lang = session.get("lang")
    cookie_lang = request.cookies.get("skillmap_lang")
    if sess_lang in SUPPORTED_LANGUAGES:
        lang = sess_lang
    elif cookie_lang in SUPPORTED_LANGUAGES:
        lang = cookie_lang
        session["lang"] = lang
    g.lang = lang
    g.text_dir = get_text_dir(lang)


# ============================================================
# Core UI Translation Dictionary (Single Source of Truth)
# ============================================================

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Brand & Meta
        "app.name": "SkillMap",
        "app.tagline": "Smart Learning & Career Platform",
        "meta.description": "SkillMap is a smart learning and career platform to explore tech career paths, build personalized roadmaps, manage resources, track projects, and evaluate skills.",
        "lang.label": "Language",
        "lang.en": "EN",
        "lang.fa": "فا",
        "lang.switch_to_en": "Switch language to English",
        "lang.switch_to_fa": "Switch language to Persian",

        # Navigation & Shell
        "nav.workspace": "Workspace",
        "nav.learning_hub": "Learning Hub",
        "nav.account": "Account",
        "nav.dashboard": "Dashboard",
        "nav.career_explorer": "Career Explorer",
        "nav.my_roadmap": "My Roadmap",
        "nav.resource_library": "Resource Library",
        "nav.project_tracker": "Project Tracker",
        "nav.study_notes": "Study Notes",
        "nav.skill_assessments": "Skill Assessments",
        "nav.profile_goals": "Profile & Goals",
        "nav.sign_out": "Sign Out",
        "nav.explore_careers": "Explore Careers",
        "nav.career_paths": "Career Paths",
        "nav.sign_in": "Sign In",
        "nav.create_account": "Create Account",
        "nav.open_menu": "Open navigation menu",
        "nav.close_menu": "Close navigation menu",
        "nav.sidebar_aria": "Primary Sidebar",
        "nav.public_aria": "Public Navigation",
        "nav.workspace_default": "SkillMap Workspace",

        # Breadcrumbs
        "bc.dashboard": "Workspace / Learning Dashboard",
        "bc.careers": "Workspace / Career Explorer",
        "bc.career_detail": "Career Explorer / {title}",
        "bc.roadmap": "Workspace / Personalized Roadmap",
        "bc.resources": "Learning Hub / Resource Library",
        "bc.projects": "Learning Hub / Project Tracker",
        "bc.notes": "Learning Hub / Study Notes",
        "bc.assessments": "Learning Hub / Skill Assessments",
        "bc.quiz": "Skill Assessments / {title} Quiz",
        "bc.profile": "Account / Profile & Goals",

        # Footer & Common Actions
        "footer.left": "SkillMap — Smart Learning & Career Platform",
        "footer.right": "All progress calculated from persisted workspace records",
        "common.dismiss": "Dismiss notification",
        "common.confirm_action": "Confirm Action",
        "common.confirm_default": "Are you sure you want to proceed?",
        "common.confirm_delete_prompt": "Are you sure you want to delete this item?",
        "common.cancel": "Cancel",
        "common.confirm_delete": "Confirm Delete",
        "common.close_modal": "Close modal",
        "common.edit": "Edit",
        "common.delete": "Delete",
        "common.remove": "Remove",
        "common.save": "Save",
        "common.save_changes": "Save Changes",
        "common.update": "Update",
        "common.apply": "Apply",
        "common.filter": "Filter",
        "common.search": "Search",
        "common.reset": "Reset",
        "common.all": "All",
        "common.general": "General",
        "common.hours_short": "hrs",
        "common.hours_unit": "h",
        "common.months_short": "mos",
        "common.skills_count": "{count} skills",
        "common.projects_count": "{count} recommended projects",
        "common.resources_count": "{count} curated resources",
        "common.questions_count": "{count} questions",
        "common.graded": "Graded",
        "common.enrolled": "Enrolled",
        "common.arrow_forward": "→",
        "common.arrow_external": "↗",

        # Landing Page
        "landing.title": "Smart Learning & Career Platform",
        "landing.kicker_1": "Structured Tech Roadmaps",
        "landing.kicker_2": "Skill Mastery Tracking",
        "landing.kicker_3": "Portfolio & Assessments",
        "landing.headline_prefix": "Turn career ambition into a",
        "landing.headline_accent": "measurable engineering roadmap.",
        "landing.lead": "Explore six curated technology career paths, generate personalized task roadmaps, curate your study library, track personal projects, and pinpoint skill gaps with interactive competency assessments.",
        "landing.cta_start": "Start Free Workspace",
        "landing.cta_demo": "Explore Demo Workspace",
        "landing.cta_browse": "Browse Career Paths",
        "landing.panel_kicker": "Included Platform Modules",
        "landing.panel_title": "Everything in one focused workspace",
        "landing.mod_1_label": "6 Curated Career Tracks",
        "landing.mod_1_val": "36 Core Skills",
        "landing.mod_2_label": "Personalized Roadmaps",
        "landing.mod_2_val": "Beginner → Advanced",
        "landing.mod_3_label": "Resource & Project Trackers",
        "landing.mod_3_val": "GitHub Linked",
        "landing.mod_4_label": "Graded Skill Assessments",
        "landing.mod_4_val": "Gap Detection",
        "landing.panel_footer": "Powered by Flask, relational SQLite persistence, and live Chart.js analytics.",
        "landing.explore_heading": "Explore Career Paths",
        "landing.explore_sub": "Each track structures skills across Beginner, Intermediate, and Advanced milestones.",
        "landing.view_all_paths": "View All Paths",
        "landing.inspect_curriculum": "Inspect Curriculum",

        # Auth: Login / Register / Profile
        "auth.login_title": "Sign In",
        "auth.login_heading": "Sign in to SkillMap",
        "auth.login_sub": "Access your learning roadmaps, resources, projects, and skill assessments.",
        "auth.email_label": "Email Address",
        "auth.email_placeholder": "you@example.com",
        "auth.password_label": "Password",
        "auth.password_placeholder": "Enter your password",
        "auth.show_password": "Show password",
        "auth.hide_password": "Hide password",
        "auth.sign_in_btn": "Sign In",
        "auth.demo_btn": "Sign in as Demo Learner (Alex Chen)",
        "auth.demo_hint": "Includes seeded roadmaps, projects, study notes, and 7-day activity logs.",
        "auth.new_here": "New to SkillMap?",
        "auth.create_one": "Create an account",

        "auth.register_title": "Create Account",
        "auth.register_heading": "Create your SkillMap account",
        "auth.register_sub": "Set your target career path and weekly learning goal to build your personal roadmap.",
        "auth.full_name_label": "Full Name",
        "auth.full_name_placeholder": "Jordan Taylor",
        "auth.reg_email_placeholder": "jordan@example.com",
        "auth.reg_password_placeholder": "Minimum 8 characters",
        "auth.confirm_password_label": "Confirm Password",
        "auth.confirm_password_placeholder": "Repeat password",
        "auth.target_career_label": "Target Career Path",
        "auth.choose_later": "Choose later",
        "auth.weekly_goal_label": "Weekly Goal (Hours)",
        "auth.already_registered": "Already registered?",
        "auth.sign_in_link": "Sign in",

        "profile.title": "Profile & Goals",
        "profile.heading": "Profile & Learning Settings",
        "profile.sub": "Manage your personal details, primary career target, weekly study cadence, and password.",
        "profile.back_dashboard": "Back to Dashboard",
        "profile.stat_active_paths": "Active Paths",
        "profile.stat_completed_tasks": "Completed Tasks",
        "profile.stat_portfolio_projects": "Portfolio Projects",
        "profile.stat_total_hours": "Total Hours Logged",
        "profile.learner_card": "Learner Profile",
        "profile.email_hint": "Account email is used as your unique login identifier.",
        "profile.primary_career": "Primary Target Career",
        "profile.none_selected": "None selected",
        "profile.weekly_goal_hours": "Weekly Study Goal (Hours)",
        "profile.bio_label": "Learning Bio",
        "profile.bio_placeholder": "Summarize your current focus and career objectives...",
        "profile.save_btn": "Save Profile",
        "profile.security_card": "Security & Password",
        "profile.current_password": "Current Password",
        "profile.new_password": "New Password",
        "profile.confirm_new_password": "Confirm New Password",
        "profile.update_pw_btn": "Update Password",

        # Auth Flashes & Errors
        "flash.auth_required": "Please sign in to access your SkillMap workspace.",
        "flash.csrf_invalid": "Invalid or missing CSRF security token. Please refresh and try again.",
        "flash.name_length": "Full name must be between 2 and 80 characters.",
        "flash.email_invalid": "Please enter a valid email address.",
        "flash.password_length": "Password must be at least 8 characters long.",
        "flash.password_mismatch": "Passwords do not match.",
        "flash.weekly_goal_range": "Weekly study goal must be between 1 and 100 hours.",
        "flash.weekly_goal_number": "Weekly study goal must be a valid number.",
        "flash.career_not_exist": "Selected target career path does not exist.",
        "flash.career_selection_invalid": "Invalid target career selection.",
        "flash.email_exists": "An account with this email already exists.",
        "flash.welcome_new": "Welcome to SkillMap, {name}! Your learning workspace is ready.",
        "flash.login_required_fields": "Both email and password are required.",
        "flash.login_invalid": "Invalid email address or password.",
        "flash.login_success": "Signed in as {name}.",
        "flash.demo_unavailable": "Demo account is unavailable. Please register a new account.",
        "flash.demo_success": "Signed in to the Demo Learner workspace (Alex Chen).",
        "flash.logout_success": "You have been signed out safely.",
        "flash.bio_length": "Bio cannot exceed 500 characters.",
        "flash.profile_career_invalid": "Selected target career path is invalid.",
        "flash.profile_saved": "Profile settings saved.",
        "flash.current_pw_wrong": "Current password is incorrect.",
        "flash.new_pw_length": "New password must be at least 8 characters long.",
        "flash.new_pw_mismatch": "New passwords do not match.",
        "flash.pw_updated": "Password updated successfully.",

        # Dashboard
        "dash.title": "Learning Dashboard",
        "dash.open_roadmap": "Open My Roadmap",
        "dash.welcome": "Welcome back, {name}",
        "dash.primary_track": "Primary track:",
        "dash.weekly_goal_meta": "Weekly goal: {hours} hrs",
        "dash.no_primary_track": "Select a target career path to structure your learning roadmap and track skill mastery.",
        "dash.kpi_aria": "Key Learning Metrics",
        "dash.kpi_overall": "Overall Progress",
        "dash.kpi_completed_tasks": "Completed Tasks",
        "dash.kpi_enrolled_sub": "Across enrolled roadmaps",
        "dash.kpi_active_paths": "Active Learning Paths",
        "dash.kpi_projects_sub": "{count} portfolio projects tracked",
        "dash.kpi_weekly_activity": "Weekly Activity",
        "dash.kpi_weekly_goal_sub": "{pct}% of {goal}h weekly goal",
        "dash.chart_weekly_title": "Weekly Learning Activity",
        "dash.chart_weekly_aria": "Weekly learning activity bar chart",
        "dash.last_7_days": "Last 7 days",
        "dash.hrs_logged_meta": "{hours} hrs logged",
        "dash.chart_skills_title": "Skills Progress",
        "dash.chart_skills_sub": "Mastery percentage by tracked skill",
        "dash.chart_skills_aria": "Skills mastery horizontal bar chart",
        "dash.assess_skills": "Assess Skills",
        "dash.no_skills_title": "No skills tracked yet",
        "dash.no_skills_desc": "Enroll in a career path to populate your skill mastery chart.",
        "dash.active_paths_heading": "Active Learning Paths",
        "dash.add_path": "Add Path",
        "dash.tasks_of": "{done} of {total} tasks",
        "dash.target_date": "Target {date}",
        "dash.goal_prefix": "Goal: {goal}",
        "dash.no_paths_title": "No active learning paths",
        "dash.no_paths_desc": "Choose one of the six career tracks to generate structured roadmap milestones.",
        "dash.learning_stats": "Learning Statistics",
        "dash.stat_total_hours": "Total Study Hours Logged",
        "dash.stat_resources_completed": "Resources Completed",
        "dash.stat_projects_completed": "Projects Completed",
        "dash.stat_avg_project": "Average Project Progress",
        "dash.stat_avg_assessment": "Average Assessment Score",
        "dash.stat_study_notes": "Personal Study Notes",
        "dash.next_milestones": "Next Milestones & Focus Areas",
        "dash.view_all_tasks": "View All Tasks",
        "dash.weak_skills_banner": "Skills Recommended for Practice (< 70%)",
        "dash.complete_btn": "Complete",
        "dash.no_tasks_title": "No pending roadmap tasks",
        "dash.no_tasks_desc": "Add new milestones in your Roadmap or explore another career path.",
        "dash.recent_activities": "Recent Activities",
        "dash.no_activity_title": "No recent activity logged",
        "dash.no_activity_desc": "Complete roadmap tasks, save resources, or take a skill quiz to record your timeline.",
        "chart.study_hours": "Study Hours",
        "chart.hrs_logged_suffix": "hrs logged",
        "chart.mastery_label": "Mastery %",
        "chart.mastery_suffix": "% mastery",

        # Career Explorer
        "careers.title": "Career Explorer",
        "careers.heading": "Technology Career Explorer",
        "careers.sub": "Inspect structured requirements across Beginner, Intermediate, and Advanced stages, estimated learning timelines, recommended projects, and curated resources.",
        "careers.search_placeholder": "Search careers or domains...",
        "careers.search_aria": "Search career paths",
        "careers.view_details": "View Details",
        "careers.open_roadmap": "Open Roadmap",
        "careers.start_roadmap": "Start Roadmap",
        "careers.empty_title": "No career paths matched \"{query}\"",
        "careers.empty_desc": "Try clearing your search filter to explore all six technology tracks.",
        "careers.show_all": "Show All Careers",
        "careers.all_careers": "All Careers",
        "careers.est_hours": "{hours} estimated hours",
        "careers.est_months": "{months} months pace",
        "careers.open_personalized": "Open Personalized Roadmap",
        "careers.enroll_generate": "Enroll & Generate Roadmap",
        "careers.signup_start": "Sign Up to Start This Path",
        "careers.stage_title": "{level} Stage",
        "careers.rec_projects": "Recommended Portfolio Projects",
        "careers.curated_resources": "Curated Learning Resources",
        "careers.enrolled_flash": "Enrolled in {title}. Starter roadmap tasks have been generated.",
        "careers.switched_flash": "Switched active roadmap to {title}.",

        # Roadmap
        "roadmap.title": "My Roadmap",
        "roadmap.heading": "Personalized Learning Roadmap",
        "roadmap.sub": "Manage career milestones, complete learning tasks, adjust per-skill mastery, and track personal goals.",
        "roadmap.browse_all": "Browse All Paths",
        "roadmap.select_aria": "Select career path",
        "roadmap.enrolled_suffix": "(Enrolled)",
        "roadmap.load_path": "Load Path",
        "roadmap.progress_title": "{title} Progress",
        "roadmap.tasks_ratio": "{done} / {total} tasks",
        "roadmap.hours_ratio": "{done} / {total} hrs",
        "roadmap.goal_card": "Personal Learning Goal",
        "roadmap.target_milestone": "Target Milestone",
        "roadmap.goal_placeholder": "e.g., Ship 2 backend APIs and pass security quiz",
        "roadmap.target_date_label": "Target Completion Date",
        "roadmap.save_goal": "Save Goal",
        "roadmap.tasks_heading": "Learning Tasks",
        "roadmap.filters_aria": "Task filters",
        "roadmap.filter_pending": "Pending",
        "roadmap.filter_completed": "Completed",
        "roadmap.all_levels": "All Levels",
        "roadmap.toggle_aria": "Toggle completion for {title}",
        "roadmap.due_prefix": "Due {date}",
        "roadmap.confirm_remove": "Remove '{title}' from your roadmap?",
        "roadmap.no_tasks_title": "No tasks match the current filter",
        "roadmap.no_tasks_desc": "Add a custom milestone on the right or reset your level/status filters.",
        "roadmap.add_task_card": "Add Custom Task",
        "roadmap.task_title": "Task Title",
        "roadmap.task_placeholder": "e.g., Implement SQLite index benchmark",
        "roadmap.related_skill": "Related Skill",
        "roadmap.general_milestone": "General Milestone",
        "roadmap.level": "Level",
        "roadmap.est_hours": "Estimated Hours",
        "roadmap.due_date": "Due Date",
        "roadmap.notes_opt": "Notes (Optional)",
        "roadmap.notes_placeholder": "Deliverables or references for this milestone...",
        "roadmap.add_btn": "Add to Roadmap",
        "roadmap.skill_tracker": "Skill Mastery Tracker",
        "roadmap.hours_logged_short": "{hours}h logged",
        "roadmap.mastery_aria": "Mastery percent for {name}",
        "roadmap.hours_aria": "Hours logged for {name}",
        "roadmap.edit_modal_title": "Edit Learning Task",
        "roadmap.empty_title": "Choose a Career Path to Begin",
        "roadmap.empty_desc": "Use the path selector above or visit Career Explorer to enroll in Cybersecurity, Network Engineering, Backend Development, Frontend Development, Android Development, or Data Analysis.",
        "roadmap.open_explorer": "Open Career Explorer",
        "roadmap.flash_choose_valid": "Please choose a valid career path.",
        "roadmap.flash_not_found": "Selected career path was not found.",
        "roadmap.flash_loaded": "Loaded {title} roadmap.",
        "roadmap.flash_invalid_career": "Invalid career path.",
        "roadmap.flash_goal_length": "Personal goal must be between 3 and 250 characters.",
        "roadmap.flash_goal_updated": "Personal learning goal updated.",
        "roadmap.flash_select_valid": "Please select a valid career path.",
        "roadmap.flash_title_length": "Task title must be between 2 and 140 characters.",
        "roadmap.flash_task_added": "Roadmap task added.",
        "roadmap.flash_task_completed": "Marked '{title}' as completed.",
        "roadmap.flash_task_reopened": "Reopened '{title}'.",
        "roadmap.flash_task_updated": "Updated task '{title}'.",
        "roadmap.flash_task_removed": "Removed task '{title}'.",
        "roadmap.flash_skill_updated": "Updated '{name}' mastery to {pct}%.",

        # Resources
        "resources.title": "Resource Library",
        "resources.heading": "Resource Library",
        "resources.sub": "Save, categorize, filter, and track completion across documentation, courses, books, videos, and practice labs.",
        "resources.discover_curated": "Discover Curated Resources",
        "resources.completed_counter": "{done} / {total} completed",
        "resources.search_placeholder": "Search saved resources...",
        "resources.search_aria": "Search saved resources",
        "resources.all_categories": "All Categories",
        "resources.all_levels": "All Levels",
        "resources.all_status": "All Status",
        "resources.unread": "Unread",
        "resources.completed": "Completed",
        "resources.filter_cat_aria": "Filter by category",
        "resources.filter_diff_aria": "Filter by difficulty",
        "resources.filter_status_aria": "Filter by completion status",
        "resources.col_resource": "Resource",
        "resources.col_cat_level": "Category & Level",
        "resources.col_status": "Status",
        "resources.col_actions": "Actions",
        "resources.reopen": "Reopen",
        "resources.mark_complete": "Mark Complete",
        "resources.confirm_delete": "Delete '{title}' from your library?",
        "resources.empty_title": "No saved resources found",
        "resources.empty_desc": "Add a new learning link using the form or bookmark a curated resource below.",
        "resources.add_card": "Save New Resource",
        "resources.field_title": "Title",
        "resources.title_placeholder": "e.g., PostgreSQL Indexing Deep Dive",
        "resources.field_url": "URL",
        "resources.url_placeholder": "https://...",
        "resources.field_category": "Category",
        "resources.field_difficulty": "Difficulty",
        "resources.field_career_opt": "Career Path (Optional)",
        "resources.field_desc": "Description",
        "resources.desc_placeholder": "Key takeaways or chapters to focus on...",
        "resources.add_btn": "Add to Library",
        "resources.curated_heading": "Curated Catalog Suggestions",
        "resources.explore_paths": "Explore All Paths",
        "resources.save_to_library": "Save to My Library",
        "resources.all_saved_note": "All curated catalog suggestions are already saved in your personal library.",
        "resources.edit_modal_title": "Edit Saved Resource",
        "resources.flash_title_len": "Resource title must be between 2 and 140 characters.",
        "resources.flash_url_invalid": "Please provide a valid URL starting with http:// or https://.",
        "resources.flash_cat_invalid": "Invalid resource category selected.",
        "resources.flash_diff_invalid": "Invalid difficulty level selected.",
        "resources.flash_career_invalid": "Invalid career path selection.",
        "resources.flash_saved": "Resource saved to your library.",
        "resources.flash_already_saved": "This resource is already in your personal library.",
        "resources.flash_added_curated": "Added '{title}' to your library.",
        "resources.flash_completed": "Marked '{title}' as completed.",
        "resources.flash_unread": "Marked '{title}' as unread.",
        "resources.flash_updated": "Updated resource '{title}'.",
        "resources.flash_removed": "Removed '{title}' from your library.",

        # Projects
        "projects.title": "Project Tracker",
        "projects.heading": "Portfolio Project Tracker",
        "projects.sub": "Plan, build, and track technical portfolio projects linked to GitHub repositories.",
        "projects.view_roadmap": "View Roadmap",
        "projects.kpi_total": "Total Projects",
        "projects.kpi_in_progress": "In Progress",
        "projects.kpi_completed": "Completed",
        "projects.kpi_avg": "Average Completion",
        "projects.filter_aria": "Project status filter",
        "projects.search_placeholder": "Filter by stack or name...",
        "projects.search_aria": "Search projects",
        "projects.github_repo": "GitHub Repository",
        "projects.no_repo": "No repository URL linked",
        "projects.confirm_delete": "Delete project '{name}'?",
        "projects.empty_title": "No projects recorded yet",
        "projects.empty_desc": "Create your first personal project to document your tech stack, progress, and repository URL.",
        "projects.new_card": "New Personal Project",
        "projects.field_name": "Project Name",
        "projects.name_placeholder": "e.g., Network Packet Sniffer CLI",
        "projects.field_stack": "Technology Stack",
        "projects.stack_placeholder": "Python, Flask, SQLite, Chart.js",
        "projects.field_status": "Status",
        "projects.field_pct": "Completion (%)",
        "projects.field_career": "Career Path",
        "projects.general_portfolio": "General Portfolio",
        "projects.field_github": "GitHub Repository URL",
        "projects.github_placeholder": "https://github.com/username/repo",
        "projects.field_desc": "Description",
        "projects.desc_placeholder": "Architecture notes, goals, and key features...",
        "projects.create_btn": "Create Project",
        "projects.edit_modal_title": "Edit Project",
        "projects.flash_name_len": "Project name must be between 2 and 120 characters.",
        "projects.flash_stack_req": "Please specify the technology stack (e.g., Python, Flask, SQLite).",
        "projects.flash_status_invalid": "Invalid project status selected.",
        "projects.flash_github_invalid": "GitHub URL must start with http:// or https://.",
        "projects.flash_pct_invalid": "Completion percentage must be an integer between 0 and 100.",
        "projects.flash_career_invalid": "Invalid career path selection.",
        "projects.flash_created": "Project '{name}' created.",
        "projects.flash_update_verify": "Please verify project name, technology stack, status, and GitHub URL.",
        "projects.flash_updated": "Updated '{name}'.",
        "projects.flash_deleted": "Deleted project '{name}'.",

        # Study Notes
        "notes.title": "Study Notes",
        "notes.heading": "Personal Study Notes",
        "notes.sub": "Capture technical summaries, architecture decisions, and key takeaways organized by career path and skill.",
        "notes.search_placeholder": "Search notes...",
        "notes.search_aria": "Search study notes",
        "notes.all_careers": "All Career Paths",
        "notes.filter_career_aria": "Filter notes by career path",
        "notes.confirm_delete": "Delete study note '{title}'?",
        "notes.empty_title": "No study notes yet",
        "notes.empty_desc": "Write your first study note on the right to capture concepts for any learning path.",
        "notes.create_card": "Create Study Note",
        "notes.field_career": "Career Path",
        "notes.field_skill_opt": "Skill (Optional)",
        "notes.general_note": "General Path Note",
        "notes.field_title": "Note Title",
        "notes.title_placeholder": "e.g., OSPF Neighbor States Summary",
        "notes.field_content": "Content",
        "notes.content_placeholder": "Write formulas, commands, or key architectural insights...",
        "notes.save_btn": "Save Note",
        "notes.edit_modal_title": "Edit Study Note",
        "notes.update_btn": "Update Note",
        "notes.flash_invalid_career": "Please choose a valid career path for your note.",
        "notes.flash_title_len": "Note title must be between 2 and 140 characters.",
        "notes.flash_content_empty": "Note content cannot be empty.",
        "notes.flash_saved": "Study note saved.",
        "notes.flash_edit_req": "Note title and content are required.",
        "notes.flash_updated": "Study note updated.",
        "notes.flash_deleted": "Deleted note '{title}'.",

        # Skill Assessments & Quizzes
        "assess.title": "Skill Assessments",
        "assess.heading": "Skill Assessments & Diagnostics",
        "assess.sub": "Take interactive competency quizzes or log practical evaluations to identify skills needing extra practice.",
        "assess.kpi_completed": "Assessments Completed",
        "assess.kpi_avg": "Average Score",
        "assess.kpi_flagged": "Skills Flagged for Practice (< 70%)",
        "assess.quizzes_heading": "Interactive Competency Quizzes",
        "assess.quizzes_sub": "Each quiz automatically grades your answers, updates your skill mastery, and flags topics under 70%.",
        "assess.start_quiz": "Start Quiz",
        "assess.weak_heading": "Skills Needing More Practice",
        "assess.retake": "Retake",
        "assess.history_heading": "Assessment Results History",
        "assess.col_assessment": "Assessment",
        "assess.col_type": "Type",
        "assess.col_score": "Score",
        "assess.col_eval": "Evaluation",
        "assess.col_action": "Action",
        "assess.needs_practice": "Needs Practice",
        "assess.proficient": "Proficient",
        "assess.confirm_delete": "Remove assessment record '{title}'?",
        "assess.empty_title": "No assessments recorded yet",
        "assess.empty_desc": "Launch one of the career quizzes above or log a practical evaluation on the right.",
        "assess.log_card": "Log Skill Evaluation",
        "assess.target_skill": "Target Skill",
        "assess.general_eval": "General Path Assessment",
        "assess.eval_title": "Assessment Title",
        "assess.eval_placeholder": "e.g., SQL Window Functions Lab Check",
        "assess.field_type": "Type",
        "assess.field_score": "Score (0–100)",
        "assess.field_reflection": "Reflection / Weak Areas",
        "assess.reflection_placeholder": "Notes on areas requiring additional practice...",
        "assess.record_btn": "Record Assessment",
        "assess.flash_no_questions": "No quiz questions are available for this path yet.",
        "assess.flash_invalid_career": "Please choose a valid career path.",
        "assess.flash_title_len": "Assessment title must be between 2 and 140 characters.",
        "assess.flash_score_int": "Score must be an integer between 0 and 100.",
        "assess.flash_recorded": "Skill assessment recorded.",
        "assess.flash_removed": "Removed assessment '{title}'.",

        # Quiz Runner
        "quiz.title": "{title} Competency Quiz",
        "quiz.all_assessments": "All Assessments",
        "quiz.subtitle": "Answer all {count} questions to evaluate core skill readiness and uncover focus areas.",
        "quiz.graded_saved": "Quiz Graded & Saved",
        "quiz.correct_of": "{correct} of {total} correct",
        "quiz.score_label": "Score:",
        "quiz.retake_btn": "Retake Quiz",
        "quiz.back_btn": "Back to Assessments",
        "quiz.question_n": "Question {n}",
        "quiz.question_of": "Question {n} of {total}",
        "quiz.correct": "Correct",
        "quiz.incorrect": "Incorrect (Answered {chosen}, Expected {expected})",
        "quiz.none": "None",
        "quiz.explanation": "Explanation:",
        "quiz.submit_btn": "Submit & Grade Quiz",

        # Error Pages & API
        "err.not_found_short": "Not Found",
        "err.400_title": "Invalid Request",
        "err.400_msg": "The request could not be processed.",
        "err.404_title": "Page Not Found",
        "err.404_msg": "The requested SkillMap page or record does not exist.",
        "err.404_fallback": "The requested SkillMap page could not be found.",
        "err.500_title": "Server Error",
        "err.500_heading": "Unexpected Server Error",
        "err.500_msg": "Something went wrong while processing your request. Please return to the dashboard and try again.",
        "err.500_public": "Something went wrong while processing your request.",
        "err.return_dashboard": "Return to Dashboard",
        "err.return_home": "Return Home",
        "api.auth_required": "Authentication required.",
        "api.not_found": "Resource not found.",
        "api.bad_request": "Bad request.",
        "api.server_error": "Internal server error.",
        "api.task_not_found": "Task not found.",
        "api.resource_not_found": "Resource not found.",
        "api.project_not_found": "Project not found.",
        "api.invalid_pct": "Invalid completion percentage.",
    },
    "fa": {
        # Brand & Meta
        "app.name": "SkillMap",
        "app.tagline": "پلتفرم هوشمند یادگیری و مسیر شغلی",
        "meta.description": "SkillMap یک پلتفرم هوشمند یادگیری و مسیر شغلی برای کشف مسیرهای تخصصی فناوری، ساخت نقشه راه شخصی، مدیریت منابع، پیگیری پروژه‌ها و ارزیابی مهارت‌هاست.",
        "lang.label": "زبان",
        "lang.en": "EN",
        "lang.fa": "فا",
        "lang.switch_to_en": "تغییر زبان به انگلیسی",
        "lang.switch_to_fa": "تغییر زبان به فارسی",

        # Navigation & Shell
        "nav.workspace": "فضای کاری",
        "nav.learning_hub": "مرکز یادگیری",
        "nav.account": "حساب کاربری",
        "nav.dashboard": "داشبورد",
        "nav.career_explorer": "کاوشگر مسیرهای شغلی",
        "nav.my_roadmap": "نقشه راه من",
        "nav.resource_library": "کتابخانه منابع",
        "nav.project_tracker": "پیگیری پروژه‌ها",
        "nav.study_notes": "یادداشت‌های مطالعه",
        "nav.skill_assessments": "ارزیابی مهارت‌ها",
        "nav.profile_goals": "پروفایل و اهداف",
        "nav.sign_out": "خروج از حساب",
        "nav.explore_careers": "مشاهده مسیرها",
        "nav.career_paths": "مسیرهای شغلی",
        "nav.sign_in": "ورود",
        "nav.create_account": "ایجاد حساب",
        "nav.open_menu": "باز کردن منوی ناوبری",
        "nav.close_menu": "بستن منوی ناوبری",
        "nav.sidebar_aria": "منوی اصلی",
        "nav.public_aria": "ناوبری عمومی",
        "nav.workspace_default": "فضای کاری SkillMap",

        # Breadcrumbs
        "bc.dashboard": "فضای کاری / داشبورد یادگیری",
        "bc.careers": "فضای کاری / کاوشگر مسیرهای شغلی",
        "bc.career_detail": "کاوشگر مسیرهای شغلی / {title}",
        "bc.roadmap": "فضای کاری / نقشه راه شخصی",
        "bc.resources": "مرکز یادگیری / کتابخانه منابع",
        "bc.projects": "مرکز یادگیری / پیگیری پروژه‌ها",
        "bc.notes": "مرکز یادگیری / یادداشت‌های مطالعه",
        "bc.assessments": "مرکز یادگیری / ارزیابی مهارت‌ها",
        "bc.quiz": "ارزیابی مهارت‌ها / آزمون {title}",
        "bc.profile": "حساب کاربری / پروفایل و اهداف",

        # Footer & Common Actions
        "footer.left": "SkillMap — پلتفرم هوشمند یادگیری و مسیر شغلی",
        "footer.right": "تمام آمار پیشرفت مستقیماً از داده‌های ذخیره‌شده محاسبه می‌شود",
        "common.dismiss": "بستن اعلان",
        "common.confirm_action": "تأیید عملیات",
        "common.confirm_default": "آیا از انجام این کار مطمئن هستید؟",
        "common.confirm_delete_prompt": "آیا از حذف این مورد مطمئن هستید؟",
        "common.cancel": "انصراف",
        "common.confirm_delete": "تأیید حذف",
        "common.close_modal": "بستن پنجره",
        "common.edit": "ویرایش",
        "common.delete": "حذف",
        "common.remove": "حذف",
        "common.save": "ذخیره",
        "common.save_changes": "ذخیره تغییرات",
        "common.update": "به‌روزرسانی",
        "common.apply": "اعمال",
        "common.filter": "فیلتر",
        "common.search": "جست‌وجو",
        "common.reset": "بازنشانی",
        "common.all": "همه",
        "common.general": "عمومی",
        "common.hours_short": "ساعت",
        "common.hours_unit": "ساعت",
        "common.months_short": "ماه",
        "common.skills_count": "{count} مهارت",
        "common.projects_count": "{count} پروژه پیشنهادی",
        "common.resources_count": "{count} منبع منتخب",
        "common.questions_count": "{count} سؤال",
        "common.graded": "نمره‌دهی خودکار",
        "common.enrolled": "ثبت‌نام‌شده",
        "common.arrow_forward": "←",
        "common.arrow_external": "↗",

        # Landing Page
        "landing.title": "پلتفرم هوشمند یادگیری و مسیر شغلی",
        "landing.kicker_1": "نقشه‌های راه ساختاریافته",
        "landing.kicker_2": "پایش تسلط مهارتی",
        "landing.kicker_3": "نمونه‌کار و ارزیابی",
        "landing.headline_prefix": "انگیزه شغلی خود را به یک",
        "landing.headline_accent": "نقشه راه مهندسی قابل اندازه‌گیری تبدیل کنید.",
        "landing.lead": "شش مسیر تخصصی فناوری را بررسی کنید، نقشه راه یادگیری شخصی بسازید، کتابخانه منابع خود را مدیریت کنید، پروژه‌های عملی را پیگیری کنید و با آزمون‌های مهارتی نقاط ضعف خود را بشناسید.",
        "landing.cta_start": "شروع فضای کاری رایگان",
        "landing.cta_demo": "ورود به حساب نمونه (دمو)",
        "landing.cta_browse": "مشاهده مسیرهای شغلی",
        "landing.panel_kicker": "ماژول‌های پلتفرم",
        "landing.panel_title": "همه ابزارها در یک فضای کاری متمرکز",
        "landing.mod_1_label": "۶ مسیر تخصصی منتخب",
        "landing.mod_1_val": "۳۶ مهارت کلیدی",
        "landing.mod_2_label": "نقشه راه شخصی‌سازی‌شده",
        "landing.mod_2_val": "مبتدی ← پیشرفته",
        "landing.mod_3_label": "مدیریت منابع و پروژه‌ها",
        "landing.mod_3_val": "متصل به GitHub",
        "landing.mod_4_label": "آزمون‌های ارزیابی مهارت",
        "landing.mod_4_val": "تشخیص شکاف مهارتی",
        "landing.panel_footer": "ساخته‌شده با Flask، پایگاه داده SQLite و نمودارهای تحلیلی Chart.js.",
        "landing.explore_heading": "کاوش مسیرهای شغلی",
        "landing.explore_sub": "هر مسیر مهارت‌ها را در سه سطح مبتدی، متوسط و پیشرفته ساختاردهی می‌کند.",
        "landing.view_all_paths": "مشاهده همه مسیرها",
        "landing.inspect_curriculum": "بررسی سرفصل‌ها",

        # Auth: Login / Register / Profile
        "auth.login_title": "ورود",
        "auth.login_heading": "ورود به SkillMap",
        "auth.login_sub": "به نقشه‌های راه یادگیری، منابع، پروژه‌ها و ارزیابی مهارت‌های خود دسترسی پیدا کنید.",
        "auth.email_label": "نشانی ایمیل",
        "auth.email_placeholder": "you@example.com",
        "auth.password_label": "رمز عبور",
        "auth.password_placeholder": "رمز عبور خود را وارد کنید",
        "auth.show_password": "نمایش رمز عبور",
        "auth.hide_password": "مخفی کردن رمز عبور",
        "auth.sign_in_btn": "ورود به حساب",
        "auth.demo_btn": "ورود با حساب نمونه (Alex Chen)",
        "auth.demo_hint": "شامل نقشه راه آماده، پروژه‌ها، یادداشت‌های مطالعه و گزارش ۷ روز اخیر است.",
        "auth.new_here": "حساب کاربری ندارید؟",
        "auth.create_one": "ساخت حساب جدید",

        "auth.register_title": "ایجاد حساب",
        "auth.register_heading": "ساخت حساب کاربری SkillMap",
        "auth.register_sub": "مسیر شغلی هدف و ساعت مطالعه هفتگی خود را مشخص کنید تا نقشه راه شما ساخته شود.",
        "auth.full_name_label": "نام و نام خانوادگی",
        "auth.full_name_placeholder": "مثلاً سارا محمدی",
        "auth.reg_email_placeholder": "sara@example.com",
        "auth.reg_password_placeholder": "حداقل ۸ کاراکتر",
        "auth.confirm_password_label": "تکرار رمز عبور",
        "auth.confirm_password_placeholder": "رمز عبور را دوباره وارد کنید",
        "auth.target_career_label": "مسیر شغلی هدف",
        "auth.choose_later": "بعداً انتخاب می‌کنم",
        "auth.weekly_goal_label": "هدف هفتگی (ساعت)",
        "auth.already_registered": "قبلاً ثبت‌نام کرده‌اید؟",
        "auth.sign_in_link": "وارد شوید",

        "profile.title": "پروفایل و اهداف",
        "profile.heading": "تنظیمات پروفایل و یادگیری",
        "profile.sub": "مشخصات فردی، مسیر شغلی اصلی، هدف مطالعه هفتگی و رمز عبور خود را مدیریت کنید.",
        "profile.back_dashboard": "بازگشت به داشبورد",
        "profile.stat_active_paths": "مسیرهای فعال",
        "profile.stat_completed_tasks": "تسک‌های تکمیل‌شده",
        "profile.stat_portfolio_projects": "پروژه‌های نمونه‌کار",
        "profile.stat_total_hours": "مجموع ساعات ثبت‌شده",
        "profile.learner_card": "پروفایل یادگیرنده",
        "profile.email_hint": "ایمیل به‌عنوان شناسه یکتای ورود شما استفاده می‌شود.",
        "profile.primary_career": "مسیر شغلی اصلی",
        "profile.none_selected": "انتخاب نشده",
        "profile.weekly_goal_hours": "هدف مطالعه هفتگی (ساعت)",
        "profile.bio_label": "معرفی و تمرکز یادگیری",
        "profile.bio_placeholder": "اهداف شغلی و تمرکز فعلی یادگیری خود را بنویسید...",
        "profile.save_btn": "ذخیره پروفایل",
        "profile.security_card": "امنیت و رمز عبور",
        "profile.current_password": "رمز عبور فعلی",
        "profile.new_password": "رمز عبور جدید",
        "profile.confirm_new_password": "تکرار رمز عبور جدید",
        "profile.update_pw_btn": "تغییر رمز عبور",

        # Auth Flashes & Errors
        "flash.auth_required": "لطفاً برای دسترسی به فضای کاری SkillMap وارد حساب خود شوید.",
        "flash.csrf_invalid": "توکن امنیتی CSRF نامعتبر یا مفقود است. لطفاً صفحه را تازه کرده و دوباره تلاش کنید.",
        "flash.name_length": "نام کامل باید بین ۲ تا ۸۰ کاراکتر باشد.",
        "flash.email_invalid": "لطفاً یک نشانی ایمیل معتبر وارد کنید.",
        "flash.password_length": "رمز عبور باید حداقل ۸ کاراکتر باشد.",
        "flash.password_mismatch": "رمزهای عبور با یکدیگر مطابقت ندارند.",
        "flash.weekly_goal_range": "هدف مطالعه هفتگی باید بین ۱ تا ۱۰۰ ساعت باشد.",
        "flash.weekly_goal_number": "هدف مطالعه هفتگی باید یک عدد معتبر باشد.",
        "flash.career_not_exist": "مسیر شغلی انتخاب‌شده وجود ندارد.",
        "flash.career_selection_invalid": "انتخاب مسیر شغلی نامعتبر است.",
        "flash.email_exists": "حسابی با این ایمیل از قبل ثبت شده است.",
        "flash.welcome_new": "{name} عزیز، به SkillMap خوش آمدید! فضای یادگیری شما آماده است.",
        "flash.login_required_fields": "وارد کردن ایمیل و رمز عبور الزامی است.",
        "flash.login_invalid": "ایمیل یا رمز عبور نادرست است.",
        "flash.login_success": "با نام {name} وارد شدید.",
        "flash.demo_unavailable": "حساب نمونه در دسترس نیست. لطفاً یک حساب جدید بسازید.",
        "flash.demo_success": "وارد فضای کاری حساب نمونه (Alex Chen) شدید.",
        "flash.logout_success": "با موفقیت از حساب کاربری خارج شدید.",
        "flash.bio_length": "متن معرفی نمی‌تواند بیش از ۵۰۰ کاراکتر باشد.",
        "flash.profile_career_invalid": "مسیر شغلی انتخاب‌شده نامعتبر است.",
        "flash.profile_saved": "تنظیمات پروفایل ذخیره شد.",
        "flash.current_pw_wrong": "رمز عبور فعلی نادرست است.",
        "flash.new_pw_length": "رمز عبور جدید باید حداقل ۸ کاراکتر باشد.",
        "flash.new_pw_mismatch": "رمزهای عبور جدید مطابقت ندارند.",
        "flash.pw_updated": "رمز عبور با موفقیت به‌روزرسانی شد.",

        # Dashboard
        "dash.title": "داشبورد یادگیری",
        "dash.open_roadmap": "مشاهده نقشه راه",
        "dash.welcome": "خوش آمدید، {name}",
        "dash.primary_track": "مسیر اصلی:",
        "dash.weekly_goal_meta": "هدف هفتگی: {hours} ساعت",
        "dash.no_primary_track": "یک مسیر شغلی هدف انتخاب کنید تا نقشه راه و تسلط مهارتی شما ساختاردهی شود.",
        "dash.kpi_aria": "شاخص‌های کلیدی یادگیری",
        "dash.kpi_overall": "پیشرفت کلی",
        "dash.kpi_completed_tasks": "تسک‌های تکمیل‌شده",
        "dash.kpi_enrolled_sub": "در تمام نقشه‌های راه فعال",
        "dash.kpi_active_paths": "مسیرهای یادگیری فعال",
        "dash.kpi_projects_sub": "{count} پروژه نمونه‌کار ثبت‌شده",
        "dash.kpi_weekly_activity": "فعالیت هفتگی",
        "dash.kpi_weekly_goal_sub": "{pct}% از هدف {goal} ساعته هفتگی",
        "dash.chart_weekly_title": "فعالیت یادگیری هفتگی",
        "dash.chart_weekly_aria": "نمودار میله‌ای فعالیت یادگیری هفتگی",
        "dash.last_7_days": "۷ روز گذشته",
        "dash.hrs_logged_meta": "{hours} ساعت ثبت‌شده",
        "dash.chart_skills_title": "پیشرفت مهارت‌ها",
        "dash.chart_skills_sub": "درصد تسلط به تفکیک مهارت‌های پیگیری‌شده",
        "dash.chart_skills_aria": "نمودار افقی درصد تسلط مهارت‌ها",
        "dash.assess_skills": "ارزیابی مهارت‌ها",
        "dash.no_skills_title": "هنوز مهارتی ثبت نشده است",
        "dash.no_skills_desc": "در یک مسیر شغلی ثبت‌نام کنید تا نمودار پیشرفت مهارت‌های شما نمایش داده شود.",
        "dash.active_paths_heading": "مسیرهای یادگیری فعال",
        "dash.add_path": "افزودن مسیر",
        "dash.tasks_of": "{done} از {total} تسک",
        "dash.target_date": "تاریخ هدف: {date}",
        "dash.goal_prefix": "هدف: {goal}",
        "dash.no_paths_title": "مسیر یادگیری فعالی وجود ندارد",
        "dash.no_paths_desc": "یکی از شش مسیر تخصصی فناوری را انتخاب کنید تا مراحل نقشه راه ساخته شود.",
        "dash.learning_stats": "آمار یادگیری",
        "dash.stat_total_hours": "مجموع ساعات مطالعه ثبت‌شده",
        "dash.stat_resources_completed": "منابع تکمیل‌شده",
        "dash.stat_projects_completed": "پروژه‌های تکمیل‌شده",
        "dash.stat_avg_project": "میانگین پیشرفت پروژه‌ها",
        "dash.stat_avg_assessment": "میانگین نمره ارزیابی‌ها",
        "dash.stat_study_notes": "یادداشت‌های مطالعه شخصی",
        "dash.next_milestones": "مراحل بعدی و نقاط تمرکز",
        "dash.view_all_tasks": "مشاهده همه تسک‌ها",
        "dash.weak_skills_banner": "مهارت‌های نیازمند تمرین بیشتر (زیر ۷۰٪)",
        "dash.complete_btn": "تکمیل",
        "dash.no_tasks_title": "تسک در انتظاری وجود ندارد",
        "dash.no_tasks_desc": "مراحل جدیدی به نقشه راه اضافه کنید یا مسیر شغلی دیگری را بررسی کنید.",
        "dash.recent_activities": "فعالیت‌های اخیر",
        "dash.no_activity_title": "هنوز فعالیتی ثبت نشده است",
        "dash.no_activity_desc": "با تکمیل تسک‌ها، ذخیره منابع یا شرکت در آزمون مهارت، تاریخچه شما در اینجا ثبت می‌شود.",
        "chart.study_hours": "ساعت مطالعه",
        "chart.hrs_logged_suffix": "ساعت ثبت‌شده",
        "chart.mastery_label": "درصد تسلط",
        "chart.mastery_suffix": "٪ تسلط",

        # Career Explorer
        "careers.title": "کاوشگر مسیرهای شغلی",
        "careers.heading": "کاوشگر مسیرهای شغلی فناوری",
        "careers.sub": "پیش‌نیازهای ساختاریافته در سطوح مبتدی، متوسط و پیشرفته، زمان تخمینی یادگیری، پروژه‌های پیشنهادی و منابع منتخب هر مسیر را بررسی کنید.",
        "careers.search_placeholder": "جست‌وجو در مسیرها یا حوزه‌ها...",
        "careers.search_aria": "جست‌وجوی مسیرهای شغلی",
        "careers.view_details": "مشاهده جزئیات",
        "careers.open_roadmap": "باز کردن نقشه راه",
        "careers.start_roadmap": "شروع نقشه راه",
        "careers.empty_title": "مسیر شغلی با عبارت «{query}» یافت نشد",
        "careers.empty_desc": "فیلتر جست‌وجو را پاک کنید تا هر شش مسیر تخصصی نمایش داده شوند.",
        "careers.show_all": "نمایش همه مسیرها",
        "careers.all_careers": "همه مسیرها",
        "careers.est_hours": "{hours} ساعت تخمینی",
        "careers.est_months": "{months} ماه زمان پیشنهادی",
        "careers.open_personalized": "باز کردن نقشه راه شخصی",
        "careers.enroll_generate": "ثبت‌نام و ساخت نقشه راه",
        "careers.signup_start": "ثبت‌نام برای شروع این مسیر",
        "careers.stage_title": "سطح {level}",
        "careers.rec_projects": "پروژه‌های نمونه‌کار پیشنهادی",
        "careers.curated_resources": "منابع یادگیری منتخب",
        "careers.enrolled_flash": "در مسیر «{title}» ثبت‌نام شدید و تسک‌های اولیه نقشه راه ایجاد شدند.",
        "careers.switched_flash": "نقشه راه فعال به «{title}» تغییر یافت.",

        # Roadmap
        "roadmap.title": "نقشه راه من",
        "roadmap.heading": "نقشه راه یادگیری شخصی",
        "roadmap.sub": "مراحل شغلی را مدیریت کنید، تسک‌های یادگیری را تکمیل کنید، تسلط هر مهارت را تنظیم کنید و اهداف خود را پیگیری نمایید.",
        "roadmap.browse_all": "مشاهده همه مسیرها",
        "roadmap.select_aria": "انتخاب مسیر شغلی",
        "roadmap.enrolled_suffix": "(ثبت‌نام‌شده)",
        "roadmap.load_path": "بارگذاری مسیر",
        "roadmap.progress_title": "پیشرفت {title}",
        "roadmap.tasks_ratio": "{done} / {total} تسک",
        "roadmap.hours_ratio": "{done} / {total} ساعت",
        "roadmap.goal_card": "هدف یادگیری شخصی",
        "roadmap.target_milestone": "هدف اصلی",
        "roadmap.goal_placeholder": "مثلاً ساخت ۲ سرویس REST API و قبولی در آزمون امنیت",
        "roadmap.target_date_label": "تاریخ هدف تکمیل",
        "roadmap.save_goal": "ذخیره هدف",
        "roadmap.tasks_heading": "تسک‌های یادگیری",
        "roadmap.filters_aria": "فیلترهای تسک",
        "roadmap.filter_pending": "در انتظار",
        "roadmap.filter_completed": "تکمیل‌شده",
        "roadmap.all_levels": "همه سطوح",
        "roadmap.toggle_aria": "تغییر وضعیت تکمیل برای {title}",
        "roadmap.due_prefix": "سررسید {date}",
        "roadmap.confirm_remove": "آیا تسک «{title}» از نقشه راه حذف شود؟",
        "roadmap.no_tasks_title": "تسکی مطابق فیلتر فعلی یافت نشد",
        "roadmap.no_tasks_desc": "از فرم کناری یک تسک جدید اضافه کنید یا فیلتر سطح و وضعیت را بازنشانی کنید.",
        "roadmap.add_task_card": "افزودن تسک دلخواه",
        "roadmap.task_title": "عنوان تسک",
        "roadmap.task_placeholder": "مثلاً پیاده‌سازی بنچمارک ایندکس در SQLite",
        "roadmap.related_skill": "مهارت مرتبط",
        "roadmap.general_milestone": "مرحله عمومی مسیر",
        "roadmap.level": "سطح",
        "roadmap.est_hours": "ساعت تخمینی",
        "roadmap.due_date": "تاریخ سررسید",
        "roadmap.notes_opt": "توضیحات (اختیاری)",
        "roadmap.notes_placeholder": "خروجی‌ها یا منابع مورد نیاز برای این مرحله...",
        "roadmap.add_btn": "افزودن به نقشه راه",
        "roadmap.skill_tracker": "پایشگر تسلط مهارت‌ها",
        "roadmap.hours_logged_short": "{hours} ساعت ثبت‌شده",
        "roadmap.mastery_aria": "درصد تسلط برای {name}",
        "roadmap.hours_aria": "ساعت ثبت‌شده برای {name}",
        "roadmap.edit_modal_title": "ویرایش تسک یادگیری",
        "roadmap.empty_title": "برای شروع یک مسیر شغلی انتخاب کنید",
        "roadmap.empty_desc": "از منوی انتخاب بالا یا بخش کاوشگر مسیرهای شغلی برای ثبت‌نام در امنیت سایبری، مهندسی شبکه، توسعه بک‌اند، توسعه فرانت‌اند، توسعه اندروید یا تحلیل داده استفاده کنید.",
        "roadmap.open_explorer": "باز کردن کاوشگر مسیرها",
        "roadmap.flash_choose_valid": "لطفاً یک مسیر شغلی معتبر انتخاب کنید.",
        "roadmap.flash_not_found": "مسیر شغلی انتخاب‌شده یافت نشد.",
        "roadmap.flash_loaded": "نقشه راه «{title}» بارگذاری شد.",
        "roadmap.flash_invalid_career": "مسیر شغلی نامعتبر است.",
        "roadmap.flash_goal_length": "متن هدف شخصی باید بین ۳ تا ۲۵۰ کاراکتر باشد.",
        "roadmap.flash_goal_updated": "هدف یادگیری شخصی به‌روزرسانی شد.",
        "roadmap.flash_select_valid": "لطفاً یک مسیر شغلی معتبر انتخاب کنید.",
        "roadmap.flash_title_length": "عنوان تسک باید بین ۲ تا ۱۴۰ کاراکتر باشد.",
        "roadmap.flash_task_added": "تسک جدید به نقشه راه اضافه شد.",
        "roadmap.flash_task_completed": "تسک «{title}» به‌عنوان تکمیل‌شده علامت خورد.",
        "roadmap.flash_task_reopened": "تسک «{title}» دوباره باز شد.",
        "roadmap.flash_task_updated": "تسک «{title}» به‌روزرسانی شد.",
        "roadmap.flash_task_removed": "تسک «{title}» حذف شد.",
        "roadmap.flash_skill_updated": "تسلط در «{name}» به {pct}٪ به‌روزرسانی شد.",

        # Resources
        "resources.title": "کتابخانه منابع",
        "resources.heading": "کتابخانه منابع یادگیری",
        "resources.sub": "مستندات، دوره‌ها، کتاب‌ها، ویدئوها و آزمایشگاه‌های عملی را ذخیره، دسته‌بندی، فیلتر و پیگیری کنید.",
        "resources.discover_curated": "کشف منابع منتخب",
        "resources.completed_counter": "{done} / {total} تکمیل‌شده",
        "resources.search_placeholder": "جست‌وجو در منابع ذخیره‌شده...",
        "resources.search_aria": "جست‌وجوی منابع ذخیره‌شده",
        "resources.all_categories": "همه دسته‌ها",
        "resources.all_levels": "همه سطوح",
        "resources.all_status": "همه وضعیت‌ها",
        "resources.unread": "مطالعه‌نشده",
        "resources.completed": "تکمیل‌شده",
        "resources.filter_cat_aria": "فیلتر بر اساس دسته‌بندی",
        "resources.filter_diff_aria": "فیلتر بر اساس سطح دشواری",
        "resources.filter_status_aria": "فیلتر بر اساس وضعیت مطالعه",
        "resources.col_resource": "منبع",
        "resources.col_cat_level": "دسته و سطح",
        "resources.col_status": "وضعیت",
        "resources.col_actions": "عملیات",
        "resources.reopen": "بازگشایی",
        "resources.mark_complete": "ثبت تکمیل",
        "resources.confirm_delete": "آیا «{title}» از کتابخانه شما حذف شود؟",
        "resources.empty_title": "منبع ذخیره‌شده‌ای یافت نشد",
        "resources.empty_desc": "با استفاده از فرم کناری لینک جدیدی اضافه کنید یا یکی از منابع منتخب زیر را ذخیره کنید.",
        "resources.add_card": "ذخیره منبع جدید",
        "resources.field_title": "عنوان",
        "resources.title_placeholder": "مثلاً راهنمای عمیق Indexing در PostgreSQL",
        "resources.field_url": "نشانی اینترنتی (URL)",
        "resources.url_placeholder": "https://...",
        "resources.field_category": "دسته‌بندی",
        "resources.field_difficulty": "سطح دشواری",
        "resources.field_career_opt": "مسیر شغلی (اختیاری)",
        "resources.field_desc": "توضیحات",
        "resources.desc_placeholder": "نکات کلیدی یا فصل‌های مهم برای تمرکز...",
        "resources.add_btn": "افزودن به کتابخانه",
        "resources.curated_heading": "پیشنهادهای منتخب کاتالوگ",
        "resources.explore_paths": "مشاهده همه مسیرها",
        "resources.save_to_library": "ذخیره در کتابخانه من",
        "resources.all_saved_note": "تمام منابع منتخب کاتالوگ از قبل در کتابخانه شخصی شما ذخیره شده‌اند.",
        "resources.edit_modal_title": "ویرایش منبع ذخیره‌شده",
        "resources.flash_title_len": "عنوان منبع باید بین ۲ تا ۱۴۰ کاراکتر باشد.",
        "resources.flash_url_invalid": "لطفاً یک نشانی معتبر با http:// یا https:// وارد کنید.",
        "resources.flash_cat_invalid": "دسته‌بندی انتخاب‌شده نامعتبر است.",
        "resources.flash_diff_invalid": "سطح دشواری انتخاب‌شده نامعتبر است.",
        "resources.flash_career_invalid": "مسیر شغلی انتخاب‌شده نامعتبر است.",
        "resources.flash_saved": "منبع در کتابخانه شما ذخیره شد.",
        "resources.flash_already_saved": "این منبع از قبل در کتابخانه شخصی شما وجود دارد.",
        "resources.flash_added_curated": "منبع «{title}» به کتابخانه شما اضافه شد.",
        "resources.flash_completed": "منبع «{title}» به‌عنوان تکمیل‌شده ثبت شد.",
        "resources.flash_unread": "وضعیت «{title}» به مطالعه‌نشده تغییر یافت.",
        "resources.flash_updated": "منبع «{title}» به‌روزرسانی شد.",
        "resources.flash_removed": "منبع «{title}» از کتابخانه حذف شد.",

        # Projects
        "projects.title": "پیگیری پروژه‌ها",
        "projects.heading": "پیگیری پروژه‌های نمونه‌کار",
        "projects.sub": "پروژه‌های فنی نمونه‌کار متصل به مخازن GitHub را برنامه‌ریزی، پیاده‌سازی و پیگیری کنید.",
        "projects.view_roadmap": "مشاهده نقشه راه",
        "projects.kpi_total": "کل پروژه‌ها",
        "projects.kpi_in_progress": "در حال انجام",
        "projects.kpi_completed": "تکمیل‌شده",
        "projects.kpi_avg": "میانگین پیشرفت",
        "projects.filter_aria": "فیلتر وضعیت پروژه",
        "projects.search_placeholder": "فیلتر با فناوری یا نام...",
        "projects.search_aria": "جست‌وجو در پروژه‌ها",
        "projects.github_repo": "مخزن GitHub",
        "projects.no_repo": "نشانی مخزن ثبت نشده است",
        "projects.confirm_delete": "آیا پروژه «{name}» حذف شود؟",
        "projects.empty_title": "هنوز پروژه‌ای ثبت نشده است",
        "projects.empty_desc": "اولین پروژه شخصی خود را بسازید تا پشته فناوری، درصد پیشرفت و لینک مخزن آن را مستند کنید.",
        "projects.new_card": "پروژه شخصی جدید",
        "projects.field_name": "نام پروژه",
        "projects.name_placeholder": "مثلاً ابزار تحلیل بسته شبکه با CLI",
        "projects.field_stack": "پشته فناوری",
        "projects.stack_placeholder": "Python, Flask, SQLite, Chart.js",
        "projects.field_status": "وضعیت",
        "projects.field_pct": "درصد تکمیل (%)",
        "projects.field_career": "مسیر شغلی",
        "projects.general_portfolio": "نمونه‌کار عمومی",
        "projects.field_github": "نشانی مخزن GitHub",
        "projects.github_placeholder": "https://github.com/username/repo",
        "projects.field_desc": "توضیحات",
        "projects.desc_placeholder": "نکات معماری، اهداف و قابلیت‌های کلیدی...",
        "projects.create_btn": "ایجاد پروژه",
        "projects.edit_modal_title": "ویرایش پروژه",
        "projects.flash_name_len": "نام پروژه باید بین ۲ تا ۱۲۰ کاراکتر باشد.",
        "projects.flash_stack_req": "لطفاً پشته فناوری پروژه را مشخص کنید (مثلاً Python, Flask, SQLite).",
        "projects.flash_status_invalid": "وضعیت پروژه نامعتبر است.",
        "projects.flash_github_invalid": "نشانی GitHub باید با http:// یا https:// شروع شود.",
        "projects.flash_pct_invalid": "درصد تکمیل باید عددی صحیح بین ۰ تا ۱۰۰ باشد.",
        "projects.flash_career_invalid": "مسیر شغلی انتخاب‌شده نامعتبر است.",
        "projects.flash_created": "پروژه «{name}» ایجاد شد.",
        "projects.flash_update_verify": "لطفاً نام پروژه، پشته فناوری، وضعیت و نشانی GitHub را بررسی کنید.",
        "projects.flash_updated": "پروژه «{name}» به‌روزرسانی شد.",
        "projects.flash_deleted": "پروژه «{name}» حذف شد.",

        # Study Notes
        "notes.title": "یادداشت‌های مطالعه",
        "notes.heading": "یادداشت‌های مطالعه شخصی",
        "notes.sub": "خلاصه‌های فنی، تصمیمات معماری و نکات کلیدی را بر اساس مسیر شغلی و مهارت دسته‌بندی و نگهداری کنید.",
        "notes.search_placeholder": "جست‌وجو در یادداشت‌ها...",
        "notes.search_aria": "جست‌وجوی یادداشت‌های مطالعه",
        "notes.all_careers": "همه مسیرهای شغلی",
        "notes.filter_career_aria": "فیلتر یادداشت‌ها بر اساس مسیر شغلی",
        "notes.confirm_delete": "آیا یادداشت «{title}» حذف شود؟",
        "notes.empty_title": "هنوز یادداشتی ثبت نشده است",
        "notes.empty_desc": "اولین یادداشت خود را از فرم کناری بنویسید تا نکات مهم هر مسیر شغلی را ثبت کنید.",
        "notes.create_card": "ایجاد یادداشت مطالعه",
        "notes.field_career": "مسیر شغلی",
        "notes.field_skill_opt": "مهارت (اختیاری)",
        "notes.general_note": "یادداشت عمومی مسیر",
        "notes.field_title": "عنوان یادداشت",
        "notes.title_placeholder": "مثلاً خلاصه وضعیت‌های همسایگی OSPF",
        "notes.field_content": "متن یادداشت",
        "notes.content_placeholder": "فرمول‌ها، دستورات یا نکات کلیدی معماری را بنویسید...",
        "notes.save_btn": "ذخیره یادداشت",
        "notes.edit_modal_title": "ویرایش یادداشت مطالعه",
        "notes.update_btn": "به‌روزرسانی یادداشت",
        "notes.flash_invalid_career": "لطفاً یک مسیر شغلی معتبر برای یادداشت انتخاب کنید.",
        "notes.flash_title_len": "عنوان یادداشت باید بین ۲ تا ۱۴۰ کاراکتر باشد.",
        "notes.flash_content_empty": "متن یادداشت نمی‌تواند خالی باشد.",
        "notes.flash_saved": "یادداشت مطالعه ذخیره شد.",
        "notes.flash_edit_req": "عنوان و متن یادداشت الزامی است.",
        "notes.flash_updated": "یادداشت مطالعه به‌روزرسانی شد.",
        "notes.flash_deleted": "یادداشت «{title}» حذف شد.",

        # Skill Assessments & Quizzes
        "assess.title": "ارزیابی مهارت‌ها",
        "assess.heading": "ارزیابی و عیب‌یابی مهارت‌ها",
        "assess.sub": "در آزمون‌های تعاملی تسلط شرکت کنید یا ارزیابی‌های عملی را ثبت کنید تا مهارت‌های نیازمند تمرین بیشتر مشخص شوند.",
        "assess.kpi_completed": "ارزیابی‌های انجام‌شده",
        "assess.kpi_avg": "میانگین نمره",
        "assess.kpi_flagged": "مهارت‌های نیازمند تمرین (زیر ۷۰٪)",
        "assess.quizzes_heading": "آزمون‌های تعاملی سنجش مهارت",
        "assess.quizzes_sub": "هر آزمون به‌صورت خودکار پاسخ‌های شما را تصحیح می‌کند، درصد تسلط مهارت را به‌روزرسانی می‌کند و مباحث زیر ۷۰٪ را علامت‌گذاری می‌کند.",
        "assess.start_quiz": "شروع آزمون",
        "assess.weak_heading": "مهارت‌های نیازمند تمرین بیشتر",
        "assess.retake": "آزمون مجدد",
        "assess.history_heading": "تاریخچه نتایج ارزیابی",
        "assess.col_assessment": "عنوان ارزیابی",
        "assess.col_type": "نوع",
        "assess.col_score": "نمره",
        "assess.col_eval": "وضعیت",
        "assess.col_action": "عملیات",
        "assess.needs_practice": "نیازمند تمرین",
        "assess.proficient": "مسلط",
        "assess.confirm_delete": "آیا رکورد ارزیابی «{title}» حذف شود؟",
        "assess.empty_title": "هنوز ارزیابی‌ای ثبت نشده است",
        "assess.empty_desc": "یکی از آزمون‌های بالا را آغاز کنید یا از فرم کناری یک ارزیابی عملی ثبت نمایید.",
        "assess.log_card": "ثبت ارزیابی مهارت",
        "assess.target_skill": "مهارت هدف",
        "assess.general_eval": "ارزیابی عمومی مسیر",
        "assess.eval_title": "عنوان ارزیابی",
        "assess.eval_placeholder": "مثلاً تمرین عملی توابع Window در SQL",
        "assess.field_type": "نوع ارزیابی",
        "assess.field_score": "نمره (۰ تا ۱۰۰)",
        "assess.field_reflection": "بازخورد / نقاط نیازمند تقویت",
        "assess.reflection_placeholder": "یادداشت‌هایی درباره بخش‌هایی که نیاز به تمرین بیشتر دارند...",
        "assess.record_btn": "ثبت ارزیابی",
        "assess.flash_no_questions": "هنوز سؤالی برای آزمون این مسیر ثبت نشده است.",
        "assess.flash_invalid_career": "لطفاً یک مسیر شغلی معتبر انتخاب کنید.",
        "assess.flash_title_len": "عنوان ارزیابی باید بین ۲ تا ۱۴۰ کاراکتر باشد.",
        "assess.flash_score_int": "نمره باید یک عدد صحیح بین ۰ تا ۱۰۰ باشد.",
        "assess.flash_recorded": "ارزیابی مهارت ثبت شد.",
        "assess.flash_removed": "ارزیابی «{title}» حذف شد.",

        # Quiz Runner
        "quiz.title": "آزمون سنجش مهارت {title}",
        "quiz.all_assessments": "همه ارزیابی‌ها",
        "quiz.subtitle": "به هر {count} سؤال پاسخ دهید تا آمادگی مهارتی شما سنجیده شود و نقاط تمرکز بعدی مشخص شوند.",
        "quiz.graded_saved": "آزمون تصحیح و ذخیره شد",
        "quiz.correct_of": "{correct} پاسخ درست از {total}",
        "quiz.score_label": "نمره:",
        "quiz.retake_btn": "شرکت مجدد",
        "quiz.back_btn": "بازگشت به ارزیابی‌ها",
        "quiz.question_n": "سؤال {n}",
        "quiz.question_of": "سؤال {n} از {total}",
        "quiz.correct": "درست",
        "quiz.incorrect": "نادرست (پاسخ شما {chosen}، پاسخ صحیح {expected})",
        "quiz.none": "بدون پاسخ",
        "quiz.explanation": "توضیح:",
        "quiz.submit_btn": "ثبت و تصحیح آزمون",

        # Error Pages & API
        "err.not_found_short": "یافت نشد",
        "err.400_title": "درخواست نامعتبر",
        "err.400_msg": "امکان پردازش این درخواست وجود نداشت.",
        "err.404_title": "صفحه یافت نشد",
        "err.404_msg": "صفحه یا رکورد درخواستی در SkillMap وجود ندارد.",
        "err.404_fallback": "صفحه درخواستی در SkillMap یافت نشد.",
        "err.500_title": "خطای سرور",
        "err.500_heading": "خطای غیرمنتظره سرور",
        "err.500_msg": "هنگام پردازش درخواست خطایی رخ داد. لطفاً به داشبورد بازگردید و دوباره تلاش کنید.",
        "err.500_public": "هنگام پردازش درخواست خطایی رخ داد.",
        "err.return_dashboard": "بازگشت به داشبورد",
        "err.return_home": "بازگشت به صفحه اصلی",
        "api.auth_required": "احراز هویت الزامی است.",
        "api.not_found": "مورد درخواستی یافت نشد.",
        "api.bad_request": "درخواست نامعتبر است.",
        "api.server_error": "خطای داخلی سرور رخ داد.",
        "api.task_not_found": "تسک یافت نشد.",
        "api.resource_not_found": "منبع یافت نشد.",
        "api.project_not_found": "پروژه یافت نشد.",
        "api.invalid_pct": "درصد تکمیل نامعتبر است.",
    },
}

ENUM_TRANSLATIONS: dict[str, dict[str, dict[str, str]]] = {
    "level": {
        "en": {"Beginner": "Beginner", "Intermediate": "Intermediate", "Advanced": "Advanced"},
        "fa": {"Beginner": "مبتدی", "Intermediate": "متوسط", "Advanced": "پیشرفته"},
    },
    "category": {
        "en": {
            "Documentation": "Documentation",
            "Course": "Course",
            "Book": "Book",
            "Video": "Video",
            "Article": "Article",
            "Tool": "Tool",
            "Practice Lab": "Practice Lab",
        },
        "fa": {
            "Documentation": "مستندات",
            "Course": "دوره آموزشی",
            "Book": "کتاب",
            "Video": "ویدئو",
            "Article": "مقاله",
            "Tool": "ابزار",
            "Practice Lab": "آزمایشگاه عملی",
        },
    },
    "status": {
        "en": {
            "Planned": "Planned",
            "In Progress": "In Progress",
            "Completed": "Completed",
            "On Hold": "On Hold",
        },
        "fa": {
            "Planned": "برنامه‌ریزی‌شده",
            "In Progress": "در حال انجام",
            "Completed": "تکمیل‌شده",
            "On Hold": "متوقف‌شده",
        },
    },
    "assessment_type": {
        "en": {"Quiz": "Quiz", "Self-Evaluation": "Self-Evaluation", "Practical": "Practical"},
        "fa": {"Quiz": "آزمون", "Self-Evaluation": "خودارزیابی", "Practical": "عملی"},
    },
}

WEEKDAYS_FA = {
    0: "دوشنبه",
    1: "سه‌شنبه",
    2: "چهارشنبه",
    3: "پنج‌شنبه",
    4: "جمعه",
    5: "شنبه",
    6: "یکشنبه",
}

MONTHS_FA = {
    1: "ژانویه",
    2: "فوریه",
    3: "مارس",
    4: "آوریل",
    5: "مه",
    6: "ژوئن",
    7: "ژوئیه",
    8: "اوت",
    9: "سپتامبر",
    10: "اکتبر",
    11: "نوامبر",
    12: "دسامبر",
}

# ============================================================
# Dynamic Catalog & Domain Translations (Persian)
# Preserves programming languages, tools & technical keywords
# ============================================================

CAREER_FA: dict[str, dict[str, str]] = {
    "cybersecurity": {
        "title": "امنیت سایبری (Cybersecurity)",
        "tagline": "از زیرساخت‌ها دفاع کنید، آسیب‌پذیری‌ها را ممیزی کنید و به رخدادهای امنیتی پاسخ دهید.",
        "description": "مهندسان امنیت سایبری از سیستم‌ها، شبکه‌ها و برنامه‌ها در برابر دسترسی غیرمجاز و نشت داده محافظت می‌کنند. این مسیر از مبانی Linux و شبکه آغاز شده و به تهدیدمدل‌سازی، امنیت برنامه‌های وب، پایش SIEM و پاسخ به رخدادها می‌رسد.",
        "difficulty_summary": "مبتدی تا پیشرفته",
    },
    "network-engineering": {
        "title": "مهندسی شبکه (Network Engineering)",
        "tagline": "توپولوژی‌های مسیریابی پایدار طراحی کنید، سوئیچ‌ها را خودکارسازی کنید و جریان بسته‌ها را عیب‌یابی نمایید.",
        "description": "مهندسان شبکه زیرساخت ارتباطی فیزیکی و ابری برنامه‌های مدرن را معماری می‌کنند. در این مسیر بر سابنتینگ IPv4/IPv6، سوئیچینگ و VLAN، پروتکل‌های مسیریابی پویا مانند OSPF و BGP، طراحی VPC ابری و اتوماسیون شبکه با Python مسلط می‌شوید.",
        "difficulty_summary": "مبتدی تا پیشرفته",
    },
    "backend-development": {
        "title": "توسعه بک‌اند (Backend Development)",
        "tagline": "ساخت APIها، مدل‌های داده رابطه‌ای، سیستم‌های احراز هویت و سرویس‌های مقیاس‌پذیر.",
        "description": "مهندسان بک‌اند منطق سمت سرور، پایگاه‌های داده و APIهای پشتیبان برنامه‌های وب و موبایل را می‌سازند. سرویس‌های Python/Flask یا Node، طراحی اسکیمای نرمال‌سازی‌شده SQL، طراحی REST API، کشینگ، تست خودکار و استقرار کانتینری را بیاموزید.",
        "difficulty_summary": "مبتدی تا پیشرفته",
    },
    "frontend-development": {
        "title": "توسعه فرانت‌اند (Frontend Development)",
        "tagline": "رابط‌های کاربری دسترس‌پذیر، واکنش‌گرا و پرسرعت را با استانداردهای مدرن وب بسازید.",
        "description": "مهندسان فرانت‌اند نیازمندی‌های محصول را به تجربه‌های کاربری سریع، دسترس‌پذیر و واکنش‌گرا در مرورگر تبدیل می‌کنند. تسلط بر HTML5 معنایی، سیستم‌های چیدمان مدرن CSS، جاوااسکریپت و TypeScript ماژولار، دسترس‌پذیری (WCAG)، مدیریت وضعیت و کارایی مرورگر را به دست آورید.",
        "difficulty_summary": "مبتدی تا پیشرفته",
    },
    "android-development": {
        "title": "توسعه اندروید (Android Development)",
        "tagline": "اپلیکیشن‌های بومی و روان Android را با Kotlin، Jetpack Compose و ذخیره‌سازی آفلاین بسازید.",
        "description": "مهندسان اندروید اپلیکیشن‌های موبایل پایدار را برای میلیاردها دستگاه می‌سازند. Kotlin مدرن، رابط کاربری اعلانی با Jetpack Compose، معماری MVVM، ذخیره‌سازی محلی Room SQLite، هم‌زمانی با Coroutines و انتشار در Play Store را یاد بگیرید.",
        "difficulty_summary": "مبتدی تا پیشرفته",
    },
    "data-analysis": {
        "title": "تحلیل داده (Data Analysis)",
        "tagline": "داده‌های خام را به بینش‌های آماری، داشبوردهای مدیریتی و تصمیمات شفاف تبدیل کنید.",
        "description": "تحلیلگران داده داده‌های عملیاتی پراکنده را به شاخص‌های قابل اتکا و روایت‌های کاربردی تبدیل می‌کنند. تحلیل با SQL، پردازش داده با Python و pandas، تحلیل اکتشافی داده، آزمون فرضیه، مدل‌سازی ابعادی و مصورسازی شفاف داده‌ها را بیاموزید.",
        "difficulty_summary": "مبتدی تا پیشرفته",
    },
}

SKILL_FA: dict[str, dict[str, str]] = {
    # Cybersecurity
    "Linux & Shell Security": {
        "name": "امنیت Linux و Shell",
        "description": "مجوزهای کاربری، مقاوم‌سازی systemd، پیکربندی SSH و ممیزی اسکریپت‌های Bash.",
    },
    "TCP/IP & Packet Analysis": {
        "name": "TCP/IP و تحلیل بسته‌های شبکه",
        "description": "لایه‌های OSI، سابنتینگ، بررسی ترافیک DNS/TLS و تحلیل بسته با Wireshark.",
    },
    "Web Application Security": {
        "name": "امنیت برنامه‌های وب (OWASP)",
        "description": "آسیب‌پذیری‌های OWASP Top 10، خطاهای احراز هویت و دفاع در برابر SQLi، XSS و CSRF.",
    },
    "Network Defense & Firewalls": {
        "name": "دفاع شبکه و فایروال‌ها",
        "description": "بخش‌بندی Zero-Trust، قوانین iptables/nftables، سیستم‌های IDS/IPS و تونل‌سازی VPN.",
    },
    "SIEM & Threat Hunting": {
        "name": "SIEM و شکار تهدید",
        "description": "تجمیع لاگ‌ها، قوانین همبستگی، نگاشت MITRE ATT&CK و تریاژ ناهنجاری‌ها.",
    },
    "Incident Response & Forensics": {
        "name": "پاسخ به رخداد و جرم‌یابی دیجیتال",
        "description": "راهنمای مهار رخداد، جمع‌آوری شواهد حافظه و دیسک و گزارش‌نویسی پس از حادثه.",
    },
    # Network Engineering
    "IPv4 & IPv6 Subnetting": {
        "name": "سابنتینگ IPv4 و IPv6",
        "description": "نشانه‌گذاری CIDR، تخصیص VLSM، برنامه‌ریزی آدرس‌دهی و اندازه دامنه پخش.",
    },
    "Switching & VLAN Design": {
        "name": "سوئیچینگ و طراحی VLAN",
        "description": "ترانکینگ 802.1Q، پروتکل Spanning Tree (STP) و امنیت پورت‌ها.",
    },
    "Dynamic Routing (OSPF)": {
        "name": "مسیریابی پویا (OSPF)",
        "description": "بسته‌های LSA، معماری چندناحیه‌ای OSPF، خلاصه‌سازی مسیرها و بازیابی خطا.",
    },
    "DNS, DHCP & Load Balancing": {
        "name": "DNS، DHCP و توزیع بار",
        "description": "رکوردهای معتبر DNS، رله DHCP، پراکسی معکوس L4/L7 و بررسی سلامت سرویس‌ها.",
    },
    "BGP & Edge Peering": {
        "name": "BGP و همتاسازی لبه شبکه",
        "description": "سیستم‌های خودمختار (AS)، ویژگی‌های مسیر، فیلترینگ مسیر و افزونگی چندمسیره.",
    },
    "Network Automation": {
        "name": "اتوماسیون شبکه",
        "description": "اسکریپت‌نویسی با Paramiko/Netmiko، پایش تله‌متری و اعتبارسنجی اعلانی توپولوژی.",
    },
    # Backend Development
    "HTTP, REST & Routing": {
        "name": "HTTP، REST و مسیریابی",
        "description": "چرخه درخواست و پاسخ، کدهای وضعیت HTTP، مذاکره محتوا و طراحی تمیز Endpointها.",
    },
    "Relational SQL & Modeling": {
        "name": "SQL رابطه‌ای و مدل‌سازی داده",
        "description": "نرمال‌سازی (1NF–3NF)، کلیدهای خارجی، JOINها، ایندکس‌گذاری و ایزوله‌سازی تراکنش‌ها.",
    },
    "Authentication & Security": {
        "name": "احراز هویت و امنیت سمت سرور",
        "description": "هش‌کردن رمز عبور (PBKDF2/Argon2)، مدیریت نشست، کنترل دسترسی RBAC و محافظت CSRF.",
    },
    "Automated Testing & CI": {
        "name": "تست خودکار و CI",
        "description": "مجموعه تست‌های واحد و یکپارچه، Fixtureها، شبیه‌سازی APIهای بیرونی و پوشش رگرسیون.",
    },
    "Caching & Async Queues": {
        "name": "کشینگ و صف‌های ناهمزمان",
        "description": "استراتژی‌های کش Redis، پردازشگرهای پس‌زمینه، Idempotency و محدودسازی نرخ درخواست.",
    },
    "Observability & Performance": {
        "name": "پایش‌پذیری و کارایی",
        "description": "پروفایلینگ کوئری‌ها، لاگ‌گیری ساختاریافته، حذف مشکل N+1 و بازیابی خطای امن.",
    },
    # Frontend Development
    "Semantic HTML5 & Accessibility": {
        "name": "HTML5 معنایی و دسترس‌پذیری",
        "description": "المان‌های Landmark، نقش‌های ARIA، مدیریت فوکوس صفحه‌کلید و معنای صفحه‌خوان‌ها.",
    },
    "Modern CSS Grid & Flexbox": {
        "name": "CSS Grid و Flexbox مدرن",
        "description": "شبکه‌بندی منعطف و واکنش‌گرا، متغیرهای CSS، Container Queries و سیستم طراحی.",
    },
    "DOM & Async JavaScript": {
        "name": "DOM و JavaScript ناهمزمان",
        "description": "Event Delegation، Fetch API، Promise/async-await و به‌روزرسانی تمیز وضعیت رابط.",
    },
    "Data Visualization & Canvas": {
        "name": "مصورسازی داده و Canvas",
        "description": "نمودارهای تعاملی Chart.js و SVG، راهنمای واکنش‌گرا و قالب‌بندی دقیق داده‌ها.",
    },
    "Component Architecture & TypeScript": {
        "name": "معماری کامپوننت و TypeScript",
        "description": "جریان یک‌طرفه وضعیت، تایپ‌گذاری سخت‌گیرانه، اجزای قابل استفاده مجدد و مرز خطا.",
    },
    "Core Web Vitals & Performance": {
        "name": "Core Web Vitals و کارایی وب",
        "description": "تقسیم باندل، حذف پرش چیدمان (CLS)، هدرهای کش و ممیزی Lighthouse.",
    },
    # Android Development
    "Kotlin Language Fundamentals": {
        "name": "مبانی زبان Kotlin",
        "description": "ایمنی Null، کلاس‌های داده، Sealed Interfaceها، توابع توسعه‌ای و کالکشن‌ها.",
    },
    "Jetpack Compose UI": {
        "name": "رابط کاربری Jetpack Compose",
        "description": "توابع Composable اعلانی، State Hoisting، تم‌سازی Material 3 و چیدمان تطبیقی.",
    },
    "Lifecycle & MVVM Architecture": {
        "name": "چرخه حیات و معماری MVVM",
        "description": "ViewModel، StateFlow، جریان داده یک‌طرفه و حفظ وضعیت در تغییرات پیکربندی.",
    },
    "Room SQLite & Networking": {
        "name": "Room SQLite و ارتباط شبکه",
        "description": "کش محلی رابطه‌ای با Room DAO، کلاینت‌های Retrofit/Ktor و نگاشت DTO.",
    },
    "Coroutines & WorkManager": {
        "name": "Coroutines و WorkManager",
        "description": "هم‌زمانی ساختاریافته، عملگرهای Flow، Dispatcherها و همگام‌سازی پایدار در پس‌زمینه.",
    },
    "Testing & Performance Profiling": {
        "name": "تست و پروفایلینگ کارایی",
        "description": "تست‌های رابط کاربری Compose، Macrobenchmark، کشف نشت حافظه و بهینه‌سازی APK.",
    },
    # Data Analysis
    "SQL Analytics & Window Functions": {
        "name": "تحلیل SQL و Window Functions",
        "description": "CTEها، تجمیع‌ها، عبارات CASE، توابع RANK/ROW_NUMBER و کوئری‌های هم‌گروهی.",
    },
    "Spreadsheet & KPI Modeling": {
        "name": "مدل‌سازی KPI و صفحه‌گسترده",
        "description": "جداول محوری (Pivot Tables)، منطق جست‌وجو، اعتبارسنجی داده و تعریف شاخص‌ها.",
    },
    "Python & Pandas Data Cleaning": {
        "name": "پاک‌سازی داده با Python و Pandas",
        "description": "مدیریت مقادیر گمشده، بازآرایی مرتب داده‌ها، ادغام‌ها، ایندکس زمان و پایپ‌لاین‌ها.",
    },
    "Exploratory Visualization": {
        "name": "مصورسازی اکتشافی داده",
        "description": "انتخاب نمودار مناسب، تشخیص داده‌های پرت و مقیاس‌گذاری صادقانه محورها.",
    },
    "Statistical Inference & A/B Testing": {
        "name": "استنباط آماری و A/B Testing",
        "description": "فاصله اطمینان، مقدار p-value، محاسبه حجم نمونه و عیب‌یابی رگرسیون.",
    },
    "BI Dashboards & Data Storytelling": {
        "name": "داشبوردهای BI و داستان‌سرایی با داده",
        "description": "لایه شاخص‌های Star Schema، گزارش‌دهی مدیریتی و ترکیب روایت تحلیلی.",
    },
}

REC_PROJECT_FA: dict[str, dict[str, str]] = {
    "SSH & Firewall Hardening Baseline": {
        "title": "اسکریپت پایه مقاوم‌سازی SSH و فایروال",
        "description": "یک اسکریپت Bash خودکار بنویسید که مجوزهای Linux را بررسی کند، قوانین UFW را تنظیم کند و روش‌های ناامن ورود SSH را غیرفعال سازد.",
    },
    "OWASP Vulnerability Lab Analyzer": {
        "title": "تحلیل‌گر آزمایشگاه آسیب‌پذیری OWASP",
        "description": "یک اسکنر Python بسازید که هدرهای ناامن HTTP، فلگ‌های کوکی و الگوهای ورودی بازتابی را روی برنامه‌های آزمایشی شناسایی کند.",
    },
    "Mini SIEM Log Correlation Engine": {
        "title": "موتور مینی‌SIEM برای همبستگی لاگ‌ها",
        "description": "لاگ‌های auth.log و Nginx را در SQLite/Python وارد کنید تا حملات Brute-Force و جهش‌های غیرعادی IP شناسایی شوند.",
    },
    "CIDR Subnet Planner CLI": {
        "title": "ابزار خط فرمان برنامه‌ریزی سابنت CIDR",
        "description": "ابزاری با Python بسازید که بازه شبکه، تعداد میزبان‌های قابل استفاده و تخصیص‌های غیرهم‌پوشان VLSM را محاسبه کند.",
    },
    "Multi-VLAN & OSPF Topology Lab": {
        "title": "آزمایشگاه توپولوژی چند-VLAN و OSPF",
        "description": "یک توپولوژی افزونه با ۳ روتر و ۲ سوئیچ به همراه مسیریابی بین-VLAN و مستندسازی تست‌های Failover طراحی کنید.",
    },
    "Automated Config Drift Auditor": {
        "title": "ممیزی خودکار تغییر پیکربندی روترها",
        "description": "ابزاری با Python ایجاد کنید که پیکربندی روترها را با فایل مرجع YAML مقایسه کرده و هشدار انحراف ثبت کند.",
    },
    "Bookmark & Tagging REST API": {
        "title": "سرویس REST API بوکمارک و برچسب‌گذاری",
        "description": "یک سرویس REST با Flask و SQLite همراه با صفحه‌بندی، فیلتر جست‌وجو و اعتبارسنجی ورودی ایجاد کنید.",
    },
    "Role-Based Issue Tracker Backend": {
        "title": "بک‌اند سیستم پیگیری تسک با نقش کاربری",
        "description": "احراز هویت چندکاربره، مجوزهای پروژه، لاگ ممیزی و مجموعه کامل تست‌های یکپارچه را پیاده‌سازی کنید.",
    },
    "Rate-Limited Webhook Processor": {
        "title": "پردازشگر Webhook با محدودسازی نرخ",
        "description": "یک API دریافت رویداد Idempotent با صف تلاش مجدد، تأیید امضای دیجیتال و متریک‌های پایش بسازید.",
    },
    "Accessible Editorial Landing Page": {
        "title": "صفحه فرود مجله‌ای دسترس‌پذیر",
        "description": "یک وب‌سایت واکنش‌گرا و قابل ناوبری با صفحه‌کلید با المان‌های معنایی و بدون سرریز چیدمان بسازید.",
    },
    "Interactive Expense & Budget Dashboard": {
        "title": "داشبورد تعاملی هزینه و بودجه",
        "description": "یک داشبورد سمت کلاینت با نمودارهای Chart.js، فیلتر زنده و جداول دسترس‌پذیر ایجاد کنید.",
    },
    "Collaborative Kanban State Engine": {
        "title": "موتور وضعیت تخته Kanban تعاملی",
        "description": "جابه‌جایی دسترس‌پذیر کارت‌ها، همگام‌سازی خوش‌بینانه با API و بازیابی وضعیت آفلاین را پیاده‌سازی کنید.",
    },
    "Habit Streak Tracker in Compose": {
        "title": "اپلیکیشن پیگیری عادت‌ها با Compose",
        "description": "فهرست عادت‌ها را با Material 3، State Hoisting و توکن‌های تم تاریک/روشن طراحی کنید.",
    },
    "Offline-First Study Flashcards": {
        "title": "فلش‌کارت‌های مطالعه آفلاین‌محور",
        "description": "دسته‌های کارت را در Room SQLite با زمان‌بندی مرور فاصله‌دار و ViewModel StateFlow ذخیره کنید.",
    },
    "Real-Time Transit Companion": {
        "title": "دستیار لحظه‌ای حمل‌ونقل شهری",
        "description": "دریافت دوره‌ای REST، کش محلی و هشدارهای WorkManager را با مخازن تست‌شده ترکیب کنید.",
    },
    "E-Commerce Cohort Retention SQL Study": {
        "title": "تحلیل ماندگاری مشتریان فروشگاه با SQL",
        "description": "کوئری‌های تحلیلی SQL را با CTE و Window Functions برای محاسبه نرخ بازگشت ماهانه مشتریان بنویسید.",
    },
    "Transit Delay Exploratory Notebook": {
        "title": "نوت‌بوک اکتشافی تأخیرهای حمل‌ونقل",
        "description": "۱۰۰ هزار ردیف برنامه زمانی حمل‌ونقل عمومی را با pandas پاک‌سازی و گلوگاه‌های اوج تأخیر را مصورسازی کنید.",
    },
    "A/B Experiment Evaluation Report": {
        "title": "گزارش ارزیابی آزمایش A/B",
        "description": "افزایش نرخ تبدیل، معناداری آماری و اثرات بخش‌های مختلف کاربران را در یک گزارش تکرارپذیر تحلیل کنید.",
    },
}

RESOURCE_FA: dict[str, dict[str, str]] = {
    "OWASP Web Security Testing Guide": {
        "title": "راهنمای تست امنیت وب OWASP (WSTG)",
        "description": "روش‌شناسی جامع برای آزمودن کنترل‌های امنیتی برنامه‌های وب.",
    },
    "OverTheWire: Bandit Wargame": {
        "title": "چالش‌های عملی OverTheWire: Bandit",
        "description": "تمرین‌های عملی خط فرمان Linux و مبانی سطح دسترسی در مراحل پلکانی.",
    },
    "MITRE ATT&CK Framework": {
        "title": "چارچوب دانشی MITRE ATT&CK",
        "description": "پایگاه دانش تاکتیک‌ها و تکنیک‌های مهاجمان برای شکار تهدید و کشف نفوذ.",
    },
    "PortSwigger Web Security Academy": {
        "title": "آکادمی امنیت وب PortSwigger",
        "description": "آزمایشگاه‌های تعاملی درباره SQL Injection، CSRF، دور زدن احراز هویت و SSRF.",
    },
    "Cloudflare Learning Center: Networking": {
        "title": "مرکز آموزش شبکه Cloudflare",
        "description": "توضیحات روشن درباره BGP، DNS، Anycast و معماری مسیریابی اینترنت.",
    },
    "Beej's Guide to Network Concepts": {
        "title": "راهنمای مفاهیم شبکه Beej",
        "description": "راهنمای پایه‌ای سوکت‌ها، فریم‌بندی TCP/IP و رفتار سطح پایین شبکه.",
    },
    "RFC 2328 — OSPF Version 2": {
        "title": "استاندارد RFC 2328 — پروتکل OSPF نسخه ۲",
        "description": "مشخصات رسمی پروتکل مسیریابی Link-State برای OSPF.",
    },
    "Nornir Network Automation Docs": {
        "title": "مستندات اتوماسیون شبکه Nornir",
        "description": "فریم‌ورک ماژولار Python برای مدیریت موجودی تجهیزات و اجرای موازی تسک‌های شبکه.",
    },
    "Flask Official Documentation": {
        "title": "مستندات رسمی Flask",
        "description": "مرجع رسمی Blueprintها، الگوی کارخانه برنامه (App Factory)، تست‌نویسی و نشست‌ها.",
    },
    "SQLite Query Language & Indexing": {
        "title": "بهینه‌سازی کوئری و ایندکس در SQLite",
        "description": "بررسی عمیق ایندکس‌های B-tree در SQLite، دستور EXPLAIN QUERY PLAN و محدودیت‌ها.",
    },
    "OWASP API Security Top 10": {
        "title": "فهرست OWASP API Security Top 10",
        "description": "چک‌لیست ضروری امنیت احراز هویت، مجوزدهی و محدودسازی نرخ در APIها.",
    },
    "Designing Data-Intensive Applications": {
        "title": "کتاب Designing Data-Intensive Applications",
        "description": "الگوهای بنیادین معماری برای سازگاری داده، تکرارپذیری و پردازش دسته‌ای و جریانی.",
    },
    "MDN Web Docs: Learn Web Development": {
        "title": "مستندات MDN: آموزش توسعه وب",
        "description": "مرجع استاندارد برای HTML5، CSS Grid، Flexbox و Web APIها.",
    },
    "web.dev: Learn Accessibility": {
        "title": "دوره دسترس‌پذیری وب در web.dev",
        "description": "الگوهای مهندسی کاربردی برای کنتراست WCAG، ناوبری صفحه‌کلید و ARIA.",
    },
    "Chart.js Official Documentation": {
        "title": "مستندات رسمی Chart.js",
        "description": "مرجع کامل نمودارهای واکنش‌گرا، مجموعه‌داده‌ها، محورها و تولتیپ‌های تعاملی.",
    },
    "Patterns.dev — Rendering & Performance": {
        "title": "Patterns.dev — رندرینگ و کارایی وب",
        "description": "الگوهای مدرن معماری وب برای رندرینگ، پیش‌واکشی و بودجه کارایی.",
    },
    "Android Basics with Compose": {
        "title": "دوره مبانی اندروید با Jetpack Compose",
        "description": "برنامه درسی رسمی Google شامل Kotlin، چیدمان Compose و معماری اپلیکیشن.",
    },
    "Kotlin Language Documentation": {
        "title": "مستندات رسمی زبان Kotlin",
        "description": "راهنمای رسمی Coroutines، ایمنی Null و APIهای کتابخانه استاندارد Kotlin.",
    },
    "Guide to App Architecture": {
        "title": "راهنمای معماری اپلیکیشن اندروید",
        "description": "توصیه‌های رسمی Jetpack درباره لایه UI، لایه دامنه و منبع واحد حقیقت داده.",
    },
    "Testing on Android Developers": {
        "title": "راهنمای تست‌نویسی در Android Developers",
        "description": "راهبردهای تست واحد، یکپارچه و رابط کاربری Compose برای پایداری محصول.",
    },
    "Mode SQL Tutorial": {
        "title": "آموزش کاربردی SQL در Mode",
        "description": "درس‌های عملی SQL متمرکز بر کسب‌وکار شامل JOIN، تجمیع و Window Functions.",
    },
    "Pandas Official User Guide": {
        "title": "راهنمای کاربری رسمی Pandas",
        "description": "مرجع اصلی برای ایندکس‌گذاری، گروه‌بندی، ادغام و تحلیل سری‌های زمانی.",
    },
    "Storytelling with Data": {
        "title": "کتاب Storytelling with Data",
        "description": "اصول طراحی نمودارهای تحلیلی خلوت، دقیق و ارتباط شفاف با مدیران.",
    },
    "Evan Miller's A/B Testing Guide": {
        "title": "راهنمای آماری A/B Testing از Evan Miller",
        "description": "مبانی دقیق آماری برای محاسبه حجم نمونه و پرهیز از خطاهای توقف زودهنگام.",
    },
    # Demo User Resources
    "SQLite Foreign Keys & WAL Mode Guide": {
        "title": "راهنمای کلیدهای خارجی و حالت WAL در SQLite",
        "description": "نکاتی درباره فعال‌سازی PRAGMA foreign_keys و خواندن هم‌زمان در SQLite.",
    },
    "Flask Application Factory Pattern": {
        "title": "الگوی Application Factory در Flask",
        "description": "راهنمای رسمی برای ساختار ماژولار Blueprintها و پیکربندی تست.",
    },
    "Test-Driven Development with Python": {
        "title": "کتاب Test-Driven Development with Python",
        "description": "جریان کار کامل برای تست یکپارچه مسیرهای وب و لایه پایگاه داده.",
    },
    "PortSwigger SQL Injection Labs": {
        "title": "آزمایشگاه‌های SQL Injection در PortSwigger",
        "description": "تمرین‌های عملی حملات SQLi مبتنی بر Union و Blind.",
    },
}

QUESTION_FA: dict[str, dict[str, str]] = {
    "Which protocol operates at the Transport layer and guarantees ordered, reliable byte-stream delivery?": {
        "question_text": "کدام پروتکل در لایه Transport عمل می‌کند و تحویل مرتب و مطمئن جریان بایت‌ها را تضمین می‌کند؟",
        "option_a": "UDP",
        "option_b": "TCP",
        "option_c": "ICMP",
        "option_d": "ARP",
        "explanation": "پروتکل TCP با استفاده از شماره توالی و تأییدیه (ACK)، ارتباط اتصال‌محور، مرتب و مطمئن را فراهم می‌کند.",
    },
    "What octal permission grants the file owner read/write/execute, the group read/execute, and others no access?": {
        "question_text": "کدام سطح دسترسی عددی (Octal) به مالک فایل اجازه خواندن/نوشتن/اجرا، به گروه اجازه خواندن/اجرا و به سایرین عدم دسترسی می‌دهد؟",
        "option_a": "750",
        "option_b": "644",
        "option_c": "755",
        "option_d": "700",
        "explanation": "عدد 7 (rwx) برای مالک، 5 (r-x) برای گروه و 0 (---) برای سایرین معادل 750 است.",
    },
    "What is the primary defense against SQL Injection when querying a relational database?": {
        "question_text": "اصلی‌ترین راه دفاع در برابر آسیب‌پذیری SQL Injection هنگام اجرای کوئری در پایگاه داده رابطه‌ای چیست؟",
        "option_a": "حذف دستی کوتیشن‌ها در JavaScript",
        "option_b": "استفاده از کوئری‌های پارامتری (Parameterized Statements)",
        "option_c": "کدگذاری Base64 برای ورودی‌های کاربر",
        "option_d": "فقط مخفی‌کردن جزئیات خطای سرور",
        "explanation": "کوئری‌های پارامتری ساختار SQL را از داده‌های غیرقابل اعتماد جدا می‌کنند تا ورودی کاربر نتواند نحو کوئری را تغییر دهد.",
    },
    "Which cookie attribute prevents client-side JavaScript from reading a session identifier via document.cookie?": {
        "question_text": "کدام ویژگی کوکی مانع از آن می‌شود که JavaScript سمت کلاینت شناسه نشست را از طریق document.cookie بخواند؟",
        "option_a": "SameSite=Strict",
        "option_b": "Secure",
        "option_c": "HttpOnly",
        "option_d": "Max-Age",
        "explanation": "ویژگی HttpOnly به مرورگر دستور می‌دهد کوکی را از API مربوط به document.cookie پنهان کند تا خطر سرقت نشست در XSS کاهش یابد.",
    },
    "In the MITRE ATT&CK matrix, what does the 'Persistence' tactic describe?": {
        "question_text": "در ماتریس MITRE ATT&CK، تاکتیک «Persistence» (پایداری) به چه معناست؟",
        "option_a": "تکنیک‌هایی برای خارج‌کردن فایل‌های آرشیوشده از شبکه",
        "option_b": "تکنیک‌هایی که مهاجمان برای حفظ دسترسی پس از راه‌اندازی مجدد سیستم به کار می‌برند",
        "option_c": "پویش پورت‌های باز در محیط بیرونی شبکه",
        "option_d": "رمزنگاری نسخه‌های پشتیبان برای باج‌افزار",
        "explanation": "تاکتیک Persistence شامل روش‌هایی مانند تسک‌های زمان‌بندی‌شده یا اسکریپت‌های راه‌اندازی است که دسترسی را پس از ری‌استارت حفظ می‌کنند.",
    },
    "How many usable host IPv4 addresses are available in a /26 subnet?": {
        "question_text": "در یک سابنت IPv4 با پیشوند ‎/26 چند نشانی میزبان قابل استفاده وجود دارد؟",
        "option_a": "64",
        "option_b": "62",
        "option_c": "30",
        "option_d": "126",
        "explanation": "در سابنت ‎/26 تعداد ۶ بیت برای میزبان باقی می‌ماند (2^6 = 64 آدرس) که با کسر آدرس شبکه و Broadcast، ۶۲ آدرس قابل استفاده به دست می‌آید.",
    },
    "Which IEEE standard defines VLAN tagging on Ethernet trunk frames?": {
        "question_text": "کدام استاندارد IEEE برچسب‌گذاری VLAN روی فریم‌های ترانک اترنت را تعریف می‌کند؟",
        "option_a": "802.11ax",
        "option_b": "802.1Q",
        "option_c": "802.3af",
        "option_d": "802.1X",
        "explanation": "استاندارد IEEE 802.1Q یک برچسب ۴ بایتی VLAN به هدر فریم اترنت اضافه می‌کند تا چندین VLAN روی یک لینک ترانک عبور کنند.",
    },
    "In a multi-area OSPF network, which area must all other areas connect to directly (or via virtual link)?": {
        "question_text": "در یک شبکه OSPF چندناحیه‌ای، همه نواحی دیگر باید مستقیماً (یا از طریق Virtual Link) به کدام ناحیه متصل شوند؟",
        "option_a": "Area 1",
        "option_b": "Area 255",
        "option_c": "Area 0 (Backbone)",
        "option_d": "Area 10",
        "explanation": "ناحیه Area 0 یا ستون فقرات (Backbone) در OSPF مسئول توزیع اطلاعات مسیریابی بین نواحی دیگر است.",
    },
    "During the DORA DHCP lease sequence, which message does the client send first?": {
        "question_text": "در فرآیند دریافت آدرس DHCP (الگوی DORA)، کلاینت ابتدا کدام پیام را ارسال می‌کند؟",
        "option_a": "DHCP Offer",
        "option_b": "DHCP Request",
        "option_c": "DHCP Discover",
        "option_d": "DHCP Ack",
        "explanation": "کلاینت ابتدا پیام DHCP Discover را در شبکه پخش می‌کند تا سرورهای DHCP در دسترس را پیدا کند.",
    },
    "Which BGP path attribute is evaluated first (among standard attributes after Weight) to prefer an outbound route?": {
        "question_text": "در BGP پس از ویژگی Weight، کدام ویژگی استاندارد مسیر در اولویت اول برای ترجیح مسیر خروجی ارزیابی می‌شود؟",
        "option_a": "طول AS_PATH",
        "option_b": "MED",
        "option_c": "LOCAL_PREF",
        "option_d": "کد Origin",
        "explanation": "پس از ویژگی اختصاصی Weight، پروتکل BGP مقدار LOCAL_PREF را بررسی می‌کند و مقدار بالاتر در سیستم خودمختار ترجیح داده می‌شود.",
    },
    "Which HTTP status code indicates a resource was successfully created following a POST request?": {
        "question_text": "کدام کد وضعیت HTTP نشان می‌دهد که در پی یک درخواست POST، یک منبع جدید با موفقیت ایجاد شده است؟",
        "option_a": "200 OK",
        "option_b": "201 Created",
        "option_c": "204 No Content",
        "option_d": "302 Found",
        "explanation": "کد 201 Created به‌صراحت بیان می‌کند که درخواست موفق بوده و به ساخت یک منبع جدید منجر شده است.",
    },
    "What is the primary purpose of an ON DELETE CASCADE foreign key constraint?": {
        "question_text": "هدف اصلی قید کلید خارجی ON DELETE CASCADE در SQL چیست؟",
        "option_a": "رمزنگاری خودکار رکوردهای فرزند",
        "option_b": "حذف خودکار ردیف‌های فرزند وابسته هنگام حذف ردیف والد",
        "option_c": "جلوگیری از هرگونه خواندن از جدول فرزند",
        "option_d": "تبدیل مقادیر NULL به رشته خالی",
        "explanation": "قید ON DELETE CASCADE یکپارچگی ارجاعی را با حذف خودکار ردیف‌های فرزندی که به ردیف والد حذف‌شده اشاره دارند، حفظ می‌کند.",
    },
    "Why should user passwords be stored using salted slow hashes (e.g., scrypt, Argon2, PBKDF2) rather than SHA-256?": {
        "question_text": "چرا رمزهای عبور کاربران باید با هش‌های کند و نمک‌دار (مانند scrypt، Argon2 یا PBKDF2) ذخیره شوند و نه با SHA-256 ساده؟",
        "option_a": "SHA-256 نمی‌تواند رشته‌های طولانی‌تر از ۱۶ کاراکتر را هش کند",
        "option_b": "هش‌های کند و نمک‌دار در برابر Rainbow Table و حملات Brute-Force با GPU مقاوم‌اند",
        "option_c": "هش‌های نمک‌دار به مدیران اجازه رمزگشایی رمزها را می‌دهند",
        "option_d": "SHA-256 فقط در مرورگرها پشتیبانی می‌شود",
        "explanation": "هش‌های سریع مانند SHA-256 خام با سرعت میلیاردها حدس در ثانیه قابل شکستن هستند، اما Salt یکتا و ضریب هزینه بالا سرعت مهاجم را به‌شدت کاهش می‌دهد.",
    },
    "What characterizes the 'N+1 query problem' in backend applications?": {
        "question_text": "مشکل «کوئری N+1» در برنامه‌های بک‌اند چگونه رخ می‌دهد؟",
        "option_a": "اجرای ۱ کوئری برای N رکورد و سپس اجرای N کوئری جداگانه برای داده‌های مرتبط آن‌ها",
        "option_b": "برگرداندن N+1 هدر HTTP در هر پاسخ",
        "option_c": "اتمام اتصالات پایگاه داده در نیمه‌شب",
        "option_d": "ذخیره JSON در بیش از N ستون",
        "explanation": "واکشی فهرستی با N ردیف و سپس اجرای کوئری برای داده‌های مرتبط هر ردیف درون حلقه باعث N+1 رفت‌وبرگشت به پایگاه داده می‌شود.",
    },
    "What makes an API endpoint idempotent?": {
        "question_text": "چه ویژگی‌ای یک Endpoint در API را Idempotent (تکرارپذیر بی‌اثر) می‌سازد؟",
        "option_a": "پاسخ‌گویی در کمتر از ۱۰ میلی‌ثانیه",
        "option_b": "تکرار درخواست یکسان، همان وضعیت سرور را ایجاد کند که اجرای یک‌باره آن ایجاد می‌کند",
        "option_c": "فقط پارامترهای GET را بپذیرد",
        "option_d": "همه پاسخ‌ها را برای همیشه کش کند",
        "explanation": "ویژگی Idempotency تضمین می‌کند تلاش‌های مجدد تکراری (مثلاً در اثر تایم‌اوت شبکه) اثر جانبی تکراری در سرور ایجاد نکنند.",
    },
    "Which HTML element is semantically appropriate for the primary navigation block of a page?": {
        "question_text": "کدام تگ HTML از نظر معنایی برای بخش اصلی ناوبری یک صفحه مناسب است؟",
        "option_a": "<div class='nav'>",
        "option_b": "<nav>",
        "option_c": "<section>",
        "option_d": "<aside>",
        "explanation": "المان <nav> بخش‌های اصلی ناوبری صفحه را به‌طور مستقیم به فناوری‌های کمکی و صفحه‌خوان‌ها معرفی می‌کند.",
    },
    "In CSS Grid, what does `grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))` accomplish?": {
        "question_text": "در CSS Grid دستور `grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))` چه کاری انجام می‌دهد؟",
        "option_a": "عرض تمام ستون‌ها را بدون توجه به عرض صفحه دقیقاً ۲۶۰ پیکسل نگه می‌دارد",
        "option_b": "ستون‌های واکنش‌گرا می‌سازد که به‌صورت خودکار می‌شکنند و فضای باقی‌مانده را تقسیم می‌کنند",
        "option_c": "همه آیتم‌ها را در دسکتاپ عمودی می‌چیند",
        "option_d": "یک آیتم تکی را در مرکز افقی قرار می‌دهد",
        "explanation": "ترکیب auto-fit و minmax(260px, 1fr) به تعداد فضای موجود ستون‌هایی با حداقل ۲۶۰px قرار داده و فضای اضافه را مساوی پخش می‌کند.",
    },
    "Why is event delegation on a parent container useful for dynamic lists?": {
        "question_text": "چرا استفاده از Event Delegation روی المان والد برای فهرست‌های پویا مفید است؟",
        "option_a": "حبابی‌شدن رویداد (Bubbling) در مرورگر را غیرفعال می‌کند",
        "option_b": "یک شنونده واحد رویدادهای آیتم‌های جدید اضافه‌شده را هم بدون اتصال مجدد مدیریت می‌کند",
        "option_c": "کد هم‌زمان را به WebAssembly تبدیل می‌کند",
        "option_d": "محدودیت‌های CORS را دور می‌زند",
        "explanation": "از آنجا که رویدادها در درخت DOM به بالا حرکت می‌کنند، یک Listener روی والد پایدار رویداد فرزندان آینده را نیز دریافت می‌کند.",
    },
    "Which Core Web Vital measures unexpected visual movement of page elements during loading?": {
        "question_text": "کدام شاخص Core Web Vitals جابه‌جایی غیرمنتظره و بصری المان‌های صفحه هنگام بارگذاری را اندازه‌گیری می‌کند؟",
        "option_a": "LCP (Largest Contentful Paint)",
        "option_b": "INP (Interaction to Next Paint)",
        "option_c": "CLS (Cumulative Layout Shift)",
        "option_d": "TTFB (Time to First Byte)",
        "explanation": "شاخص CLS میزان تغییر غیرمنتظره چیدمان محتوای قابل مشاهده را در زمان رندر شدن صفحه اندازه‌گیری می‌کند.",
    },
    "According to WCAG AA guidelines, what is the minimum contrast ratio for normal-sized body text?": {
        "question_text": "طبق استاندارد دسترس‌پذیری WCAG سطح AA، حداقل نسبت کنتراست برای متن عادی چقدر است؟",
        "option_a": "2.0:1",
        "option_b": "3.0:1",
        "option_c": "4.5:1",
        "option_d": "7.0:1",
        "explanation": "استاندارد WCAG 2.1 سطح AA حداقل کنتراست 4.5:1 برای متن عادی و 3:1 برای متن بزرگ را الزامی می‌داند.",
    },
    "Which Kotlin operator safely accesses a property only if the receiver is non-null?": {
        "question_text": "کدام عملگر در Kotlin فقط در صورتی که متغیر non-null باشد، به‌صورت ایمن به ویژگی آن دسترسی پیدا می‌کند؟",
        "option_a": "!!",
        "option_b": "?.",
        "option_c": "::",
        "option_d": "->",
        "explanation": "عملگر فراخوانی ایمن (?.) ویژگی یا متد را در صورت non-null بودن ارزیابی می‌کند و در غیر این صورت null برمی‌گرداند.",
    },
    "What is 'state hoisting' in Jetpack Compose?": {
        "question_text": "مفهوم «State Hoisting» در Jetpack Compose به چه معناست؟",
        "option_a": "نگهداری تمام وضعیت رابط کاربری در متغیرهای استاتیک سراسری",
        "option_b": "انتقال وضعیت به فراخواننده یک Composable تا فرزند بدون وضعیت و قابل استفاده مجدد شود",
        "option_c": "رمزنگاری وضعیت در SharedPreferences",
        "option_d": "اجرای رندر رابط کاربری روی Dispatchers.IO",
        "explanation": "State Hoisting وضعیت را به پایین و رویدادها را به بالا منتقل می‌کند تا Composableها دارای منبع واحد حقیقت و تست‌پذیر شوند.",
    },
    "Why is ViewModel preferred over holding state directly inside an Activity?": {
        "question_text": "چرا استفاده از ViewModel بر نگهداری مستقیم وضعیت درون Activity ترجیح دارد؟",
        "option_a": "ViewModel به‌طور خودکار در تغییرات پیکربندی مانند چرخش صفحه زنده می‌ماند",
        "option_b": "ViewModel می‌تواند مجوزهای AndroidManifest را دور بزند",
        "option_c": "ViewModel فریم‌های OpenGL را سریع‌تر رندر می‌کند",
        "option_d": "ViewModel جایگزین پایگاه داده SQLite می‌شود",
        "explanation": "ViewModel به مخزن LifecycleOwner متصل است و در بازآفرینی‌های پیکربندی مانند چرخش صفحه از بین نمی‌رود.",
    },
    "Which Kotlin Coroutines dispatcher is designed specifically for disk and network I/O operations?": {
        "question_text": "کدام Dispatcher در Kotlin Coroutines مخصوص عملیات ورودی/خروجی دیسک و شبکه طراحی شده است؟",
        "option_a": "Dispatchers.Main",
        "option_b": "Dispatchers.IO",
        "option_c": "Dispatchers.Unconfined",
        "option_d": "Dispatchers.UI",
        "explanation": "Dispatchers.IO از یک استخر رشته مشترک استفاده می‌کند که برای کارهای مسدودکننده I/O مانند پایگاه داده و شبکه بهینه شده است.",
    },
    "In Room, what annotation marks an interface containing SQL query methods?": {
        "question_text": "در کتابخانه Room، کدام Annotation یک Interface حاوی متدهای کوئری SQL را مشخص می‌کند؟",
        "option_a": "@Entity",
        "option_b": "@Database",
        "option_c": "@Dao",
        "option_d": "@Repository",
        "explanation": "@Dao (Data Access Object) متدهایی را تعریف می‌کند که با @Query، @Insert، @Update و @Delete نشانه‌گذاری شده‌اند.",
    },
    "Which SQL clause filters groups AFTER aggregation (such as COUNT or SUM) has been computed?": {
        "question_text": "کدام عبارت SQL گروه‌ها را پس از محاسبه توابع تجمیعی (مانند COUNT یا SUM) فیلتر می‌کند؟",
        "option_a": "WHERE",
        "option_b": "HAVING",
        "option_c": "ORDER BY",
        "option_d": "GROUP BY",
        "explanation": "عبارت WHERE ردیف‌ها را قبل از گروه‌بندی فیلتر می‌کند، اما HAVING گروه‌های تجمیع‌شده را فیلتر می‌نماید.",
    },
    "What does a SQL window function (`OVER (PARTITION BY ...)` ) do compared to `GROUP BY`?": {
        "question_text": "یک تابع پنجره‌ای SQL (`OVER (PARTITION BY ...)`) در مقایسه با `GROUP BY` چه کاری انجام می‌دهد؟",
        "option_a": "ردیف‌های تکراری را برای همیشه حذف می‌کند",
        "option_b": "مقدار تجمیعی یا رتبه را محاسبه می‌کند در حالی که تمام ردیف‌های فردی را حفظ می‌نماید",
        "option_c": "فقط روی ستون‌های متنی کار می‌کند",
        "option_d": "جداول را به فایل CSV تبدیل می‌کند",
        "explanation": "توابع پنجره‌ای محاسبات را روی پنجره‌ای از ردیف‌ها انجام می‌دهند بدون آنکه مجموعه نتایج را به یک ردیف در هر گروه فشرده کنند.",
    },
    "In pandas, which method fills missing (NaN) values with a specified replacement?": {
        "question_text": "در کتابخانه pandas، کدام متد مقادیر گمشده (NaN) را با مقدار جایگزین مشخص پر می‌کند؟",
        "option_a": "dropna()",
        "option_b": "fillna()",
        "option_c": "isna()",
        "option_d": "astype()",
        "explanation": "متد fillna() مقادیر NaN را با یک مقدار ثابت، نگاشت دیکشنری یا روش پرکردن روبه‌جلو/عقب جایگزین می‌کند.",
    },
    "What error occurs when an analyst repeatedly checks an A/B test and stops as soon as p < 0.05?": {
        "question_text": "وقتی تحلیلگر مرتباً نتیجه آزمون A/B را چک کند و به‌محض رسیدن به p < 0.05 آن را متوقف کند، چه خطایی رخ می‌دهد؟",
        "option_a": "تورم خطای نوع اول (مثبت کاذب / Type I Error)",
        "option_b": "تقسیم بر صفر",
        "option_c": "سوگیری نرمال‌سازی داده",
        "option_d": "حذف بقای نمونه",
        "explanation": "سرک‌کشیدن مکرر به نتایج بدون اصلاح آماری، نرخ خطای مثبت کاذب (Type I) را بسیار بالاتر از ۵٪ می‌برد.",
    },
    "Why should bar charts comparing absolute magnitudes generally start their numeric axis at zero?": {
        "question_text": "چرا نمودارهای میله‌ای که مقادیر مطلق را مقایسه می‌کنند معمولاً باید محور عددی خود را از صفر شروع کنند؟",
        "option_a": "برای سریع‌تر شدن رندر CSS",
        "option_b": "تا طول میله‌ها متناسب با مقادیر واقعی باقی بماند",
        "option_c": "چون SQL مقدار صفر را الزامی می‌داند",
        "option_d": "برای پنهان‌کردن خودکار داده‌های پرت",
        "explanation": "بریدن محور در نمودار میله‌ای تفاوت‌های کوچک را بزرگ‌نمایی می‌کند زیرا خوانندگان مقادیر را از روی طول و مساحت میله مقایسه می‌کنند.",
    },
}

DEMO_PROJECTS_FA: dict[str, dict[str, str]] = {
    "LedgerFlow API": {
        "name": "سرویس LedgerFlow API",
        "description": "سرویس REST ثبت هزینه‌های حسابداری دوطرفه با تراکنش‌های Idempotent و لاگ ممیزی SQLite.",
    },
    "AuthVault Session Service": {
        "name": "سرویس نشست AuthVault",
        "description": "میکروسرویس احراز هویت قابل استفاده مجدد با PBKDF2، میان‌افزار CSRF و کنترل دسترسی نقش.",
    },
    "LogSentinel Analyzer": {
        "name": "تحلیلگر لاگ LogSentinel",
        "description": "تحلیلگر خط فرمان برای بررسی لاگ‌های SSH و Nginx و شناسایی حملات Brute-Force.",
    },
}

DEMO_NOTES_FA: dict[str, dict[str, str]] = {
    "SQLite Indexing Rules of Thumb": {
        "title": "قواعد کلیدی ایندکس‌گذاری در SQLite",
        "content": "۱. همیشه ستون‌های کلید خارجی استفاده‌شده در JOIN و فیلتر WHERE user_id = ? را ایندکس کنید.\n۲. از ایندکس ترکیبی (user_id, created_at) برای فید فعالیت داشبورد استفاده نمایید.\n۳. پیش از انتشار فیلترهای جدید، نقشه اجرا را با EXPLAIN QUERY PLAN بررسی کنید.",
    },
    "Session Cookie Hardening Checklist": {
        "title": "چک‌لیست مقاوم‌سازی کوکی نشست",
        "content": "- فعال‌سازی HttpOnly برای مسدود کردن دسترسی document.cookie.\n- تنظیم مناسب SameSite=Lax/None همراه با پرچم Secure روی HTTPS.\n- اعتبارسنجی توکن CSRF در تمام درخواست‌های تغییردهنده وضعیت (POST/PATCH/DELETE).",
    },
}

DEMO_ASSESSMENTS_FA: dict[str, str] = {
    "Backend Core Fundamentals Check": "آزمون مبانی هسته بک‌اند",
    "Automated Testing & Fixtures Drill": "تمرین تست خودکار و Fixtureها",
}

DEMO_FEEDBACK_FA: dict[str, str] = {
    "Strong grasp of HTTP status codes and relational constraints.": "تسلط قوی بر کدهای وضعیت HTTP و محدودیت‌های رابطه‌ای پایگاه داده.",
    "Review isolated test fixtures and edge-case assertion patterns.": "مرور Fixtureهای ایزوله تست و الگوهای بررسی حالات مرزی توصیه می‌شود.",
    "Flagged for extra practice (< 70%).": "نیازمند تمرین بیشتر (زیر ۷۰٪).",
    "Meets competency benchmark.": "دارای سطح تسلط استاندارد.",
}

DEMO_GOALS_FA: dict[str, str] = {
    "Ship 2 tested Flask REST APIs and master relational SQL indexing.": "تحویل ۲ سرویس REST API تست‌شده با Flask و تسلط بر ایندکس‌گذاری SQL رابطه‌ای.",
    "Complete OWASP Top 10 labs and Linux hardening checklist.": "تکمیل آزمایشگاه‌های OWASP Top 10 و چک‌لیست مقاوم‌سازی Linux.",
}


# ============================================================
# Translation Helpers
# ============================================================

def t(key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
    """Look up a localized UI string by dot-key with safe fallback to English."""
    active = lang or get_lang()
    table = TRANSLATIONS.get(active, TRANSLATIONS["en"])
    text = table.get(key)
    if text is None:
        text = TRANSLATIONS["en"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def t_enum(group: str, value: str, lang: Optional[str] = None) -> str:
    """Translate canonical English enum values ('Beginner', 'Planned', etc.)."""
    active = lang or get_lang()
    return ENUM_TRANSLATIONS.get(group, {}).get(active, {}).get(value, value)


def t_career_field(slug: Optional[str], field: str, fallback: str, lang: Optional[str] = None) -> str:
    """Return localized career field ('title', 'tagline', 'description', 'difficulty_summary')."""
    active = lang or get_lang()
    if active != "fa" or not slug:
        return fallback
    return CAREER_FA.get(slug, {}).get(field, fallback)


def t_skill_name(name: Optional[str], lang: Optional[str] = None) -> str:
    """Return localized skill name if available in catalog."""
    if not name:
        return ""
    active = lang or get_lang()
    if active != "fa":
        return name
    return SKILL_FA.get(name, {}).get("name", name)


def t_skill_desc(name: Optional[str], fallback: str, lang: Optional[str] = None) -> str:
    """Return localized skill description if available in catalog."""
    active = lang or get_lang()
    if active != "fa" or not name:
        return fallback
    return SKILL_FA.get(name, {}).get("description", fallback)


def t_task_title(title: str, lang: Optional[str] = None) -> str:
    """Translate system-generated roadmap starter task titles while leaving custom tasks intact."""
    active = lang or get_lang()
    if active != "fa" or not title:
        return title
    if title.startswith("Master "):
        raw_skill = title[len("Master "):]
        return f"تسلط بر {t_skill_name(raw_skill, active)}"
    if title.startswith("Apply ") and title.endswith(" in a hands-on exercise"):
        raw_skill = title[len("Apply "):-len(" in a hands-on exercise")]
        return f"پیاده‌سازی عملی {t_skill_name(raw_skill, active)} در تمرین کاربردی"
    return title


def t_task_desc(
    desc: str,
    skill_name: Optional[str] = None,
    skill_eng_desc: Optional[str] = None,
    lang: Optional[str] = None,
) -> str:
    """Translate system-generated roadmap task descriptions while leaving custom text intact."""
    active = lang or get_lang()
    if active != "fa" or not desc:
        return desc
    if skill_name and skill_eng_desc and desc == skill_eng_desc:
        return t_skill_desc(skill_name, desc, active)
    m_generic = re.match(r"^Build or document a practical lab demonstrating (.+)\.$", desc)
    if m_generic:
        target = m_generic.group(1)
        if skill_name:
            target = t_skill_name(skill_name, active)
        else:
            for eng_name in SKILL_FA:
                if eng_name.lower() == target.lower():
                    target = t_skill_name(eng_name, active)
                    break
        return f"یک آزمایشگاه عملی برای نمایش مهارت «{target}» بسازید یا مستند کنید."
    return desc


def t_rec_project_title(title: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return title
    return REC_PROJECT_FA.get(title, {}).get("title", title)


def t_rec_project_desc(title: str, fallback: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return fallback
    return REC_PROJECT_FA.get(title, {}).get("description", fallback)


def t_resource_title(title: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return title
    return RESOURCE_FA.get(title, {}).get("title", title)


def t_resource_desc(title: str, fallback: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return fallback
    return RESOURCE_FA.get(title, {}).get("description", fallback)


def t_project_name(name: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return name
    return DEMO_PROJECTS_FA.get(name, {}).get("name", name)


def t_project_desc(name: str, fallback: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return fallback
    return DEMO_PROJECTS_FA.get(name, {}).get("description", fallback)


def t_note_title(title: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return title
    return DEMO_NOTES_FA.get(title, {}).get("title", title)


def t_note_content(title: str, fallback: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa":
        return fallback
    return DEMO_NOTES_FA.get(title, {}).get("content", fallback)


def t_goal(goal: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa" or not goal:
        return goal
    if goal in DEMO_GOALS_FA:
        return DEMO_GOALS_FA[goal]
    m = re.match(r"^Complete core (.+) milestones and portfolio projects$", goal)
    if m:
        career_title = _translate_career_title_by_name(m.group(1), active)
        return f"تکمیل مراحل اصلی و پروژه‌های نمونه‌کار در مسیر {career_title}"
    return goal


def _translate_career_title_by_name(eng_title: str, lang: str = "fa") -> str:
    if lang != "fa":
        return eng_title
    slug_guess = eng_title.strip().lower().replace(" ", "-")
    if slug_guess in CAREER_FA:
        return CAREER_FA[slug_guess]["title"]
    return eng_title


def t_question(q: Any, lang: Optional[str] = None) -> dict[str, Any]:
    """Return a localized dict representation of an assessment_questions row."""
    row = dict(q)
    active = lang or get_lang()
    if active == "fa":
        fa_q = QUESTION_FA.get(row.get("question_text", ""))
        if fa_q:
            row["question_text"] = fa_q["question_text"]
            row["option_a"] = fa_q["option_a"]
            row["option_b"] = fa_q["option_b"]
            row["option_c"] = fa_q["option_c"]
            row["option_d"] = fa_q["option_d"]
            row["explanation"] = fa_q["explanation"]
    return row


def t_assessment_title(title: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa" or not title:
        return title
    if title in DEMO_ASSESSMENTS_FA:
        return DEMO_ASSESSMENTS_FA[title]
    m = re.match(r"^(.+) Competency Quiz$", title)
    if m:
        return f"آزمون سنجش مهارت {_translate_career_title_by_name(m.group(1), active)}"
    return title


def t_assessment_feedback(feedback: str, lang: Optional[str] = None) -> str:
    active = lang or get_lang()
    if active != "fa" or not feedback:
        return feedback
    if feedback in DEMO_FEEDBACK_FA:
        return DEMO_FEEDBACK_FA[feedback]
    m_focus = re.match(r"^Focus next on: (.+)\.$", feedback)
    if m_focus:
        parts = [t_skill_name(p.strip(), active) for p in m_focus.group(1).split(",")]
        return f"تمرکز بعدی روی: {'، '.join(parts)}."
    m_excel = re.match(r"^Excellent mastery across all (.+) core topics\.$", feedback)
    if m_excel:
        return f"تسلط عالی بر تمام مباحث اصلی {_translate_career_title_by_name(m_excel.group(1), active)}."
    return feedback


def t_activity_desc(desc: str, lang: Optional[str] = None) -> str:
    """Translate deterministic system-logged activity feed descriptions."""
    active = lang or get_lang()
    if active != "fa" or not desc:
        return desc

    fixed = {
        "Created SkillMap learner account": "حساب یادگیرنده SkillMap ایجاد شد",
        "Updated profile settings and weekly study goal": "تنظیمات پروفایل و هدف مطالعه هفتگی به‌روزرسانی شد",
        "Updated account password": "رمز عبور حساب کاربری تغییر یافت",
        "Finished reading SQLite Foreign Keys Guide": "مطالعه راهنمای کلیدهای خارجی SQLite تکمیل شد",
    }
    if desc in fixed:
        return fixed[desc]

    patterns = [
        (r"^Enrolled in (.+) learning roadmap$", lambda m: f"ثبت‌نام در نقشه راه {_translate_career_title_by_name(m.group(1), active)}"),
        (r"^Updated learning goal: (.+)$", lambda m: f"به‌روزرسانی هدف یادگیری: {t_goal(m.group(1), active)}"),
        (r"^Added roadmap task: (.+)$", lambda m: f"افزودن تسک نقشه راه: {t_task_title(m.group(1), active)}"),
        (r"^Completed task: (.+)$", lambda m: f"تکمیل تسک: {t_task_title(m.group(1), active)}"),
        (r"^Updated (.+) mastery to (\d+)%$", lambda m: f"به‌روزرسانی تسلط در «{t_skill_name(m.group(1), active)}» به {m.group(2)}٪"),
        (r"^Saved resource: (.+)$", lambda m: f"ذخیره منبع: {t_resource_title(m.group(1), active)}"),
        (r"^Bookmarked curated resource: (.+)$", lambda m: f"نشان‌کردن منبع منتخب: {t_resource_title(m.group(1), active)}"),
        (r"^Completed resource: (.+)$", lambda m: f"تکمیل مطالعه منبع: {t_resource_title(m.group(1), active)}"),
        (r"^Created project: (.+)$", lambda m: f"ایجاد پروژه: {t_project_name(m.group(1), active)}"),
        (r"^Updated (.+) progress to (\d+)%$", lambda m: f"به‌روزرسانی پیشرفت «{t_project_name(m.group(1), active)}» به {m.group(2)}٪"),
        (r"^Updated (.+) to (\d+)%$", lambda m: f"به‌روزرسانی «{t_project_name(m.group(1), active)}» به {m.group(2)}٪"),
        (r"^Updated (.+) \((Planned|In Progress|Completed|On Hold), (\d+)%\)$", lambda m: f"به‌روزرسانی «{t_project_name(m.group(1), active)}» ({t_enum('status', m.group(2), active)}، {m.group(3)}٪)"),
        (r"^Added study note: (.+)$", lambda m: f"افزودن یادداشت مطالعه: {t_note_title(m.group(1), active)}"),
        (r"^Completed (.+) Competency Quiz \((\d+)%\)$", lambda m: f"تکمیل آزمون سنجش مهارت {_translate_career_title_by_name(m.group(1), active)} ({m.group(2)}٪)"),
        (r"^Completed (.+) \((\d+)%\)$", lambda m: f"تکمیل «{t_assessment_title(m.group(1), active)}» ({m.group(2)}٪)"),
        (r"^Logged (Quiz|Self-Evaluation|Practical): (.+) \((\d+)%\)$", lambda m: f"ثبت {t_enum('assessment_type', m.group(1), active)}: {t_assessment_title(m.group(2), active)} ({m.group(3)}٪)"),
    ]
    for pattern, builder in patterns:
        match = re.match(pattern, desc)
        if match:
            return builder(match)
    return desc


def t_weekday_label(day_obj: datetime, lang: Optional[str] = None) -> str:
    """Format short weekday + day-of-month label for weekly activity chart."""
    active = lang or get_lang()
    if active == "fa":
        return f"{WEEKDAYS_FA.get(day_obj.weekday(), '')} {day_obj.day}"
    return day_obj.strftime("%a %d")


def format_localized_datetime(value: Any, lang: Optional[str] = None) -> str:
    """Format SQLite timestamps into localized readable strings."""
    if not value:
        return ""
    active = lang or get_lang()
    dt_obj: Optional[datetime] = None
    has_time = True
    if isinstance(value, datetime):
        dt_obj = value
    else:
        text = str(value).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                dt_obj = datetime.strptime(text[:19], fmt)
                has_time = fmt != "%Y-%m-%d"
                break
            except ValueError:
                continue
        if dt_obj is None:
            return text

    if active == "fa":
        month_name = MONTHS_FA.get(dt_obj.month, str(dt_obj.month))
        if has_time:
            return f"{dt_obj.day} {month_name} {dt_obj.year} · {dt_obj.strftime('%H:%M')}"
        return f"{dt_obj.day} {month_name} {dt_obj.year}"

    return dt_obj.strftime("%b %d, %Y") if not has_time else dt_obj.strftime("%b %d, %Y · %H:%M")


def get_client_i18n(lang: Optional[str] = None) -> dict[str, Any]:
    """Provide minimal runtime translations to app.js and charts.js from the single source of truth."""
    active = lang or get_lang()
    return {
        "lang": active,
        "dir": get_text_dir(active),
        "confirmDefault": t("common.confirm_delete_prompt", active),
        "tasksRatio": t("roadmap.tasks_ratio", active),
        "hoursRatio": t("roadmap.hours_ratio", active),
        "hoursLoggedShort": t("roadmap.hours_logged_short", active),
        "resourceReopen": t("resources.reopen", active),
        "resourceMarkComplete": t("resources.mark_complete", active),
        "resourceCompleted": t("resources.completed", active),
        "resourceUnread": t("resources.unread", active),
        "chartStudyHours": t("chart.study_hours", active),
        "chartHrsSuffix": t("chart.hrs_logged_suffix", active),
        "chartMasteryLabel": t("chart.mastery_label", active),
        "chartMasterySuffix": t("chart.mastery_suffix", active),
        "hoursUnit": t("common.hours_unit", active),
        "showPassword": t("auth.show_password", active),
        "hidePassword": t("auth.hide_password", active),
    }
