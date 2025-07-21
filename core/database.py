# Create core/database.py
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from core.config import settings
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Global database client and connection
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """Connect to MongoDB on application startup."""
    global client, db
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB_NAME]
        
        # Verify connection is working
        await client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    """Close MongoDB connection on application shutdown."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Return database instance."""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo first.")
    return db


# Collection helpers
def get_collection(collection_name: str):
    """Get a specific collection from the database."""
    return get_database()[collection_name]