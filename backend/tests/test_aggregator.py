from backend.app.orchestrator.aggregator import aggregate_agent_responses
from backend.app.agents.base import AgentOutput


def make_output(agent, answer, confidence=0.8, requires_escalation=False, sources=None):
    return AgentOutput(agent=agent, answer=answer, confidence=confidence, requires_escalation=requires_escalation, sources=sources or [], reasoning_summary="")


def test_one_agent_simple():
    out = make_output("faq", "Our warranty is 1 year.", sources=[{"doc_id": "warranty", "text": "AstraHome provides a 1-year limited manufacturer warranty."}])
    res = aggregate_agent_responses([out])
    assert "warranty" in res["final_answer"].lower()
    assert res["escalate"] is False


def test_two_agents_non_conflicting():
    a1 = make_output("billing", "You were charged $129.00 for AX1.", sources=[{"doc_id": "pricing", "text": "AX1-100: $129.00"}])
    a2 = make_output("technical_support", "Please try restarting the device and check Wi-Fi.")
    res = aggregate_agent_responses([a1, a2])
    assert "$129.00" in res["final_answer"] or "129" in res["final_answer"]
    assert "restart" in res["final_answer"].lower()


def test_three_agents_combination():
    a1 = make_output("billing", "Refunds are processed within 7-10 business days.")
    a2 = make_output("technical_support", "Ensure your subscription is active and app shows 'Premium' status.")
    a3 = make_output("product", "Home Secure Kit includes AstraCam X1 and 2 AstraPlugs.")
    res = aggregate_agent_responses([a1, a2, a3])
    assert "7-10" in res["final_answer"] or "premium" in res["final_answer"].lower()


def test_conflicting_answers_prefer_evidence():
    a1 = make_output("billing", "You can return unopened items within 30 days.", sources=[{"doc_id": "refund_policy", "text": "Unopened, unused items: return within 30 days of delivery for full refund."}], confidence=0.9)
    a2 = make_output("technical_support", "Usually returns are accepted within 14 days for opened items.", confidence=0.7)
    res = aggregate_agent_responses([a1, a2])
    # expectation: prefer evidence-backed 30 days
    assert "30 days" in res["final_answer"]


def test_missing_agent_output_and_escalation():
    a1 = make_output("billing", "", confidence=0.0, requires_escalation=True)
    a2 = make_output("faq", "Standard shipping is 3-5 business days.")
    res = aggregate_agent_responses([a1, a2])
    assert "3-5" in res["final_answer"]
    assert res["escalate"] is True


def test_agent_failure_all():
    a1 = make_output("billing", "", confidence=0.0, requires_escalation=True)
    a2 = make_output("technical_support", "", confidence=0.0, requires_escalation=True)
    res = aggregate_agent_responses([a1, a2])
    assert res["escalate"] is True
    assert "don't have any information" in res["final_answer"].lower() or "flagged for human review" in res["final_answer"].lower()


def test_no_retrieved_evidence_uncertainty():
    a1 = make_output("product", "It might be available in some regions.", confidence=0.5)
    res = aggregate_agent_responses([a1])
    assert "couldn't find direct evidence" in res["final_answer"].lower() or "note" in res["final_answer"].lower()
