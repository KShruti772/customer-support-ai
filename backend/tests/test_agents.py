import pytest

from backend.app.llm.service import LLMService
from backend.app.rag.pipeline import RAGPipeline
from backend.app.agents.billing_agent import BillingAgent
from backend.app.agents.technical_agent import TechnicalAgent
from backend.app.agents.product_agent import ProductAgent
from backend.app.agents.complaint_agent import ComplaintAgent
from backend.app.agents.faq_agent import FAQAgent
from backend.app.agents.base import AgentInput


class MockRAG:
    def __init__(self, docs):
        self.docs = docs

    def semantic_search(self, query, top_k=5):
        # Return docs that contain any query word
        res = []
        q = query.lower()
        for i, d in enumerate(self.docs):
            if any(w in d["text"].lower() for w in q.split()[:2]):
                res.append({"metadata": {"doc_id": d.get("id", f"doc{i}"), "text": d["text"]}, "score": 0.9})
        # fallback: return first doc
        if not res and self.docs:
            res = [{"metadata": {"doc_id": self.docs[0].get("id", "doc0"), "text": self.docs[0]["text"]}, "score": 0.1}]
        return res


def make_services():
    # LLMService with dummy provider
    llm = LLMService(provider="dummy")
    return llm


@pytest.fixture
def sample_docs():
    return [{"id": "p1", "text": "Warranty is 1 year."}, {"id": "p2", "text": "Shipping 3-5 days."}]


def test_billing_agent(sample_docs):
    rag = MockRAG(sample_docs)
    llm = make_services()
    agent = BillingAgent(rag, llm)
    inp = AgentInput(user_id="u1", conversation_id="c1", user_message="How do I get a refund?", conversation_history=[])
    out = agent.handle(inp)
    assert out.agent == "billing"
    assert isinstance(out.answer, str)


def test_technical_agent(sample_docs):
    rag = MockRAG(sample_docs)
    llm = make_services()
    agent = TechnicalAgent(rag, llm)
    inp = AgentInput(user_id="u2", conversation_id="c2", user_message="I forgot my password", conversation_history=[])
    out = agent.handle(inp)
    assert out.agent == "technical_support"


def test_product_agent(sample_docs):
    rag = MockRAG(sample_docs)
    llm = make_services()
    agent = ProductAgent(rag, llm)
    inp = AgentInput(user_id="u3", conversation_id="c3", user_message="What is the warranty?", conversation_history=[])
    out = agent.handle(inp)
    assert out.agent == "product"


def test_complaint_agent_escalation(sample_docs):
    rag = MockRAG(sample_docs)
    llm = make_services()
    agent = ComplaintAgent(rag, llm)
    inp = AgentInput(user_id="u4", conversation_id="c4", user_message="I am angry and want a refund now", conversation_history=[])
    out = agent.handle(inp)
    assert out.agent == "complaint"
    assert out.requires_escalation is True


def test_faq_agent(sample_docs):
    rag = MockRAG(sample_docs)
    llm = make_services()
    agent = FAQAgent(rag, llm)
    inp = AgentInput(user_id="u5", conversation_id="c5", user_message="How long is the warranty?", conversation_history=[])
    out = agent.handle(inp)
    assert out.agent == "faq"
    assert "warranty" in out.answer.lower() or out.answer != ""
