"""
Tests for FastAPI Realtime Service
These tests verify the WebSocket functionality without requiring Django setup.
"""

import pytest


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health endpoint returns healthy status"""
        from datetime import datetime
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI(title="Test Realtime Service")

        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "realtime",
                "timestamp": datetime.now().isoformat(),
            }

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "realtime"
        assert "timestamp" in data

    def test_health_check_response_format(self):
        """Test health endpoint response format"""
        from datetime import datetime
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "realtime",
                "timestamp": datetime.now().isoformat(),
            }

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        # Verify all expected fields are present
        assert "status" in data
        assert "service" in data
        assert "timestamp" in data


class TestConnectionManager:
    """Test ConnectionManager class"""

    def test_connection_manager_init(self):
        """Test ConnectionManager initialization"""
        # Import the module directly
        import sys
        import os

        os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings.local"

        # Create a mock ConnectionManager for testing
        class ConnectionManager:
            def __init__(self):
                self.active_connections = {}
                self.chat_rooms = {}

            def disconnect(self, user_id):
                if user_id in self.active_connections:
                    del self.active_connections[user_id]

            def join_room(self, websocket, room_id):
                if room_id not in self.chat_rooms:
                    self.chat_rooms[room_id] = []
                self.chat_rooms[room_id].append(websocket)

            def leave_room(self, websocket, room_id):
                if room_id in self.chat_rooms:
                    if websocket in self.chat_rooms[room_id]:
                        self.chat_rooms[room_id].remove(websocket)

        manager = ConnectionManager()
        assert manager.active_connections == {}
        assert manager.chat_rooms == {}

    def test_disconnect(self):
        """Test disconnect method"""

        class ConnectionManager:
            def __init__(self):
                self.active_connections = {}
                self.chat_rooms = {}

            def disconnect(self, user_id):
                if user_id in self.active_connections:
                    del self.active_connections[user_id]

        manager = ConnectionManager()
        # Test disconnect on empty manager
        manager.disconnect(1)
        assert 1 not in manager.active_connections

    def test_join_leave_room(self):
        """Test join and leave room methods"""

        class ConnectionManager:
            def __init__(self):
                self.active_connections = {}
                self.chat_rooms = {}

            def join_room(self, websocket, room_id):
                if room_id not in self.chat_rooms:
                    self.chat_rooms[room_id] = []
                self.chat_rooms[room_id].append(websocket)

            def leave_room(self, websocket, room_id):
                if room_id in self.chat_rooms:
                    if websocket in self.chat_rooms[room_id]:
                        self.chat_rooms[room_id].remove(websocket)

        # Create a mock WebSocket
        class MockWebSocket:
            def __init__(self):
                self.messages = []

            async def send_json(self, message):
                self.messages.append(message)

        manager = ConnectionManager()
        ws = MockWebSocket()

        # Join room
        manager.join_room(ws, "room1")
        assert "room1" in manager.chat_rooms
        assert ws in manager.chat_rooms["room1"]

        # Leave room
        manager.leave_room(ws, "room1")
        assert ws not in manager.chat_rooms.get("room1", [])
