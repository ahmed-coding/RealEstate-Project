# AGENTS.md - Real Estate Platform Development Guidelines

This document provides guidelines for agentic coding agents working on this codebase.

---

## 1. Project Overview

- **Stack**: Django 4.2.5 · DRF · PostgreSQL · Celery · RabbitMQ · FastAPI
- **Location**: All Django code in `core/`, services in `core/apps/`
- **Manage**: `python manage.py` from `core/` directory
- **Database**: SQLite (dev), PostgreSQL (production)

---

## 2. Build / Lint / Test Commands

### Running Django Commands
```bash
cd core

# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell
```

### Testing (pytest)
Tests are located in `core/apps/<app>/tests/` or `core/apps/tests/`.

```bash
# Install test dependencies first (add to requirements.txt):
# pytest, pytest-django, pytest-asyncio, factory-boy, coverage

# Run all tests
pytest

# Run single test file
pytest core/apps/users/tests/test_views.py

# Run single test function
pytest core/apps/users/tests/test_views.py::test_register_view

# Run with coverage
pytest --cov=core/apps --cov-report=html

# Run with coverage gate (fail if < 60%)
pytest --cov=core/apps --cov-fail-under=60
```

### Linting (as per PRD v2.0 CI)
```bash
# Install: flake8, black, bandit

# Lint code
flake8 core/ apps/ workers/ realtime/ --max-line-length=120

# Check formatting (don't fix)
black --check core/ apps/ workers/

# Security scan
bandit -r core/apps/ -x core/ML/
```

### Celery Commands
```bash
# Start worker
celery -A core worker -l info -Q default

# Start beat scheduler
celery -A core beat -l info

# Start flower (monitoring)
celery -A core flower --port=5555
```

---

## 3. Code Style Guidelines

### Imports
- Use absolute imports: `from apps.users.models import User`
- Group imports: standard library → third-party → Django → local
- Sort alphabetically within groups
- Maximum line length: 120 characters
- Use `__all__` in modules to define public API

### Formatting
- Use Black for formatting (line length 120)
- Use single quotes for strings, double for docstrings
- Use trailing commas in multi-line structures
- Leave two blank lines between top-level definitions

### Types
- Use type hints for function arguments and return values
- Prefer `List`, `Dict` from `typing` for compatibility
- Use `Optional[X]` instead of `X | None`
- Add `# type: ignore` only when necessary

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `PropertySerializer`)
- **Functions/variables**: `snake_case` (e.g., `get_user_by_email`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- **Django models**: `PascalCase` with singular name (e.g., `class Property`)
- **Django apps**: `snake_case` (e.g., `property`, `authentication`)
- **Files**: `snake_case` (e.g., `property_views.py`)
- **Tests**: `test_<module>_<function>` (e.g., `test_property_create_success`)

### Error Handling
- Never use bare `except:` — use specific exceptions
- Use `try/except` blocks with proper exception types
- Return appropriate HTTP status codes (400, 404, 500)
- Log errors with proper logging module
- Never expose raw exception messages to API responses

### Django REST Framework
- Use ViewSets for CRUD operations
- Use Serializers for validation and serialization
- Apply `permission_classes` per-view, not globally
- Use `select_related` and `prefetch_related` to avoid N+1 queries
- Use pagination for list endpoints

---

## 4. Project Structure

```
core/
├── manage.py
├── requirements.txt
├── core/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── local.py        # Dev overrides
│   │   └── production.py   # Production config
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── apps/
    ├── users/              # User model + auth
    ├── authentication/    # Token auth, OTP, password reset
    ├── property/          # Property listings
    ├── address/           # Country, City, State, Address
    ├── category/          # MPTT category tree
    ├── chat/              # Chat rooms and messages
    ├── notifications/     # Notification model + tasks
    ├── friend/            # Friend list and requests
    ├── favorite/          # User favorites
    ├── review/            # Property reviews and ratings
    ├── alarms/            # Property match alarms
    ├── banners/           # Promotional banners
    └── ticket/            # Support tickets
```

---

## 5. Key Constraints (from PRD v2.0)

1. **Backward API Compatibility**: Preserve all REST endpoint paths and response shapes
2. **Single Database**: One PostgreSQL instance with pgvector
3. **AI Data Isolation**: AI accesses data only through MCP tools, never direct ORM
4. **No Private Data in LLM**: Never include private messages, email, phone in prompts
5. **Admin-Configurable AI**: LLM model selection via Django Admin panel
6. **Migrations Committed**: All migration files committed to git
7. **Security First**: Fix all Phase 0 security issues before any feature work

---

## 6. Security Requirements (Phase 0)

- All secrets go in environment variables, never hardcoded
- OTP stored in DB, never returned in API response
- Password reset uses cryptographic tokens with 15-min expiry
- `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]`
- CORS whitelist instead of `CORS_ORIGIN_ALLOW_ALL`
- `ALLOWED_HOSTS` set explicitly in production

---

## 7. Git Workflow

- Create feature branch from `main`
- Run linting before committing
- All tests must pass before merging
- Commit messages: imperative mood, concise
- Never commit secrets or `.env` files

---

## 8. Testing Strategy

- Use `factory_boy` for test fixtures
- Test auth flows (register, OTP verify, login)
- Test property CRUD operations
- Test search functionality
- Test Celery tasks
- Target: 70% code coverage

---

## 9. Development Notes

- Use `python-dotenv` for environment variables
- Create `.env` from `.env.example` template
- Enable pgvector extension in PostgreSQL
- Use Redis for Celery result backend
- Use Celery Beat for scheduled tasks
- FastAPI service for WebSocket (replaces Django Channels)