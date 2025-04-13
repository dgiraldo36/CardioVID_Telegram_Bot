import os
import urllib.parse
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    # Bot settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_NAME: str = os.getenv("BOT_NAME", "CardioVID_Bot")
    
    # MongoDB settings
    MONGODB_CONNECTION_STRING: str = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "cardiovid_bot")
    
    # Application settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        case_sensitive = True
    
    def __init__(self, **data):
        super().__init__(**data)
        # Fix MongoDB connection string if it contains credentials
        if '+srv://' in self.MONGODB_CONNECTION_STRING and '@' in self.MONGODB_CONNECTION_STRING:
            # Extract username and password from connection string
            prefix = self.MONGODB_CONNECTION_STRING.split('://', 1)[0] + '://'
            user_pass = self.MONGODB_CONNECTION_STRING.split('://', 1)[1].split('@', 1)[0]
            rest = self.MONGODB_CONNECTION_STRING.split('@', 1)[1]
            
            if ':' in user_pass:
                username, password = user_pass.split(':', 1)
                # URL encode username and password
                username = urllib.parse.quote_plus(username)
                password = urllib.parse.quote_plus(password)
                
                # Reconstruct connection string
                self.MONGODB_CONNECTION_STRING = f"{prefix}{username}:{password}@{rest}"

# Create a global settings instance
settings = Settings()

# Validate that required settings are set
if not settings.BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set") 