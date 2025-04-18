from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class UserDB(BaseModel):
    """Database model for user data"""
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    current_node: str = "saludo_inicial"
    responses: Dict[str, Any] = Field(default_factory=dict)
    registered_at: str
    last_interaction: str
    education_opt_in: bool = False
    
    @classmethod
    def create_new(cls, telegram_id: int, first_name: str, last_name: Optional[str] = None, 
                username: Optional[str] = None) -> "UserDB":
        """Create a new user record with default values"""
        now = datetime.now().isoformat()
        return cls(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            registered_at=now,
            last_interaction=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage"""
        return self.model_dump(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserDB":
        """Create model from dictionary (from MongoDB)"""
        return cls(**data)

class NodeResponse(BaseModel):
    """Model for individual node responses within a session"""
    node_id: str
    response: str
    timestamp: str
    message_text: Optional[str] = None

class UserSession(BaseModel):
    """Model for complete user interaction sessions"""
    telegram_id: int
    session_id: str
    start_time: str
    end_time: str
    session_type: str  # "normal" o "empeoramiento"
    responses: List[NodeResponse]
    completed: bool = False
    final_message: Optional[str] = None
    
    @classmethod
    def create_new(cls, telegram_id: int, session_type: str = "normal") -> "UserSession":
        """Create a new session"""
        now = datetime.now().isoformat()
        return cls(
            telegram_id=telegram_id,
            session_id=f"{telegram_id}_{now}",
            start_time=now,
            end_time=now,
            session_type=session_type,
            responses=[]
        )
    
    def add_response(self, node_id: str, response: str, message_text: Optional[str] = None) -> None:
        """Add a response to the session"""
        now = datetime.now().isoformat()
        
        # Asegurar que node_id y response sean strings
        node_id_str = str(node_id) if node_id is not None else "unknown_node"
        response_str = str(response) if response is not None else ""
        
        # Asegurar que message_text sea string o None
        message_text_str = None
        if message_text is not None:
            try:
                message_text_str = str(message_text)
            except:
                message_text_str = "Error en mensaje"
        
        self.responses.append(
            NodeResponse(
                node_id=node_id_str,
                response=response_str,
                timestamp=now,
                message_text=message_text_str
            )
        )
        self.end_time = now
    
    def complete_session(self, final_message: Optional[str] = None) -> None:
        """Mark the session as completed"""
        self.completed = True
        self.end_time = datetime.now().isoformat()
        if final_message:
            self.final_message = final_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for MongoDB storage"""
        return self.model_dump(exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserSession":
        """Create model from dictionary (from MongoDB)"""
        return cls(**data) 