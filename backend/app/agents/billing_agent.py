from __future__ import annotations
from .base import AgentBase, AgentInput, AgentOutput


class BillingAgent(AgentBase):
    name = "billing"
    system_instructions = (
        "You are the Billing Agent for AstraHome. Answer customer questions about payments, subscriptions, invoices, and refunds. "
        "Use only the provided retrieved company information. If the information is missing, say you don't have enough data and provide steps to contact billing@astrahome.com."
    )

    def __init__(self, rag, llm_service):
        super().__init__(rag, llm_service)

    def handle(self, payload: AgentInput) -> AgentOutput:
        # Billing-specific pre-checks
        if payload.params and payload.params.get("require_invoice"):
            # instruct LLM to prioritize invoice info
            self.system_instructions += "\nPrioritize invoice numbers and billing dates if present in retrieved context."
        return super().handle(payload)
