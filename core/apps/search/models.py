"""
Search models for pgvector-based semantic search.
Replaces Algolia for property search.
"""

from django.db import models
from django.conf import settings

# Try to import pgvector VectorField, fall back to JSONField if not available
try:
    from pgvector.django import VectorField
except ImportError:
    # Fallback for when pgvector is not available
    VectorField = None


class PropertyEmbedding(models.Model):
    """
    Stores vector embeddings for properties for semantic search.
    Generated using OpenRouter AI models.
    """

    property = models.OneToOneField(
        "apps.Property", on_delete=models.CASCADE, related_name="embedding"
    )

    # Store embedding as vector (1536 dimensions for text-embedding-3-small)
    # Use JSONField as fallback if pgvector is not available
    if VectorField:
        embedding = VectorField(dimensions=1536)
    else:
        # Fallback: store as JSON list of floats
        embedding = models.JSONField(default=list)

    # Source text used to generate embedding (useful for debugging)
    embedded_text = models.TextField(blank=True, default="")

    # Model used to generate the embedding
    embedding_model = models.CharField(max_length=100, default="text-embedding-3-small")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PropertyEmbedding"
        indexes = [
            # Note: HnswIndex requires pgvector extension
            # Will be created when migrations run with pgvector enabled
        ]

    def __str__(self):
        return f"Embedding for {self.property.name}"


class SearchQueryLog(models.Model):
    """
    Logs search queries for analytics and improving search results.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_logs",
    )
    query = models.CharField(max_length=500)
    search_type = models.CharField(
        max_length=20,
        choices=[
            ("keyword", "Keyword"),
            ("semantic", "Semantic"),
            ("hybrid", "Hybrid"),
        ],
        default="hybrid",
    )
    results_count = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "SearchQueryLog"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.query} - {self.search_type}"
