"""
Telegram Conversation State Management
Handles multi-step conversation flows with Telegram bot
"""
import time
from enum import Enum, auto
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


class ConversationState(Enum):
    """States for report submission conversation"""
    IDLE = auto()
    AWAITING_TITLE = auto()
    AWAITING_CATEGORY = auto()
    AWAITING_PRIORITY = auto()
    AWAITING_DESCRIPTION = auto()
    AWAITING_PHOTOS = auto()
    AWAITING_CONFIRMATION = auto()


@dataclass
class ConversationData:
    """Data stored for a conversation"""
    state: ConversationState = ConversationState.IDLE
    data: Dict[str, Any] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)
    user_id: Optional[int] = None


class ConversationStore:
    """
    In-memory conversation state store with TTL
    
    Automatically expires conversations after TTL_SECONDS
    """
    
    TTL_SECONDS = 1800  # 30 minutes timeout
    
    def __init__(self):
        self._conversations: Dict[int, ConversationData] = {}
    
    def _cleanup_expired(self) -> None:
        """Remove expired conversations"""
        now = time.time()
        expired = [
            chat_id for chat_id, data in self._conversations.items()
            if now - data.last_updated > self.TTL_SECONDS
        ]
        for chat_id in expired:
            del self._conversations[chat_id]
    
    def start_conversation(self, chat_id: int, user_id: Optional[int] = None) -> None:
        """
        Start a new conversation
        
        Args:
            chat_id: Telegram chat ID
            user_id: Optional linked user ID
        """
        self._cleanup_expired()
        self._conversations[chat_id] = ConversationData(
            state=ConversationState.AWAITING_TITLE,
            data={},
            user_id=user_id
        )
    
    def get_state(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current conversation state
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Dict with state and data, or None if no active conversation
        """
        self._cleanup_expired()
        
        if chat_id not in self._conversations:
            return None
        
        data = self._conversations[chat_id]
        return {
            'state': data.state,
            'data': data.data.copy(),
            'user_id': data.user_id
        }
    
    def update_state(
        self,
        chat_id: int,
        state: ConversationState,
        data_update: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update conversation state
        
        Args:
            chat_id: Telegram chat ID
            state: New conversation state
            data_update: Data to merge into existing conversation data
        """
        self._cleanup_expired()
        
        if chat_id not in self._conversations:
            raise ValueError(f"No active conversation for chat_id {chat_id}")
        
        conv_data = self._conversations[chat_id]
        conv_data.state = state
        conv_data.last_updated = time.time()
        
        if data_update:
            conv_data.data.update(data_update)
    
    def update_data(self, chat_id: int, key: str, value: Any) -> None:
        """
        Update a single data field in conversation
        
        Args:
            chat_id: Telegram chat ID
            key: Data field name
            value: Data field value
        """
        self._cleanup_expired()
        
        if chat_id not in self._conversations:
            raise ValueError(f"No active conversation for chat_id {chat_id}")
        
        self._conversations[chat_id].data[key] = value
        self._conversations[chat_id].last_updated = time.time()
    
    def end_conversation(self, chat_id: int) -> None:
        """
        End and remove a conversation
        
        Args:
            chat_id: Telegram chat ID
        """
        if chat_id in self._conversations:
            del self._conversations[chat_id]
    
    def is_active(self, chat_id: int) -> bool:
        """
        Check if there's an active conversation
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            True if conversation exists and not expired
        """
        self._cleanup_expired()
        return chat_id in self._conversations
    
    def get_all_active(self) -> Dict[int, ConversationData]:
        """
        Get all active conversations (for debugging)
        
        Returns:
            Dict mapping chat_id to conversation data
        """
        self._cleanup_expired()
        return self._conversations.copy()


# Category mappings for report submission
REPORT_CATEGORIES = {
    '1': ('maintenance', '🔧 Maintenance'),
    '2': ('cleaning', '🧹 Cleaning'),
    '3': ('safety', '🚨 Safety'),
    '4': ('noise', '🔊 Noise'),
    '5': ('other', '📝 Other')
}

PRIORITY_LEVELS = {
    '1': ('low', '🟢 Low'),
    '2': ('normal', '🔵 Normal'),
    '3': ('high', '🟠 High'),
    '4': ('urgent', '🔴 Urgent')
}


def get_category_name(key: str) -> str:
    """Get category name from key"""
    return REPORT_CATEGORIES.get(key, ('other', '📝 Other'))[0]


def get_category_display(key: str) -> str:
    """Get category display name from key"""
    return REPORT_CATEGORIES.get(key, ('other', '📝 Other'))[1]


def get_priority_name(key: str) -> str:
    """Get priority name from key"""
    return PRIORITY_LEVELS.get(key, ('normal', '🔵 Normal'))[0]


def get_priority_display(key: str) -> str:
    """Get priority display name from key"""
    return PRIORITY_LEVELS.get(key, ('normal', '🔵 Normal'))[1]


# Singleton instance
_conversation_store: Optional[ConversationStore] = None


def get_conversation_store() -> ConversationStore:
    """Get or create ConversationStore singleton"""
    global _conversation_store
    if _conversation_store is None:
        _conversation_store = ConversationStore()
    return _conversation_store
