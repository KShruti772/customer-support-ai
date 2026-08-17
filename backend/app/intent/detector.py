from __future__ import annotations
from typing import List, Dict, Any
import re


class IntentDetector:
    """Rule-based intent detector with confidence scores.

    Returns dict:
    {
      "intents": [{"name": str, "confidence": float}],
      "confidence": float,  # max confidence
      "requires_multiple_agents": bool
    }

    This simple detector uses keyword sets per intent. It is deterministic and transparent,
    suitable for an internship project. Replaceable by an ML model later.
    """

    INTENT_KEYWORDS = {
        "billing": [r"bill", r"charge", r"payment", r"invoice", r"charged", r"premium", r"subscription", r"locked"],
        "refund": [r"refund", r"return", r"money back", r"reimburse"],
        "product": [r"price", r"pricing", r"spec", r"feature", r"sku", r"availability", r"outdoor", r"rated", r"discount", r"bulk"],
        "technical_support": [r"login", r"password", r"install", r"error", r"bug", r"connect", r"wifi", r"update", r"work", r"fail", r"lock"],
        "complaint": [r"angry", r"complain", r"unacceptable", r"sue", r"bad service", r"refund now", r"manager", r"escalate"],
        "general_faq": [r"warranty", r"shipping", r"how to", r"how do i", r"contact", r"support"],
    }

    def __init__(self, min_confidence: float = 0.4):
        self.min_confidence = min_confidence

    def detect(self, text: str) -> Dict[str, Any]:
        text_l = text.lower() if text else ""
        scores: Dict[str, float] = {}
        for intent, patterns in self.INTENT_KEYWORDS.items():
            score = 0.0
            for p in patterns:
                if re.search(p, text_l):
                    score += 1.0
            if score > 0:
                # Normalize confidence: min(1.0, score / 2.0)
                # This gives: 1 match = 0.5, 2+ matches = 1.0
                # without penalizing by pattern count
                scores[intent] = min(1.0, score / 2.0)

        # sort intents by score
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        intents_list = [{"name": name, "confidence": conf} for name, conf in sorted_intents]

        max_conf = intents_list[0]["confidence"] if intents_list else 0.0

        # determine if multiple agents likely needed
        requires_multi = False
        if len(intents_list) >= 2:
            # if top two confidences are similar above threshold, require multiple
            if intents_list[0]["confidence"] >= self.min_confidence and intents_list[1]["confidence"] >= self.min_confidence:
                requires_multi = True

        # also if certain combinations present like billing + technical
        names = [i["name"] for i in intents_list]
        if "billing" in names and "technical_support" in names:
            requires_multi = True

        return {"intents": intents_list, "confidence": max_conf, "requires_multiple_agents": requires_multi}
