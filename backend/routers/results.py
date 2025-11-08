from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Annotated, List
from bson import ObjectId
from datetime import datetime

from routers.auth import get_current_user
from core.database import get_database
from models.result_model import ResultResponse, ResultStats

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/", response_model=List[ResultResponse])
async def get_user_results(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    skip: int = 0
):
    """Get all verification results for the current user"""
    db = get_database()
    results_collection: AsyncIOMotorCollection = db["results"]
    
    cursor = results_collection.find(
        {"user_id": ObjectId(current_user["_id"])}
    ).sort("timestamp", -1).skip(skip).limit(limit)
    
    results = await cursor.to_list(length=limit)
    
    return [
        ResultResponse(
            id=str(result["_id"]),
            user_id=str(result["user_id"]),
            type=result["type"],
            result=result["result"],
            confidence=result["confidence"],
            content=result.get("content"),
            timestamp=result["timestamp"]
        )
        for result in results
    ]


@router.get("/stats", response_model=ResultStats)
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get verification statistics for the current user"""
    db = get_database()
    results_collection: AsyncIOMotorCollection = db["results"]
    
    user_id = ObjectId(current_user["_id"])
    
    # Get total count
    total = await results_collection.count_documents({"user_id": user_id})
    
    # Get counts by type
    text_count = await results_collection.count_documents(
        {"user_id": user_id, "type": "text"}
    )
    image_count = await results_collection.count_documents(
        {"user_id": user_id, "type": "image"}
    )
    video_count = await results_collection.count_documents(
        {"user_id": user_id, "type": "video"}
    )
    
    # Get AI vs Human detection counts
    ai_detected = await results_collection.count_documents(
        {"user_id": user_id, "result": True}
    )
    human_detected = await results_collection.count_documents(
        {"user_id": user_id, "result": False}
    )
    
    return ResultStats(
        total_verifications=total,
        text_count=text_count,
        image_count=image_count,
        video_count=video_count,
        ai_detected=ai_detected,
        human_detected=human_detected
    )

