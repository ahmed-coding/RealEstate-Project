"""
Search Service Main Application
FastAPI service for Elasticsearch-based property search
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

from elasticsearch import AsyncElasticsearch
from shared.utils.logging import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger("search-service", level=os.getenv("LOG_LEVEL", "INFO"))


# Elasticsearch client
es_client = None
INDEX_NAME = "properties"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global es_client

    # Startup
    logger.info("Starting Search Service...")

    # Connect to Elasticsearch
    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    es_client = AsyncElasticsearch([es_url])

    # Create index if not exists
    await create_index()

    yield

    # Shutdown
    logger.info("Shutting down Search Service...")
    if es_client:
        await es_client.close()


async def create_index():
    """Create Elasticsearch index with mappings"""
    try:
        if not await es_client.indices.exists(index=INDEX_NAME):
            await es_client.indices.create(
                index=INDEX_NAME,
                body={
                    "mappings": {
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "text", "analyzer": "standard"},
                            "description": {"type": "text", "analyzer": "standard"},
                            "price": {"type": "float"},
                            "size": {"type": "integer"},
                            "category": {"type": "keyword"},
                            "city": {"type": "keyword"},
                            "state": {"type": "keyword"},
                            "country": {"type": "keyword"},
                            "for_sale": {"type": "boolean"},
                            "for_rent": {"type": "boolean"},
                            "is_active": {"type": "boolean"},
                            "features": {"type": "keyword"},
                            "created_at": {"type": "date"}
                        }
                    }
                }
            )
            logger.info(f"Created index: {INDEX_NAME}")
    except Exception as e:
        logger.error(f"Error creating index: {e}")


# Create FastAPI application
app = FastAPI(
    title="Real Estate Search Service",
    description="Elasticsearch-based property search service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class PropertySearchRequest(BaseModel):
    query: str
    filters: Optional[dict] = None
    page: int = 1
    size: int = 10


class PropertyDocument(BaseModel):
    id: int
    name: str
    description: str
    price: float
    size: int
    category: str
    city: str
    state: str
    country: str
    for_sale: bool
    for_rent: bool
    is_active: bool
    features: List[str] = []


class SearchResponse(BaseModel):
    total: int
    page: int
    size: int
    results: List[PropertyDocument]


# Search endpoints
@app.post("/search", response_model=SearchResponse)
async def search_properties(request: PropertySearchRequest):
    """
    Search properties using Elasticsearch
    """
    try:
        # Build query
        must_clauses = []

        # Full-text search
        if request.query:
            must_clauses.append({
                "multi_match": {
                    "query": request.query,
                    "fields": ["name^3", "description", "features", "city", "state"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })

        # Apply filters
        if request.filters:
            for field, value in request.filters.items():
                if value is not None:
                    must_clauses.append({"term": {field: value}})

        # Default filter for active properties
        must_clauses.append({"term": {"is_active": True}})

        # Build final query
        query = {
            "bool": {
                "must": must_clauses
            }
        }

        # Pagination
        from_offset = (request.page - 1) * request.size

        # Execute search
        result = await es_client.search(
            index=INDEX_NAME,
            query=query,
            from_=from_offset,
            size=request.size,
            sort=[{"created_at": "desc"}]
        )

        # Parse results
        hits = result["hits"]
        total = hits["total"]["value"]

        results = []
        for hit in hits["hits"]:
            source = hit["_source"]
            results.append(PropertyDocument(**source))

        return SearchResponse(
            total=total,
            page=request.page,
            size=request.size,
            results=results
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/properties/{property_id}")
async def get_property(property_id: int):
    """Get a property by ID"""
    try:
        result = await es_client.get(index=INDEX_NAME, id=property_id)
        return result["_source"]
    except Exception as e:
        raise HTTPException(status_code=404, detail="Property not found")


@app.post("/properties")
async def index_property(property: PropertyDocument):
    """Index a property"""
    try:
        await es_client.index(
            index=INDEX_NAME,
            id=property.id,
            document=property.dict()
        )
        return {"status": "indexed", "id": property.id}
    except Exception as e:
        logger.error(f"Index error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/properties/{property_id}")
async def delete_property(property_id: int):
    """Delete a property from index"""
    try:
        await es_client.delete(index=INDEX_NAME, id=property_id)
        return {"status": "deleted", "id": property_id}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Property not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    es_status = "unknown"
    try:
        if es_client:
            await es_client.ping()
            es_status = "healthy"
    except:
        es_status = "unhealthy"

    return {
        "status": "healthy" if es_status == "healthy" else "degraded",
        "service": "search-service",
        "elasticsearch": es_status,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real Estate Search Service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("SEARCH_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("SEARCH_SERVICE_PORT", "8003"))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
