# core/brain/conversation_manager.py
# Universal conversation tracking for all chatbots

import asyncio
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, asdict, field

from .brain import CommunalBrain
from ..logging import get_logger


logger = get_logger(__name__)


ConversationEventCallback = Callable[[Dict[str, Any]], Awaitable[None] | None]

EVENT_CONVERSATION_STARTED = "conversation_started"
EVENT_CONVERSATION_ENDED = "conversation_ended"
EVENT_TURN_APPENDED = "turn_appended"

@dataclass
class ConversationTurn:
    """A single turn in a conversation"""
    timestamp: datetime
    user_message: str
    bot_response: str
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    turn_id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class Conversation:
    """A complete conversation session"""
    session_id: str
    chatbot_name: str
    device_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    turns: List[ConversationTurn] = field(default_factory=list)
    status: str = "active"  # active, completed, archived
    metadata: Dict[str, Any] = field(default_factory=dict)

class UniversalConversationManager:
    """Shared conversation tracking across all chatbots in the homelab"""

    def __init__(self, brain: CommunalBrain):
        self.brain = brain
        self.active_conversations: Dict[str, Conversation] = {}
        self._listeners: Dict[str, List[ConversationEventCallback]] = defaultdict(list)
        self._conversation_locks: Dict[str, asyncio.Lock] = {}

    def register_listener(self, event_name: str, callback: ConversationEventCallback) -> None:
        """Register an event listener"""
        self._listeners[event_name].append(callback)

    def unregister_listener(self, event_name: str, callback: ConversationEventCallback) -> None:
        """Remove a previously registered event listener"""
        if event_name in self._listeners and callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    def _get_lock(self, session_id: str) -> asyncio.Lock:
        lock = self._conversation_locks.get(session_id)
        if lock is None:
            lock = asyncio.Lock()
            self._conversation_locks[session_id] = lock
        return lock

    async def start_conversation(self, chatbot_name: str, session_id: Optional[str] = None) -> str:
        """Start a new conversation session"""
        if session_id is None:
            session_id = f"{chatbot_name}_{uuid.uuid4().hex[:8]}"

        conversation = Conversation(
            session_id=session_id,
            chatbot_name=chatbot_name,
            device_id=self.brain.device_id,
            start_time=datetime.now()
        )

        lock = self._get_lock(session_id)
        async with lock:
            self.active_conversations[session_id] = conversation
            await self._save_conversation(conversation)

        await self._dispatch_event(EVENT_CONVERSATION_STARTED, {
            "session_id": session_id,
            "chatbot_name": chatbot_name,
            "device_id": self.brain.device_id,
        })

        return session_id

    async def add_turn(self, session_id: str, user_message: str, bot_response: str,
                       tokens_used: int = 0, metadata: Optional[Dict[str, Any]] = None) -> ConversationTurn:
        """Add a conversation turn"""
        metadata = metadata or {}
        lock = self._get_lock(session_id)
        async with lock:
            conversation = self.active_conversations.get(session_id)
            if conversation is None:
                conversation = await self._load_conversation(session_id)
                if conversation:
                    self.active_conversations[session_id] = conversation
                else:
                    chatbot_name = session_id.split('_')[0] if '_' in session_id else 'unknown'
                    conversation = Conversation(
                        session_id=session_id,
                        chatbot_name=chatbot_name,
                        device_id=self.brain.device_id,
                        start_time=datetime.now()
                    )
                    self.active_conversations[session_id] = conversation

            turn = ConversationTurn(
                timestamp=datetime.now(),
                user_message=user_message,
                bot_response=bot_response,
                tokens_used=tokens_used,
                metadata=metadata,
            )

            conversation.turns.append(turn)
            await self._save_conversation(conversation)

        await self._dispatch_event(EVENT_TURN_APPENDED, {
            "session_id": session_id,
            "turn_id": turn.turn_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "tokens_used": tokens_used,
            "metadata": metadata,
        })

        return turn

    async def get_conversation_history(self, session_id: str, max_turns: int = 10) -> List[ConversationTurn]:
        """Get recent conversation history"""
        lock = self._get_lock(session_id)
        async with lock:
            conversation = self.active_conversations.get(session_id)
            if conversation is None:
                conversation = await self._load_conversation(session_id)
                if conversation:
                    self.active_conversations[session_id] = conversation
                else:
                    return []

            history = list(conversation.turns[-max_turns:] if conversation.turns else [])

        return history

    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary statistics for a conversation"""
        lock = self._get_lock(session_id)
        async with lock:
            conversation = self.active_conversations.get(session_id)
            if conversation is None:
                conversation = await self._load_conversation(session_id)
                if conversation:
                    self.active_conversations[session_id] = conversation
                else:
                    return {}

            summary = self._build_summary(session_id, conversation)

        return summary

    async def end_conversation(self, session_id: str) -> None:
        """End a conversation and archive it"""
        conversation: Optional[Conversation] = None
        lock = self._get_lock(session_id)
        async with lock:
            conversation = self.active_conversations.get(session_id)
            if conversation is None:
                conversation = await self._load_conversation(session_id)
                if conversation:
                    self.active_conversations[session_id] = conversation
                else:
                    return

            conversation.end_time = datetime.now()
            conversation.status = 'completed'
            await self._save_conversation(conversation)

            self.active_conversations.pop(session_id, None)
            self._conversation_locks.pop(session_id, None)

        await self._dispatch_event(EVENT_CONVERSATION_ENDED, {
            "session_id": session_id,
            "chatbot_name": conversation.chatbot_name if conversation else None,
            "device_id": conversation.device_id if conversation else None,
        })

    async def list_active_conversations(self) -> List[Dict[str, Any]]:
        """List all active conversations across all chatbots"""
        summaries: List[Dict[str, Any]] = []
        for session_id in list(self.active_conversations.keys()):
            summary = await self.get_conversation_summary(session_id)
            if summary:
                summaries.append(summary)
        return summaries

    async def list_all_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent conversations from communal brain"""
        try:
            conversations = await self.brain.list_conversations(limit)
        except Exception:
            logger.exception("Failed to list conversations from communal brain")
            conversations = []

        if len(conversations) < limit:
            active = await self.list_active_conversations()
            seen = {conv.get('session_id') for conv in conversations if conv.get('session_id')}
            for conv in active:
                if conv['session_id'] not in seen:
                    conversations.append(conv)
        return conversations[:limit]

    async def _save_conversation(self, conversation: Conversation) -> None:
        """Persist conversation data to the communal brain"""
        data = self._serialize_conversation(conversation)

        try:
            await self.brain.store_conversation(conversation.session_id, data)
        except Exception:
            logger.exception("Failed to store conversation %s", conversation.session_id)

    async def _load_conversation(self, session_id: str) -> Optional[Conversation]:
        """Load conversation from the communal brain"""
        try:
            data = await self.brain.load_conversation(session_id)
        except Exception:
            logger.exception("Failed to load conversation %s", session_id)
            data = None
        if not data:
            return None

        turns: List[ConversationTurn] = []
        for turn_data in data.get('turns', []):
            timestamp = turn_data.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    timestamp = datetime.now()

            turn = ConversationTurn(
                timestamp=timestamp,
                user_message=turn_data.get('user_message', ''),
                bot_response=turn_data.get('bot_response', ''),
                tokens_used=turn_data.get('tokens_used', 0),
                metadata=turn_data.get('metadata', {}) or {},
                turn_id=turn_data.get('turn_id', uuid.uuid4().hex)
            )
            turns.append(turn)

        conversation = Conversation(
            session_id=data['session_id'],
            chatbot_name=data.get('chatbot_name', 'unknown'),
            device_id=data.get('device_id', self.brain.device_id),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            turns=turns,
            status=data.get('status', 'unknown'),
            metadata=data.get('metadata', {}) or {}
        )

        return conversation

    async def cleanup_old_conversations(self, days_old: int = 30):
        """Clean up old completed conversations"""
        # Implementation placeholder – will integrate with archival workflow
        return None

    async def export_conversation_snapshot(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Return a serialized snapshot of the conversation for downstream processors"""
        lock = self._get_lock(session_id)
        async with lock:
            conversation = self.active_conversations.get(session_id)
            if conversation is None:
                conversation = await self._load_conversation(session_id)
                if conversation:
                    self.active_conversations[session_id] = conversation
                else:
                    return None

            snapshot = self._serialize_conversation(conversation)
            snapshot['summary'] = self._build_summary(session_id, conversation)

        return snapshot

    async def _dispatch_event(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Notify registered listeners of conversation events"""
        listeners = list(self._listeners.get(event_name, []))
        if not listeners:
            return

        for callback in listeners:
            try:
                result = callback(payload)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("Conversation event listener failed: %s", event_name)

    def _build_summary(self, session_id: str, conversation: Conversation) -> Dict[str, Any]:
        total_turns = len(conversation.turns)
        total_tokens = sum(turn.tokens_used for turn in conversation.turns)
        if conversation.end_time:
            duration = (conversation.end_time - conversation.start_time).total_seconds()
        elif total_turns > 0:
            duration = (datetime.now() - conversation.start_time).total_seconds()
        else:
            duration = None

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
            'average_tokens_per_turn': total_tokens / total_turns if total_turns > 0 else 0,
        }

    def _serialize_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        data = asdict(conversation)
        data['start_time'] = conversation.start_time.isoformat()
        if conversation.end_time:
            data['end_time'] = conversation.end_time.isoformat()
        for turn in data['turns']:
            timestamp = turn.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                turn['timestamp'] = timestamp.isoformat()
            else:
                turn['timestamp'] = str(timestamp)
            turn['metadata'] = turn.get('metadata') or {}
        return data
