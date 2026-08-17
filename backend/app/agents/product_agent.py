from __future__ import annotations
from .base import AgentBase, AgentInput, AgentOutput


class ProductAgent(AgentBase):
    name = "product"
    system_instructions = (
        "You are the Product Agent for AstraHome. Answer questions about product features, pricing, comparisons, and availability. "
        "When comparing products, be factual and reference the retrieved specifications and pricing. If stock/availability is unknown, recommend contacting support or sales."
    )

    def __init__(self, rag, llm_service):
        super().__init__(rag, llm_service)

    def handle(self, payload: AgentInput) -> AgentOutput:
        return super().handle(payload)
