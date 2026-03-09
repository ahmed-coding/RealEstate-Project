"""
RAG Engine
Retrieval Augmented Generation for AI Assistant
"""
from typing import Dict, Any, List, Optional
from rag.vector_store import VectorStore
from llm_router.router import LLMRouter
from shared.schemas.ai import LLMTaskType, LLMRequest


class RAGEngine:
    """Retrieval Augmented Generation engine"""

    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_router = LLMRouter()

    async def query(
        self,
        question: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        top_k: int = 5,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a query through RAG pipeline

        Args:
            question: User question
            user_id: User ID for personalization
            session_id: Session ID for conversation history
            top_k: Number of documents to retrieve
            system_prompt: Custom system prompt

        Returns:
            Dict with answer, sources, model_used
        """
        # Step 1: Retrieve relevant documents
        documents = await self.vector_store.search(
            query=question,
            top_k=top_k,
            user_id=user_id
        )

        # Step 2: Build context from retrieved documents
        context = self._build_context(documents)

        # Step 3: Generate answer using LLM
        prompt = self._build_prompt(question, context)

        if system_prompt:
            full_system = system_prompt + "\n\n" + self._get_base_system_prompt()
        else:
            full_system = self._get_base_system_prompt()

        response = await self.llm_router.route_request(
            LLMRequest(
                task_type=LLMTaskType.CONVERSATIONAL_CHAT,
                prompt=prompt,
                context={"documents": documents},
                temperature=0.7
            )
        )

        # Step 4: Extract sources and citations
        sources = [doc.get("source", "unknown") for doc in documents]
        citations = self._extract_citations(documents)

        return {
            "answer": response.content,
            "sources": sources,
            "model_used": response.model_used,
            "citations": citations,
            "documents": documents
        }

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents"""
        if not documents:
            return "No relevant information found."

        context_parts = ["Relevant information:\n"]

        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            source = doc.get("source", "unknown")

            context_parts.append(f"\n{i}. Source: {source}")
            context_parts.append(f"Content: {content}\n")

        return "\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        """Build the full prompt with question and context"""
        return f"""Based on the following context, answer the user's question.

Context:
{context}

Question: {question}

Provide a helpful, accurate response based on the context provided. If the context doesn't contain enough information to answer the question, acknowledge that and provide your best answer based on general knowledge."""

    def _get_base_system_prompt(self) -> str:
        """Get the base system prompt for the AI assistant"""
        return """You are a helpful AI assistant for a real estate platform. You can help users with:
- Finding properties
- Understanding market trends
- Property recommendations
- General real estate questions

Always be polite, accurate, and helpful. When possible, cite your sources."""

    def _extract_citations(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Extract citations from retrieved documents"""
        citations = []

        for doc in documents:
            source = doc.get("source", "")
            page = doc.get("page", "")

            citation = source
            if page:
                citation += f" (page {page})"

            citations.append(citation)

        return citations

    async def add_document(
        self,
        content: str,
        source: str,
        metadata: Dict[str, Any] = None
    ):
        """Add a document to the vector store"""
        await self.vector_store.add_document(
            content=content,
            source=source,
            metadata=metadata or {}
        )

    async def index_property(self, property_id: int):
        """Index a property for search"""
        # This would fetch property data and add to vector store
        # Placeholder implementation
        pass


class RecommendationEngine:
    """Recommendation engine using RAG"""

    def __init__(self):
        self.vector_store = VectorStore()

    async def get_behavioral_recommendations(
        self,
        user_id: int,
        favorites: List[int],
        search_history: List[str],
        limit: int = 10
    ) -> List[int]:
        """
        Get recommendations based on user behavior

        Args:
            user_id: User ID
            favorites: List of favorited property IDs
            search_history: List of search queries
            limit: Number of recommendations

        Returns:
            List of recommended property IDs
        """
        # Placeholder - in production, implement collaborative filtering
        # This would use user behavior to find similar users' preferences

        # For now, return empty list
        return []

    async def get_content_recommendations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[int]:
        """
        Get content-based recommendations

        Args:
            user_id: User ID
            limit: Number of recommendations

        Returns:
            List of recommended property IDs
        """
        # Placeholder - would use property features to find similar properties

        return []

    async def get_hybrid_recommendations(
        self,
        user_id: int,
        favorites: List[int],
        search_history: List[str],
        limit: int = 10
    ) -> List[int]:
        """
        Get hybrid recommendations combining behavioral and content-based

        Args:
            user_id: User ID
            favorites: List of favorited property IDs
            search_history: List of search queries
            limit: Number of recommendations

        Returns:
            List of recommended property IDs
        """
        # Combine both approaches
        # In production, would weight and combine results

        return []

    async def get_similar_properties(
        self,
        property_id: int,
        limit: int = 5
    ) -> List[int]:
        """
        Get properties similar to a given property

        Args:
            property_id: Reference property ID
            limit: Number of similar properties

        Returns:
            List of similar property IDs
        """
        # Use vector similarity to find similar properties
        # Placeholder implementation

        return []

    async def get_trending_properties(
        self,
        limit: int = 10
    ) -> List[int]:
        """
        Get trending properties

        Args:
            limit: Number of trending properties

        Returns:
            List of trending property IDs
        """
        # Would query for most viewed/favorited properties
        # Placeholder

        return []
