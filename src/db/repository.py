from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from loguru import logger

from src.config.settings import settings
from .models import UserDB, UserSession

class MongoDBRepository:
    """Repository class for MongoDB operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.users: Optional[AsyncIOMotorCollection] = None
        self.sessions: Optional[AsyncIOMotorCollection] = None
    
    async def connect(self):
        """Connect to MongoDB"""
        if self.client is None:
            try:
                self.client = AsyncIOMotorClient(
                    settings.MONGODB_CONNECTION_STRING,
                    ssl=True,
                    tlsAllowInvalidCertificates=True
                )
                self.db = self.client[settings.MONGODB_DATABASE]
                self.users = self.db.users
                self.sessions = self.db.sessions
                
                # Create indexes
                await self.users.create_index("telegram_id", unique=True)
                await self.sessions.create_index("telegram_id")
                await self.sessions.create_index("session_id", unique=True)
                await self.sessions.create_index([("telegram_id", 1), ("start_time", -1)])
                
                logger.info(f"Connected to MongoDB: {settings.MONGODB_DATABASE}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("Closed MongoDB connection")
    
    async def get_user(self, telegram_id: int) -> Optional[UserDB]:
        """Get user by Telegram ID"""
        if self.users is None:
            await self.connect()
        
        user_data = await self.users.find_one({"telegram_id": telegram_id})
        if user_data:
            return UserDB.from_dict(user_data)
        return None
    
    async def create_user(self, user: UserDB) -> UserDB:
        """Create a new user"""
        if self.users is None:
            await self.connect()
        
        user_dict = user.to_dict()
        await self.users.insert_one(user_dict)
        logger.info(f"Created new user: {user.telegram_id}")
        return user
    
    async def update_user(self, user: UserDB) -> UserDB:
        """Update an existing user"""
        if self.users is None:
            await self.connect()
        
        user_dict = user.to_dict()
        await self.users.update_one(
            {"telegram_id": user.telegram_id},
            {"$set": user_dict}
        )
        logger.info(f"Updated user: {user.telegram_id}")
        return user
    
    async def save_user(self, user: UserDB) -> UserDB:
        """Create or update user"""
        existing_user = await self.get_user(user.telegram_id)
        if existing_user:
            return await self.update_user(user)
        else:
            return await self.create_user(user)
    
    async def get_active_session(self, telegram_id: int) -> Optional[UserSession]:
        """Get the active (incomplete) session for a user"""
        if self.sessions is None:
            await self.connect()
        
        session_data = await self.sessions.find_one({
            "telegram_id": telegram_id,
            "completed": False
        })
        if session_data:
            return UserSession.from_dict(session_data)
        return None
    
    async def create_session(self, session: UserSession) -> UserSession:
        """Create a new session"""
        if self.sessions is None:
            await self.connect()
        
        session_dict = session.to_dict()
        await self.sessions.insert_one(session_dict)
        logger.info(f"Created new session for user: {session.telegram_id}")
        return session
    
    async def update_session(self, session: UserSession) -> UserSession:
        """Update an existing session"""
        if self.sessions is None:
            await self.connect()
        
        session_dict = session.to_dict()
        await self.sessions.update_one(
            {"session_id": session.session_id},
            {"$set": session_dict}
        )
        logger.info(f"Updated session: {session.session_id}")
        return session
    
    async def get_user_sessions(self, telegram_id: int, limit: int = 10) -> List[UserSession]:
        """Get completed sessions for a user"""
        if self.sessions is None:
            await self.connect()
        
        cursor = self.sessions.find({
            "telegram_id": telegram_id,
            "completed": True
        }).sort("start_time", -1).limit(limit)
        
        sessions = []
        async for doc in cursor:
            sessions.append(UserSession.from_dict(doc))
        return sessions 