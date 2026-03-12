"""
AI Service Main Application
FastAPI application for AI-powered features
"""
import sys
import os

# Add the gateway root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.shared.utils.database import DatabaseManager
from backend.shared.utils.logging import setup_logger
from api.routes import price_prediction, descriptions, recommendations, assistant
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers


# Setup logging
logger = setup_logger("ai-service", level=os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Service...")

    # Initialize database connections
    try:
        engine = DatabaseManager.get_engine()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down AI Service...")


# Create FastAPI application
app = FastAPI(
    title="Real Estate AI Service",
    description="AI-powered features for the real estate platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(
    price_prediction.router,
    prefix="/api/ai/price-prediction",
    tags=["Price Prediction"]
)

app.include_router(
    descriptions.router,
    prefix="/api/ai/descriptions",
    tags=["Description Generation"]
)

app.include_router(
    recommendations.router,
    prefix="/api/ai/recommendations",
    tags=["Recommendations"]
)

app.include_router(
    assistant.router,
    prefix="/api/ai/assistant",
    tags=["AI Assistant"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real Estate AI Service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("AI_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("AI_SERVICE_PORT", "8001"))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "true").lower() == "true"
    )
