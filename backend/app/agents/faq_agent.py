from __future__ import annotations
from .base import AgentBase, AgentInput, AgentOutput


class FAQAgent(AgentBase):
    name = "faq"
    system_instructions = (
        "You are the FAQ Agent for AstraHome. Provide short factual answers to general company questions, policies, and contact information using only the retrieved content. If no answer is found, point the user to support@astrahome.com."
    )

    def __init__(self, rag, llm_service):
        super().__init__(rag, llm_service)

    def handle(self, payload: AgentInput) -> AgentOutput:
        return super().handle(payload)
