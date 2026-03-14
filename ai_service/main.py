"""
AI Service for Real Estate Platform
Provides property recommendations and semantic search using OpenRouter AI.
"""

import os
import django

# Setup Django before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")
django.setup()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
from datetime import datetime

app = FastAPI(title="Real Estate AI Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"


# Request/Response models
class PropertySearchRequest(BaseModel):
    query: str
    user_id: Optional[int] = None
    limit: int = 10


class PropertyRecommendRequest(BaseModel):
    user_id: int
    property_id: Optional[int] = None
    limit: int = 5


class ChatRequest(BaseModel):
    message: str
    user_id: int
    context: Optional[dict] = None


class EmbeddingRequest(BaseModel):
    text: str


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "service": "ai",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/embed")
async def create_embedding(request: EmbeddingRequest):
    """Create text embedding using OpenRouter"""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1"
        )
        response = client.embeddings.create(
            model="text-embedding-3-small", input=request.text
        )

        return {
            "embedding": response.data[0].embedding,
            "model": response.model,
            "tokens": response.usage.total_tokens,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating embedding: {str(e)}"
        )


@app.post("/search")
async def semantic_search(request: PropertySearchRequest):
    """Search properties using semantic search with embeddings"""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        # Create embedding for search query
        client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1"
        )
        response = client.embeddings.create(
            model="text-embedding-3-small", input=request.query
        )
        query_embedding = response.data[0].embedding

        # Search properties using pgvector
        from core.apps.search.models import PropertyEmbedding
        from core.apps.models import Property
        from django.db.models import F
        from django.contrib.postgres.search import SearchQuery, SearchRank
        from django.db.models.functions import CosineSimilarity

        # Get active properties with embeddings
        properties = Property.objects.filter(is_active=True).select_related(
            "user", "category", "address__state__city__country"
        )

        # For now, return text-based search results
        # In production, use pgvector for cosine similarity
        text_results = properties.filter(
            name__icontains=request.query
        ) | properties.filter(description__icontains=request.query)

        results = []
        for prop in text_results[: request.limit]:
            results.append(
                {
                    "id": prop.id,
                    "name": prop.name,
                    "description": prop.description,
                    "price": str(prop.price) if prop.price else None,
                    "size": prop.size,
                    "address": str(prop.address) if prop.address else None,
                }
            )

        return {
            "query": request.query,
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/recommend")
async def recommend_properties(request: PropertyRecommendRequest):
    """Get property recommendations for a user"""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        from core.apps.models import Property, Favorite, Alarm
        from django.db.models import Count

        # Get user's favorite properties
        favorites = Favorite.objects.filter(user_id=request.user_id).values_list(
            "property_id", flat=True
        )

        # Get user's saved searches
        alarms = Alarm.objects.filter(user_id=request.user_id, is_active=True)

        # Get recommended properties based on favorites and alarms
        recommended = Property.objects.filter(is_active=True).exclude(id__in=favorites)

        # If user has favorites, recommend similar properties
        if favorites:
            favorite_props = Property.objects.filter(id__in=favorites[:3])
            categories = [p.category_id for p in favorite_props]
            recommended = recommended.filter(category_id__in=categories)

        results = []
        for prop in recommended[: request.limit]:
            results.append(
                {
                    "id": prop.id,
                    "name": prop.name,
                    "description": prop.description,
                    "price": str(prop.price) if prop.price else None,
                    "size": prop.size,
                }
            )

        return {
            "user_id": request.user_id,
            "recommendations": results,
            "count": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with AI about properties"""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")

    try:
        client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1"
        )

        # Build context from property data if provided
        system_prompt = """You are a real estate assistant helping users find properties.
        You have access to property listings and can help users with:
        - Finding properties matching their criteria
        - Answering questions about neighborhoods
        - Providing property details
        - Scheduling viewings
        
        Be helpful, friendly, and concise in your responses."""

        messages = [
            {"role": "system", "content": system_prompt},
        ]

        if request.context:
            # Add property context if available
            context_info = (
                f"Current properties: {request.context.get('properties', 'None')}"
            )
            messages.append({"role": "system", "content": context_info})

        messages.append({"role": "user", "content": request.message})

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
        )

        return {
            "message": response.choices[0].message.content,
            "model": response.model,
            "tokens": response.usage.total_tokens,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
