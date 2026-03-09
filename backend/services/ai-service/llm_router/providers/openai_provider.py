"""
OpenAI Provider
OpenAI GPT integration for LLM requests
"""
import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI


class OpenAIProvider:
    """OpenAI GPT provider implementation"""

    def __init__(self, api_key: Optional[str] = None, default_model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.default_model = default_model
        self.client = None

        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        context: Dict[str, Any] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using OpenAI GPT

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
            raise ValueError("OpenAI API key not configured")

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
            raise ValueError("OpenAI API key not configured")

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
