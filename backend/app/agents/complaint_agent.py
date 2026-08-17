from __future__ import annotations
from .base import AgentBase, AgentInput, AgentOutput


class ComplaintAgent(AgentBase):
    name = "complaint"
    system_instructions = (
        "You are the Complaint Agent for AstraHome. Handle customer complaints sensitively and follow escalation rules. "
        "Acknowledge the customer's issue, offer immediate remedial steps where possible, and escalate to a human agent when the issue cannot be resolved by policy or when the customer requests escalation."
    )

    def __init__(self, rag, llm_service):
        super().__init__(rag, llm_service)

    def handle(self, payload: AgentInput) -> AgentOutput:
        # For complaints, detect sentiment and escalate if severe
        out = super().handle(payload)
        # simple heuristic: if user message contains 'angry' or 'unacceptable', escalate
        text = payload.user_message.lower()
        if any(k in text for k in ["angry", "unacceptable", "sue", "refund now"]):
            out.requires_escalation = True
            out.reasoning_summary = (out.reasoning_summary or "") + "; Escalation flagged by keyword"
        return out
