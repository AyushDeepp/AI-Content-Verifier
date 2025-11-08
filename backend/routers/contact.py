from fastapi import APIRouter, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime

from core.database import get_database
from models.contact_model import ContactCreate, ContactResponse

router = APIRouter(prefix="/api/contact", tags=["contact"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact(contact_data: ContactCreate):
    """Submit a contact form message"""
    if not contact_data.name or not contact_data.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name and message are required"
        )
    
    db = get_database()
    contacts_collection: AsyncIOMotorCollection = db["contacts"]
    
    contact_doc = {
        "name": contact_data.name,
        "email": contact_data.email,
        "message": contact_data.message,
        "timestamp": datetime.utcnow()
    }
    
    result_id = await contacts_collection.insert_one(contact_doc)
    
    return ContactResponse(
        id=str(result_id.inserted_id),
        name=contact_data.name,
        email=contact_data.email,
        message=contact_data.message,
        timestamp=contact_doc["timestamp"]
    )

