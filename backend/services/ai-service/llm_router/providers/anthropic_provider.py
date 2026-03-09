"""
Anthropic Provider
Anthropic Claude integration for LLM requests
"""
import os
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic


class AnthropicProvider:
    """Anthropic Claude provider implementation"""

    def __init__(self, api_key: Optional[str] = None, default_model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.default_model = default_model
        self.client = None

        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        context: Dict[str, Any] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using Anthropic Claude

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
            raise ValueError("Anthropic API key not configured")

        # Build messages
        messages = []

        if system_prompt:
            # Anthropic uses system parameter
            system = system_prompt
        elif context:
            system = f"Context: {context}"
        else:
            system = "You are a helpful assistant for a real estate platform."

        messages.append({"role": "user", "content": prompt})

        # Make API call
        response = await self.client.messages.create(
            model=self.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages
        )

        # Extract content
        content = ""
        if response.content:
            content = response.content[0].text

        return {
            "content": content,
            "model": response.model,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
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
            tools: List of tool definitions (Anthropic tool use format)
            context: Additional context

        Returns:
            Dict with content, tool use, and tokens_used
        """
        if not self.client:
            raise ValueError("Anthropic API key not configured")

        system = f"Context: {context}" if context else "You are a helpful assistant."

        messages = [{"role": "user", "content": prompt}]

        # Convert OpenAI tools format to Anthropic format
        anthropic_tools = self._convert_tools(tools)

        response = await self.client.messages.create(
            model=self.default_model,
            max_tokens=2000,
            temperature=0.7,
            system=system,
            messages=messages,
            tools=anthropic_tools
        )

        # Check for tool use
        tool_use = None
        content = ""

        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_use = block

        return {
            "content": content,
            "tool_use": tool_use,
            "model": response.model,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }

    def _convert_tools(self, openai_tools: list) -> list:
        """
        Convert OpenAI tool format to Anthropic format

        Args:
            openai_tools: List of OpenAI tool definitions

        Returns:
            List of Anthropic tool definitions
        """
        # Simplified conversion - in production, implement full conversion
        anthropic_tools = []

        for tool in openai_tools:
            anthropic_tool = {
                "name": tool.get("name"),
                "description": tool.get("description"),
                "input_schema": tool.get("parameters", {})
            }
            anthropic_tools.append(anthropic_tool)

        return anthropic_tools
