"""
Recommendations API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
import time

from shared.schemas.ai import (
    RecommendationInput,
    RecommendationOutput
)
from tools.property_tools import get_user_favorites, get_user_search_history
from rag.retriever import RecommendationEngine
from shared.utils.logging import setup_logger, log_ai_request, log_ai_response

logger = setup_logger("ai-service.recommendations")
router = APIRouter()


@router.post("/personalized", response_model=RecommendationOutput)
async def get_personalized_recommendations(input_data: RecommendationInput):
    """
    Get personalized property recommendations for a user

    Uses hybrid recommendation approach:
    - Behavioral: Based on user's search history and viewed properties
    - Content-Based: Based on property features, location, and price
    """
    start_time = time.time()

    log_ai_request(
        logger=logger,
        task_type="recommendations",
        user_id=input_data.user_id,
        prompt_length=0
    )

    try:
        recommendation_engine = RecommendationEngine()

        # Get user behavioral data
        favorites = await get_user_favorites(input_data.user_id)
        search_history = await get_user_search_history(input_data.user_id)

        # Get recommendations based on type
        if input_data.recommendation_type == "behavioral":
            property_ids = await recommendation_engine.get_behavioral_recommendations(
                user_id=input_data.user_id,
                favorites=favorites,
                search_history=search_history,
                limit=input_data.limit
            )
        elif input_data.recommendation_type == "content":
            property_ids = await recommendation_engine.get_content_recommendations(
                user_id=input_data.user_id,
                limit=input_data.limit
            )
        else:  # hybrid
            property_ids = await recommendation_engine.get_hybrid_recommendations(
                user_id=input_data.user_id,
                favorites=favorites,
                search_history=search_history,
                limit=input_data.limit
            )

        # Generate scores (placeholder - in production, calculate real scores)
        scores = [0.95 - (i * 0.05) for i in range(len(property_ids))]

        latency_ms = (time.time() - start_time) * 1000

        log_ai_response(
            logger=logger,
            task_type="recommendations",
            user_id=input_data.user_id,
            success=True,
            latency_ms=latency_ms
        )

        return RecommendationOutput(
            property_ids=property_ids,
            scores=scores,
            recommendation_type=input_data.recommendation_type,
            model_used="hybrid_recommendation"
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log_ai_response(
            logger=logger,
            task_type="recommendations",
            user_id=input_data.user_id,
            success=False,
            latency_ms=latency_ms,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, detail=f"Recommendations failed: {str(e)}")


@router.get("/similar/{property_id}")
async def get_similar_properties(property_id: int, limit: int = 5):
    """
    Get properties similar to a given property
    """
    start_time = time.time()

    try:
        recommendation_engine = RecommendationEngine()

        similar_property_ids = await recommendation_engine.get_similar_properties(
            property_id=property_id,
            limit=limit
        )

        return {
            "property_id": property_id,
            "similar_properties": similar_property_ids
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Similar properties lookup failed: {str(e)}")


@router.post("/refresh")
async def refresh_recommendations(user_id: int):
    """
    Refresh recommendation cache for a user

    Triggers background task to update user recommendations
    """
    try:
        # In production, this would queue a Celery task
        # from workers.tasks.recommendation_tasks import refresh_user_recommendations
        # refresh_user_recommendations.delay(user_id)

        return {
            "status": "queued",
            "message": f"Recommendation refresh queued for user {user_id}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to queue refresh: {str(e)}")


@router.get("/trending")
async def get_trending_properties(limit: int = 10):
    """
    Get trending properties across the platform
    """
    try:
        recommendation_engine = RecommendationEngine()

        trending_ids = await recommendation_engine.get_trending_properties(limit=limit)

        return {
            "trending_properties": trending_ids,
            "count": len(trending_ids)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Trending properties failed: {str(e)}")
