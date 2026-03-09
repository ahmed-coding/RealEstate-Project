# AI-Powered Real Estate Platform Modernization
## Product Requirements Document (PRD)

---

# 1. Executive Summary

This project aims to modernize the current real estate backend built with Django and Django REST Framework.

The system currently powers production mobile and web applications. The goal of this initiative is to introduce modern AI capabilities, scalable infrastructure, and microservice-ready architecture while maintaining full backward compatibility with existing APIs.

Key objectives:

- Introduce AI-powered features for buyers, sellers, and administrators.
- Replace the real-time system built with Django Channels with a modern WebSocket service using FastAPI.
- Introduce background processing with Celery using RabbitMQ and Redis.
- Implement AI capabilities using LLMs without requiring custom machine learning training.
- Transition gradually toward a microservices architecture.

---

# 2. Key Constraints

The following constraints must be respected:

1. Existing APIs must remain unchanged.
2. Current mobile and web applications must continue working without modification.
3. Migration must be incremental.
4. Sensitive user data must never be exposed to AI models.

---

# 3. High Level System Architecture

The system will adopt a hybrid architecture where Django acts as an API Gateway while new services handle AI and real-time workloads.

Clients (Mobile / Web)
│
NGINX
│
Django API Gateway (Existing APIs)
│
┌──────┼───────────────┐
│ │ │
AI Service Realtime Service Core Database
(FastAPI) (FastAPI WS) PostgreSQL
│ │
RAG Engine │
│ │
LLM Router │
│ │
Vector Database │
│ │
Celery Workers
│
RabbitMQ
│
Redis


This architecture allows the system to evolve without disrupting existing clients.

---

# 4. Microservices Migration Strategy

Migration will be gradual.

## Phase 1 – Infrastructure

Introduce:

- Redis
- RabbitMQ
- Celery Workers
- AI Service
- Realtime Service

## Phase 2 – Feature Extraction

Gradually extract:

- chat service
- notification service
- search service

## Phase 3 – Service Scaling

Services become independently scalable.

---

# 5. AI System Overview

The AI layer will provide intelligent capabilities for three groups of users.

## Sellers

Features:

- price recommendations
- property description generation
- listing optimization suggestions

## Buyers

Features:

- personalized property recommendations
- conversational property search

## Administrators

Features:

- analytics insights
- seller performance analysis
- market demand analysis

---

# 6. LLM-Based Price Prediction

Because no trained ML model is available, the price prediction system will rely on LLM reasoning.

## Inputs

- location
- property size
- property type
- number of rooms
- number of bathrooms
- amenities
- nearby property prices

## Pipeline

Property Data
│
Market Data Query
│
Prompt Generation
│
LLM Reasoning
│
Price Estimate


## Output

- estimated price
- recommended price range
- reasoning explanation

---

# 7. Property Description Generation

The system will generate professional property descriptions automatically.

## Inputs

- property details
- location
- amenities
- nearby attractions

## Output

A marketing-ready property listing description.

---

# 8. Recommendation Engine

The recommendation engine will use a hybrid approach.

## Behavioral Recommendations

Based on:

- search history
- viewed properties
- favorites

## Content-Based Recommendations

Based on:

- property type
- location
- price range
- amenities

---

# 9. RAG System (Retrieval Augmented Generation)

The AI assistant will use a RAG architecture to ground responses in real platform data.

## Data Sources

- property listings
- reviews
- market analytics
- platform statistics

## Pipeline


This architecture allows the system to evolve without disrupting existing clients.

---

# 4. Microservices Migration Strategy

Migration will be gradual.

## Phase 1 – Infrastructure

Introduce:

- Redis
- RabbitMQ
- Celery Workers
- AI Service
- Realtime Service

## Phase 2 – Feature Extraction

Gradually extract:

- chat service
- notification service
- search service

## Phase 3 – Service Scaling

Services become independently scalable.

---

# 5. AI System Overview

The AI layer will provide intelligent capabilities for three groups of users.

## Sellers

Features:

- price recommendations
- property description generation
- listing optimization suggestions

## Buyers

Features:

- personalized property recommendations
- conversational property search

## Administrators

Features:

- analytics insights
- seller performance analysis
- market demand analysis

---

# 6. LLM-Based Price Prediction

Because no trained ML model is available, the price prediction system will rely on LLM reasoning.

## Inputs

- location
- property size
- property type
- number of rooms
- number of bathrooms
- amenities
- nearby property prices

## Pipeline
User Question
│
Embedding Generation
│
Vector Search
│
Relevant Context
│
LLM Response


Vector search will be implemented using PostgreSQL with vector embeddings.

---

# 10. LLM Orchestration System

The system must support multiple AI models.

An LLM Router will decide which model to use depending on the task.

Example routing:

| Task                   | Model Type         |
| ---------------------- | ------------------ |
| Description generation | general LLM        |
| Price reasoning        | analytical LLM     |
| Conversational chat    | conversational LLM |

The router dynamically selects the appropriate model.

---

# 11. AI Tools Layer

The AI system must not access the database directly.

Instead it interacts through controlled tools.

## Example Tools

- get_property_details
- get_market_statistics
- search_properties
- get_seller_performance

This prevents data leakage and improves security.

---

# 12. Realtime System

The realtime service replaces Django Channels.

## Technology

- FastAPI
- WebSocket
- Redis Pub/Sub

## Features

- chat messaging
- real-time notifications
- live updates

FastAPI will load Django environment to reuse ORM and authentication.

---

# 13. Background Processing

Celery workers handle asynchronous workloads.

## Example Tasks

- AI processing
- property embedding generation
- recommendation updates
- notification delivery
- analytics processing

## Infrastructure

Broker: RabbitMQ

Result backend: Redis

---

# 14. Security

Security principles:

- AI must not access private user data directly
- All AI queries must pass through the tools layer
- strict authentication enforcement
- logging of all AI interactions

Sensitive information such as private messages must never be used in prompts.

---

# 15. Deployment Architecture

The platform will run as containerized services.

## Core Components

- Django API Gateway
- AI Service
- Realtime Service
- Celery Workers
- PostgreSQL
- Redis
- RabbitMQ

All services will run behind NGINX.

---

# 16. Observability

Monitoring must include:

- API performance
- WebSocket connections
- Celery worker health
- AI response latency

Logs must track:

- AI requests
- system errors
- task execution metrics

---

# 17. Development Roadmap

## Stage 1

Infrastructure setup:

- Redis
- RabbitMQ
- Celery

## Stage 2

Realtime migration:

- remove Django Channels
- implement FastAPI WebSocket service

## Stage 3

AI services:

- price prediction
- description generation
- recommendation engine

## Stage 4

AI assistant:

- RAG system
- embeddings
- vector search
- admin analytics assistant

## Stage 5

Optimization and scaling.

---

# 18. Success Metrics

Success will be measured using:

- increase in property engagement
- improved listing creation speed
- better search relevance
- higher conversion rates
- improved user satisfaction



# 19. Folder Architecture
backend/
│
├ gateway/
│   └ django_api/
│       ├ apps/
│       │   ├ users/
│       │   ├ properties/
│       │   ├ reviews/
│       │   ├ chat/
│       │   └ notifications/
│       │
│       ├ services/
│       ├ repositories/
│       └ core/
│
├ services/
│   │
│   ├ ai-service/
│   │   ├ api/
│   │   ├ rag/
│   │   ├ llm_router/
│   │   ├ tools/
│   │   └ prompts/
│   │
│   ├ realtime-service/
│   │   └ fastapi_ws/
│   │
│   └ search-service/
│
├ workers/
│   ├ celery_app.py
│   └ tasks/
│
├ infrastructure/
│   ├ docker/
│   └ nginx/
│
└ shared/
    ├ schemas/
    └ utils/