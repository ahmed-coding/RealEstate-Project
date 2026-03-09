"""
AI Assistant API Routes (RAG-powered)
"""
from fastapi import APIRouter, HTTPException, Depends
import time

from shared.schemas.ai import (
    RAGQueryInput,
    RAGQueryOutput
)
from rag.retriever import RAGEngine
from shared.utils.security import verify_token
from shared.utils.logging import setup_logger, log_ai_request, log_ai_response

logger = setup_logger("ai-service.assistant")
router = APIRouter()


@router.post("/chat", response_model=RAGQueryOutput)
async def chat_with_assistant(
    input_data: RAGQueryInput,
    current_user: dict = Depends(verify_token)
):
    """
    Chat with AI assistant powered by RAG

    The assistant can answer questions about:
    - Property listings
    - Market statistics
    - Platform features
    - Buying/selling tips

    Uses retrieval-augmented generation to ground responses in real data.
    """
    start_time = time.time()

    log_ai_request(
        logger=logger,
        task_type="conversational_chat",
        user_id=current_user.get("user_id"),
        prompt_length=len(input_data.user_question)
    )

    try:
        rag_engine = RAGEngine()

        # Process the query through RAG pipeline
        result = await rag_engine.query(
            question=input_data.user_question,
            user_id=input_data.user_id,
            session_id=input_data.session_id,
            top_k=input_data.top_k
        )

        latency_ms = (time.time() - start_time) * 1000

        log_ai_response(
            logger=logger,
            task_type="conversational_chat",
            user_id=current_user.get("user_id"),
            success=True,
            latency_ms=latency_ms
        )

        return RAGQueryOutput(
            answer=result["answer"],
            sources=result["sources"],
            model_used=result["model_used"],
            citations=result.get("citations", [])
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log_ai_response(
            logger=logger,
            task_type="conversational_chat",
            user_id=current_user.get("user_id"),
            success=False,
            latency_ms=latency_ms,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/market-analysis")
async def get_market_analysis(
    location: str,
    property_type: str = "property",
    current_user: dict = Depends(verify_token)
):
    """
    Get AI-powered market analysis for a location

    Provides insights about:
    - Price trends
    - Demand analysis
    - Investment opportunities
    """
    start_time = time.time()

    try:
        rag_engine = RAGEngine()

        question = f"What is the market analysis for {property_type} properties in {location}?"

        result = await rag_engine.query(
            question=question,
            user_id=current_user.get("user_id"),
            top_k=10
        )

        return {
            "location": location,
            "property_type": property_type,
            "analysis": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Market analysis failed: {str(e)}")


@router.get("/tools")
async def list_available_tools():
    """
    List all available AI tools

    Returns tools that the AI assistant can use to answer questions
    """
    from tools.property_tools import get_available_tools

    tools = get_available_tools()

    return {
        "tools": tools,
        "count": len(tools)
    }


@router.post("/admin/analytics")
async def get_admin_analytics(
    query: str,
    current_user: dict = Depends(verify_token)
):
    """
    Admin analytics assistant

    Provides insights for administrators about:
    - Seller performance
    - Market demand
    - User engagement
    """
    start_time = time.time()

    # Verify admin role
    if current_user.get("user_type") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        rag_engine = RAGEngine()

        # Add admin context to query
        full_query = f"As an admin, {query}"

        result = await rag_engine.query(
            question=full_query,
            user_id=current_user.get("user_id"),
            top_k=15,
            system_prompt="You are an analytics assistant for a real estate platform admin. Provide data-driven insights."
        )

        return {
            "query": query,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Analytics query failed: {str(e)}")
