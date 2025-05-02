from fastapi import APIRouter, HTTPException
from typing import List
from .models import Alert, Topic
import json

router = APIRouter()

# Sample data for alerts and topics
alerts_data = [
    {"id": 1, "message": "Spike detected in topic A", "timestamp": "2023-10-01T12:00:00Z"},
    {"id": 2, "message": "Spike detected in topic B", "timestamp": "2023-10-01T12:05:00Z"},
]

topics_data = [
    {"id": 1, "name": "Topic A", "volume": 150},
    {"id": 2, "name": "Topic B", "volume": 200},
]

@router.get("/alerts", response_model=List[Alert])
async def get_alerts():
    return alerts_data

@router.get("/topics", response_model=List[Topic])
async def get_topics():
    return topics_data