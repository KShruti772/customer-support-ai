from __future__ import annotations
from typing import List, Dict, Any
import logging

from backend.app.intent.detector import IntentDetector

_LOG = logging.getLogger(__name__)


class AgentRouter:
    """Maps detected intents to agent names and enforces routing rules.

    - validate detected intents
    - select appropriate agents
    - handle unknown intents and low confidence
    - support multiple agents with execution limits
    """

    INTENT_TO_AGENT = {
        "billing": ["billing"],
        "refund": ["billing"],
        "product": ["product"],
        "technical_support": ["technical_support"],
        "complaint": ["complaint"],
        "general_faq": ["faq"],
    }

    def __init__(self, min_confidence: float = 0.4, max_agents: int = 3):
        self.detector = IntentDetector(min_confidence)
        self.min_confidence = min_confidence
        self.max_agents = max_agents

    def route(self, text: str) -> Dict[str, Any]:
        det = self.detector.detect(text)
        intents = det.get("intents", [])
        selected_agents: List[str] = []
        reason: List[str] = []

        if not intents:
            # fallback to FAQ agent for unknown queries
            reason.append("no_intent_detected")
            return {"intents": [], "agents": ["faq"], "requires_escalation": False, "reason": reason}

        # iterate over intents and map to agents
        for intent in intents:
            name = intent["name"] if isinstance(intent, dict) else intent[0]
            conf = intent["confidence"] if isinstance(intent, dict) else intent[1]
            if conf < self.min_confidence:
                reason.append(f"low_confidence:{name}:{conf}")
                continue
            mapped = self.INTENT_TO_AGENT.get(name)
            if not mapped:
                reason.append(f"unknown_intent:{name}")
                continue
            for agent in mapped:
                if agent not in selected_agents:
                    selected_agents.append(agent)
            if len(selected_agents) >= self.max_agents:
                reason.append("max_agents_reached")
                break

        # If detector flagged multiple intents explicitly, honor it and include multiple agents
        if det.get("requires_multiple_agents") and len(selected_agents) < self.max_agents:
            # attempt to include next best intent even if near threshold
            for intent in intents:
                name = intent["name"]
                mapped = self.INTENT_TO_AGENT.get(name) or []
                for agent in mapped:
                    if agent not in selected_agents and len(selected_agents) < self.max_agents:
                        selected_agents.append(agent)

        if not selected_agents:
            # low confidence for all -> route to FAQ and flag for escalation if confidence extremely low
            reason.append("no_agents_selected")
            requires_escalation = det.get("confidence", 0.0) < 0.1
            return {"intents": det, "agents": ["faq"], "requires_escalation": requires_escalation, "reason": reason}

        return {"intents": det, "agents": selected_agents, "requires_escalation": False, "reason": reason}
