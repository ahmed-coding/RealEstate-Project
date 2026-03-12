"""
Realtime Service Main Application
FastAPI WebSocket service for real-time chat and notifications
"""
import os
import sys
# Add the gateway root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.shared.utils.logging import setup_logger
from fastapi_ws.auth.middleware import WebSocketAuthMiddleware
from fastapi_ws.websocket.notifications import NotificationManager
from fastapi_ws.websocket.chat import ChatManager
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager


# Add parent directory to path for imports

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger("realtime-service", level=os.getenv("LOG_LEVEL", "INFO"))


# Global managers
chat_manager = ChatManager()
notification_manager = NotificationManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Realtime Service...")

    # Initialize Redis connection
    await notification_manager.connect_redis()

    yield

    # Shutdown
    logger.info("Shutting down Realtime Service...")
    await notification_manager.disconnect_redis()


# Create FastAPI application
app = FastAPI(
    title="Real Estate Realtime Service",
    description="WebSocket service for real-time chat and notifications",
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


# WebSocket endpoints
@app.websocket("/ws/chat/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: int):
    """
    WebSocket endpoint for chat

    Args:
        websocket: WebSocket connection
        room_id: Chat room ID
    """
    # Authenticate via middleware
    # In production, get user from token
    user_id = websocket.query_params.get("user_id")

    if not user_id:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await websocket.accept()

    # Add to chat manager
    await chat_manager.connect(websocket, room_id, int(user_id))

    try:
        # Notify room of new user
        await chat_manager.broadcast_to_room(
            room_id=room_id,
            message={
                "type": "user_joined",
                "user_id": user_id,
                "room_id": room_id
            },
            exclude_user=int(user_id)
        )

        # Handle messages
        while True:
            data = await websocket.receive_json()
            await chat_manager.handle_message(
                websocket=websocket,
                room_id=room_id,
                user_id=int(user_id),
                message=data
            )

    except WebSocketDisconnect:
        await chat_manager.disconnect(websocket, room_id, int(user_id))

        # Notify room of user leaving
        await chat_manager.broadcast_to_room(
            room_id=room_id,
            message={
                "type": "user_left",
                "user_id": user_id,
                "room_id": room_id
            },
            exclude_user=int(user_id)
        )
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await chat_manager.disconnect(websocket, room_id, int(user_id))


@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for notifications

    Args:
        websocket: WebSocket connection
    """
    # Get user from query params
    user_id = websocket.query_params.get("user_id")

    if not user_id:
        await websocket.close(code=4001, reason="Authentication required")
        return

    await websocket.accept()

    # Subscribe to user's notification channel
    await notification_manager.subscribe(websocket, int(user_id))

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Process any control messages if needed

    except WebSocketDisconnect:
        await notification_manager.unsubscribe(websocket, int(user_id))
    except Exception as e:
        logger.error(f"Notification WebSocket error: {e}")
        await notification_manager.unsubscribe(websocket, int(user_id))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "realtime-service",
        "version": "1.0.0",
        "active_connections": chat_manager.get_connection_count()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real Estate Realtime Service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("REALTIME_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("REALTIME_SERVICE_PORT", "8002"))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "true").lower() == "true"
    )
