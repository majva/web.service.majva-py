from pydantic import BaseModel
from datetime import datetime


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    message: str
    date_time: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "message": "version: 1.3.10.45",
                "date_time": "2024-04-05T12:00:00"
            }
        }
