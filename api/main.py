from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
import json
import os
from delta_client import DeltaClient
from models import Alert, Topic, AlertResponse, TopicResponse
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AlphaPhage API",
    description="REST API for AlphaPhage narrative mining platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for Delta client
def get_delta_client():
    client = DeltaClient()
    try:
        yield client
    finally:
        client.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/v1/alerts", response_model=List[Alert])
async def get_alerts(
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30),
    client: DeltaClient = Depends(get_delta_client)
):
    """Fetch recent alerts with optional filtering"""
    try:
        alerts = client.get_alerts(limit, severity, days)
        return alerts
    except Exception as e:
        logger.error(json.dumps({"event": "get_alerts_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="Error fetching alerts")

@app.get("/api/v1/topics", response_model=List[Topic])
async def get_topics(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(2, ge=1, le=30),
    client: DeltaClient = Depends(get_delta_client)
):
    """Fetch trending topics from the last few days"""
    try:
        topics = client.get_trending_topics(limit, days)
        return topics
    except Exception as e:
        logger.error(json.dumps({"event": "get_topics_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="Error fetching topics")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", Config.PORT))
    uvicorn.run(app, host=Config.HOST, port=port)