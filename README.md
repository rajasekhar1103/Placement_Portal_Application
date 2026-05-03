# Placement Portal — Project README

## Overview

This repository implements a campus placement portal: a full-stack web application for managing recruitment drives, company registrations, and student applications. It includes a Flask backend API, a Vue-based frontend SPA, database models, background job handling, and example deployment artifacts.

This README explains the repository layout, setup and run instructions for development and production, testing guidance, and useful references to key files.

## Key Features

- User authentication and role-based access (admin/company/student)
- Dataset/digital asset uploads and validation
- Recruitment drive creation and management
- Student application workflows and status tracking
- Interactive dashboards and visualizations
- Background job processing for long-running tasks
- Exportable reports (CSV/JSON/PDF)

## Repository Structure

- `backend/` — Flask application, routes, models, and background tasks. See [backend/app.py](backend/app.py).
- `frontend/` — Vue application (Vite) with components and router. See [frontend/src/main.js](frontend/src/main.js) and [frontend/index.html](frontend/index.html).
- `uploads/` — Uploaded files storage (created at runtime).
- `CODEBASE_AUDIT_REPORT.md` — Audit notes and codebase summary.
- `App_Development_Project_Report.md` — Academic project report for submission.

## Prerequisites

- Python 3.10+ (for backend)
- Node.js 16+ and npm/yarn (for frontend)
- Optional: Docker & docker-compose for containerized deployment

## Backend — Local Development

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# or on cmd: .\.venv\Scripts\activate
```

2. Install Python dependencies:

```powershell
pip install -r backend/requirements.txt
```

3. Environment variables (recommended): create a `.env` or export variables. Common variables used by `backend/config.py`:

- `FLASK_ENV=development`
- `DATABASE_URL` (e.g. `sqlite:///data.db` or PostgreSQL URL)
- `CELERY_BROKER_URL` (e.g. `redis://localhost:6379/0`)
- `CELERY_RESULT_BACKEND` (e.g. `redis://localhost:6379/1`)
- `ADMIN_EMAIL` and `ADMIN_PASSWORD`
- `UPLOAD_FOLDER` (default created at runtime)

4. Run the development server:

```powershell
# Run directly (auto-creates DB and seeds admin)
python backend/app.py

# Or create a run.py and run:
python run.py
```

5. (Optional) Start Celery worker for background tasks:

```powershell
celery -A backend.app.celery worker --loglevel=info
```

## Frontend — Local Development

1. Install dependencies and run dev server:

```bash
cd frontend
npm install
npm run dev
```

2. Open the Vite URL to view the app. The backend API defaults to port `5000`.

## Production Deployment (suggested)

- Build frontend for production and serve static files via the backend or NGINX.

```bash
cd frontend
npm run build
# Copy dist to backend/static or configure NGINX to serve frontend
```

- Use Gunicorn + NGINX to serve the Flask app:

```bash
# Example Gunicorn command
gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app
```

- Docker-compose (example): create `docker-compose.yml` to run `web`, `worker`, `redis`, and `postgres` services and run:

```bash
docker-compose up --build -d
```

## Database Migrations

This project uses SQLAlchemy and Alembic for schema migrations. Example workflow:

```bash
# Initialize migrations (first time)
alembic init migrations
# Create a migration
alembic revision --autogenerate -m "Add initial schema"
# Apply migrations
alembic upgrade head
```

## Testing

Run unit and integration tests with pytest from the repository root:

```powershell
pytest -q
```

## Useful Files

- `backend/app.py` — application factory and Flask entrypoint
- `backend/config.py` — configuration and environment variables
- `backend/extensions.py` — initialized Flask extensions (db, jwt, cache, celery)
- `backend/routes/` — API blueprints (auth, admin, company, student)
- `frontend/src/` — Vue components and router
- `App_Development_Project_Report.md` — detailed project report for submission

## Security & Best Practices

- Store secrets (database passwords, admin credentials) in environment variables or a secrets manager.
- Use HTTPS & secure cookies in production.
- Enforce strong password hashing (bcrypt/Argon2) and proper session management.
- Apply input validation and use parameterized queries to prevent injection attacks.

## Extending the Project

- Add OpenAPI docs using FastAPI or Flask-RESTX/Flask-Smorest for Swagger UI.
- Integrate CI/CD pipelines to run tests and build artifacts automatically.
- Add S3-compatible storage for large file uploads and scheduled export jobs.

---