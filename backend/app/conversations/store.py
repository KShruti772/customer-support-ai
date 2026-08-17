from typing import Optional, List, Dict, Any
from .models import Conversation, ConversationCreate, Message
from datetime import datetime


class ConversationNotFound(Exception):
    pass


class DatabaseError(Exception):
    pass


class ConversationStore:
    """Abstract-ish conversation store interface. Implementations should provide these methods."""

    def create_conversation(self, payload: ConversationCreate) -> Conversation:
        raise NotImplementedError()

    def add_message(self, session_id: str, sender: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        raise NotImplementedError()

    def get_conversation(self, session_id: str) -> Conversation:
        raise NotImplementedError()

    def list_conversations_for_user(self, user_id: str) -> List[Conversation]:
        raise NotImplementedError()

    def get_trimmed_history(self, session_id: str, max_messages: int = 20) -> List[Message]:
        raise NotImplementedError()


class InMemoryConversationStore(ConversationStore):
    def __init__(self):
        self._store: Dict[str, Conversation] = {}

    def create_conversation(self, payload: ConversationCreate) -> Conversation:
        # Only pass session_id if provided to allow Pydantic default generation
        if payload.session_id:
            conv = Conversation(
                session_id=payload.session_id,
                user_id=payload.user_id,
                metadata=payload.metadata,
            )
        else:
            conv = Conversation(
                user_id=payload.user_id,
                metadata=payload.metadata,
            )
        self._store[conv.session_id] = conv
        return conv

    def add_message(self, session_id: str, sender: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        conv = self._store.get(session_id)
        if not conv:
            raise ConversationNotFound(session_id)
        msg = Message(sender=sender, text=text, metadata=metadata)
        conv.messages.append(msg)
        conv.updated_at = datetime.utcnow()
        return msg

    def get_conversation(self, session_id: str) -> Conversation:
        conv = self._store.get(session_id)
        if not conv:
            raise ConversationNotFound(session_id)
        return conv

    def list_conversations_for_user(self, user_id: str) -> List[Conversation]:
        return [c for c in self._store.values() if c.user_id == user_id]

    def get_trimmed_history(self, session_id: str, max_messages: int = 20) -> List[Message]:
        conv = self.get_conversation(session_id)
        # return the most recent `max_messages` messages
        return conv.messages[-max_messages:]


# Module-level default store. Tests can monkeypatch this if needed.
default_store: ConversationStore = InMemoryConversationStore()


class MongoConversationStore(ConversationStore):
    """Placeholder Mongo implementation. Uses motor (async) in production. Kept minimal here.

    Note: Not used by tests; provided as a template for a production migration.
    """

    def __init__(self, client):
        # client is expected to be a motor or pymongo client
        self._client = client
        self._db = client.get_database("customer_support")
        self._col = self._db.get_collection("conversations")

    def create_conversation(self, payload: ConversationCreate) -> Conversation:
        raise NotImplementedError("MongoConversationStore.create_conversation must be implemented for async driver")

    def add_message(self, session_id: str, sender: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        raise NotImplementedError("MongoConversationStore.add_message must be implemented for async driver")

    def get_conversation(self, session_id: str) -> Conversation:
        raise NotImplementedError("MongoConversationStore.get_conversation must be implemented for async driver")

    def list_conversations_for_user(self, user_id: str) -> List[Conversation]:
        raise NotImplementedError("MongoConversationStore.list_conversations_for_user must be implemented for async driver")

    def get_trimmed_history(self, session_id: str, max_messages: int = 20) -> List[Message]:
        raise NotImplementedError("MongoConversationStore.get_trimmed_history must be implemented for async driver")
