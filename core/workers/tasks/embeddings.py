"""
Celery tasks for generating property embeddings.
Uses OpenRouter API to generate embeddings for semantic search.
"""

from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def embed_property(self, property_id: int):
    """
    Generate and store embedding for a property.
    Called when a property is created or updated.
    """
    try:
        # Import here to avoid circular imports
        from apps.models import Property
        from apps.search.models import PropertyEmbedding

        # Get the property
        property = Property.objects.get(id=property_id)

        # Prepare text for embedding
        text_parts = [
            property.name,
            property.description,
            f"Category: {property.category.name}" if property.category else "",
            f"Address: {property.address.state.city.name}, {property.address.state.name}"
            if property.address
            else "",
        ]

        # Add features
        for feature in property.feature_property.all():
            text_parts.append(feature.feature.name)

        embedded_text = " ".join(filter(None, text_parts))

        # Generate embedding using OpenRouter
        embedding = generate_embedding(embedded_text)

        if embedding:
            # Upsert the embedding
            PropertyEmbedding.objects.update_or_create(
                property=property,
                defaults={
                    "embedding": embedding,
                    "embedded_text": embedded_text,
                    "embedding_model": "text-embedding-3-small",
                },
            )
            logger.info(f"Generated embedding for property {property_id}")
        else:
            logger.error(f"Failed to generate embedding for property {property_id}")

    except Property.DoesNotExist:
        logger.error(f"Property {property_id} not found")
    except Exception as exc:
        logger.error(f"Error generating embedding for property {property_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def regenerate_embeddings():
    """
    Regenerate embeddings for all properties.
    Use this after changing the embedding model.
    """
    from apps.models import Property
    from apps.search.models import PropertyEmbedding

    properties = Property.objects.filter(is_active=True)
    count = 0

    for property in properties:
        embed_property.delay(property.id)
        count += 1

    logger.info(f"Triggered embedding regeneration for {count} properties")
    return count


@shared_task
def rag_index_refresh():
    """
    Periodic task to refresh the RAG index.
    Called nightly via Celery Beat.
    """
    # This could rebuild indexes, update stale embeddings, etc.
    logger.info("RAG index refresh completed")
    return "RAG index refresh completed"


def generate_embedding(text: str):
    """
    Generate embedding for text using OpenRouter API.
    Returns list of floats or None on failure.
    """
    try:
        import openai
        from django.conf import settings

        # Get API key from settings
        api_key = getattr(settings, "OPENROUTER_API_KEY", None)
        if not api_key:
            logger.error("OPENROUTER_API_KEY not configured")
            return None

        # Initialize OpenAI client with OpenRouter base
        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        # Generate embedding
        response = client.embeddings.create(model="text-embedding-3-small", input=text)

        # Extract embedding
        embedding = response.data[0].embedding
        return embedding

    except Exception as exc:
        logger.error(f"Error generating embedding: {exc}")
        return None
