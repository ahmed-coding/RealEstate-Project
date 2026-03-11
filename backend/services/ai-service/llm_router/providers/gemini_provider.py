"""
Gemini Provider
Google Gemini AI integration for LLM requests using Google AI Studio API
"""
import os
from typing import Dict, Any, Optional
import httpx
import time


class GeminiProvider:
    """Google Gemini provider implementation using direct Google AI Studio API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gemini-1.5-flash"
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.default_model = default_model
        # Google AI Studio API base URL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    async def is_available(self) -> bool:
        """Check if Gemini API is available"""
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                # Try to list models to check availability
                response = await client.get(
                    f"{self.base_url}/models?key={self.api_key}",
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        context: Dict[str, Any] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using Google Gemini

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            context: Additional context for the prompt
            system_prompt: System prompt override

        Returns:
            Dict with content, model, and tokens_used
        """
        if not self.api_key:
            raise ValueError("Gemini API key not configured")

        start_time = time.time()

        # Build the full prompt with context
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        elif context:
            context_str = f"Context: {context}\n\n"
            full_prompt = f"{context_str}{prompt}"

        async with httpx.AsyncClient() as client:
            # Use the chat/completions endpoint
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.95,
                    "topK": 40,
                }
            }

            response = await client.post(
                f"{self.base_url}/models/{self.default_model}:generateContent?key={self.api_key}",
                json=payload,
                timeout=60.0,
                headers={
                    "Content-Type": "application/json"
                }
            )

            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.text}")

            data = response.json()

            # Extract content from response
            content = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0:
                        content = parts[0].get("text", "")

            # Estimate tokens (Gemini doesn't always return this)
            tokens_used = len(content.split()) * 1.3  # Rough estimate

            return {
                "content": content,
                "model": self.default_model,
                "tokens_used": int(tokens_used),
                "latency_ms": int((time.time() - start_time) * 1000)
            }

    async def generate_with_tools(
        self,
        prompt: str,
        tools: list,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate text with function calling capability

        Args:
            prompt: User prompt
            tools: List of tool definitions
            context: Additional context

        Returns:
            Dict with content, function calls, and tokens_used
        """
        if not self.api_key:
            raise ValueError("Gemini API key not configured")

        start_time = time.time()

        # Build the full prompt with context
        full_prompt = prompt
        if context:
            context_str = f"Context: {context}\n\n"
            full_prompt = f"{context_str}{prompt}"

        async with httpx.AsyncClient() as client:
            # Convert OpenAI tools format to Gemini function declarations
            function_declarations = []
            for tool in tools:
                if "function" in tool:
                    func = tool["function"]
                    function_declarations.append({
                        "name": func.get("name"),
                        "description": func.get("description"),
                        "parameters": func.get("parameters", {})
                    })

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2000,
                },
                "tools": [
                    {
                        "functionDeclarations": function_declarations
                    }
                ] if function_declarations else []
            }

            response = await client.post(
                f"{self.base_url}/models/{self.default_model}:generateContent?key={self.api_key}",
                json=payload,
                timeout=60.0,
                headers={
                    "Content-Type": "application/json"
                }
            )

            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.text}")

            data = response.json()

            # Extract content and function calls
            content = ""
            function_call = None

            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    for part in parts:
                        if "text" in part:
                            content = part["text"]
                        elif "functionCall" in part:
                            function_call = part["functionCall"]

            tokens_used = len(content.split()) * 1.3

            return {
                "content": content,
                "function_call": function_call,
                "model": self.default_model,
                "tokens_used": int(tokens_used),
                "latency_ms": int((time.time() - start_time) * 1000)
            }


# Import LLMRequest and LLMResponse for type hints
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """LLM Response schema"""
    content: str
    model_used: str
    tokens_used: int = 0
    latency_ms: int = 0
