# Implementation Plan

[Overview]
Refactor the existing monolithic Django real estate project into a microservice-ready architecture with separate AI, Realtime, and Search services, while maintaining backward compatibility with existing APIs.

This implementation transforms the current Django + Django Channels project into a hybrid architecture where Django acts as an API Gateway, FastAPI services handle AI and WebSocket workloads, and Celery handles background processing. The refactoring follows the PRD's folder architecture specification.

[Types]
The type system changes involve creating shared schemas across Django and FastAPI services:

**Shared Schemas (Pydantic models for cross-service communication):**
- `PropertySchema`: id, name, description, price, size, location, category, images, features
- `UserSchema`: id, email, name, user_type, profile_image
- `ChatMessageSchema`: id, room_id, sender_id, content, timestamp
- `NotificationSchema`: id, target_user_id, verb, content_type, object_id, read, timestamp
- `PropertySearchSchema`: query, filters, pagination, sort_by
- `AIRecommendationSchema`: user_id, property_ids, recommendation_type, confidence
- `PricePredictionSchema`: property_id, estimated_price, price_range, reasoning

**LLM Router Types:**
- `LLMTaskType`: enum (DESCRIPTION_GENERATION, PRICE_REASONING, CONVERSATIONAL_CHAT, ANALYTICS)
- `LLMProvider`: enum (OPENAI, ANTHROPIC, LOCAL)
- `LLMRequest`: task_type, prompt, context, model_preference
- `LLMResponse`: content, model_used, tokens_used, latency_ms

[Rationale]
The existing monolithic Django project needs to be restructured to support:
1. AI-powered features (price prediction, descriptions, recommendations)
2. Modern WebSocket service (replacing Django Channels with FastAPI)
3. Background processing with Celery
4. Gradual microservices migration

The refactoring maintains all existing APIs unchanged to ensure backward compatibility with mobile and web clients.

[Files]
**New Directory Structure to Create:**
```
backend/
├── gateway/
│   └── django_api/
│       ├── apps/
│       │   ├── users/
│       │   ├── properties/
│       │   ├── reviews/
│       │   ├── chat/
│       │   └── notifications/
│       ├── services/
│       ├── repositories/
│       └── core/
├── services/
│   ├── ai-service/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── price_prediction.py
│   │   │   │   ├── descriptions.py
│   │   │   │   ├── recommendations.py
│   │   │   │   └── assistant.py
│   │   │   └── main.py
│   │   ├── rag/
│   │   │   ├── vector_store.py
│   │   │   ├── document_loader.py
│   │   │   └── retriever.py
│   │   ├── llm_router/
│   │   │   ├── router.py
│   │   │   ├── providers/
│   │   │   │   ├── openai_provider.py
│   │   │   │   └── anthropic_provider.py
│   │   │   └── prompts/
│   │   │       ├── price_prediction.py
│   │   │       ├── description.py
│   │   │       └── assistant.py
│   │   ├── tools/
│   │   │   ├── property_tools.py
│   │   │   ├── market_tools.py
│   │   │   └── seller_tools.py
│   │   └── requirements.txt
│   ├── realtime-service/
│   │   ├── fastapi_ws/
│   │   │   ├── main.py
│   │   │   ├── websocket/
│   │   │   │   ├── chat.py
│   │   │   │   └── notifications.py
│   │   │   ├── auth/
│   │   │   │   └── middleware.py
│   │   │   └── dependencies/
│   │   │       └── database.py
│   │   └── requirements.txt
│   └── search-service/
│       ├── api/
│       │   └── routes/
│       │       └── search.py
│       ├── indexer/
│       └── requirements.txt
├── workers/
│   ├── celery_app.py
│   └── tasks/
│       ├── ai_tasks.py
│       ├── embedding_tasks.py
│       ├── notification_tasks.py
│       └── recommendation_tasks.py
├── infrastructure/
│   ├── docker/
│   │   ├── ai-service/
│   │   │   └── Dockerfile
│   │   ├── realtime-service/
│   │   │   └── Dockerfile
│   │   └── workers/
│   │       └── Dockerfile
│   └── nginx/
│       └── nginx.conf
└── shared/
    ├── schemas/
    │   ├── property.py
    │   ├── user.py
    │   ├── chat.py
    │   ├── notification.py
    │   └── ai.py
    └── utils/
        ├── database.py
        ├── logging.py
        └── security.py
```

**Existing Files to Modify:**
- `core/core/asgi.py`: Remove Django Channels, update to route to FastAPI realtime service
- `core/core/settings/base.py`: Add Celery with RabbitMQ, update Redis config
- `core/docker-compose.yml`: Add new services (AI, Realtime, Workers)
- `core/requirements.txt`: Add FastAPI, Celery, vector DB clients

**Files to Migrate (from core/apps to gateway/django_api/apps):**
- `core/apps/users/` → `gateway/django_api/apps/users/`
- `core/apps/property/` → `gateway/django_api/apps/properties/`
- `core/apps/chat/` → `gateway/django_api/apps/chat/`
- `core/apps/notifications/` → `gateway/django_api/apps/notifications/`
- `core/apps/reviews/` → `gateway/django_api/apps/reviews/`

[Functions]
**New Functions to Create:**

**AI Service:**
- `generate_price_prediction(property_data: dict) -> PricePrediction`: Generate AI-powered price estimate
- `generate_property_description(property_data: dict) -> str`: Generate marketing description
- `get_recommendations(user_id: int, limit: int) -> list`: Get personalized property recommendations
- `process_rag_query(user_question: str, user_id: int) -> str`: RAG-powered AI assistant
- `route_llm_request(task_type: LLMTaskType, prompt: str) -> LLMResponse`: Route to appropriate LLM provider
- `search_vector_db(query_embedding: list, top_k: int) -> list`: Search vector database
- `get_property_tools()`: Return available tools for AI agents

**Realtime Service:**
- `handle_websocket_connection(websocket, token)`: Handle new WebSocket connections
- `handle_chat_message(room_id, message)`: Process incoming chat messages
- `broadcast_to_room(room_id, message)`: Broadcast message to room participants
- `send_notification(user_id, notification)`: Send real-time notification

**Celery Tasks:**
- `generate_property_embedding(property_id)`: Generate and store property embeddings
- `update_recommendations(user_id)`: Update user recommendation cache
- `process_ai_price_prediction(property_id)`: Async price prediction
- `send_push_notification(user_id, message)`: Send push notification
- `sync_property_to_search(property_id)`: Sync property to search index

**Modified Functions:**
- `core/core/asgi.py`: Update application to route WebSocket to FastAPI service
- `core/apps/chat/consumers.py`: Deprecate (moved to realtime-service)
- `core/apps/notifications/consumers.py`: Deprecate (moved to realtime-service)

[Classes]
**New Classes:**

**Shared Schemas:**
- `PropertySchema` (pydantic.BaseModel): Cross-service property representation
- `UserSchema` (pydantic.BaseModel): User data for AI services
- `LLMRequest/LLMResponse`: LLM communication schemas
- `ToolDefinition`: AI tool specification schema

**AI Service:**
- `LLMRouter`: Routes requests to appropriate LLM provider
- `OpenAIProvider`: OpenAI GPT integration
- `AnthropicProvider`: Anthropic Claude integration
- `VectorStore`: PostgreSQL vector search management
- `RAGEngine`: Retrieval Augmented Generation pipeline

**Realtime Service:**
- `WebSocketManager`: Manages active WebSocket connections
- `ChatManager`: Handles chat room logic
- `NotificationPusher`: Manages notification delivery

**Celery Tasks:**
- `AITask`: Base class for AI-related async tasks
- `EmbeddingTask`: Property embedding generation
- `RecommendationTask`: User recommendation updates

**Modified Classes:**
- `Property` (core/apps/models.py): Add embedding field, update save method
- `User` (core/apps/models.py): Add preferences field for recommendations
- `Notification` (core/apps/models.py): Add vector embedding for search

[Dependencies]
**New Python Packages:**

**AI Service:**
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- openai>=1.3.0
- anthropic>=0.18.0
- psycopg2-binary>=2.9.9
- sqlalchemy>=2.0.0
- tiktoken>=0.5.0
- python-dotenv>=1.0.0
- httpx>=0.25.0

**Realtime Service:**
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- redis>=5.0.0
- python-dotenv>=1.0.0
- pydantic>=2.5.0

**Celery Workers:**
- celery>=5.3.0
- kombu>=5.3.0
- billiard>=4.2.0
- vine>=5.1.0

**Search Service:**
- elasticsearch>=8.11.0
- huggingface-hub>=0.19.0
- sentence-transformers>=2.2.0

**Docker Services to Add:**
- rabbitmq:3.12-management (for Celery broker)
- qdrant (or use PostgreSQL with pgvector for vector storage)

[Testing]
**Test Files to Create:**

- `services/ai-service/tests/test_price_prediction.py`: Unit tests for price prediction
- `services/ai-service/tests/test_llm_router.py`: Test LLM routing logic
- `services/ai-service/tests/test_rag.py`: Test RAG pipeline
- `services/realtime-service/tests/test_websocket.py`: WebSocket connection tests
- `services/realtime-service/tests/test_chat.py`: Chat functionality tests
- `workers/tasks/tests/test_ai_tasks.py`: Celery task tests
- `workers/tasks/tests/test_embedding_tasks.py`: Embedding generation tests

**Test Strategy:**
- Use pytest for all test suites
- Mock external LLM APIs in unit tests
- Integration tests with PostgreSQL and Redis
- WebSocket tests with FastAPI TestClient

[Implementation Order]
**Phase 1: Infrastructure Setup (Week 1)**
1. Create the new folder structure
2. Set up PostgreSQL with pgvector extension
3. Configure RabbitMQ in docker-compose
4. Set up Celery with RabbitMQ broker
5. Create shared schemas and utilities

**Phase 2: Django Gateway Migration (Week 2)**
1. Migrate core apps to new structure
2. Update Django settings for Celery with RabbitMQ
3. Configure Redis for caching and pub/sub
4. Update ASGI to remove Django Channels

**Phase 3: Realtime Service (Week 3)**
1. Create FastAPI realtime service
2. Implement WebSocket connections
3. Set up Redis pub/sub for message broadcasting
4. Create authentication middleware
5. Connect to Django database for ORM access

**Phase 4: AI Service (Week 4-5)**
1. Create FastAPI AI service
2. Implement LLM router with OpenAI/Anthropic
3. Build RAG pipeline with vector search
4. Create tool layer for property data access
5. Implement price prediction endpoint
6. Implement description generation endpoint

**Phase 5: Search Service (Week 6)**
1. Create FastAPI search service
2. Implement property indexing
3. Set up Elasticsearch or PostgreSQL full-text search
4. Create search API endpoints

**Phase 6: Celery Workers (Week 7)**
1. Create Celery tasks for AI processing
2. Implement embedding generation tasks
3. Create recommendation update tasks
4. Set up periodic tasks for cache refresh

**Phase 7: Integration & Testing (Week 8)**
1. Integrate all services with NGINX
2. End-to-end testing
3. Performance optimization
4. Documentation

[Migration Notes]
- Maintain backward compatibility with existing API endpoints
- Use feature flags for gradual rollout
- Keep Django Channels until full migration verification
- Log all AI interactions for compliance
- Never expose private user data to AI models

