from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services import chat_service
from backend.app.agents.base import AgentOutput

c=TestClient(app)

r=c.post('/auth/register', json={'username':'bob','password':'secret'})
print('reg', r.status_code, r.text)
r2=c.post('/auth/login', json={'username':'bob','password':'secret'})
print('login', r2.status_code, r2.text)

token=r2.json().get('access_token')
print('token', token)

# patch

def fake_execute(agents, user_text, rag_context=None):
    return [AgentOutput(agent='faq', answer='Hello debug', confidence=0.95, requires_escalation=False, sources=[])]

chat_service.default_chat_service.execute_agents = fake_execute

headers={'Authorization':f'Bearer {token}'}
r3=c.post('/chat', json={'message':'Hi there'}, headers=headers)
print('chat', r3.status_code, r3.text)
