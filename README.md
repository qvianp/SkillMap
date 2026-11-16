# SkillMap
### Technical Learning & Career Roadmap Platform

#### Video Demo
https://youtu.be/Hy7dR9j1l7s

## Description

SkillMap is a web-based platform designed to help people organize their technical learning journey and explore potential career paths in the technology industry.

One of the main challenges people face when learning programming and other technical skills is knowing where to start, what to learn next, and how to organize their progress. SkillMap aims to address this problem by providing an integrated environment where users can explore career opportunities, manage learning roadmaps, save educational resources, and track their personal projects.

The main goal of this project is to make technical learning more organized, structured, and manageable.

## Features

### 1. Dashboard
The dashboard provides an overview of the user's learning activities and progress, helping users keep track of their learning journey.

### 2. Career Explorer
Users can explore different technology career paths, including:

- Backend Development
- Frontend Development
- Cybersecurity
- Network Engineering

Each career path introduces relevant skills and technologies that users can explore.

### 3. Learning Roadmap
Users can organize their learning journey into manageable stages and track the skills they are working toward.

### 4. Learning Resources
Users can save and organize useful educational resources to access them later.

### 5. Personal Projects
Users can manage their personal projects and monitor their development progress.

### 6. User Authentication
SkillMap includes user registration, login, and account management functionality.

### 7. Bilingual Interface
The application supports Persian and English, with layouts adapted to RTL and LTR text directions.

## Technologies Used

- **Python:** Main backend programming language.
- **Flask:** Backend web framework.
- **SQLite:** Database management and data storage.
- **HTML5:** Page structure.
- **CSS3:** Styling and responsive layouts.
- **JavaScript:** Frontend interactions and dynamic functionality.
- **TypeScript:** Supporting frontend development tools.

## Project Structure

- `app.py`: Main Flask application and application initialization.
- `auth.py`: Authentication-related functionality.
- `config.py`: Application configuration.
- `database.py`: Database operations and connection management.
- `init_db.py`: Database initialization.
- `seed_data.py`: Initial and sample data setup.
- `translations.py`: Persian and English translation resources.
- `routes/`: Application routes and feature-specific backend endpoints.
- `templates/`: HTML templates for the different application pages.
- `static/`: CSS stylesheets, JavaScript files, and static assets.
- `src/`: Frontend source files.
- `tests/`: Automated application tests.
- `requirements.txt`: Python dependencies.
- `package.json`: Node.js project dependencies and scripts.
- `vite.config.ts`: Vite development configuration.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/qvianp/SkillMap.git
cd SkillMap
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
python init_db.py
```

The application may also initialize the database automatically when it starts, depending on its configuration.

### 5. Run the application

```bash
python app.py
```

Open the following address in your browser:

http://127.0.0.1:5000

## Design and Development

During development, particular attention was given to creating a clear and accessible user interface while maintaining a structured backend architecture.

The project combines multiple features into one environment rather than separating career exploration, learning resources, roadmaps, and personal projects into unrelated tools.

One of the important design decisions was supporting both Persian and English. This makes the platform accessible to users with different language preferences and requires consideration of both RTL and LTR layouts.

## Future Improvements

Potential future improvements include:

- More detailed career roadmaps.
- Additional learning resources.
- Advanced learning progress analytics.
- More personalized learning recommendations.
- Expanded career categories.

## Conclusion

SkillMap was developed as my CS50x Final Project to apply programming concepts and software development skills in a practical application.

Building this project gave me an opportunity to work with Python, Flask, SQL, frontend technologies, database design, and application architecture.

My goal is to continue improving SkillMap and make it a useful platform for people who want to build their technical skills and plan their future careers.
