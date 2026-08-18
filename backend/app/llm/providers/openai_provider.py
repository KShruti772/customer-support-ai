from __future__ import annotations
import os
import time
import logging
from typing import List, Dict, Any

import openai
from openai import RateLimitError, APIError

_LOG = logging.getLogger(__name__)


class OpenAIProvider:
    def __init__(self, api_key_env: str = "OPENAI_API_KEY", model: str = "gpt-4o-mini", max_retries: int = 3):
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise EnvironmentError(f"Missing API key in env var {api_key_env}")
        openai.api_key = api_key
        self.model = model
        self.max_retries = max_retries

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 512, timeout: int = 30) -> Dict[str, Any]:
        """Call OpenAI chat completion with retries for rate limits and transient errors.

        messages: list of {'role': 'system'|'user'|'assistant', 'content': str}
        Returns: dict with keys: text (str), raw (original response), usage (if available), latency
        """
        attempt = 0
        start = time.time()
        while True:
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    request_timeout=timeout,
                )
                latency = time.time() - start
                # extract text
                choices = resp.get("choices", [])
                if choices:
                    text = "".join([c.get("message", {}).get("content", "") for c in choices])
                else:
                    text = ""
                usage = resp.get("usage") if isinstance(resp, dict) else None
                return {"text": text, "raw": resp, "usage": usage, "latency": latency}

            except RateLimitError as e:
                attempt += 1
                _LOG.warning("OpenAI rate limit encountered (attempt %s/%s)", attempt, self.max_retries)
                if attempt >= self.max_retries:
                    _LOG.exception("Rate limit: max retries reached")
                    raise
                backoff = 2 ** attempt
                time.sleep(backoff)
                continue
            except APIError as e:
                _LOG.exception("OpenAI API error: %s", str(e))
                raise
