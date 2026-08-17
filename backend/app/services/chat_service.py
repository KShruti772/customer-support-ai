from typing import Optional, List
from backend.app.conversations import store as conv_store
from backend.app.conversations import models as conv_models
from backend.app.orchestrator import aggregator
from backend.app.intent.detector import IntentDetector
from backend.app.router.router import AgentRouter
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    final_answer: str
    escalate: bool
    sources: List[dict]


class ChatService:
    def __init__(self, conversation_store: conv_store.ConversationStore = conv_store.default_store):
        self.conversation_store = conversation_store

    def _load_or_create_conversation(self, session_id: Optional[str], user_id: Optional[str]):
        if session_id:
            try:
                return self.conversation_store.get_conversation(session_id)
            except conv_store.ConversationNotFound:
                raise
        else:
            create = conv_models.ConversationCreate(user_id=user_id)
            return self.conversation_store.create_conversation(create)

    def execute_agents(self, agents: List[str], user_text: str, rag_context=None):
        # Default simple executor: returns a single assistant response echoing intent.
        # In production, this should instantiate concrete agents and execute them (possibly concurrently).
        outputs = []
        for a in agents:
            outputs.append(
                # keep shape compatible with AgentOutput used by aggregator
                conv_models.Message(sender="assistant", text=f"[{a}] response to: {user_text}")
            )
        return outputs

    def chat(self, user_id: str, message: str, session_id: Optional[str] = None) -> ChatResult:
        # load or create conversation
        try:
            conv = self._load_or_create_conversation(session_id, user_id)
        except conv_store.ConversationNotFound:
            logger.info("Conversation %s not found", session_id)
            raise

        # store user message
        self.conversation_store.add_message(conv.session_id, "user", message)

        # detect intent & route
        detector = IntentDetector()
        intent = detector.detect(message)
        router = AgentRouter()
        routing = router.route(message)

        agents = routing.get("agents") or ["faq"]

        # retrieve RAG context - pipeline exists but may be heavy; call if available
        rag_context = None
        try:
            from backend.app.rag.pipeline import RAGPipeline

            # placeholder: you would call semantic search with user query and agents' contexts
            rag = RAGPipeline()
            rag_context = rag.semantic_search(message, top_k=3)
        except Exception:
            logger.debug("RAG pipeline unavailable or failed, continuing without context")

        # execute agents (simplified)
        agent_outputs = self.execute_agents(agents, message, rag_context)

        # convert agent outputs to aggregator-compatible objects if needed
        # For now, map assistant messages into a simple AgentOutput-like dict
        from backend.app.agents.base import AgentOutput

        ao_list = []
        for m in agent_outputs:
            # m may already be an AgentOutput (from real agents or tests)
            if isinstance(m, AgentOutput):
                ao_list.append(m)
            else:
                # fallback: assume a Message-like object
                ao = AgentOutput(agent=getattr(m, "sender", "assistant"), answer=getattr(m, "text", ""), confidence=0.7, requires_escalation=False, sources=[])
                ao_list.append(ao)

        agg = aggregator.aggregate_agent_responses(ao_list)

        # store assistant response
        assistant_text = agg.get("final_answer")
        self.conversation_store.add_message(conv.session_id, "assistant", assistant_text)

        return ChatResult(final_answer=assistant_text, escalate=agg.get("escalate", False), sources=agg.get("sources", []))


default_chat_service = ChatService()
