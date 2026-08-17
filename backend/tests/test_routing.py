import pytest

from backend.app.router.router import AgentRouter


router = AgentRouter(min_confidence=0.2, max_agents=3)


cases = [
    # Clear billing
    ("Why was I charged twice on my card?", ["billing"]),
    ("I need an invoice for last month", ["billing"]),
    # Refund
    ("I want a refund for my camera", ["billing"]),
    ("How do I return an opened item?", ["billing"]),
    # Technical
    ("My camera won't connect to WiFi", ["technical_support"]),
    ("I forgot my password and can't login", ["technical_support"]),
    ("App shows error code 502 during setup", ["technical_support"]),
    # Product
    ("What is the price of AstraCam X1?", ["product"]),
    ("Is AstraPlug P1 outdoor rated?", ["product"]),
    ("Compare AstraCam X1 and X2 specifications", ["product"]),
    # Complaint
    ("I'm angry about the service and want to complain", ["complaint"]),
    ("This product is unacceptable and I want to escalate", ["complaint"]),
    # FAQ / General
    ("What is your warranty period?", ["faq"]),
    ("How long does shipping take?", ["faq"]),
    ("How can I contact support?", ["faq"]),
    # Multi-intent queries
    ("I paid yesterday but Premium is still locked.", ["billing", "technical_support"]),
    ("I requested a refund and the device also has a firmware error", ["billing", "technical_support"]),
    ("Price seems wrong and the app won't let me update payment", ["product", "billing", "technical_support"]),
    # Ambiguous queries (should fallback to faq or multiple)
    ("It doesn't work after update", ["technical_support"]),
    ("Is there a warranty on batteries?", ["faq"]),
    # Unknown queries
    ("What's the weather like today?", ["faq"]),
    ("Tell me a joke", ["faq"]),
    # Low confidence phrases
    ("I have a question about something", ["faq"]),
    ("Help", ["faq"]),
    # Edge multi-intent
    ("My subscription charged me but device still not working", ["billing", "technical_support"]),
    ("I want my money back and to speak to a manager", ["billing", "complaint"]),
    ("How do I install the thermostat and what is the price?", ["technical_support", "product"]),
    ("The device is broken and I want a refund now", ["billing", "complaint"]),
    ("Where can I find the user manual and warranty info?", ["faq"]),
    ("Is there a discount for bulk orders?", ["product"]),
    ("My package was delivered but missing items", ["faq"]),
    ("I was billed after I canceled the trial", ["billing"]),
]


@pytest.mark.parametrize("query,expected", cases)
def test_routing_cases(query, expected):
    out = router.route(query)
    agents = out["agents"]
    # Ensure expected agents subset of result and order not important
    for e in expected:
        assert e in agents
    # No duplicates
    assert len(agents) == len(set(agents))
