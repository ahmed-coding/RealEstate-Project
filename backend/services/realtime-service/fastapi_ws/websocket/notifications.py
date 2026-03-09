"""
Notification WebSocket Manager
Manages real-time notification connections using Redis Pub/Sub
"""
from typing import Dict, List
from fastapi import WebSocket
import json
import redis.asyncio as redis
import os


class NotificationManager:
    """Manages notification WebSocket connections with Redis Pub/Sub"""

    def __init__(self):
        self.redis_client = None
        # user_id -> websocket
        self.subscriptions: Dict[int, WebSocket] = {}
        # pub/sub channels
        self.pubsub = None

    async def connect_redis(self):
        """Connect to Redis"""
        try:
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))

            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            print(f"Connected to Redis at {redis_host}:{redis_port}")

        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    async def disconnect_redis(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()

    async def subscribe(self, websocket: WebSocket, user_id: int):
        """
        Subscribe user to notification channel

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        self.subscriptions[user_id] = websocket

        # Start listening to Redis pub/sub in background
        if self.redis_client and not hasattr(self, '_pubsub_task'):
            self._pubsub_task = True
            # In production, start a background task to listen for messages

    async def unsubscribe(self, websocket: WebSocket, user_id: int):
        """
        Unsubscribe user from notification channel

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        self.subscriptions.pop(user_id, None)

    async def send_notification(self, user_id: int, notification: dict):
        """
        Send notification to a user

        Args:
            user_id: Target user ID
            notification: Notification data
        """
        # Try to send directly via WebSocket
        websocket = self.subscriptions.get(user_id)

        if websocket:
            try:
                await websocket.send_json(notification)
                return
            except Exception:
                # Remove dead connection
                self.subscriptions.pop(user_id, None)

        # Fallback: store in Redis for later delivery
        if self.redis_client:
            await self.store_notification(user_id, notification)

    async def broadcast_notification(self, notification: dict, user_ids: List[int] = None):
        """
        Broadcast notification to multiple users

        Args:
            notification: Notification data
            user_ids: List of user IDs (if None, broadcast to all)
        """
        if user_ids:
            for user_id in user_ids:
                await self.send_notification(user_id, notification)
        else:
            # Broadcast to all connected users
            for user_id, websocket in self.subscriptions.items():
                try:
                    await websocket.send_json(notification)
                except Exception:
                    self.subscriptions.pop(user_id, None)

    async def store_notification(self, user_id: int, notification: dict):
        """
        Store notification in Redis for offline delivery

        Args:
            user_id: User ID
            notification: Notification data
        """
        if self.redis_client:
            key = f"notifications:{user_id}"
            await self.redis_client.lpush(key, json.dumps(notification))
            # Keep only last 100 notifications
            await self.redis_client.ltrim(key, 0, 99)

    async def get_stored_notifications(self, user_id: int) -> List[dict]:
        """
        Get stored notifications for a user

        Args:
            user_id: User ID

        Returns:
            List of notifications
        """
        if self.redis_client:
            key = f"notifications:{user_id}"
            notifications = await self.redis_client.lrange(key, 0, -1)
            return [json.loads(n) for n in notifications]
        return []

    async def clear_stored_notifications(self, user_id: int):
        """Clear stored notifications for a user"""
        if self.redis_client:
            key = f"notifications:{user_id}"
            await self.redis_client.delete(key)

    def get_subscription_count(self) -> int:
        """Get number of active subscriptions"""
        return len(self.subscriptions)

    async def handle_redis_message(self, message: dict):
        """
        Handle incoming message from Redis pub/sub

        Args:
            message: Redis message
        """
        try:
            data = json.loads(message.get("data", "{}"))
            user_id = data.get("user_id")

            if user_id:
                await self.send_notification(user_id, data)
        except Exception:
            pass
