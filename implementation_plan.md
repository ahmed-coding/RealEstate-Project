# Implementation Plan

[Overview]
Refactor the LLM router to use OpenRouter as the unified API gateway for all providers (OpenAI, Anthropic, Groq, Cohere, HuggingFace) with a base_url of "https://openrouter.ai/api/v1". Add support for a USE_PAID_MODELS environment variable to toggle between free and paid models, and add a new Google Gemini provider.

[Types]
The type system changes involve:

**New LLM Provider Enum Value:**
- `GEMINI = "gemini"` - Add to LLMProvider enum

**Environment Variables:**
- `USE_PAID_MODELS` (bool) - Toggle between free-only and all models from OpenRouter
- `OPENROUTER_API_KEY` (str) - API key for OpenRouter
- `GEMINI_API_KEY` (str) - API key for Google Gemini

**Model Lists:**
- `FREE_MODELS` - List of free tier models available via OpenRouter
- `PAID_MODELS` - List of premium models (only used when USE_PAID_MODELS=true)
- `ALL_MODELS` - Combined list of all available models

[Files]
**New Files to Create:**
- `backend/services/ai-service/llm_router/providers/gemini_provider.py` - New Google Gemini provider implementation

**Existing Files to Modify:**
- `backend/services/ai-service/llm_router/router.py`:
  - Add GEMINI to LLMProvider enum
  - Add GeminiProvider to providers dictionary
  - Update TASK_PROVIDER_MAP to include Gemini
  - Update _find_provider_by_model to recognize gemini models
  - Add model filtering based on USE_PAID_MODELS env var
  - Update all provider classes to use OpenRouter base_url

- `backend/services/ai-service/llm_router/providers/openai_provider.py`:
  - Update to use OpenRouter base_url dynamically
  - Add model filtering based on USE_PAID_MODELS

- `backend/services/ai-service/requirements.txt`:
  - Add google-generativeai package for Gemini support

[Functions]
**New Functions:**
- `get_free_models()` - Returns list of free models from OpenRouter
- `get_all_models()` - Returns list of all models from OpenRouter
- `get_allowed_models()` - Returns models based on USE_PAID_MODELS setting

**Modified Functions:**
- `OllamaProvider.__init__` - No change (local provider)
- `HuggingFaceProvider.__init__` - No change (uses HuggingFace API directly)
- `CohereProvider.__init__` - Update to use OpenRouter base_url
- `GroqProvider.__init__` - Update to use OpenRouter base_url
- `AnthropicProvider.__init__` - Update to use OpenRouter base_url
- `OpenAIProvider.__init__` - Already uses OpenRouter, add model filtering

[Classes]
**New Classes:**
- `GeminiProvider` - Google Gemini provider using OpenAI-compatible API via OpenRouter or direct Gemini API

**Modified Classes:**
- `LLMProvider` - Add GEMINI enum value
- `LLMRouter` - Add GeminiProvider to providers, update routing logic

[Dependencies]
**New Packages:**
- `google-generativeai>=0.3.0` - For Google Gemini API

[Testing]
**Test Requirements:**
- Test model filtering with USE_PAID_MODELS=true/false
- Test Gemini provider integration
- Test provider fallback when models are unavailable

[Implementation Order]
1. Update `router.py` - Add GEMINI to enum and update model filtering logic
2. Create `gemini_provider.py` - New Gemini provider
3. Update `openai_provider.py` - Add model filtering
4. Update `router.py` providers - Change Cohere, Groq, Anthropic to use OpenRouter
5. Update `requirements.txt` - Add google-generativeai
6. Test the implementation
