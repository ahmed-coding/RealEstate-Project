"""
Shared AI Schemas
Pydantic models for AI service communication
"""
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from decimal import Decimal


class LLMTaskType(str, Enum):
    """LLM task types for routing"""
    DESCRIPTION_GENERATION = "description_generation"
    PRICE_REASONING = "price_reasoning"
    CONVERSATIONAL_CHAT = "conversational_chat"
    ANALYTICS = "analytics"
    RECOMMENDATION = "recommendation"


class LLMProvider(str, Enum):
    """LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class LLMRequest(BaseModel):
    """Request schema for LLM processing"""
    task_type: LLMTaskType
    prompt: str
    context: Dict[str, Any] = {}
    model_preference: Optional[LLMProvider] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=10000)


class LLMResponse(BaseModel):
    """Response schema from LLM"""
    content: str
    model_used: str
    provider: LLMProvider
    tokens_used: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class PricePredictionInput(BaseModel):
    """Input for price prediction"""
    location: str
    property_size: int
    property_type: str
    number_of_rooms: int = 0
    number_of_bathrooms: int = 0
    amenities: List[str] = []
    nearby_prices: List[Decimal] = []


class PricePredictionOutput(BaseModel):
    """Output from price prediction"""
    estimated_price: Decimal
    price_range_low: Decimal
    price_range_high: Decimal
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    model_used: str


class PropertyDescriptionInput(BaseModel):
    """Input for property description generation"""
    property_name: str
    property_type: str
    location: str
    size: int
    rooms: int = 0
    bathrooms: int = 0
    amenities: List[str] = []
    nearby_attractions: List[str] = []
    style: str = "professional"  # professional, casual, luxury


class PropertyDescriptionOutput(BaseModel):
    """Output from property description generation"""
    description: str
    short_description: str
    key_highlights: List[str] = []
    model_used: str


class RecommendationInput(BaseModel):
    """Input for recommendations"""
    user_id: int
    limit: int = Field(default=10, ge=1, le=50)
    recommendation_type: str = "hybrid"  # behavioral, content, hybrid


class RecommendationOutput(BaseModel):
    """Output from recommendations"""
    property_ids: List[int]
    scores: List[float] = []
    recommendation_type: str
    model_used: str


class RAGQueryInput(BaseModel):
    """Input for RAG-powered query"""
    user_question: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class RAGQueryOutput(BaseModel):
    """Output from RAG query"""
    answer: str
    sources: List[Dict[str, Any]] = []
    model_used: str
    citations: List[str] = []


class ToolDefinition(BaseModel):
    """AI tool definition schema"""
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str


class ToolCall(BaseModel):
    """Tool call request from AI"""
    tool_name: str
    parameters: Dict[str, Any]


class ToolResult(BaseModel):
    """Tool call result"""
    tool_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None


class EmbeddingInput(BaseModel):
    """Input for embedding generation"""
    text: str
    model: str = "text-embedding-ada-002"


class EmbeddingOutput(BaseModel):
    """Output from embedding generation"""
    embedding: List[float]
    model: str
    tokens: int


class VectorSearchInput(BaseModel):
    """Input for vector search"""
    query_embedding: List[float]
    top_k: int = Field(default=5, ge=1, le=50)
    filter_criteria: Dict[str, Any] = {}


class VectorSearchOutput(BaseModel):
    """Output from vector search"""
    results: List[Dict[str, Any]]
    distances: List[float] = []
