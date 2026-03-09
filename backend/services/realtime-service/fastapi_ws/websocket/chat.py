"""
Chat WebSocket Manager
Manages real-time chat connections and messaging
"""
from typing import Dict, List, Optional
from fastapi import WebSocket
import json
from datetime import datetime


class ChatManager:
    """Manages chat WebSocket connections"""

    def __init__(self):
        # room_id -> {user_id -> websocket}
        self.rooms: Dict[int, Dict[int, WebSocket]] = {}
        # room_id -> set of user_ids
        self.room_users: Dict[int, set[int]] = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        """
        Add user to chat room

        Args:
            websocket: WebSocket connection
            room_id: Room ID
            user_id: User ID
        """
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
            self.room_users[room_id] = set()

        self.rooms[room_id][user_id] = websocket
        self.room_users[room_id].add(user_id)

    async def disconnect(self, websocket: WebSocket, room_id: int, user_id: int):
        """
        Remove user from chat room

        Args:
            websocket: WebSocket connection
            room_id: Room ID
            user_id: User ID
        """
        if room_id in self.rooms:
            self.rooms[room_id].pop(user_id, None)

            if room_id in self.room_users:
                self.room_users[room_id].discard(user_id)

                # Clean up empty rooms
                if not self.room_users[room_id]:
                    del self.room_users[room_id]
                    del self.rooms[room_id]

    async def handle_message(
        self,
        websocket: WebSocket,
        room_id: int,
        user_id: int,
        message: dict
    ):
        """
        Handle incoming chat message

        Args:
            websocket: WebSocket connection
            room_id: Room ID
            user_id: User ID
            message: Message data
        """
        command = message.get("command")

        if command == "send":
            await self.send_message(
                room_id=room_id,
                user_id=user_id,
                content=message.get("message", "")
            )
        elif command == "typing":
            await self.broadcast_to_room(
                room_id=room_id,
                message={
                    "type": "typing",
                    "user_id": user_id,
                    "is_typing": message.get("is_typing", True)
                },
                exclude_user=user_id
            )

    async def send_message(
        self,
        room_id: int,
        user_id: int,
        content: str
    ):
        """
        Send message to all users in room

        Args:
            room_id: Room ID
            user_id: Sender user ID
            content: Message content
        """
        if not content.strip():
            return

        message_data = {
            "type": "message",
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        await self.broadcast_to_room(
            room_id=room_id,
            message=message_data
        )

        # Save message to database
        # In production, this would save to Django database via API call
        await self.save_message(room_id, user_id, content)

    async def broadcast_to_room(
        self,
        room_id: int,
        message: dict,
        exclude_user: Optional[int] = None
    ):
        """
        Broadcast message to all users in room

        Args:
            room_id: Room ID
            message: Message to broadcast
            exclude_user: User ID to exclude
        """
        if room_id not in self.rooms:
            return

        message_json = json.dumps(message)

        for uid, websocket in self.rooms[room_id].items():
            if uid != exclude_user:
                try:
                    await websocket.send_text(message_json)
                except Exception:
                    # Remove dead connections
                    await self.disconnect(websocket, room_id, uid)

    async def save_message(self, room_id: int, user_id: int, content: str):
        """
        Save message to database

        In production, this would call Django API to save message
        """
        # Placeholder - would call Django API
        pass

    def get_room_users(self, room_id: int) -> List[int]:
        """Get list of users in a room"""
        return list(self.room_users.get(room_id, set()))

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(users) for users in self.room_users.values())

    def is_user_in_room(self, room_id: int, user_id: int) -> bool:
        """Check if user is in room"""
        return user_id in self.room_users.get(room_id, set())
