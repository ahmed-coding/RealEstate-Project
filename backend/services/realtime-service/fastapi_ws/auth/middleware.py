"""
WebSocket Authentication Middleware
Handles WebSocket authentication
"""
from typing import Optional
from fastapi import HTTPException, status
import jwt
import os


class WebSocketAuthMiddleware:
    """Middleware for WebSocket authentication"""

    def __init__(self):
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY", "django-insecure-change-this-in-production")
        self.algorithm = "HS256"

    async def authenticate(self, token: str) -> dict:
        """
        Authenticate WebSocket connection using token

        Args:
            token: JWT token from query params

        Returns:
            User data from token

        Raises:
            HTTPException: If token is invalid
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        try:
            payload = jwt.decode(token, self.secret_key,
                                 algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    def create_token(self, user_id: int, email: str, user_type: str = "customer") -> str:
        """
        Create JWT token for WebSocket auth

        Args:
            user_id: User ID
            email: User email
            user_type: User type

        Returns:
            JWT token
        """
        from datetime import datetime, timedelta

        payload = {
            "user_id": user_id,
            "email": email,
            "user_type": user_type,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
