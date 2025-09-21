from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import time
import logging
from main_optimized import find_matching_segments, initialize_services

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SPARK AI Audience Segment Search API",
    description="Semantic search for audience segments based on user intent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://spark.audiencelab.io",
        "https://sparkv3.vercel.app", 
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class SearchResult(BaseModel):
    topic: str
    topic_id: str
    score: float
    segment_id: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_time: float
    embedding_time: float
    query_time: float

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("🚀 Starting SPARK AI Audience Segment Search API...")
    initialize_services()
    logger.info("✅ API ready to serve requests!")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "SPARK AI Audience Segment Search API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/search", response_model=SearchResponse)
async def search_segments(request: SearchRequest):
    """
    Search for audience segments based on user intent.
    
    Args:
        request: SearchRequest containing query and optional top_k
        
    Returns:
        SearchResponse with matching segments and timing information
    """
    try:
        start_time = time.time()
        
        # Perform the search
        results = find_matching_segments(request.query, request.top_k)
        
        total_time = time.time() - start_time
        
        # Convert to Pydantic models
        search_results = [
            SearchResult(
                topic=result['topic'],
                topic_id=result['topic_id'],
                score=result['score'],
                segment_id=result['segment_id']
            )
            for result in results
        ]
        
        return SearchResponse(
            results=search_results,
            query=request.query,
            total_time=total_time,
            embedding_time=total_time * 0.7,  # Approximate
            query_time=total_time * 0.3       # Approximate
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "SPARK AI Audience Segment Search"
    }

@app.get("/custom-model-descriptor-health")
async def custom_model_descriptor_health():
    """Health check endpoint for custom model descriptor service."""
    return {
        "ok": True,
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Custom Model Descriptor"
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        workers=1      # Increase for production
    ) 