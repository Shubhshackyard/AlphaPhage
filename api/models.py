from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Alert(BaseModel):
    alert_id: str = Field(..., description="Unique identifier for the alert")
    alert_time: datetime = Field(..., description="When the alert was generated")
    alert_message: str = Field(..., description="Alert message")
    topic_id: int = Field(..., description="Topic ID associated with the alert")
    topic_label: str = Field(..., description="Topic label")
    volume: int = Field(..., description="Topic volume")
    expected_volume: float = Field(..., description="Expected topic volume")
    z_score: float = Field(..., description="Z-score of the anomaly")
    severity: str = Field(..., description="Alert severity (LOW, MEDIUM, HIGH)")
    
    class Config:
        schema_extra = {
            "example": {
                "alert_id": "550e8400-e29b-41d4-a716-446655440000",
                "alert_time": "2023-10-15T14:30:00Z",
                "alert_message": "Anomaly detected in topic: bitcoin crash",
                "topic_id": 42,
                "topic_label": "bitcoin crash market",
                "volume": 1500,
                "expected_volume": 500.0,
                "z_score": 4.2,
                "severity": "HIGH"
            }
        }

class Topic(BaseModel):
    topic_id: int = Field(..., description="Topic ID")
    topic_label: str = Field(..., description="Topic label")
    volume: int = Field(..., description="Number of mentions")
    last_updated: datetime = Field(..., description="Last update time")
    
    class Config:
        schema_extra = {
            "example": {
                "topic_id": 42,
                "topic_label": "bitcoin crash market",
                "volume": 1500,
                "last_updated": "2023-10-15T14:30:00Z"
            }
        }

class AlertResponse(BaseModel):
    alerts: List[Alert]
    
class TopicResponse(BaseModel):
    topics: List[Topic]