from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Annotated
from datetime import datetime
from bson import ObjectId

from models.user_model import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    ProfileUpdate,
    PasswordValidate,
    PasswordChange,
)
from core.database import get_database
from core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    decode_access_token
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get current authenticated user from JWT token"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_doc = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_doc)
    
    # Return user without password
    user = await users_collection.find_one({"_id": result.inserted_id})
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"]
    )


@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login user and return JWT token"""
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    
    # Find user by email
    user = await users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user["full_name"],
        created_at=current_user["created_at"]
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile (full name only, email cannot be changed)"""
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    
    user_id = ObjectId(current_user["_id"])
    
    # Update only full_name
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"full_name": profile_data.full_name}}
    )
    
    # Get updated user
    updated_user = await users_collection.find_one({"_id": user_id})
    
    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        full_name=updated_user["full_name"],
        created_at=updated_user["created_at"]
    )


@router.post("/validate-password")
async def validate_password(
    password_data: PasswordValidate,
    current_user: dict = Depends(get_current_user)
):
    """Validate current password before allowing password change"""
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    
    user_id = ObjectId(current_user["_id"])
    user = await users_collection.find_one({"_id": user_id})
    
    if not verify_password(password_data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    return {"valid": True}


@router.post("/change-password", response_model=UserResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    db = get_database()
    users_collection: AsyncIOMotorCollection = db["users"]
    
    user_id = ObjectId(current_user["_id"])
    user = await users_collection.find_one({"_id": user_id})
    
    # Verify current password
    if not verify_password(password_data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password length
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Hash new password and update
    hashed_password = get_password_hash(password_data.new_password)
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    # Get updated user
    updated_user = await users_collection.find_one({"_id": user_id})
    
    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        full_name=updated_user["full_name"],
        created_at=updated_user["created_at"]
    )

