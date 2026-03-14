"""
FastAPI Realtime Service for Real Estate Platform
Handles WebSocket connections for chat and notifications
Loads Django ORM models directly
"""

import os
import django

# Setup Django before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")
django.setup()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
from datetime import datetime

app = FastAPI(title="Real Estate Realtime Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        # Active connections: {user_id: WebSocket}
        self.active_connections: dict[int, WebSocket] = {}
        # Chat rooms: {room_id: [WebSocket]}
        self.chat_rooms: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast(self, message: dict, room_id: str = None):
        if room_id and room_id in self.chat_rooms:
            for connection in self.chat_rooms[room_id]:
                await connection.send_json(message)

    def join_room(self, websocket: WebSocket, room_id: str):
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = []
        self.chat_rooms[room_id].append(websocket)

    def leave_room(self, websocket: WebSocket, room_id: str):
        if room_id in self.chat_rooms:
            if websocket in self.chat_rooms[room_id]:
                self.chat_rooms[room_id].remove(websocket)


manager = ConnectionManager()


# Token validation dependency
async def get_current_user(websocket: WebSocket):
    """Validate token from websocket query params or headers"""
    token = websocket.query_params.get("token")
    if not token:
        # Try to get from headers
        token = websocket.headers.get("Authorization", "").replace("Token ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Validate token against Django
    from rest_framework.authtoken.models import Token
    from django.contrib.auth.models import AnonymousUser

    try:
        token_obj = await Token.objects.aget(key=token)
        return token_obj.user
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")


# WebSocket endpoints
@app.websocket("/ws/notifications/")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications"""
    # Extract token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    # Validate token
    from rest_framework.authtoken.models import Token

    try:
        token_obj = await Token.objects.aget(key=token)
        user = token_obj.user
    except Token.DoesNotExist:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            # Keep connection alive, wait for messages
            data = await websocket.receive_text()
            # Handle any client messages if needed
            print(f"Received from user {user.id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user.id)
        print(f"User {user.id} disconnected")


@app.websocket("/ws/chat/{room_id}/")
async def websocket_chat(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for chat rooms"""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    # Validate token
    from rest_framework.authtoken.models import Token

    try:
        token_obj = await Token.objects.aget(key=token)
        user = token_obj.user
    except Token.DoesNotExist:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    manager.join_room(websocket, room_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Save message to database
            from apps.models import PrivateChatRoom, RoomChatMessage

            try:
                room = await PrivateChatRoom.objects.aget(id=room_id)
                message = RoomChatMessage(
                    user=user, room=room, content=message_data.get("content", "")
                )
                await message.asave()

                # Broadcast to all in room
                broadcast_message = {
                    "type": "chat_message",
                    "user_id": user.id,
                    "user_name": user.name or user.email,
                    "content": message.content,
                    "timestamp": datetime.now().isoformat(),
                }
                await manager.broadcast(broadcast_message, room_id)

            except PrivateChatRoom.DoesNotExist:
                await websocket.send_json({"error": "Room not found"})

    except WebSocketDisconnect:
        manager.leave_room(websocket, room_id)
        print(f"User {user.id} left chat room {room_id}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    return {
        "status": "healthy",
        "service": "realtime",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
