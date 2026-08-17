from __future__ import annotations
from .base import AgentBase, AgentInput, AgentOutput


class TechnicalAgent(AgentBase):
    name = "technical_support"
    system_instructions = (
        "You are the Technical Support Agent for AstraHome. Assist with login, password reset, installation, errors, and bug reports. "
        "When providing steps, be concise and numbered. If the issue requires logs or photos, request them. If this is outside your scope, escalate."
    )

    def __init__(self, rag, llm_service):
        super().__init__(rag, llm_service)

    def handle(self, payload: AgentInput) -> AgentOutput:
        # Technical may require escalation for sensitive operations
        # example: password reset should be routed to secure flow (do not ask for passwords)
        if "password" in payload.user_message.lower():
            # add instruction not to request credentials
            self.system_instructions += "\nDo not ask the user for passwords or secret tokens. Provide instructions to use the secure password reset page."
        return super().handle(payload)
