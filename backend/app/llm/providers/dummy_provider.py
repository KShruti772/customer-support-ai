from __future__ import annotations
from typing import List, Dict, Any
import time


class DummyProvider:
    """A deterministic provider used for local testing that does not call external APIs."""

    def __init__(self, **kwargs):
        pass

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.0, max_tokens: int = 256, timeout: int = 10) -> Dict[str, Any]:
        # Create a simple echo-style response using last user message and included context
        time_start = time.time()
        user_msgs = [m["content"] for m in messages if m["role"] == "user"]
        last_user = user_msgs[-1] if user_msgs else ""
        # find retrieved context in system message
        system_msgs = [m["content"] for m in messages if m["role"] == "system"]
        context = "\n".join(system_msgs)
        resp_text = f"Answer (dummy): based on retrieved info. Query: {last_user[:200]}"
        return {"text": resp_text, "raw": None, "usage": None, "latency": time.time() - time_start}
