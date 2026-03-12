"""
Anthropic Provider
Anthropic Claude integration for LLM requests via OpenRouter
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import constants directly to avoid circular import
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def get_allowed_models():
    """Get allowed models based on USE_PAID_MODELS environment variable"""
    import os
    use_paid = os.getenv("USE_PAID_MODELS", "false").lower() == "true"
    if use_paid:
        return [
            "qwen/qwen-2.5-7b-instruct",
            "qwen/qwen-2.5-14b-instruct", 
            "meta-llama/llama-3.1-8b-instruct",
            "meta-llama/llama-3.2-1b-instruct",
            "mistralai/mistral-7b-instruct",
            "google/gemma-2-9b-it",
            "google/gemma-2-27b-it",
            "deepseek-ai/deepseek-llm-7b-chat",
            "microsoft/phi-3-mini-128k-instruct",
            "anthropic/claude-3-haiku",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai/gpt-4-turbo",
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "google/gemini-pro-1.5",
        ]
    return [
        "qwen/qwen-2.5-7b-instruct",
        "qwen/qwen-2.5-14b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.2-1b-instruct",
        "mistralai/mistral-7b-instruct",
        "google/gemma-2-9b-it",
        "google/gemma-2-27b-it",
        "deepseek-ai/deepseek-llm-7b-chat",
        "microsoft/phi-3-mini-128k-instruct",
        "anthropic/claude-3-haiku",
    ]


class AnthropicProvider:
    """Anthropic Claude provider implementation via OpenRouter"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = None
    ):
        # Use OpenRouter API key
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = OPENROUTER_BASE_URL
        
        # Get allowed models based on USE_PAID_MODELS
        allowed_models = get_allowed_models()
        
        # Filter models that work with Anthropic via OpenRouter
        anthropic_models = [m for m in allowed_models if m.startswith("anthropic/")]
        
        # Set default model
        if default_model:
            self.default_model = default_model
        elif anthropic_models:
            # Prioritize Claude 3.5 Sonnet, then Opus, then Haiku
            priority_models = [
                "anthropic/claude-3.5-sonnet",
                "anthropic/claude-3-opus",
                "anthropic/claude-3-haiku"
            ]
            self.default_model = next(
                (m for m in priority_models if m in anthropic_models),
                anthropic_models[0]
            )
        else:
            self.default_model = "anthropic/claude-3.5-sonnet"

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
        Generate text using Anthropic Claude via OpenRouter

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
            raise ValueError("OpenRouter API key not configured")

        import time
        start_time = time.time()

        # Build system message
        if system_prompt:
            system = system_prompt
        elif context:
            system = f"Context: {context}"
        else:
            system = "You are a helpful assistant for a real estate platform."

        async with httpx.AsyncClient() as client:
            # OpenRouter uses OpenAI-compatible format for Anthropic
            payload = {
                "model": self.default_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
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
                raise Exception(f"Anthropic via OpenRouter error: {response.text}")

            data = response.json()

            content = ""
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]

            usage = data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)

            return {
                "content": content,
                "model": self.default_model,
                "tokens_used": tokens_used,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

    async def generate_with_tools(
        self,
        prompt: str,
        tools: list,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate text with tool use capability

        Args:
            prompt: User prompt
            tools: List of tool definitions (OpenAI tool format)
            context: Additional context

        Returns:
            Dict with content, tool use, and tokens_used
        """
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        import time
        start_time = time.time()

        system = f"Context: {context}" if context else "You are a helpful assistant."

        async with httpx.AsyncClient() as client:
            payload = {
                "model": self.default_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "tools": tools,
                "temperature": 0.7,
                "max_tokens": 2000,
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
                raise Exception(f"Anthropic via OpenRouter error: {response.text}")

            data = response.json()

            message = data["choices"][0]["message"]
            content = message.get("content", "")
            function_call = message.get("tool_calls", None)

            usage = data.get("usage", {})

            return {
                "content": content,
                "function_call": function_call,
                "model": self.default_model,
                "tokens_used": usage.get("total_tokens", 0),
                "latency_ms": int((time.time() - start_time) * 1000)
            }
