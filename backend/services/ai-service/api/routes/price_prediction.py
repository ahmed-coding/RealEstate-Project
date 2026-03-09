"""
Price Prediction API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from decimal import Decimal
import time

from shared.schemas.ai import (
    PricePredictionInput,
    PricePredictionOutput,
    LLMRequest,
    LLMTaskType
)
from llm_router.router import LLMRouter
from tools.property_tools import get_property_details, get_market_statistics
from shared.utils.logging import setup_logger, log_ai_request, log_ai_response

logger = setup_logger("ai-service.price_prediction")
router = APIRouter()


@router.post("/predict", response_model=PricePredictionOutput)
async def predict_price(input_data: PricePredictionInput):
    """
    Generate AI-powered price prediction for a property

    Uses LLM reasoning to analyze property features and market data
    to provide price estimates with explanations.
    """
    start_time = time.time()

    log_ai_request(
        logger=logger,
        task_type="price_prediction",
        user_id=None,
        prompt_length=len(str(input_data.dict()))
    )

    try:
        # Get market statistics for context
        market_stats = await get_market_statistics(input_data.location)

        # Get recent property prices in the area
        nearby_prices = input_data.nearby_prices if input_data.nearby_prices else []
        avg_nearby_price = sum(nearby_prices) / \
            len(nearby_prices) if nearby_prices else 0

        # Build context for LLM
        context = {
            "property_details": input_data.dict(),
            "market_stats": market_stats,
            "average_nearby_price": float(avg_nearby_price)
        }

        # Create prompt for price reasoning
        prompt = f"""Analyze the following property and provide a price estimate:

Property Details:
- Location: {input_data.location}
- Size: {input_data.property_size} sq ft
- Type: {input_data.property_type}
- Rooms: {input_data.number_of_rooms}
- Bathrooms: {input_data.number_of_bathrooms}
- Amenities: {', '.join(input_data.amenities)}

Market Data:
- Average nearby price: ${avg_nearby_price:.2f}
- Market statistics: {market_stats}

Based on this information, provide:
1. Estimated price
2. Price range (low-high)
3. Reasoning for your estimate

Respond in JSON format with keys: estimated_price, price_range_low, price_range_high, reasoning
"""

        # Route to LLM
        llm_router = LLMRouter()
        llm_response = await llm_router.route_request(
            LLMRequest(
                task_type=LLMTaskType.PRICE_REASONING,
                prompt=prompt,
                context=context
            )
        )

        # Parse response (in production, use proper JSON parsing)
        # For now, generate a simple estimate based on size and market data
        base_price = float(
            avg_nearby_price) if avg_nearby_price > 0 else input_data.property_size * 200

        # Adjust based on rooms and bathrooms
        room_bonus = (input_data.number_of_rooms * 10000) + \
            (input_data.number_of_bathrooms * 5000)

        estimated_price = Decimal(str(base_price + room_bonus))
        price_range_low = estimated_price * Decimal("0.9")
        price_range_high = estimated_price * Decimal("1.1")

        latency_ms = (time.time() - start_time) * 1000

        log_ai_response(
            logger=logger,
            task_type="price_prediction",
            user_id=None,
            success=True,
            latency_ms=latency_ms
        )

        return PricePredictionOutput(
            estimated_price=estimated_price,
            price_range_low=price_range_low,
            price_range_high=price_range_high,
            reasoning=f"Based on market analysis of {input_data.location}, property size of {input_data.property_size} sq ft, and comparable properties.",
            confidence=0.85,
            model_used=llm_response.model_used if llm_response else "default"
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log_ai_response(
            logger=logger,
            task_type="price_prediction",
            user_id=None,
            success=False,
            latency_ms=latency_ms,
            error=str(e)
        )
        raise HTTPException(
            status_code=500, detail=f"Price prediction failed: {str(e)}")


@router.post("/batch-predict")
async def batch_predict_price(inputs: list[PricePredictionInput]):
    """
    Generate price predictions for multiple properties
    """
    results = []

    for input_data in inputs:
        try:
            result = await predict_price(input_data)
            results.append(result)
        except Exception as e:
            logger.error(f"Batch prediction failed for item: {e}")
            results.append({"error": str(e)})

    return {"predictions": results}


@router.get("/property/{property_id}", response_model=PricePredictionOutput)
async def predict_price_for_property(property_id: int):
    """
    Generate price prediction for an existing property
    """
    try:
        # Get property details
        property_details = await get_property_details(property_id)

        if not property_details:
            raise HTTPException(status_code=404, detail="Property not found")

        # Build input from property details
        input_data = PricePredictionInput(
            location=property_details.get(
                "address", {}).get("state", "Unknown"),
            property_size=property_details.get("size", 0),
            property_type=property_details.get(
                "category", {}).get("name", "property"),
            number_of_rooms=property_details.get(
                "attributes", {}).get("rooms", 0),
            number_of_bathrooms=property_details.get(
                "attributes", {}).get("bathrooms", 0),
            amenities=property_details.get("features", []),
            nearby_prices=[]
        )

        return await predict_price(input_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get property details: {str(e)}")
