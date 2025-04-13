import json
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.conversation.models import Conversation, ConversationNode, User, ConversationState

class ConversationManager:
    def __init__(self, conversation_file: str = "conversation.json"):
        self.conversation_file = conversation_file
        self.conversation_data = self._load_conversation()
        self.nodes_map: Dict[str, ConversationNode] = {
            node.id: node for node in self.conversation_data.conversation
        }
        # Map node_ids to ConversationState values for state machine
        self.node_state_map = {
            "saludo_inicial": ConversationState.INITIAL,
            "filtro_1": ConversationState.FILTRO_1,
            "filtro_2": ConversationState.FILTRO_2,
            "teleconsulta": ConversationState.FIN,
            "hospital_dia": ConversationState.FIN,
            "recomendaciones_finales": ConversationState.FIN,
            "despedida": ConversationState.FIN,
            "fin": ConversationState.EDUCATION_OPT,
            "registro_educacion": ConversationState.END,
            "cerrar_chat": ConversationState.END
        }
        logger.info(f"Loaded {len(self.nodes_map)} conversation nodes from {conversation_file}")
    
    def _load_conversation(self) -> Conversation:
        """Load conversation data from JSON file and validate with Pydantic model"""
        try:
            with open(self.conversation_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Conversation(**data)
        except Exception as e:
            logger.error(f"Error loading conversation file: {str(e)}")
            raise
    
    def get_node(self, node_id: str) -> Optional[ConversationNode]:
        """Get a conversation node by its ID"""
        return self.nodes_map.get(node_id)
    
    def format_message(self, node: ConversationNode, user_data: Dict[str, Any] = None) -> str:
        """Format message with user data placeholders"""
        if not user_data:
            user_data = {}
        
        message = node.message
        # Replace placeholders like {{name}} with actual values
        for key, value in user_data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in message:
                message = message.replace(placeholder, str(value))
        
        return message
    
    def get_state_for_node(self, node_id: str) -> int:
        """Convert node_id to ConversationState value"""
        return self.node_state_map.get(node_id, ConversationState.RESPONDING)
    
    def record_response(self, user: User, node_id: str, response: str) -> User:
        """Record user's response to a specific node"""
        timestamp = datetime.now().isoformat()
        user.responses[node_id] = {"answer": response, "timestamp": timestamp}
        user.last_interaction = timestamp
        return user
    
    def get_next_node_id(self, current_node_id: str, selected_option: str) -> Optional[str]:
        """Determine the next node based on the user's selection"""
        current_node = self.get_node(current_node_id)
        if not current_node:
            return None
        
        # If there are options, find the matching option text
        if current_node.options:
            for option in current_node.options:
                if option.text == selected_option:
                    return option.next
        
        # If no matching option or no options, return next node if defined
        return current_node.next
    
    def create_keyboard_markup(self, node: ConversationNode) -> Optional[InlineKeyboardMarkup]:
        """Create an inline keyboard markup for a conversation node"""
        if not node.options:
            return None
        
        keyboard = []
        for option in node.options:
            keyboard.append([InlineKeyboardButton(text=option.text, callback_data=option.text)])
        
        return InlineKeyboardMarkup(keyboard) 