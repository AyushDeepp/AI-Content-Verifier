from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    message: str


class ContactResponse(BaseModel):
    id: str
    name: str
    email: str
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

