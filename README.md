# AI-Powered Real Estate Platform - Backend Architecture

<p align="center">
  <img src="https://img.shields.io/badge/Django-4.2.5-green?style=for-the-badge&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/FastAPI-0.104.0-blue?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-7.0-red?style=for-the-badge&logo=redis" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-24.0-blue?style=for-the-badge&logo=docker" alt="Docker">
</p>

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Services](#services)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [LLM Providers](#llm-providers)
- [Development Roadmap](#development-roadmap)

---

## 🌟 Overview

This is a modernized real estate backend platform built with a microservices architecture. The system combines Django as an API Gateway with FastAPI services for AI and real-time workloads, featuring:

- **AI-Powered Features**: Property price prediction, description generation, recommendations, and conversational AI assistant
- **Real-time Communication**: WebSocket-based chat and notifications
- **Advanced Search**: Elasticsearch-powered property search
- **Background Processing**: Celery workers for async tasks
- **Vector Search**: RAG (Retrieval Augmented Generation) for AI assistant

---

## 🏗️ Architecture

```
                          ┌─────────────────┐
                          │   Mobile/Web    │
                          │    Clients      │
                          └────────┬────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │      NGINX      │
                          │ Reverse Proxy   │
                          └────────┬────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │    Django API Gateway        │
                    │   (Port 8000)                │
                    │   - REST API                 │
                    │   - Auth                     │
                    │   - Property Management      │
                    └──────────────┬───────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌─────────────────┐       ┌───────────────┐
│  AI Service  │         │ Realtime Service│       │Search Service │
│ (FastAPI)    │         │  (FastAPI WS)   │       │(FastAPI)      │
│  Port 8001   │         │    Port 8002    │       │  Port 8003    │
└──────┬────────┘         └────────┬────────┘       └───────┬───────┘
       │                           │                        │
       ▼                           ▼                        ▼
┌──────────────┐          ┌─────────────────┐      ┌───────────────┐
│ RAG Engine   │          │   Redis Pub/Sub │      │ Elasticsearch  │
│ Vector Store │          │                 │      │               │
└──────┬───────┘          └─────────────────┘      └───────────────┘
       │
       ▼
┌──────────────┐
│ LLM Router   │
│ - OpenAI     │
│ - Anthropic  │
│ - Ollama     │
│ - HuggingFace│
│ - Cohere     │
│ - Groq       │
└──────────────┘

        ┌─────────────────────────────────────────────────────────┐
        │                   Celery Workers                        │
        │  - AI Processing     - Embedding Generation            │
        │  - Notifications     - Recommendation Updates          │
        └─────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
           ┌───────────────┐            ┌───────────────┐
           │    RabbitMQ   │            │     Redis     │
           │    (Broker)   │            │(Result Backend)│
           └───────────────┘            └───────────────┘
                    │
                    ▼
           ┌───────────────┐
           │   PostgreSQL  │
           │   (Database)  │
           └───────────────┘
```

---

## 🛠️ Technologies

### Core Frameworks

| Technology                | Version | Purpose                                      |
| ------------------------- | ------- | -------------------------------------------- |
| **Django**                | 4.2.5   | API Gateway, REST API, ORM, Authentication   |
| **Django REST Framework** | 3.14.0  | REST API development                         |
| **FastAPI**               | 0.104.0 | AI Service, Realtime Service, Search Service |
| **Uvicorn**               | 0.24.0  | ASGI server for FastAPI                      |
| **Celery**                | 5.3.4   | Background task processing                   |
| **Daphne**                | 4.0.0   | ASGI server for Django Channels              |

### Databases & Message Queues

| Technology        | Version | Purpose                                          |
| ----------------- | ------- | ------------------------------------------------ |
| **PostgreSQL**    | 14+     | Primary relational database                      |
| **Redis**         | 7.0     | Caching, Session storage, Pub/Sub, Celery broker |
| **RabbitMQ**      | 3.12+   | Message broker for Celery (alternative to Redis) |
| **Elasticsearch** | 8.x     | Full-text search engine for properties           |

### AI & Machine Learning

| Technology        | Purpose                                   |
| ----------------- | ----------------------------------------- |
| **OpenAI API**    | GPT models for advanced AI tasks (paid)   |
| **Anthropic API** | Claude models for AI tasks (paid)         |
| **Ollama**        | Local LLM deployment (FREE)               |
| **HuggingFace**   | Free inference API for open-source models |
| **Cohere**        | Enterprise AI platform with free tier     |
| **Groq**          | Fast AI inference with free tier          |
| **LangChain**     | LLM orchestration and chaining            |
| **pgvector**      | Vector similarity search in PostgreSQL    |

### Real-time Communication

| Technology          | Purpose                                     |
| ------------------- | ------------------------------------------- |
| **WebSocket**       | Bidirectional real-time communication       |
| **Django Channels** | Original WebSocket support (being migrated) |
| **Redis Pub/Sub**   | Message broadcasting for WebSockets         |

### Authentication & Security

| Technology              | Purpose                             |
| ----------------------- | ----------------------------------- |
| **JWT**                 | JSON Web Token authentication       |
| **Firebase Admin**      | Firebase authentication integration |
| **django-cors-headers** | Cross-origin resource sharing       |
| **python-dotenv**       | Environment variable management     |

### DevOps & Infrastructure

| Technology         | Purpose                       |
| ------------------ | ----------------------------- |
| **Docker**         | Containerization              |
| **Docker Compose** | Multi-container orchestration |
| **NGINX**          | Reverse proxy, load balancer  |
| **Gunicorn**       | WSGI server for Django        |
| **Flower**         | Celery task monitoring        |

### Additional Libraries

| Category               | Libraries                     |
| ---------------------- | ----------------------------- |
| **API Documentation**  | drf-spectacular, Swagger UI   |
| **Data Validation**    | Pydantic, email-validator     |
| **Image Processing**   | Pillow (PIL)                  |
| **Data Import/Export** | django-import-export          |
| **Search**             | django-filter, Algolia        |
| **Logging**            | structlog, python-json-logger |
| **Testing**            | pytest, pytest-django         |

---

## 📁 Project Structure

```
backend/
│
├── gateway/                          # Django API Gateway
│   └── django_api/
│       ├── apps/                      # Django applications
│       │   ├── users/                 # User management
│       │   ├── properties/            # Property CRUD
│       │   ├── reviews/                # Property reviews
│       │   ├── chat/                  # Chat functionality
│       │   └── notifications/          # Push notifications
│       ├── core/                      # Django settings
│       │   ├── settings.py
│       │   └── urls.py
│       ├── services/                  # Business logic
│       └── repositories/              # Data access layer
│
├── services/                         # Microservices
│   │
│   ├── ai-service/                   # AI Processing Service
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── assistant.py      # RAG-powered AI assistant
│   │   │       ├── price_prediction.py
│   │   │       ├── descriptions.py
│   │   │       └── recommendations.py
│   │   ├── rag/
│   │   │   ├── vector_store.py       # Vector embeddings storage
│   │   │   └── retriever.py          # Context retrieval
│   │   ├── llm_router/
│   │   │   ├── router.py              # LLM provider routing
│   │   │   └── providers/
│   │   │       ├── openai_provider.py
│   │   │       └── anthropic_provider.py
│   │   ├── tools/                    # AI tools layer
│   │   │   ├── property_tools.py
│   │   │   ├── market_tools.py
│   │   │   └── seller_tools.py
│   │   └── main.py
│   │
│   ├── realtime-service/             # WebSocket Service
│   │   ├── fastapi_ws/
│   │   │   ├── websocket/
│   │   │   │   ├── chat.py           # Real-time chat
│   │   │   │   └── notifications.py  # Real-time notifications
│   │   │   ├── auth/
│   │   │   │   └── middleware.py     # WebSocket auth
│   │   │   └── dependencies/
│   │   └── main.py
│   │
│   └── search-service/               # Search Service
│       ├── api/
│       │   └── routes/
│       ├── indexer/                  # Property indexing
│       └── main.py
│
├── workers/                          # Celery Workers
│   ├── celery_app.py
│   └── tasks/
│       ├── ai_tasks.py               # AI processing tasks
│       ├── embedding_tasks.py        # Vector embedding tasks
│       ├── notification_tasks.py     # Notification delivery
│       └── recommendation_tasks.py   # Recommendation updates
│
├── infrastructure/                   # Infrastructure
│   ├── docker/
│   │   └── docker-compose.yml        # Full stack deployment
│   └── nginx/
│       └── nginx.conf                # Reverse proxy config
│
└── shared/                           # Shared Code
    ├── schemas/                      # Pydantic models
    │   ├── property.py
    │   ├── user.py
    │   ├── chat.py
    │   ├── notification.py
    │   └── ai.py
    └── utils/                        # Shared utilities
        ├── database.py
        ├── logging.py
        └── security.py
```

---

## 🔌 Services

### 1. Django API Gateway (Port 8000)

**Purpose**: Main REST API serving existing mobile/web applications

**Features**:
- User authentication (JWT + Firebase)
- Property CRUD operations
- Review and rating system
- Favorite properties
- Banner management
- Ticket/support system
- Alarm system for property alerts

**URL Patterns**:
- `/api/auth/` - Authentication
- `/api/property/` - Properties
- `/api/user/` - User profiles
- `/api/review/` - Reviews
- `/api/banners/` - Banners

---

### 2. AI Service (Port 8001)

**Purpose**: All AI-powered features using LLM routing

**Features**:

| Feature                    | Description                           | Endpoint                   |
| -------------------------- | ------------------------------------- | -------------------------- |
| **Price Prediction**       | LLM-based property price estimation   | `/api/ai/price-prediction` |
| **Description Generation** | AI-generated property descriptions    | `/api/ai/descriptions`     |
| **Recommendations**        | Personalized property recommendations | `/api/ai/recommendations`  |
| **AI Assistant**           | RAG-powered conversational assistant  | `/api/ai/assistant`        |

**RAG Pipeline**:
```
User Question → Embedding Generation → Vector Search (pgvector) → 
Relevant Context → LLM Response
```

---

### 3. Realtime Service (Port 8002)

**Purpose**: WebSocket-based real-time communication

**Features**:
- Real-time chat messaging
- Live notifications
- Connection status tracking
- Redis Pub/Sub for message broadcasting

**WebSocket Endpoints**:
- `ws://host:8002/chat/{room_id}/` - Chat rooms
- `ws://host:8002/notifications/` - Personal notifications

---

### 4. Search Service (Port 8003)

**Purpose**: Advanced property search with Elasticsearch

**Features**:
- Full-text search
- Faceted search (filters)
- Geospatial search
- Auto-complete suggestions
- Property indexing

---

### 5. Celery Workers

**Purpose**: Asynchronous background task processing

**Task Types**:

| Task                   | Description                               |
| ---------------------- | ----------------------------------------- |
| `ai_tasks`             | Generate descriptions, price predictions  |
| `embedding_tasks`      | Generate vector embeddings for properties |
| `notification_tasks`   | Send push/email notifications             |
| `recommendation_tasks` | Update user recommendations               |

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 14+
- Redis 7.0+

### Quick Start

1. **Clone the repository**
```
bash
git clone <repository-url>
cd realEstate-Project-v2/gateway
```

2. **Set up environment variables**
```
bash
# Create .env file
cp backend/infrastructure/.env.example backend/infrastructure/.env

# Edit with your API keys
nano backend/infrastructure/.env
```

3. **Start all services**
```
bash
cd backend/infrastructure/docker
docker-compose up -d
```

4. **Access the services**
- Django API: http://localhost:8000
- API Docs: http://localhost:8000/api/doc/
- AI Service: http://localhost:8001
- Realtime Service: http://localhost:8002
- Search Service: http://localhost:8003
- NGINX: http://localhost:80

---

## 📡 API Endpoints

### Django Gateway

```
bash
# Authentication
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/refresh/

# Properties
GET    /api/property/
POST   /api/property/
GET    /api/property/{id}/
PUT    /api/property/{id}/
DELETE /api/property/{id}/

# Reviews
GET /api/review/
POST /api/review/

# Favorites
POST   /api/property/{id}/favorite/
DELETE /api/property/{id}/favorite/
```

### AI Service

```
bash
# Price Prediction
POST /api/ai/price-prediction
{
  "location": "New York, NY",
  "property_type": "apartment",
  "size": 1200,
  "rooms": 3,
  "bathrooms": 2,
  "amenities": ["parking", "gym"]
}

# Description Generation
POST /api/ai/descriptions
{
  "property_id": 123,
  "style": "modern"
}

# Recommendations
POST /api/ai/recommendations
{
  "user_id": 456,
  "limit": 10
}

# AI Assistant (RAG)
POST /api/ai/assistant
{
  "message": "What are the best 2-bedroom apartments in Manhattan under $500k?"
}
```

---

## 🔐 Environment Variables

### Required Variables

```
bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=RealEstate
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345

# Redis
REDIS_URL=redis://redis:6379/0

# RabbitMQ (Optional - Redis is default broker)
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
```

### LLM Provider Variables

```
bash
# ==================== FREE PROVIDERS ====================

# Ollama (Local LLM - Completely Free)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# HuggingFace (Free Tier)
HUGGINGFACE_API_TOKEN=your_huggingface_token

# Cohere (Free Tier Available)
COHERE_API_KEY=your_cohere_key

# Groq (Free Tier Available)
GROQ_API_KEY=your_groq_key

# ==================== PAID PROVIDERS ====================

# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key
```

### Service-Specific Variables

```
bash
# AI Service
EMBEDDING_DIM=1536
VECTOR_DB_URL=postgresql://postgres:12345@postgres:5432/RealEstate

# Realtime Service
DJANGO_SECRET_KEY=your-django-secret
DJANGO_DB_URL=postgresql://postgres:12345@postgres:5432/RealEstate

# Search Service
ELASTICSEARCH_URL=http://elasticsearch:9200
```

---

## 🤖 LLM Providers

### Free Providers (Recommended for Development)

| Provider        | Model                 | Cost         | Setup Required |
| --------------- | --------------------- | ------------ | -------------- |
| **Ollama**      | llama2, mistral, qwen | Free (local) | Run locally    |
| **HuggingFace** | flan-t5-large, falcon | Free tier    | Get API token  |
| **Cohere**      | command-r-plus        | Free tier    | Get API key    |
| **Groq**        | mixtral-8x7b          | Free tier    | Get API key    |

### Paid Providers

| Provider      | Model                | Description         |
| ------------- | -------------------- | ------------------- |
| **OpenAI**    | gpt-4, gpt-3.5-turbo | Industry standard   |
| **Anthropic** | claude-3-opus        | Excellent reasoning |

### LLM Router

The system automatically routes requests to the best available provider:

```
python
# Task to Provider Priority Mapping
TASK_PROVIDER_MAP = {
    LLMTaskType.DESCRIPTION_GENERATION: [OLLAMA, HUGGINGFACE, OPENAI],
    LLMTaskType.PRICE_REASONING: [GROQ, COHERE, OLLAMA],
    LLMTaskType.CONVERSATIONAL_CHAT: [OLLAMA, HUGGINGFACE, OPENAI],
    LLMTaskType.ANALYTICS: [COHERE, GROQ, OLLAMA],
}
```

---

## 📅 Development Roadmap

### Stage 1: Infrastructure Setup
- [x] Redis integration
- [x] RabbitMQ integration
- [x] Celery workers
- [x] PostgreSQL configuration

### Stage 2: Realtime Migration
- [ ] Remove Django Channels
- [ ] Implement FastAPI WebSocket service
- [ ] Set up Redis Pub/Sub

### Stage 3: AI Services
- [ ] Price prediction system
- [ ] Description generation
- [ ] Recommendation engine
- [ ] Vector embeddings

### Stage 4: AI Assistant
- [ ] RAG system implementation
- [ ] Embedding generation
- [ ] Vector search (pgvector)
- [ ] Admin analytics assistant

### Stage 5: Optimization & Scaling
- [ ] Service autoscaling
- [ ] Caching strategies
- [ ] Performance monitoring

---

## 📊 Success Metrics

- ✅ Increased property engagement
- ✅ Improved listing creation speed
- ✅ Better search relevance
- ✅ Higher conversion rates
- ✅ Improved user satisfaction

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 👥 Contributing

Please read the contributing guidelines before submitting pull requests.

---

## 📞 Support

For issues and questions, please open a GitHub issue or contact the development team.

---

<p align="center">
  Built with ❤️ using Django, FastAPI, and Modern AI Technologies
</p>
