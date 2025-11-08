from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGO_URI)
        mongodb.database = mongodb.client.get_database("ai_content_verifier")
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("Disconnected from MongoDB")


def get_database():
    """Get database instance"""
    return mongodb.database

