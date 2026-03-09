"""
LLM Router
Routes LLM requests to appropriate providers based on task type
"""
import os
import asyncio
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel
import httpx

from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider


class LLMTaskType(str, Enum):
    """LLM Task Types"""
    DESCRIPTION_GENERATION = "description_generation"
    PRICE_REASONING = "price_reasoning"
    CONVERSATIONAL_CHAT = "conversational_chat"
    ANALYTICS = "analytics"
    EMBEDDING = "embedding"


class LLMProvider(str, Enum):
    """LLM Providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    GROQ = "groq"


class LLMRequest(BaseModel):
    """LLM Request schema"""
    task_type: LLMTaskType
    prompt: str
    context: Optional[Dict[str, Any]] = None
    model_preference: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class LLMResponse(BaseModel):
    """LLM Response schema"""
    content: str
    model_used: str
    tokens_used: int = 0
    latency_ms: int = 0


class LLMRouter:
    """Routes LLM requests to appropriate providers"""

    # Task to preferred provider mapping
    TASK_PROVIDER_MAP = {
        LLMTaskType.DESCRIPTION_GENERATION: [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI],
        LLMTaskType.PRICE_REASONING: [LLMProvider.GROQ, LLMProvider.COHERE, LLMProvider.OLLAMA],
        LLMTaskType.CONVERSATIONAL_CHAT: [LLMProvider.OLLAMA, LLMProvider.HUGGINGFACE, LLMProvider.OPENAI],
        LLMTaskType.ANALYTICS: [LLMProvider.COHERE, LLMProvider.GROQ, LLMProvider.OLLAMA],
    }

    def __init__(self):
        self.providers = {
            LLMProvider.OPENAI: OpenAIProvider(),
            LLMProvider.ANTHROPIC: AnthropicProvider(),
            LLMProvider.OLLAMA: OllamaProvider(),
            LLMProvider.HUGGINGFACE: HuggingFaceProvider(),
            LLMProvider.COHERE: CohereProvider(),
            LLMProvider.GROQ: GroqProvider(),
        }

    async def route_request(self, request: LLMRequest) -> LLMResponse:
        """
        Route request to appropriate LLM provider

        Args:
            request: LLM request with task type and prompt

        Returns:
            LLMResponse from the provider
        """
        # Get preferred providers for task
        preferred_providers = self.TASK_PROVIDER_MAP.get(
            request.task_type,
            [LLMProvider.OLLAMA, LLMProvider.OPENAI]
        )

        # If user has a preference, try that first
        if request.model_preference:
            provider = self._find_provider_by_model(request.model_preference)
            if provider:
                preferred_providers = [provider] + preferred_providers

        # Try each provider in order
        last_error = None
        for provider_type in preferred_providers:
            try:
                provider = self.providers[provider_type]
                if await provider.is_available():
                    return await provider.generate(request)
            except Exception as e:
                last_error = e
                continue

        # All providers failed
        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    def _find_provider_by_model(self, model: str) -> Optional[LLMProvider]:
        """Find provider by model name"""
        model_lower = model.lower()

        if "gpt" in model_lower:
            return LLMProvider.OPENAI
        elif "claude" in model_lower:
            return LLMProvider.ANTHROPIC
        elif "llama" in model_lower or "mistral" in model_lower or "qwen" in model_lower:
            return LLMProvider.OLLAMA
        elif any(m in model_lower for m in ["falcon", "bloom", "flan", "m2"]):
            return LLMProvider.HUGGINGFACE
        elif "command" in model_lower:
            return LLMProvider.COHERE
        elif "mixtral" in model_lower or "llama" in model_lower:
            return LLMProvider.GROQ

        return None

    def get_available_providers(self) -> Dict[str, bool]:
        """Get availability of all providers"""
        return asyncio.run(self._check_providers())

    async def _check_providers(self) -> Dict[str, bool]:
        """Check which providers are available"""
        results = {}
        for provider_type, provider in self.providers.items():
            try:
                results[provider_type.value] = await provider.is_available()
            except:
                results[provider_type.value] = False
        return results


class OllamaProvider:
    """Ollama local LLM provider"""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama2")

    async def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except:
            return False

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Ollama"""
        import time
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.default_model,
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens,
                }
            }

            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")

            data = response.json()

            return LLMResponse(
                content=data.get("response", ""),
                model_used=f"ollama:{self.default_model}",
                tokens_used=data.get("eval_count", 0),
                latency_ms=int((time.time() - start_time) * 1000)
            )


class HuggingFaceProvider:
    """HuggingFace Inference API provider (free tier)"""

    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN", "")
        self.base_url = "https://api-inference.huggingface.co/models"
        # Default free models
        self.default_model = "google/flan-t5-large"

    async def is_available(self) -> bool:
        """Check if HuggingFace API is available"""
        if not self.api_token:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.default_model}",
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using HuggingFace"""
        import time
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            payload = {
                "inputs": request.prompt,
                "parameters": {
                    "temperature": request.temperature,
                    "max_new_tokens": request.max_tokens,
                }
            }

            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"

            response = await client.post(
                f"{self.base_url}/{self.default_model}",
                json=payload,
                headers=headers,
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"HuggingFace error: {response.text}")

            data = response.json()

            # Parse response based on model format
            content = ""
            if isinstance(data, list) and len(data) > 0:
                content = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                content = data.get("generated_text", "")

            return LLMResponse(
                content=content,
                model_used=f"huggingface:{self.default_model}",
                tokens_used=len(content.split()),
                latency_ms=int((time.time() - start_time) * 1000)
            )


class CohereProvider:
    """Cohere AI provider (free tier available)"""

    def __init__(self):
        self.api_key = os.getenv("COHERE_API_KEY", "")
        self.base_url = "https://api.cohere.ai/v1"
        self.default_model = "command-r-plus"  # Has free tier

    async def is_available(self) -> bool:
        """Check if Cohere API is available"""
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Cohere"""
        import time
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.default_model,
                "prompt": request.prompt,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }

            response = await client.post(
                f"{self.base_url}/generate",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"Cohere error: {response.text}")

            data = response.json()

            return LLMResponse(
                content=data.get("text", ""),
                model_used=f"cohere:{self.default_model}",
                tokens_used=data.get("tokens_generated", 0),
                latency_ms=int((time.time() - start_time) * 1000)
            )


class GroqProvider:
    """Groq provider (free tier available)"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = "mixtral-8x7b-32768"  # Free model

    async def is_available(self) -> bool:
        """Check if Groq API is available"""
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Groq (OpenAI-compatible)"""
        import time
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.default_model,
                "messages": [{"role": "user", "content": request.prompt}],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }

            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"Groq error: {response.text}")

            data = response.json()

            content = ""
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]

            usage = data.get("usage", {})

            return LLMResponse(
                content=content,
                model_used=f"groq:{self.default_model}",
                tokens_used=usage.get("total_tokens", 0),
                latency_ms=int((time.time() - start_time) * 1000)
            )
