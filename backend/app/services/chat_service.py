from typing import Optional, List, Dict, Any
from uuid import uuid4
from pathlib import Path
from backend.app.conversations import store as conv_store
from backend.app.conversations import models as conv_models
from backend.app.orchestrator import aggregator
from backend.app.intent.detector import IntentDetector
from backend.app.router.router import AgentRouter
from backend.app.agents.faq_agent import FAQAgent
from backend.app.agents.billing_agent import BillingAgent
from backend.app.agents.technical_agent import TechnicalAgent
from backend.app.agents.complaint_agent import ComplaintAgent
from backend.app.agents.product_agent import ProductAgent
from backend.app.agents.base import AgentInput, AgentOutput
from backend.app.llm.service import LLMService
from backend.app.rag.pipeline import RAGPipeline
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChatResult:
    final_answer: str
    escalate: bool
    sources: List[dict]


class ChatService:
    def __init__(
        self,
        conversation_store: conv_store.ConversationStore = conv_store.default_store,
        llm_service: "LLMService" = None,
        rag: RAGPipeline = None,
    ):
        self.conversation_store = conversation_store
        self.llm_service = llm_service or LLMService(provider="dummy")
        # Initialize RAGPipeline with docs/ corpus if not provided
        if rag is not None:
            self.rag = rag
        else:
            docs_dir = Path(__file__).resolve().parent.parent / "docs"
            self.rag = RAGPipeline(
                source_folder=str(docs_dir),
                index_path=str(docs_dir / "faiss.index"),
                embedding_model_name="dummy",
                chunk_size=500,
                chunk_overlap=50,
            )
        self.rag.build_index(rebuild=False)

    def _load_or_create_conversation(self, session_id: Optional[str], user_id: Optional[str]):
        if session_id:
            try:
                return self.conversation_store.get_conversation(session_id)
            except conv_store.ConversationNotFound:
                raise
        else:
            create = conv_models.ConversationCreate(user_id=user_id)
            return self.conversation_store.create_conversation(create)

    # Agent name to class mapping — single source of truth
    AGENT_CLASSES = {
        "faq": FAQAgent,
        "billing": BillingAgent,
        "technical_support": TechnicalAgent,
        "complaint": ComplaintAgent,
        "product": ProductAgent,
    }

    def execute_agents(
        self,
        agents: List[str],
        user_text: str,
        rag_context=None,
        user_id: str = "",
        conversation_id: str = "",
    ) -> List[AgentOutput]:
        """Execute the given agent names against the user message.

        Resolves each agent name to its class, instantiates the agent with
        the injected LLM service and RAG wrapper, calls ``handle()`` with
        an ``AgentInput``, and gathers the resulting ``AgentOutput`` objects.

        If an agent name is unknown, a failing ``AgentOutput`` is produced
        so the aggregator can continue without crashing.
        """
        outputs: List[AgentOutput] = []

        for agent_name in agents:
            agent_class = self.AGENT_CLASSES.get(agent_name)
            if not agent_class:
                outputs.append(
                    AgentOutput(
                        agent=agent_name,
                        answer="",
                        confidence=0.0,
                        requires_escalation=True,
                        sources=[],
                        reasoning_summary=f"Unknown agent: {agent_name}",
                    )
                )
                continue

            try:
                agent = agent_class(rag=self.rag, llm_service=self.llm_service)

                inp = AgentInput(
                    user_id=user_id or str(uuid4()),
                    conversation_id=conversation_id or str(uuid4()),
                    user_message=user_text,
                    conversation_history=[],
                    params={},
                )

                output: AgentOutput = agent.handle(inp)
                outputs.append(output)
            except Exception as e:
                _LOG.exception("Agent %s execution failed: %s", agent_name, str(e))
                outputs.append(
                    AgentOutput(
                        agent=agent_name,
                        answer="",
                        confidence=0.0,
                        requires_escalation=True,
                        sources=[],
                        reasoning_summary=f"Agent execution failed: {str(e)}",
                    )
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

        # retrieve RAG context from the initialized pipeline
        rag_context = None
        try:
            rag_context = self.rag.semantic_search(message, top_k=3)
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
