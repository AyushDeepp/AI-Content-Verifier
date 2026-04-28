from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class ResultCreate(BaseModel):
    type: Literal["text", "image", "video"]
    result: bool
    confidence: float
    content: Optional[str] = None
    analysis_details: Optional[list] = None


class ResultResponse(BaseModel):
    id: str
    user_id: str
    type: str
    result: bool
    confidence: float
    content: Optional[str] = None
    timestamp: datetime
    analysis_details: Optional[list] = None
    
    class Config:
        from_attributes = True


class ResultStats(BaseModel):
    total_verifications: int
    text_count: int
    image_count: int
    video_count: int
    ai_detected: int
    human_detected: int

