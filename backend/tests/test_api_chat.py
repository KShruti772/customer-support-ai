from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services import auth_service, chat_service
from backend.app.agents.base import AgentOutput

client = TestClient(app)


def test_register_login_and_chat_success(monkeypatch):
    # register with valid password (8+ chars, letter + number)
    r = client.post("/auth/register", json={"username": "bob", "password": "secret123"})
    assert r.status_code == 201
    assert r.json()["user"]["username"] == "bob"

    # login
    r2 = client.post("/auth/login", json={"username": "bob", "password": "secret123"})
    assert r2.status_code == 200
    token = r2.json()["access_token"]

    # patch executor to deterministic AgentOutput
    def fake_execute(agents, user_text, rag_context=None):
        return [AgentOutput(agent="faq", answer="Hello, this is a test reply.", confidence=0.95, requires_escalation=False, sources=[])]

    monkeypatch.setattr(chat_service.default_chat_service, "execute_agents", fake_execute)

    # chat
    headers = {"Authorization": f"Bearer {token}"}
    r3 = client.post("/chat", json={"message": "Hi there"}, headers=headers)
    assert r3.status_code == 200
    body = r3.json()
    assert "Hello, this is a test reply." in body["answer"]
    assert "session_id" in body


def test_chat_unauthorized():
    r = client.post("/chat", json={"message": "hello"})
    assert r.status_code == 401


def test_chat_invalid_session(monkeypatch):
    # register/login with valid password
    client.post("/auth/register", json={"username": "carol", "password": "password1"})
    r = client.post("/auth/login", json={"username": "carol", "password": "password1"})
    token = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Provide a bad session id
    r2 = client.post("/chat", json={"message": "x", "session_id": "not-found"}, headers=headers)
    assert r2.status_code == 404
