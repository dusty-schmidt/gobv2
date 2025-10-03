# core/brain/conversation_manager.py
# Universal conversation tracking for all chatbots

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .brain import CommunalBrain

@dataclass
class ConversationTurn:
    """A single turn in a conversation"""
    timestamp: datetime
    user_message: str
    bot_response: str
    tokens_used: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Conversation:
    """A complete conversation session"""
    session_id: str
    chatbot_name: str
    device_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    turns: List[ConversationTurn] = None
    status: str = "active"  # active, completed, archived
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.turns is None:
            self.turns = []
        if self.metadata is None:
            self.metadata = {}

class UniversalConversationManager:
    """Shared conversation tracking across all chatbots in the homelab"""

    def __init__(self, brain: CommunalBrain):
        self.brain = brain
        self.active_conversations: Dict[str, Conversation] = {}

    def start_conversation(self, chatbot_name: str, session_id: Optional[str] = None) -> str:
        """Start a new conversation session

        Args:
            chatbot_name: Name of the chatbot (e.g., 'mini', 'nano')
            session_id: Optional custom session ID

        Returns:
            The session ID for this conversation
        """
        if session_id is None:
            session_id = f"{chatbot_name}_{uuid.uuid4().hex[:8]}"

        conversation = Conversation(
            session_id=session_id,
            chatbot_name=chatbot_name,
            device_id=self.brain.device_id,
            start_time=datetime.now()
        )

        self.active_conversations[session_id] = conversation

        # Persist to communal brain
        self._save_conversation(conversation)

        return session_id

    def add_turn(self, session_id: str, user_message: str, bot_response: str,
                 tokens_used: int = 0, metadata: Optional[Dict[str, Any]] = None):
        """Add a conversation turn

        Args:
            session_id: The conversation session ID
            user_message: User's input message
            bot_response: Chatbot's response
            tokens_used: Number of tokens used in this turn
            metadata: Additional metadata for this turn
        """
        if session_id not in self.active_conversations:
            # Try to load from communal brain
            conversation = self._load_conversation(session_id)
            if conversation:
                self.active_conversations[session_id] = conversation
            else:
                # Create new conversation if not found
                chatbot_name = session_id.split('_')[0] if '_' in session_id else 'unknown'
                self.start_conversation(chatbot_name, session_id)

        conversation = self.active_conversations[session_id]

        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=user_message,
            bot_response=bot_response,
            tokens_used=tokens_used,
            metadata=metadata or {}
        )

        conversation.turns.append(turn)

        # Persist the updated conversation
        self._save_conversation(conversation)

    def get_conversation_history(self, session_id: str, max_turns: int = 10) -> List[ConversationTurn]:
        """Get recent conversation history

        Args:
            session_id: The conversation session ID
            max_turns: Maximum number of recent turns to return

        Returns:
            List of recent conversation turns
        """
        if session_id not in self.active_conversations:
            conversation = self._load_conversation(session_id)
            if conversation:
                self.active_conversations[session_id] = conversation
            else:
                return []

        conversation = self.active_conversations[session_id]
        return conversation.turns[-max_turns:] if conversation.turns else []

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary statistics for a conversation

        Args:
            session_id: The conversation session ID

        Returns:
            Dictionary with conversation statistics
        """
        if session_id not in self.active_conversations:
            conversation = self._load_conversation(session_id)
            if not conversation:
                return {}
        else:
            conversation = self.active_conversations[session_id]

        total_turns = len(conversation.turns)
        total_tokens = sum(turn.tokens_used for turn in conversation.turns)
        duration = None

        if conversation.end_time:
            duration = (conversation.end_time - conversation.start_time).total_seconds()
        elif total_turns > 0:
            # Still active, calculate duration so far
            duration = (datetime.now() - conversation.start_time).total_seconds()

        return {
            'session_id': session_id,
            'chatbot_name': conversation.chatbot_name,
            'device_id': conversation.device_id,
            'start_time': conversation.start_time.isoformat(),
            'end_time': conversation.end_time.isoformat() if conversation.end_time else None,
            'status': conversation.status,
            'total_turns': total_turns,
            'total_tokens': total_tokens,
            'duration_seconds': duration,
            'average_tokens_per_turn': total_tokens / total_turns if total_turns > 0 else 0
        }

    def end_conversation(self, session_id: str):
        """End a conversation and archive it

        Args:
            session_id: The conversation session ID
        """
        if session_id in self.active_conversations:
            conversation = self.active_conversations[session_id]
            conversation.end_time = datetime.now()
            conversation.status = 'completed'

            # Final save and archive
            self._save_conversation(conversation)

            # Remove from active conversations
            del self.active_conversations[session_id]

    def list_active_conversations(self) -> List[Dict[str, Any]]:
        """List all active conversations across all chatbots"""
        return [self.get_conversation_summary(session_id)
                for session_id in self.active_conversations.keys()]

    def list_all_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent conversations from communal brain

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversation summaries
        """
        # This would query the communal brain for conversation metadata
        # For now, return active conversations
        return self.list_active_conversations()[:limit]

    def _save_conversation(self, conversation: Conversation):
        """Save conversation to communal brain"""
        # Convert to JSON-serializable format
        data = asdict(conversation)
        # Convert datetime objects to ISO strings
        data['start_time'] = conversation.start_time.isoformat()
        if conversation.end_time:
            data['end_time'] = conversation.end_time.isoformat()
        for turn in data['turns']:
            turn['timestamp'] = turn['timestamp']

        # Store in communal brain (this would be implemented in the brain)
        self.brain.store_conversation(conversation.session_id, data)

    def _load_conversation(self, session_id: str) -> Optional[Conversation]:
        """Load conversation from communal brain"""
        data = self.brain.load_conversation(session_id)
        if not data:
            return None

        # Convert back to Conversation object
        turns = []
        for turn_data in data.get('turns', []):
            turns.append(ConversationTurn(**turn_data))

        conversation = Conversation(
            session_id=data['session_id'],
            chatbot_name=data['chatbot_name'],
            device_id=data['device_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            turns=turns,
            status=data.get('status', 'unknown'),
            metadata=data.get('metadata', {})
        )

        return conversation

    def cleanup_old_conversations(self, days_old: int = 30):
        """Clean up old completed conversations

        Args:
            days_old: Remove conversations older than this many days
        """
        # This would be implemented in the brain to archive/remove old conversations
        pass