# Real Estate Platform — Modernization & Microservices Migration
## Product Requirements Document · v2.0

---

| Field | Detail |
|---|---|
| **Status** | Draft — In Review |
| **Version** | 2.0 |
| **Supersedes** | PRD v1 (v1-backup branch) |
| **Owner** | Solo Developer |
| **Date** | March 2026 |
| **Stack** | Django · FastAPI · PostgreSQL · pgvector · Redis · Celery · RabbitMQ · OpenRouter |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Critical Security Fixes — Must Complete Before Phase 1](#2-critical-security-fixes--must-complete-before-phase-1)
3. [New Project Structure](#3-new-project-structure)
4. [AI Architecture](#4-ai-architecture)
5. [Search — pgvector Replaces Algolia](#5-search--pgvector-replaces-algolia)
6. [FastAPI Realtime Service](#6-fastapi-realtime-service)
7. [Background Processing — Celery](#7-background-processing--celery)
8. [Docker Compose — Full Service Stack](#8-docker-compose--full-service-stack)
9. [CI/CD — GitHub Actions](#9-cicd--github-actions)
10. [Phased Migration Roadmap](#10-phased-migration-roadmap)
11. [Testing Strategy](#11-testing-strategy)
12. [Constraints & Principles](#12-constraints--principles)
13. [Success Metrics](#13-success-metrics)
- [Appendix A — Dependency Changes](#appendix-a--dependency-changes)

---

## 1. Executive Summary

This document replaces PRD v1 and defines the complete upgrade path for the Real Estate backend platform. It corrects critical security vulnerabilities identified in the v1-backup code review, restructures the Django project into a true microservice-ready architecture, and lays out a phased roadmap toward an AI-powered platform with RAG, MCP tool integrations, and pgvector-based semantic search.

The migration strategy is deliberately incremental — **fix first, then restructure, then extend** — so that the solo developer can ship stable improvements without breaking the existing mobile and web clients currently in development.

### Key Changes from PRD v1

- Security vulnerabilities patched before any new feature work begins
- Django project restructured: apps split into independent modules under `core/services/`
- FastAPI realtime service replaces Django Channels, sharing the same Django ORM models
- Algolia replaced with pgvector + Django for semantic property search
- AI layer uses OpenRouter with a dynamic model router and a controlled MCP tool layer
- RAG pipeline built on pgvector embeddings stored in PostgreSQL
- LLM provider model manageable from Django Admin panel (no code changes needed to swap models)
- GitHub Actions CI/CD pipeline included from Phase 1

---

## 2. Critical Security Fixes — Must Complete Before Phase 1

These issues were identified in the v1-backup code review. **All must be resolved before any architectural work begins.** No new features ship until these are closed.

---

### 2.1 Secrets & Credentials

> **🔴 CRITICAL** — The Django `SECRET_KEY`, email password, and SMTP credentials are hardcoded in `base.py` and committed to version history.

**Required actions:**

- Move all secrets to environment variables using `python-dotenv`
- Create `.env.example` with placeholder keys — commit this, never the real `.env`
- Rotate the email password immediately (`realestate@bastblog.com`)
- Add `SECRET_KEY`, `EMAIL_HOST_PASSWORD`, and any API keys to `.gitignore`

```python
# base.py — correct pattern
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
```

---

### 2.2 Broken OTP Verification

> **🔴 CRITICAL** — `send_verify_email()` returns the OTP in the API response body — any caller can read it. `verify_email()` returns `is_valid: True` for any non-empty string and never validates the code against what was sent.

**Required actions:**

- Store OTP in a `VerificationCode` model row (already exists) tied to the email address
- **Never** return the code in the API response — send it via email only
- Validate `verify_email()` by querying `VerificationCode` where email matches and code matches
- Add a 10-minute expiry check on `VerificationCode.expire_date`
- Delete the `VerificationCode` row after successful verification

---

### 2.3 Password Reset — No Token or Expiry

> **🔴 CRITICAL** — Anyone who knows a user's email address can reset their password. There is no reset token, no expiry window, and no current-password confirmation.

**Required actions:**

- Generate a cryptographically random token: `secrets.token_urlsafe(32)` on reset request
- Store token + expiry (15 minutes) in a `PasswordResetToken` model
- Send only the token link via email — never the token in the API response
- Verify token exists, is not expired, and belongs to the email before allowing password change
- Invalidate the token after single use

---

### 2.4 Additional Security Hardening

| Issue | Fix Required |
|---|---|
| `CORS_ORIGIN_ALLOW_ALL = True` | Set `CORS_ORIGIN_WHITELIST` to actual frontend URLs |
| `ALLOWED_HOSTS = ['*']` in production.py | List explicit domains only |
| Production settings use SQLite | Activate the PostgreSQL config block |
| `DEFAULT_PERMISSION_CLASSES` is empty | Set to `[IsAuthenticated]` as default; override per-view for public endpoints |
| Bare `except:` in models.py (3 places) | Replace with specific exception types |
| `Banner.__str__` calls `self.save()` | Remove the `save()` call — `__str__` must be side-effect free |
| `CustomBannerManager` missing `()` | Change to: `objects = CustomBannerManager()` |
| `Property.save()` writes to `self.unique_no` | Fix field name to `self.unique_number` |
| ML model loaded at module import | Wrap in `try/except` or use lazy loading |

---

## 3. New Project Structure

The current codebase places all models in a single 1,600-line `apps/models.py`. The new structure moves each domain into an independent Django app under `core/services/`, each with its own models, views, serializers, urls, and tests. FastAPI services live in a separate top-level folder.

### 3.1 Directory Layout

```

├──core/                          # Django project root
│  ├── settings/
│  │   ├── base.py                # Shared settings (no secrets)
│  │   ├── local.py               # Dev overrides
│  │   └── production.py          # Production (PostgreSQL, Redis)
│  ├── urls.py                    # Root URL config
│  ├── asgi.py
│  └── wsgi.py
│
├─services/                      # All Django apps (microservice-ready)
│  ├── users/                     # Custom User model + auth
│  │   ├── models.py
│  │   ├── views.py
│  │   ├── serializers.py
│  │   ├── urls.py
│  │   └── tests/
│  ├── authentication/            # Token auth, OTP, password reset
│  ├── property/                  # Property listings, features, attribute values
│  ├── address/                   # Country, City, State, Address
│  ├── category/                  # MPTT category tree
│  ├── search/                    # pgvector semantic search (replaces Algolia)
│  ├── chat/                      # Chat rooms and messages (REST only)
│  ├── notifications/             # Notification model + Celery tasks
│  ├── friend/                    # Friend list and requests
│  ├── favorite/                  # User favorites
│  ├── review/                    # Property reviews and ratings
│  ├── alarms/                    # Property match alarms
│  ├── banners/                   # Promotional banners
│  ├── ticket/                    # Support tickets
│  └── ai/                        # AI config models + MCP tool registry
│      ├── models.py              # LLMProvider, PromptTemplate, MCPTool
│      ├── router.py              # OpenRouter LLM routing logic
│      ├── tools.py               # MCP tool implementations
│      ├── rag.py                 # RAG pipeline (embed → retrieve → respond)
│      └── admin.py               # Admin panel AI management
│
├─realtime/                      # FastAPI WebSocket service
│  ├── main.py                    # FastAPI app entry point
│  ├── consumers/
│  │   ├── chat.py                # Chat WebSocket consumer
│  │   └── notifications.py       # Notification WebSocket consumer
│  ├── auth.py                    # Token validation (calls Django ORM)
│  └── requirements.txt
│
├─workers/                       # Celery worker app
│  ├── tasks/
│  │   ├── notifications.py
│  │   ├── embeddings.py          # Property embedding generation
│  │   ├── ai_tasks.py            # AI processing tasks
│  │   └── alarms.py              # Alarm matching tasks
│  └── celery.py
│
├─docker-compose.yml
├──docker-compose.prod.yml
├──.env.example
└──.github/
└── workflows/
    ├── ci.yml                 # Tests + lint on every push
    └── deploy.yml             # Deploy on merge to main
```

---

### 3.2 Service Boundaries and Database Sharing

All services share a **single PostgreSQL database**. FastAPI loads the Django project settings and ORM directly — this avoids duplicating models and keeps migrations in one place while still allowing the real-time service to evolve independently.

| Service | Technology / Notes |
|---|---|
| **Django API Gateway** | DRF · all REST endpoints · Token auth · Admin panel |
| **FastAPI Realtime** | WebSocket chat + notifications · loads Django ORM · Redis pub/sub |
| **Celery Workers** | Async tasks: embeddings, AI calls, alarm matching, notification delivery |
| **AI Service** (within Django) | OpenRouter router · RAG pipeline · MCP tools layer · Admin-configurable |
| **Search Service** (within Django) | pgvector embeddings in PostgreSQL · replaces Algolia |
| **PostgreSQL** | Single DB · all models · pgvector extension enabled |
| **Redis** | Celery result backend · FastAPI channel layer |
| **RabbitMQ** | Celery broker · advanced message routing |

---

### 3.3 Model Migration Strategy

Models are moved from the monolithic `apps/models.py` into their respective service folders. Django migrations are regenerated from scratch on a clean database. Existing data can be preserved using data migrations or a dump/restore cycle.
0. Use uv to create venv 
1. Create each service app: `uv run manage.py startapp <name> services/<name>`
2. Move the relevant model classes from `apps/models.py` into `services/<name>/models.py`
3. Update all import paths across views, serializers, signals, and admin files
4. Delete `apps/models.py` after all models are migrated
5. Run `makemigrations` for each service app individually
6. Run `migrate` on a clean database to verify integrity
7. Write a data migration script if preserving existing SQLite data

---

## 4. AI Architecture

The AI layer is built around four interlocking components: an **admin-configurable LLM provider system**, an **OpenRouter-based model router**, a **RAG pipeline** backed by pgvector, and an **MCP tool layer** that gives the AI controlled access to platform data without touching the database directly.

---

### 4.1 Admin-Configurable LLM Models

A new Django app (`services/ai/`) introduces database models that allow the developer to create, enable, disable, and swap LLM providers and prompt templates from the Django Admin panel — **no code deployments needed**.

#### `LLMProvider` model

| Field | Description |
|---|---|
| `name` | Human label, e.g. `"Claude 3.5 Sonnet"` |
| `model_id` | OpenRouter model string, e.g. `"anthropic/claude-3.5-sonnet"` |
| `task_type` | Choices: `description_gen`, `price_reasoning`, `chat`, `search`, `embedding` |
| `is_active` | Toggle on/off from Admin without code change |
| `priority` | Integer — router picks the highest-priority active model per task type |
| `max_tokens` | Per-model token budget |
| `temperature` | Float — configurable from Admin |
| `fallback_model` | ForeignKey to self — used if primary model fails or is rate-limited |

#### `PromptTemplate` model

| Field | Description |
|---|---|
| `name` | Template identifier, e.g. `"property_description_v2"` |
| `task_type` | Links to the same task_type choices as `LLMProvider` |
| `system_prompt` | TextField — editable from Admin |
| `user_prompt_template` | TextField with `{variable}` placeholders |
| `is_active` | Active flag |
| `version` | Integer — increment on edit, old versions preserved |

#### `MCPTool` model

| Field | Description |
|---|---|
| `name` | Tool name, e.g. `"get_property_details"` |
| `description` | Used in the LLM tool call schema |
| `is_enabled` | Toggle from Admin |
| `allowed_user_types` | JSONField — which user roles may trigger this tool |
| `rate_limit_per_minute` | IntegerField — prevent abuse |

---

### 4.2 OpenRouter LLM Router

The router (`services/ai/router.py`) selects the correct model for a task by querying `LLMProvider` where `task_type` matches and `is_active` is `True`, ordered by `priority`. All calls go through OpenRouter's unified API — **switching models requires only an Admin panel change**, never a code deploy.

```python
# services/ai/router.py — simplified
def get_model_for_task(task_type: str) -> LLMProvider:
    return LLMProvider.objects.filter(
        task_type=task_type, is_active=True
    ).order_by('-priority').first()


def call_llm(task_type: str, messages: list, tools: list = None) -> dict:
    provider = get_model_for_task(task_type)
    template = PromptTemplate.objects.filter(
        task_type=task_type, is_active=True
    ).order_by('-version').first()

    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )
    return client.chat.completions.create(
        model=provider.model_id,
        messages=messages,
        tools=tools,
        max_tokens=provider.max_tokens,
        temperature=provider.temperature,
    )
```

---

### 4.3 RAG Pipeline (pgvector)

Property listings, reviews, and market data are embedded using a text embedding model routed through OpenRouter. Vectors are stored in PostgreSQL using the pgvector extension. At query time, the user's question is embedded and a cosine similarity search retrieves the most relevant context, which is then injected into the LLM prompt.

| Pipeline Step | Implementation |
|---|---|
| **1. Document ingestion** | Celery task: `workers/tasks/embeddings.py` — triggered on `Property` post_save |
| **2. Text preparation** | Property fields concatenated: name + description + features + address |
| **3. Embedding generation** | OpenRouter embedding model (`task_type='embedding'`) via `LLMProvider` |
| **4. Vector storage** | pgvector `VectorField` on `PropertyEmbedding` model in `services/search/` |
| **5. Query embedding** | User question embedded at query time using the same model |
| **6. Similarity search** | PostgreSQL `cosine_distance` query — top K results |
| **7. Context injection** | Retrieved property data injected into `PromptTemplate` as `{context}` |
| **8. LLM response** | OpenRouter call using `task_type='chat'` model with injected context |

#### `PropertyEmbedding` model (`services/search/models.py`)

```python
from pgvector.django import VectorField

class PropertyEmbedding(models.Model):
    property    = models.OneToOneField(Property, on_delete=models.CASCADE)
    embedding   = VectorField(dimensions=1536)   # match your embedding model output
    embedded_text = models.TextField()           # source text — useful for debugging
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [HnswIndex(
            name='property_embedding_idx',
            fields=['embedding'],
            m=16, ef_construction=64,
            opclasses=['vector_cosine_ops']
        )]
```

---

### 4.4 MCP Tool Layer

The AI system **must never query the database directly**. All data access is routed through registered MCP tools. Each tool is a Python function in `services/ai/tools.py` and is exposed to the LLM via the OpenRouter tool_choice API. Tools are enabled/disabled at runtime from the Admin panel via the `MCPTool` model.

| Tool Name | Description / Data Returned |
|---|---|
| `get_property_details` | Property name, price, features, address, images |
| `search_properties` | Vector similarity search — returns top N matching properties |
| `get_market_statistics` | Avg price per m², listing counts by category and state |
| `get_seller_performance` | Listing count, avg rating, response rate for a seller |
| `get_property_reviews` | Latest reviews and average rating for a property |
| `get_price_estimate` | LLM-based price reasoning given property attributes |
| `get_category_trends` | Most viewed/favorited categories in the last 30 days |
| `search_by_alarm_criteria` | Properties matching a user's saved alarm filters |

> **⚠️ Security Rule** — Tools never return raw foreign keys, internal IDs, private messages, or personal user data (email, phone, device token). All tool outputs are sanitized before being passed to the LLM. Private messages must never appear in any prompt.

---

## 5. Search — pgvector Replaces Algolia

Algolia is removed entirely. The `services/search/` app provides both **keyword search** (PostgreSQL full-text search) and **semantic/vector search** (pgvector), keeping all data inside the existing database with no external dependency or per-query billing.

### 5.1 Migration from Algolia

- Remove `algoliasearch`, `algoliasearch-django` from `requirements.txt`
- Delete the `ALGOLIA` settings block from `base.py`
- Remove `algolia_serializers.py` and all references to it
- Remove the `algolia_reindex` and `algolia_applysettings` commands from documentation
- Enable the pgvector PostgreSQL extension: `CREATE EXTENSION IF NOT EXISTS vector;`
- Install the pgvector Python package: `pip install pgvector`

### 5.2 Search Service Architecture

| Search Type | Implementation |
|---|---|
| **Keyword search** | PostgreSQL `SearchVector` on `name` + `description` fields |
| **Semantic search** | pgvector cosine similarity on `PropertyEmbedding.embedding` |
| **Hybrid search** | Keyword results re-ranked by vector similarity score |
| **Filter + search** | Pre-filter by category, price, state, `for_sale`/`for_rent`, then search |
| **Autocomplete** | PostgreSQL trigram similarity (`pg_trgm` extension) on property name |

### 5.3 Embedding Update Strategy

Embeddings stay in sync with property data via Django signals and Celery tasks:

1. `Property` post_save signal enqueues `embed_property` Celery task
2. Task generates the embedding via OpenRouter and upserts `PropertyEmbedding`
3. A `regenerate_embeddings` management command allows bulk re-embedding after model changes

---

## 6. FastAPI Realtime Service

The Django Channels implementation is replaced by a standalone FastAPI application that handles WebSocket connections for chat and notifications. It shares the same PostgreSQL database by **importing Django's ORM models directly** after configuring the Django settings module.

### 6.1 Setup Pattern

```python
# realtime/main.py
import django, os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.production')
django.setup()

from fastapi import FastAPI
from .consumers.chat import chat_router
from .consumers.notifications import notification_router

app = FastAPI()
app.include_router(chat_router)
app.include_router(notification_router)
```

### 6.2 WebSocket Endpoints

| Endpoint | Description |
|---|---|
| `ws://host/ws/chat/{room_id}/` | Private chat room — requires token auth |
| `ws://host/ws/notifications/` | User notification stream — requires token auth |

### 6.3 Channel Layer

Redis pub/sub is used as the channel layer for inter-process message delivery. This replaces `InMemoryChannelLayer` (which only works with a single process) and is required for any multi-worker production deployment.

```python
# Environment variable
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
```

### 6.4 Authentication

The `TokenAuthMiddleware` from the existing codebase is ported to FastAPI. The token is read from the `Authorization` header or the `token` query parameter and validated against the DRF `Token` model via the Django ORM.

```python
# realtime/auth.py
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

async def get_user_from_token(token_key: str | None):
    if not token_key:
        return AnonymousUser()
    try:
        token = await Token.objects.select_related('user').aget(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()
```

---

## 7. Background Processing — Celery

Celery workers are enabled from **Phase 1**. The commented-out `celery` and `rabbitmq` services in `docker-compose.yml` are uncommented and configured. The duplicate `CELERY_BEAT_SCHEDULE` definitions in `base.py` are consolidated into a single correct configuration.

### 7.1 Task Registry

| Task | Trigger | Queue |
|---|---|---|
| `embed_property` | `Property` post_save signal | `embeddings` |
| `match_alarms` | `Property` post_save signal | `alarms` |
| `send_push_notification` | `Notification` post_save | `notifications` |
| `send_email_notification` | `Notification` post_save | `notifications` |
| `generate_property_description` | Manual / seller request via API | `ai` |
| `price_estimate` | Manual / seller request via API | `ai` |
| `update_banner_status` | Celery beat — every 60 seconds | `default` |
| `update_property_state` | Celery beat — every 10 minutes | `default` |
| `rag_index_refresh` | Celery beat — nightly | `embeddings` |

### 7.2 Celery Configuration (Corrected)

```python
# core/settings/base.py — single correct Celery config
CELERY_BROKER_URL    = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672/')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

CELERY_TASK_ROUTES = {
    'workers.tasks.embeddings.*':    {'queue': 'embeddings'},
    'workers.tasks.ai_tasks.*':      {'queue': 'ai'},
    'workers.tasks.notifications.*': {'queue': 'notifications'},
}

CELERY_BEAT_SCHEDULE = {
    'update-banner-status': {
        'task':     'workers.tasks.alarms.update_banner_status',
        'schedule': 60.0,
    },
    'update-property-state': {
        'task':     'workers.tasks.alarms.update_property_state',
        'schedule': 600.0,
    },
    'rag-index-refresh': {
        'task':     'workers.tasks.embeddings.rag_index_refresh',
        'schedule': crontab(hour=2, minute=0),   # nightly at 02:00
    },
}
```

---

## 8. Docker Compose — Full Service Stack

The `docker-compose.yml` is updated to include all services. All commented-out services are uncommented and properly configured. Environment variables replace all hardcoded values.

| Service | Image / Notes |
|---|---|
| `postgres` | `postgres:16-alpine` · pgvector extension enabled at container startup |
| `redis` | `redis:7-alpine` · Celery result backend + FastAPI channel layer |
| `rabbitmq` | `rabbitmq:3-management` · Celery broker |
| `django` | Custom Dockerfile · gunicorn in production · runs migrations on startup |
| `realtime` | Custom Dockerfile · uvicorn FastAPI app · loads Django ORM |
| `celery_worker` | Same image as Django · `celery worker -Q default,embeddings,ai,notifications` |
| `celery_beat` | Same image as Django · `celery beat` · scheduled tasks only |
| `flower` | `mher/flower` · Celery monitoring UI at port 5555 |
| `nginx` | `nginx:alpine` · reverse proxy for Django + FastAPI + static/media files |

### 8.1 Startup Entrypoint

The Django container entrypoint (`entrypoint.sh`) is updated to:

1. Wait for PostgreSQL to be ready
2. Run `CREATE EXTENSION IF NOT EXISTS vector;` if not already present
3. Run `uv run manage.py migrate`
4. Run `uv run manage.py collectstatic --noinput`
5. Start gunicorn (production) or `runserver` (local)

---

## 9. CI/CD — GitHub Actions

Two workflow files are created in `.github/workflows/`. The CI workflow runs on every push and pull request. The deploy workflow runs only on merges to `main`.

### 9.1 CI Workflow (`ci.yml`)

| Step | Action |
|---|---|
| Checkout | `actions/checkout@v4` |
| Setup Python | `actions/setup-python@v5` — Python 3.11 |
| Install deps | `pip install -r requirements.txt` |
| Lint | `flake8 services/ core/ workers/ realtime/` |
| Format check | `black --check services/ core/ workers/` |
| Security scan | `bandit -r services/` — fail on high severity |
| Run tests | `pytest --cov=services --cov-report=xml` |
| Coverage gate | Fail if coverage < 60% |
| Upload report | `codecov/codecov-action` (optional) |

### 9.2 Deploy Workflow (`deploy.yml`)

| Step | Action |
|---|---|
| Trigger | On push to `main` branch only |
| Build images | `docker build` for django, realtime, celery_worker |
| Push to registry | GitHub Container Registry (`ghcr.io`) |
| SSH deploy | `appleboy/ssh-action` — pull new images, `docker-compose up -d` |
| Run migrations | `docker exec django python manage.py migrate` |
| Health check | `curl` the `/api/health/` endpoint — fail deploy if unhealthy |
| Notify | Slack or email notification on success/failure |

### 9.3 Required GitHub Secrets

```
DJANGO_SECRET_KEY
DATABASE_URL
REDIS_URL
RABBITMQ_URL
OPENROUTER_API_KEY
EMAIL_HOST_PASSWORD
FIREBASE_CREDENTIALS_JSON
SSH_HOST
SSH_USER
SSH_KEY
SLACK_WEBHOOK_URL        # optional
```

---

## 10. Phased Migration Roadmap

The migration is broken into 5 phases. Each phase must be complete and stable before the next begins.

---

### 🔴 Phase 0 — Security Fixes *(1–2 weeks)*

> **Gate:** All items below must be merged and deployed before Phase 1 begins.

- [ ] Rotate all leaked credentials (email password, SECRET_KEY)
- [x] Remove `db1.sqlite3` from git history (`git filter-repo` or `BFG`)
- [ ] Move all secrets to environment variables + create `.env.example`
- [ ] Fix OTP system — store in DB, never return in response, add 10-minute expiry
- [ ] Fix password reset — generate cryptographic token, add 15-minute expiry, single-use
- [ ] Set `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]`
- [ ] Fix `Banner.__str__` (remove `save()` call)
- [ ] Fix `CustomBannerManager()` (add parentheses)
- [ ] Fix `Property.save()` — `self.unique_no` → `self.unique_number`
- [ ] Fix bare `except:` blocks (3 locations in `models.py`)
- [ ] Activate PostgreSQL in `production.py`
- [ ] Set `ALLOWED_HOSTS` and `CORS_ORIGIN_WHITELIST` to real values

---

### 🟠 Phase 1 — Infrastructure & CI/CD *(1–2 weeks)*

- [ ] Uncomment and configure Celery + RabbitMQ in `docker-compose.yml`
- [ ] Fix `CELERY_BEAT_SCHEDULE` — remove duplicate definition, point to real task paths
- [ ] Configure Redis channel layer (replace `InMemoryChannelLayer`)
- [ ] Set up GitHub Actions `ci.yml` and `deploy.yml`
- [ ] Write first unit tests for authentication flows (register, OTP verify, login)
- [ ] Add `/api/health/` endpoint for deploy health checks
- [ ] Enable pgvector extension in PostgreSQL init script
- [ ] Verify all services start cleanly with `docker-compose up`

---

### 🔵 Phase 2 — Project Restructure *(2–3 weeks)*

- [ ] Create each service app under `services/` using `startapp`
- [ ] Move models from `apps/models.py` into their respective service
- [ ] Update all imports, signals, serializers, and admin registrations
- [ ] Regenerate migrations — verify with `pytest`
- [ ] Delete `apps/models.py` (after 100% of models migrated)
- [ ] Remove empty sub-app model stubs (`property/models.py`, `users/models.py`, etc.)
- [ ] Remove Algolia: uninstall packages, delete `algolia_serializers.py`, remove settings block
- [ ] Implement pgvector `PropertyEmbedding` model in `services/search/`
- [ ] Write `embed_property` Celery task in `workers/tasks/embeddings.py`
- [ ] Wire up `post_save` signal on `Property` to enqueue embedding task
- [ ] Write `regenerate_embeddings` management command
- [ ] Achieve ≥ 60% test coverage across all services

---

### 🟢 Phase 3 — FastAPI Realtime Service *(1–2 weeks)*

- [ ] Create `realtime/` FastAPI app with `django.setup()` bootstrap
- [ ] Port `TokenAuthMiddleware` to FastAPI dependency
- [ ] Port `ChatConsumer` to FastAPI WebSocket router
- [ ] Port `NotificationConsumer` to FastAPI WebSocket router
- [ ] Remove `daphne` and `channels` from `requirements.txt`
- [ ] Remove `channels` from `INSTALLED_APPS`
- [ ] Add `realtime` service to `docker-compose.yml`
- [ ] Update nginx config to proxy `/ws/` requests to FastAPI service
- [ ] Integration test: WebSocket connect → join room → send message → receive → disconnect

---

### 🟣 Phase 4 — AI Layer *(2–3 weeks)*

- [ ] Create `services/ai/` app
- [ ] Implement `LLMProvider`, `PromptTemplate`, `MCPTool` models + admin registrations
- [ ] Build OpenRouter-based LLM router (`services/ai/router.py`)
- [ ] Register all MCP tools in `services/ai/tools.py`
- [ ] Implement RAG pipeline: `embed → retrieve → inject → respond`
- [ ] Add AI REST endpoints:
  - `POST /api/ai/price-estimate/`
  - `POST /api/ai/generate-description/`
  - `POST /api/ai/chat/` (conversational property search)
  - `GET  /api/ai/recommendations/` (personalized property recommendations)
- [ ] Build Admin views for managing providers, templates, and tools
- [ ] Confirm no private user data reaches LLM prompts (audit all tool outputs)

---

### ⚪ Phase 5 — Optimization & Observability *(ongoing)*

- [ ] Add Sentry for error tracking (Django + FastAPI + Celery)
- [ ] Add Prometheus metrics endpoint for Django and FastAPI
- [ ] Add Grafana dashboard for Celery worker health + task throughput
- [ ] Implement API rate limiting (`django-ratelimit` or custom middleware)
- [ ] Add Redis caching layer for expensive property queries
- [ ] Performance audit — identify N+1 queries, add `select_related`/`prefetch_related`
- [ ] Scale test — verify Celery workers scale horizontally under load
- [ ] Add `HnswIndex` on `PropertyEmbedding` for faster vector search at scale

---

## 11. Testing Strategy

The current codebase has **zero test coverage**. Tests are written in parallel with the Phase 2 restructure. Minimum coverage target for production: **70%**.

| Test Layer | What to Cover | Priority |
|---|---|---|
| Unit — models | `Property.save()`, `User.delete()`, `Banner.clean()`, `VerificationCode` expiry | Phase 0 |
| Unit — auth views | OTP generation/verification, password reset token flow | Phase 0 |
| Unit — property views | CRUD, filter endpoint, attribute value update | Phase 2 |
| Unit — search | pgvector similarity returns ranked results | Phase 2 |
| Integration — chat | WebSocket connect/join/send/leave cycle via FastAPI test client | Phase 3 |
| Integration — Celery | `embed_property` task generates and stores a vector | Phase 2 |
| Integration — AI tools | `get_property_details` returns sanitized data (no private fields) | Phase 4 |
| E2E — register flow | Register → verify OTP → login → get token | Phase 1 |
| E2E — property listing | Create property → embedding generated → search returns it | Phase 2 |

**Test stack:** `pytest` + `pytest-django` + `pytest-asyncio` + `factory_boy` (fixtures) + `coverage`

---

## 12. Constraints & Principles

| Constraint | Detail |
|---|---|
| **Backward API compatibility** | All existing REST endpoint paths and response shapes are preserved throughout the migration. Mobile/web clients must continue working without modification. |
| **Incremental migration** | No big-bang rewrites. Each phase is independently deployable and reversible. |
| **Single database** | One PostgreSQL instance with pgvector. No per-service databases until scale demands it. |
| **AI data isolation** | The AI layer accesses data only through registered MCP tools. Direct ORM queries from AI code are forbidden. |
| **No private data in LLM prompts** | Private messages, email addresses, phone numbers, and device tokens are never included in prompts or tool responses. |
| **Admin-configurable AI** | All LLM model selection, prompt templates, and tool enabling must be manageable from the Django Admin panel without code changes or restarts. |
| **Deployment target agnostic** | The docker-compose stack must run identically on a VPS, EC2 instance, or any Docker-compatible host. |
| **Migrations committed to git** | Remove `migrations/` from `.gitignore`. All migration files are committed so all environments stay in sync. |

---

## 13. Success Metrics

| Metric | Target |
|---|---|
| Zero critical security vulnerabilities | All Phase 0 items resolved before Phase 1 begins |
| Test coverage | ≥ 70% by end of Phase 2 |
| API response time (p95) | < 300ms for property list and search endpoints |
| WebSocket connection stability | < 1% disconnect rate under 100 concurrent users |
| Embedding freshness | Embeddings updated within 60 seconds of property save |
| CI pipeline duration | < 5 minutes for full test + lint run |
| AI tool response time (p95) | < 3 seconds for property description generation |
| Search relevance | Top 3 results contain the expected property in > 80% of test queries |
| Zero data leaks via AI | Audit confirms no private fields appear in any LLM prompt or tool response |

---

## Appendix A — Dependency Changes

### A.1 Remove

| Package | Reason |
|---|---|
| `algoliasearch`, `algoliasearch-django` | Replaced by pgvector |
| `daphne` | Replaced by uvicorn (FastAPI service) |
| `channels`, `channels-redis` | Replaced by FastAPI WebSocket + Redis directly |
| `django-crontab` | Replaced by Celery beat |
| `autobahn`, `Twisted`, `txaio` | Pulled in by old channels/daphne stack |
| `django-rest-framework` (the `0.1.0` stub) | Use `djangorestframework==3.14.0` only |

### A.2 Add

| Package | Purpose |
|---|---|
| `pgvector` | PostgreSQL vector extension Python client |
| `fastapi` | Realtime WebSocket service framework |
| `uvicorn[standard]` | ASGI server for FastAPI |
| `httpx` | Async HTTP client for OpenRouter calls in FastAPI |
| `openai` | OpenRouter-compatible client (OpenRouter uses the OpenAI SDK) |
| `pytest`, `pytest-django`, `pytest-asyncio` | Test framework |
| `factory-boy` | Test fixture generation |
| `coverage` | Test coverage reporting |
| `bandit` | Security linting |
| `flake8`, `black` | Code quality / formatting |
| `sentry-sdk` | Error tracking (Phase 5) |

### A.3 Retain (confirmed necessary)

| Package | Purpose |
|---|---|
| `celery`, `kombu`, `billiard` | Background processing |
| `djangorestframework`, `drf-spectacular` | REST API + OpenAPI docs |
| `django-filter`, `django-cors-headers` | Filtering + CORS |
| `django-mptt` | Category tree |
| `firebase-admin` | Push notifications |
| `Pillow` | Image processing |
| `psycopg2` | PostgreSQL driver |
| `python-dotenv` | Environment variables |
| `PyJWT` | Token operations |
| `redis` | Redis Python client |
| `scikit-learn`, `joblib` | Retained until LLM-based pricing (Phase 4) replaces it |

---

*End of PRD v2.0 — Real Estate Platform Modernization*
