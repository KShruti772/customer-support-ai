import pytest
import uuid
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.conversations import store, models

client = TestClient(app)


def get_auth_headers():
    """Helper to register/login and get auth headers."""
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    # Register
    r = client.post("/auth/register", json={"username": username, "password": "Password1"})
    
    if r.status_code == 201:
        # Registration succeeded, now login to get token
        r = client.post("/auth/login", json={"username": username, "password": "Password1"})
        if r.status_code != 200:
            raise Exception(f"Login failed: {r.status_code} {r.text}")
        token = r.json()["access_token"]
    elif r.status_code == 400:
        # User already exists, login
        r = client.post("/auth/login", json={"username": username, "password": "Password1"})
        if r.status_code != 200:
            raise Exception(f"Login failed: {r.status_code} {r.text}")
        token = r.json()["access_token"]
    else:
        raise Exception(f"Auth failed: {r.status_code} {r.text}")
    
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_conversation():
    headers = get_auth_headers()
    r = client.post("/conversations", json={}, headers=headers)
    assert r.status_code == 201
    conv = r.json()
    session_id = conv["session_id"]

    # retrieve
    r2 = client.get(f"/conversations/{session_id}", headers=headers)
    assert r2.status_code == 200
    got = r2.json()
    assert got["session_id"] == session_id


def test_add_message_and_history_limit():
    headers = get_auth_headers()
    # create
    r = client.post("/conversations", json={}, headers=headers)
    assert r.status_code == 201
    session_id = r.json()["session_id"]

    # add 30 messages
    for i in range(30):
        payload = {"sender": "user", "text": f"msg {i}"}
        r2 = client.post(f"/conversations/{session_id}/messages", json=payload, headers=headers)
        assert r2.status_code == 201

    # default history limit 20
    r3 = client.get(f"/conversations/{session_id}/history", headers=headers)
    assert r3.status_code == 200
    msgs = r3.json()["messages"]
    assert len(msgs) == 20
    assert msgs[0]["text"] == "msg 10"

    # custom smaller limit
    r4 = client.get(f"/conversations/{session_id}/history?max_messages=5", headers=headers)
    assert r4.status_code == 200
    assert len(r4.json()["messages"]) == 5


def test_continue_conversation_and_user_list():
    headers = get_auth_headers()
    # Get current user ID by creating a conversation and checking it
    r = client.post("/conversations", json={}, headers=headers)
    conv = r.json()
    session_id = conv["session_id"]
    user_id = conv["user_id"]

    # add a message
    client.post(f"/conversations/{session_id}/messages", json={"sender": "user", "text": "hello"}, headers=headers)
    client.post(f"/conversations/{session_id}/messages", json={"sender": "assistant", "text": "hi"}, headers=headers)

    # list by user
    r2 = client.get(f"/conversations/user/{user_id}", headers=headers)
    assert r2.status_code == 200
    data = r2.json()
    assert len(data["conversations"]) >= 1


def test_missing_session_returns_404():
    headers = get_auth_headers()
    r = client.get("/conversations/not-a-session", headers=headers)
    assert r.status_code == 404

    r2 = client.post("/conversations/not-a-session/messages", json={"sender": "user", "text": "x"}, headers=headers)
    assert r2.status_code == 404


def test_database_failure_handling(monkeypatch):
    headers = get_auth_headers()
    
    class BrokenStore:
        def create_conversation(self, payload):
            raise Exception("db down")

    monkeypatch.setattr(store, "default_store", BrokenStore())
    r = client.post("/conversations", json={}, headers=headers)
    assert r.status_code == 500
