from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ConversationOption(BaseModel):
    text: str
    next: Optional[str] = None

class ConversationNode(BaseModel):
    id: str
    message: str
    options: Optional[List[ConversationOption]] = None
    next: Optional[str] = None

class Conversation(BaseModel):
    conversation: List[ConversationNode]

class User(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    current_node: str = "saludo_inicial"
    responses: Dict[str, Any] = Field(default_factory=dict)
    registered_at: str
    last_interaction: str
    education_opt_in: bool = False

# Define conversation states for python-telegram-bot
class ConversationState:
    INITIAL = 0
    RESPONDING = 1
    FILTRO_1 = 2
    FILTRO_2 = 3
    FIN = 4
    EDUCATION_OPT = 5
    END = 6 