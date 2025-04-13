import asyncio
from loguru import logger
from src.db.repository import MongoDBRepository
from src.config.settings import settings

async def test_connection():
    """Test MongoDB connection"""
    logger.info(f"Testing connection to: {settings.MONGODB_CONNECTION_STRING}")
    repo = MongoDBRepository()
    try:
        await repo.connect()
        logger.info("Connection successful!")
        await repo.close()
        return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("MongoDB connection test: SUCCESS")
    else:
        print("MongoDB connection test: FAILED")