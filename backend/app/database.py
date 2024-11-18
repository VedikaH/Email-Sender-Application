from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
from typing import Optional
import logging

class Database:
    client: Optional[AsyncIOMotorClient] = None # type: ignore
    
    # settings = get_settings()
    @classmethod
    async def connect_db(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            # Test the connection
            await cls.client.admin.command('ping')
            logging.info("Successfully connected to MongoDB")
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        if cls.client:
            try:
                await cls.client.close()
                logging.info("MongoDB connection closed")
            except Exception as e:
                logging.error(f"Error closing MongoDB connection: {e}")
    
    @classmethod
    async def get_db(cls):
        if not cls.client:
            await cls.connect_db()
        return cls.client.email_sender
    
    @classmethod
    async def test_connection(cls):
        try:
            db = await cls.get_db()
            # Try to perform a simple operation
            await db.command('ping')
            return True
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            return False