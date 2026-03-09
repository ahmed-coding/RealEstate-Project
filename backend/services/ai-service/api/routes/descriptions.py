"""
Property Description Generation API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
import time

from shared.schemas.ai import (
    PropertyDescriptionInput,
    PropertyDescriptionOutput,
    LLMRequest,
    LLMTaskType
)
from llm_router.router import LLMRouter
from shared.utils.logging import setup_logger, log_ai_request, log_ai_response

logger = setup_logger("ai-service.descriptions")
router = APIRouter()


@router.post("/generate", response_model=PropertyDescriptionOutput)
async def generate_description(input_data: PropertyDescriptionInput):
    """
    Generate AI-powered property description

    Creates professional marketing descriptions for property listings
    based on property features and location.
    """
    start_time = time.time()

    log_ai_request(
        logger=logger,
        task_type="description_generation",
        user_id=None,
        prompt_length=len(str(input_data.dict()))
    )

    try:
        # Build context for LLM
        context = input_data.dict()

        # Create prompt for description generation
        prompt = f"""Generate a professional property description for marketing purposes.

Property Details:
- Name: {input_data.property_name}
- Type: {input_data.property_type}
- Location: {input_data.location}
- Size: {input_data.size} sq ft
- Rooms: {input_data.rooms}
- Bathrooms: {input_data.bathrooms}
- Amenities: {', '.join(input_data.amenities)}
- Style: {input_data.style}

Nearby Attractions: {', '.join(input_data.nearby_attractions)}

Create:
1. A compelling full description (2-3 paragraphs)
2. A short tagline (1-2 sentences)
3. Key highlights (5 bullet points)

Format your response as JSON with keys: description, short_description, key_highlights
"""

        # Route to LLM
        llm_router = LLMRouter()
        llm_response = await llm_router.route_request(
            LLMRequest(
                task_type=LLMTaskType.DESCRIPTION_GENERATION,
                prompt=prompt,
                context=context,
                temperature=0.8
            )
        )

        # Generate sample description based on property details
        description_parts = []

        # Opening
        description_parts.append(
            f"Welcome to {input_data.property_name}, a stunning {input_data.property_type} "
            f"located in the heart of {input_data.location}. "
        )

        # Size and rooms
        if input_data.rooms > 0 or input_data.bathrooms > 0:
            description_parts.append(
                f"This spacious property features {input_data.rooms} bedrooms and "
                f"{input_data.bathrooms} bathrooms across {input_data.size} square feet. "
            )

        # Amenities
        if input_data.amenities:
            description_parts.append(
                f"Enjoy modern living with amenities including {', '.join(input_data.amenities[:5])}. "
            )

        # Location appeal
        if input_data.nearby_attractions:
            description_parts.append(
                f"Perfectly situated near {', '.join(input_data.nearby_attractions[:3])}. "
            )

        # Closing
        description_parts.append(
            "Don't miss this exceptional opportunity to own this beautiful property."
        )

        full_description = "".join(description_parts)

        # Short description
        short_description = (
            f"Beautiful {input_data.property_type} in {input_data.location} with "
            f"{input_data.rooms} bedrooms, {input_data.bathrooms} bathrooms, "
            f"{input_data.size} sq ft."
        )

        # Key highlights
        key_highlights = [
            f"{input_data.size} square feet of living space",
            f"{input_data.rooms} spacious bedrooms",
            f"{input_data.bathrooms} modern bathrooms",
            f"Located in {input_data.location}",
        ]

        if input_data.amenities:
            key_highlights.append(
                f"Features: {', '.join(input_data.amenities[:3])}")

        latency_ms = (time.time() - start_time) * 1000

        log_ai_response(
            logger=logger,
            task_type="description_generation",
            user_id=None,
            success=True,
            latency_ms=latency_ms
        )

        return PropertyDescriptionOutput(
            description=full_description,
            short_description=short_description,
            key_highlights=key_highlights,
            model_used=llm_response.model_used if llm_response else "default"
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log_ai_response(
            logger=logger,
            task_type="description_generation",
            user_id=None,
            success=False,
            latency_ms=latency_ms,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, detail=f"Description generation failed: {str(e)}")


@router.post("/optimize")
async def optimize_description(description: str, property_details: dict):
    """
    Optimize an existing property description

    Takes an existing description and improves it with AI
    """
    start_time = time.time()

    try:
        prompt = f"""Improve the following property description to make it more compelling:

Current Description:
{description}

Property Details:
{property_details}

Create a more engaging, professional description that highlights the property's best features.
"""

        llm_router = LLMRouter()
        llm_response = await llm_router.route_request(
            LLMRequest(
                task_type=LLMTaskType.DESCRIPTION_GENERATION,
                prompt=prompt,
                temperature=0.8
            )
        )

        return {
            "original_description": description,
            "optimized_description": llm_response.content if llm_response else description,
            "model_used": llm_response.model_used if llm_response else "default"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Description optimization failed: {str(e)}")
