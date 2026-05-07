from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Annotated
import os
import uuid
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

from routers.auth import get_current_user
from core.database import get_database
from core.r2_storage import is_r2_configured, upload_to_r2
from services.text_detector import detect_ai_text
from services.image_detector import detect_ai_image
from services.video_detector import detect_ai_video
from models.result_model import ResultResponse

router = APIRouter(prefix="/api/detect", tags=["detect"])


class TextDetectRequest(BaseModel):
    text: str


def save_file(file_data: bytes, file_name: str, content_type: str) -> str:
    """Save file to R2 if configured, otherwise local uploads/ folder."""
    if is_r2_configured():
        return upload_to_r2(file_data, file_name, content_type)
    else:
        file_path = os.path.join("uploads", file_name)
        with open(file_path, "wb") as f:
            f.write(file_data)
        return f"/uploads/{file_name}"


@router.post("/text")
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
        "timestamp": datetime.utcnow(),
        "analysis_details": detection_result.get("analysis_details")
    }
    
    result_id = await results_collection.insert_one(result_doc)
    
    # Build response with analysis details if available
    response_data = {
        "id": str(result_id.inserted_id),
        "user_id": str(current_user["_id"]),
        "type": "text",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": request.text[:1000],
        "timestamp": result_doc["timestamp"]
    }
    
    # Add analysis_details if present
    if "analysis_details" in detection_result:
        response_data["analysis_details"] = detection_result["analysis_details"]
    
    return response_data


@router.post("/image")
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
    
    # Save file to R2 or local
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_url = save_file(image_data, file_name, file.content_type or "image/png")
    
    # Save result to database
    db = get_database()
    results_collection: AsyncIOMotorCollection = db["results"]
    
    result_doc = {
        "user_id": ObjectId(current_user["_id"]),
        "type": "image",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": file_url,
        "timestamp": datetime.utcnow(),
        "analysis_details": detection_result.get("analysis_details")
    }
    
    result_id = await results_collection.insert_one(result_doc)
    
    # Build response with analysis details if available
    response_data = {
        "id": str(result_id.inserted_id),
        "user_id": str(current_user["_id"]),
        "type": "image",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": file_url,
        "timestamp": result_doc["timestamp"]
    }
    
    # Add analysis_details if present
    if "analysis_details" in detection_result:
        response_data["analysis_details"] = detection_result["analysis_details"]
    
    return response_data


@router.post("/video")
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
    
    # Save file to R2 or local
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "mp4"
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_url = save_file(video_data, file_name, file.content_type or "video/mp4")
    
    # Save result to database
    db = get_database()
    results_collection: AsyncIOMotorCollection = db["results"]
    
    result_doc = {
        "user_id": ObjectId(current_user["_id"]),
        "type": "video",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": file_url,
        "timestamp": datetime.utcnow(),
        "analysis_details": detection_result.get("analysis_details")
    }
    
    result_id = await results_collection.insert_one(result_doc)
    
    # Build response with analysis details if available
    response_data = {
        "id": str(result_id.inserted_id),
        "user_id": str(current_user["_id"]),
        "type": "video",
        "result": detection_result["result"],
        "confidence": detection_result["confidence"],
        "content": file_url,
        "timestamp": result_doc["timestamp"]
    }
    
    # Add analysis_details if present
    if "analysis_details" in detection_result:
        response_data["analysis_details"] = detection_result["analysis_details"]
    
    return response_data


