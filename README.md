# Propylon Document Manager

A modern web application for secure document storage, versioning, and retrieval, built with Django REST Framework (backend) and React (frontend).

---

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [API Overview](#api-overview)
- [Testing](#testing)
- [Development Notes](#development-notes)

---

## Features
- Store files of any type and name
- Versioning: multiple revisions per file, always accessible
- Content Addressable Storage: fetch any version by content hash
- User authentication and per-user file isolation
- RESTful API for all operations
- Modern React frontend (TypeScript, Material UI)
- Unit tested, clean codebase

---

## Architecture
- **Backend:** Django 5, Django REST Framework, SQLite (default, can be changed)
- **Frontend:** React (TypeScript), Material UI, Vite
- **Authentication:** Token & Basic Auth (API), session for admin
- **File Storage:** Local filesystem (`/media/`), configurable

---

## Backend Setup

### 1. Prerequisites
- Python 3.11+
- [Make](https://www.gnu.org/software/make/)

### 2. Installation
```bash
make build
```
This will:
- Create a virtual environment
- Install all Python dependencies

### 3. Database & Test Data
Run migrations and load test fixtures:
```bash
make fixture
```
This will:
- Apply all migrations
- Create several test file versions for a demo user

### 4. Running the Server
```bash
make serve
```
- The API will be available at: [http://localhost:8001](http://localhost:8001)
- Django admin: [http://localhost:8001/admin](http://localhost:8001/admin)

### 5. Default Users
- You must create users via the admin panel or shell.
- Example for shell:
  ```python
   from propylon_document_manager.file_versions.models import User
   if not User.objects.filter(email="admin@example.com").exists():
	User.objects.create_superuser(email="admin@example.com", password="admin123")
   if not User.objects.filter(email="user1@example.com").exists():
	User.objects.create_user(email="user1@example.com", password="user123")
  ```

---

## Frontend Setup

### 1. Prerequisites
- Node.js 18.x (recommended: use [nvm](https://github.com/nvm-sh/nvm))
- npm

### 2. Installation
```bash
cd client/doc-manager
nvm use
npm install
```

### 3. Running the Frontend
```bash
npm start
```
- The frontend will be available at: [http://localhost:3000](http://localhost:3000)

### 4. API URL Configuration
- By default, the frontend expects the backend at `http://localhost:8001`.
- If you change the backend port, update the API URL in the frontend `.env` file.

---

## API Overview
- All API endpoints are under `/api/`
- **Authentication:** Basic Auth or Token Auth required for all endpoints

### Main Endpoints
| Method | Endpoint                                         | Description                                 |
|--------|--------------------------------------------------|---------------------------------------------|
| GET    | `/api/file_versions/`                            | List all file versions for the user         |
| POST   | `/api/file_versions/`                            | Upload a new file version                   |
| GET    | `/api/file_versions/{id}/`                       | Get details for a specific file version     |
| GET    | `/api/file_versions/{id}/share/`                 | Get shareable link for a file version       |
| GET    | `/api/file_versions/by_hash/{content_hash}/`      | Get file version by content hash            |

- Only the owner can access their files/versions.
- Each upload with the same file name creates a new version.
- Shareable links point to the latest version.

---

## Testing

### 1. Run all backend tests
```bash
make test
```
- Uses pytest and pytest-django
- Tests cover: upload, versioning, hash, user isolation, permissions, and more

### 2. Linting and formatting
- Black, isort, flake8, mypy, and more are configured in `pyproject.toml`
- Run linters as needed for code quality

---

## Development Notes
- **Database:** Default is SQLite for easy setup. For production, use PostgreSQL or another robust DB.
- **File Storage:** Files are stored in `/media/` by default. Change `MEDIA_ROOT` in settings for other storage backends.
- **Admin Panel:** Use Django admin for user and file management.
- **Fixtures:** The `make fixtures` command loads demo data for quick testing.

---

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
