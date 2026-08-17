from __future__ import annotations
from typing import List, Dict, Any, Optional
import logging

from pydantic import BaseModel, Field

_LOG = logging.getLogger(__name__)


class AgentInput(BaseModel):
    user_id: str
    conversation_id: str
    user_message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    params: Optional[Dict[str, Any]] = None


class AgentOutput(BaseModel):
    agent: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    requires_escalation: bool = False
    sources: Optional[List[Dict[str, Any]]] = None
    reasoning_summary: Optional[str] = None


class AgentBase:
    """Base class for all agents.

    Derived agents supply `name` and `system_instructions`.
    The router should call `handle()` with validated `AgentInput`.
    """

    name: str = "base"
    system_instructions: str = "You are a helpful assistant."

    def __init__(self, rag, llm_service):
        self.rag = rag
        self.llm = llm_service

    def handle(self, payload: AgentInput) -> AgentOutput:
        try:
            if not payload.user_message or not payload.user_message.strip():
                return AgentOutput(agent=self.name, answer="", confidence=0.0, requires_escalation=False, sources=[], reasoning_summary="Empty query")

            # 1) Retrieve context
            try:
                retrieved = self.rag.semantic_search(payload.user_message, top_k=5)
            except Exception as e:
                _LOG.exception("RAG retrieval failed: %s", str(e))
                return AgentOutput(agent=self.name, answer="", confidence=0.0, requires_escalation=True, sources=[], reasoning_summary="RAG retrieval failed")

            # 2) Call LLM
            try:
                resp = self.llm.generate(
                    system_instructions=self.system_instructions,
                    user_query=payload.user_message,
                    retrieved_chunks=retrieved,
                    conversation_history=payload.conversation_history or [],
                )
            except Exception as e:
                _LOG.exception("LLM call failed: %s", str(e))
                return AgentOutput(agent=self.name, answer="", confidence=0.0, requires_escalation=True, sources=[r.get("metadata") for r in retrieved], reasoning_summary="LLM call failed")

            if resp.get("error"):
                _LOG.warning("LLM responded with error: %s", resp.get("error"))
                return AgentOutput(agent=self.name, answer="", confidence=0.0, requires_escalation=True, sources=[r.get("metadata") for r in retrieved], reasoning_summary="LLM error: %s" % resp.get("error"))

            text = resp.get("text", "").strip()
            # Build output with conservative confidence heuristics
            confidence = 0.9 if retrieved else 0.5
            # include sources (metadata) and top-k scores if present
            sources = [r.get("metadata") for r in retrieved]
            return AgentOutput(agent=self.name, answer=text, confidence=confidence, requires_escalation=False, sources=sources, reasoning_summary="Retrieved %d chunks" % len(sources))

        except Exception as e:
            _LOG.exception("Unexpected agent error: %s", str(e))
            return AgentOutput(agent=self.name, answer="", confidence=0.0, requires_escalation=True, sources=[], reasoning_summary="Unexpected error")
