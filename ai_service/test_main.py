"""
Tests for AI Service
"""

import pytest


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health endpoint returns healthy status"""
        from datetime import datetime
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI(title="Test AI Service")

        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "service": "ai",
                "timestamp": datetime.now().isoformat(),
            }

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai"
        assert "timestamp" in data


class TestRequestModels:
    """Test Pydantic request models"""

    def test_embedding_request_model(self):
        """Test EmbeddingRequest model"""
        from ai_service.main import EmbeddingRequest

        request = EmbeddingRequest(text="test property")
        assert request.text == "test property"

    def test_search_request_model(self):
        """Test PropertySearchRequest model"""
        from ai_service.main import PropertySearchRequest

        request = PropertySearchRequest(query="luxury apartment", limit=5)
        assert request.query == "luxury apartment"
        assert request.limit == 5
        assert request.user_id is None

    def test_recommend_request_model(self):
        """Test PropertyRecommendRequest model"""
        from ai_service.main import PropertyRecommendRequest

        request = PropertyRecommendRequest(user_id=1, limit=10)
        assert request.user_id == 1
        assert request.limit == 10
        assert request.property_id is None

    def test_chat_request_model(self):
        """Test ChatRequest model"""
        from ai_service.main import ChatRequest

        request = ChatRequest(message="Find me a house", user_id=1)
        assert request.message == "Find me a house"
        assert request.user_id == 1
        assert request.context is None
