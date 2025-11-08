from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Annotated
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

from routers.auth import get_current_user
from core.database import get_database
from services.text_detector import detect_ai_text
from services.image_detector import detect_ai_image
from services.video_detector import detect_ai_video
from models.result_model import ResultResponse

router = APIRouter(prefix="/api/detect", tags=["detect"])


class TextDetectRequest(BaseModel):
    text: str


@router.post("/text", response_model=ResultResponse)
async def detect_text(
    request: TextDetectRequest,
    current_user: dict = Depends(get_current_user)
):
    """Detect if text is AI-generated"""
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    # Perform detection
    detection_result = await detect_ai_text(request.text)
    
    # Save result to database
    db = get_database()
    results_collection: AsyncIOMotorCollection = db["results"]
    
    result_doc = {
        "user_id": ObjectId(current_user["_id"]),
        "type": "text",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": request.text[:1000],  # Store first 1000 chars
        "timestamp": datetime.utcnow()
    }
    
    result_id = await results_collection.insert_one(result_doc)
    
    return ResultResponse(
        id=str(result_id.inserted_id),
        user_id=str(current_user["_id"]),
        type="text",
        result=detection_result["result"],
        confidence=detection_result["confidence"],
        content=request.text[:1000],
        timestamp=result_doc["timestamp"]
    )


@router.post("/image", response_model=ResultResponse)
async def detect_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Detect if image is AI-generated"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Read file content
    image_data = await file.read()
    
    # Validate file size (max 10MB)
    if len(image_data) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large (max 10MB)"
        )
    
    # Perform detection
    detection_result = await detect_ai_image(image_data)
    
    # Save result to database
    db = get_database()
    results_collection: AsyncIOMotorCollection = db["results"]
    
    result_doc = {
        "user_id": ObjectId(current_user["_id"]),
        "type": "image",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": None,
        "timestamp": datetime.utcnow()
    }
    
    result_id = await results_collection.insert_one(result_doc)
    
    return ResultResponse(
        id=str(result_id.inserted_id),
        user_id=str(current_user["_id"]),
        type="image",
        result=detection_result["result"],
        confidence=detection_result["confidence"],
        content=None,
        timestamp=result_doc["timestamp"]
    )


@router.post("/video", response_model=ResultResponse)
async def detect_video(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Detect if video is AI-generated"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )
    
    # Read file content
    video_data = await file.read()
    
    # Validate file size (max 100MB)
    if len(video_data) > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video file too large (max 100MB)"
        )
    
    # Perform detection
    detection_result = await detect_ai_video(video_data)
    
    # Save result to database
    db = get_database()
    results_collection: AsyncIOMotorCollection = db["results"]
    
    result_doc = {
        "user_id": ObjectId(current_user["_id"]),
        "type": "video",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": None,
        "timestamp": datetime.utcnow()
    }
    
    result_id = await results_collection.insert_one(result_doc)
    
    return ResultResponse(
        id=str(result_id.inserted_id),
        user_id=str(current_user["_id"]),
        type="video",
        result=detection_result["result"],
        confidence=detection_result["confidence"],
        content=None,
        timestamp=result_doc["timestamp"]
    )

