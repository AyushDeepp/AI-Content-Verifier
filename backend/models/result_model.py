from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class ResultCreate(BaseModel):
    type: Literal["text", "image", "video"]
    result: bool  # True = AI-generated, False = Human-generated
    confidence: float  # 0.0 to 1.0
    content: Optional[str] = None  # For text, store the text content


class ResultResponse(BaseModel):
    id: str
    user_id: str
    type: str
    result: bool
    confidence: float
    content: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ResultStats(BaseModel):
    total_verifications: int
    text_count: int
    image_count: int
    video_count: int
    ai_detected: int
    human_detected: int

