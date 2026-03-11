"""
OpenAI Provider
OpenAI GPT integration for LLM requests via OpenRouter
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from openai import AsyncOpenAI

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from llm_router.router import get_allowed_models, OPENROUTER_BASE_URL


class OpenAIProvider:
    """OpenAI GPT provider implementation via OpenRouter"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = None
    ):
        # Use OpenRouter API key
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = OPENROUTER_BASE_URL
        
        # Get allowed models based on USE_PAID_MODELS
        allowed_models = get_allowed_models()
        
        # Filter models that work with OpenAI-compatible endpoint (OpenAI, Anthropic, etc.)
        openai_compatible_models = [
            m for m in allowed_models
            if m.startswith("openai/") or m.startswith("anthropic/") or m.startswith("google/")
        ]
        
        # Set default model - prefer GPT-4o if available, otherwise use first available
        if default_model:
            self.default_model = default_model
        elif openai_compatible_models:
            # Prioritize GPT-4o, then GPT-4o-mini, then others
            priority_models = ["openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo"]
            self.default_model = next(
                (m for m in priority_models if m in openai_compatible_models),
                openai_compatible_models[0]
            )
        else:
            self.default_model = "openai/gpt-4o-mini"
        
        self.client = None

        if self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

    async def is_available(self) -> bool:
        """Check if OpenRouter API is available"""
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

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        context: Dict[str, Any] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using OpenAI GPT via OpenRouter

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            context: Additional context for the prompt
            system_prompt: System prompt override

        Returns:
            Dict with content, model, and tokens_used
        """
        if not self.client:
            raise ValueError("OpenRouter API key not configured")

        # Build messages
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif context:
            # Add context as system message
            context_str = f"Context: {context}"
            messages.append({"role": "system", "content": context_str})

        messages.append({"role": "user", "content": prompt})

        # Make API call
        response = await self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
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
        if not self.client:
            raise ValueError("OpenRouter API key not configured")

        messages = []

        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {context}"
            })

        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        return {
            "content": message.content,
            "function_call": message.tool_calls if message.tool_calls else None,
            "model": response.model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
