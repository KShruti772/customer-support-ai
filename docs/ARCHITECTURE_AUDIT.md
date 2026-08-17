# Architecture Audit Report
**Customer Support AI Multi-Agent System**  
**Date**: 2026-08-16  
**Status**: Audit Complete

---

## Executive Summary

The project has **foundational scaffolding** in place but is **not yet production-ready**. Core infrastructure exists (FastAPI backend, Next.js frontend, auth flow, conversation store), but critical integration points are **incomplete or missing**:

- **Register frontend page**: Does not exist
- **Chat frontend page**: Does not exist  
- **Protected route guards**: Not implemented
- **Agent instantiation**: Agents defined but not wired to router/service
- **RAG pipeline**: Defined but not initialized or used
- **LLM integration**: Only dummy provider active
- **Dataset integration**: No datasets actually used by backend
- **Test execution**: Pytest not installed

The system is **architecturally sound** but **functionally incomplete**. A deliberate, phased implementation plan is required before feature development.

---

## 1. Implementation Status Matrix

| Component | Status | Evidence/File | Notes |
|---|---|---|---|
| **Auth** | | | |
| Login | ✅ IMPLEMENTED | backend/api/auth.py, frontend/pages/login.js | Functional register + login endpoints; login UI exists; token storage works |
| Registration | 🟡 PARTIALLY | backend/api/auth.py, frontend/components/AuthForm.jsx | Backend endpoint exists; frontend page missing; link on login page present |
| Logout | ✅ IMPLEMENTED | frontend/pages/_app.js | Context method defined; localStorage cleared; router.push('/login') works |
| AuthContext | ✅ IMPLEMENTED | frontend/pages/_app.js | Token and user state management; login/logout methods; localStorage sync |
| Token verification | ✅ IMPLEMENTED | backend/services/auth_service.py | verify_token() checks expiry; raises AuthError on invalid token |
| Protected routes | ❌ NOT IMPLEMENTED | frontend/pages/ | No route guards; /chat route unprotected; unauthenticated access allowed |
| **API Layer** | | | |
| Axios client | ✅ IMPLEMENTED | frontend/lib/api.js | Configured with baseURL; sets Authorization header; methods for all endpoints |
| CORS | ✅ IMPLEMENTED | backend/app/main.py | FastAPI CORSMiddleware configured; allows all origins by default |
| **Chat/Conversation** | | | |
| Chat endpoint | ✅ IMPLEMENTED | backend/api/chat.py | POST /chat requires Bearer token; routes to ChatService; returns session_id, answer, escalate, sources |
| Conversation create | ✅ IMPLEMENTED | backend/api/conversations.py | POST /conversations creates Conversation with optional user_id |
| Conversation history | ✅ IMPLEMENTED | backend/api/conversations.py | GET /conversations/{session_id}/history with max_messages query (default 20) |
| Send message | ✅ IMPLEMENTED | backend/api/conversations.py | POST /conversations/{session_id}/messages stores message with sender/text/metadata |
| Conversation list | ✅ IMPLEMENTED | backend/api/conversations.py | GET /conversations/user/{user_id} lists user's conversations |
| Chat frontend page | ❌ NOT IMPLEMENTED | frontend/pages/ | No /chat page exists; link in login redirects to /chat but page is missing |
| Chat UI | ❌ NOT IMPLEMENTED | frontend/components/ | No chat UI component; no message input; no conversation display |
| **Intent & Routing** | | | |
| Intent detector | 🟡 PARTIALLY | backend/app/intent/detector.py | Class exists; regex-based detection; wired to ChatService but not tested |
| Agent router | ✅ IMPLEMENTED | backend/app/router/router.py | AgentRouter.route() maps intents to agents; handles unknown intents; supports multi-agent selection |
| **Agents** | | | |
| Base agent class | ✅ IMPLEMENTED | backend/app/agents/base.py | AgentBase defines handle(AgentInput) → AgentOutput; includes RAG retrieval, LLM call, error handling |
| Billing agent | 🟡 PARTIALLY | backend/app/agents/billing_agent.py | Defined with system_instructions; inherits handle(); NOT instantiated in ChatService |
| FAQ agent | 🟡 PARTIALLY | backend/app/agents/faq_agent.py | Defined with system_instructions; inherits handle(); NOT instantiated in ChatService |
| Technical agent | 🟡 PARTIALLY | backend/app/agents/technical_agent.py | Defined with system_instructions; adds password reset guard; NOT instantiated in ChatService |
| Complaint agent | 🟡 PARTIALLY | backend/app/agents/complaint_agent.py | Defined with system_instructions; detects escalation keywords; NOT instantiated in ChatService |
| Product agent | 🟡 PARTIALLY | backend/app/agents/product_agent.py | Defined with system_instructions; inherits handle(); NOT instantiated in ChatService |
| Agent instantiation | ❌ NOT IMPLEMENTED | backend/app/services/chat_service.py | ChatService.execute_agents() returns dummy Message objects; does NOT call real agents |
| **Aggregation** | | | |
| Response aggregator | ✅ IMPLEMENTED | backend/app/orchestrator/aggregator.py | aggregate_agent_responses() merges multiple AgentOutput; deduplicates; resolves contradictions; marks escalation |
| **RAG** | | | |
| RAG pipeline class | ✅ IMPLEMENTED | backend/app/rag/pipeline.py | RAGPipeline defined with build_index() and semantic_search() |
| RAG initialization | ❌ NOT IMPLEMENTED | backend/app/services/chat_service.py | RAGPipeline instantiation wrapped in try/except; fails silently if called; source_folder/index_path undefined |
| Document loading | 🟡 PARTIALLY | backend/app/rag/doc_loader.py | load_documents_from_folder() defined but not called |
| Embeddings | 🟡 PARTIALLY | backend/app/rag/embeddings.py | EmbeddingModel class defined; uses sentence-transformers; not initialized in ChatService |
| FAISS index | 🟡 PARTIALLY | backend/app/rag/faiss_index.py | FaissIndex class defined; add/search/save/load methods; never instantiated |
| Retrieval | ❌ NOT IMPLEMENTED | backend/app/services/chat_service.py | RAG context retrieved but catches Exception silently; agent_outputs are dummy Message objects |
| **LLM** | | | |
| LLM service | ✅ IMPLEMENTED | backend/app/llm/service.py | LLMService with provider abstraction; _build_messages() constructs prompt; generate() calls provider |
| Dummy provider | ✅ IMPLEMENTED | backend/app/llm/providers/dummy_provider.py | DummyProvider.generate() returns echo response; always used in current config |
| OpenAI provider | 🟡 PARTIALLY | backend/app/llm/providers/openai_provider.py | openai_provider.py exists but not inspected; not configured in LLMService init |
| **Error Handling** | | | |
| API error responses | ✅ IMPLEMENTED | backend/app/api/*.py | HTTPException raised with status_code and detail; caught by FastAPI |
| Service error logging | ✅ IMPLEMENTED | backend/app/services/chat_service.py | Logger configured; catches and logs RAG/LLM failures; continues gracefully |
| Frontend error handling | 🟡 PARTIALLY | frontend/pages/login.js | try/catch on api.login(); displays error detail; no error handling on chat flow |
| **Data Persistence** | | | |
| User store | ✅ IMPLEMENTED | backend/app/users/store.py | InMemoryUserStore; create_user(), get_user_by_username(), get_user_by_id() |
| Conversation store | ✅ IMPLEMENTED | backend/app/conversations/store.py | InMemoryConversationStore; create_conversation(), add_message(), get_conversation(), list_conversations_for_user() |
| MongoDB placeholder | 🟡 PARTIALLY | backend/app/conversations/store.py | MongoConversationStore class skeleton exists; all methods raise NotImplementedError |
| **Tests** | | | |
| Test file: auth & chat | 🟡 PARTIALLY | backend/tests/test_api_chat.py | Imports exist; 3 test functions defined; pytest not installed (ImportError on execution) |
| Test file: conversations | 🟡 PARTIALLY | backend/tests/test_conversations.py | 6 test functions defined; pytest not installed |
| Test fixtures | ✅ IMPLEMENTED | backend/tests/ | TestClient(app) used; monkeypatch for mocking; proper assertions |
| Test execution | ❌ NOT IMPLEMENTED | Terminal | pytest module missing from requirements.txt; no test run possible |
| **Frontend Pages** | | | |
| Index/home | ✅ IMPLEMENTED | frontend/pages/index.js | GET /health check; displays backend status |
| Login | ✅ IMPLEMENTED | frontend/pages/login.js | AuthForm component; calls api.login(); stores token; redirects to /chat |
| Register | ❌ NOT IMPLEMENTED | frontend/pages/register.js | Page file missing; only AuthForm component and link exist |
| Chat | ❌ NOT IMPLEMENTED | frontend/pages/chat.js | Page file missing; login.js redirects here but no target |
| Conversation history | ❌ NOT IMPLEMENTED | frontend/pages/ | No UI to display past conversations; no API calls to getHistory() |
| Layout/nav | ❌ NOT IMPLEMENTED | frontend/components/ | No navigation bar; no logout button; no user display |

---

## 2. Actual API Contract

**Base URL**: `http://localhost:8000`  
**Auth Method**: Bearer token in Authorization header

| Method | Endpoint | Auth | Request Body | Response Body | Status | Error Behavior | Implementation |
|---|---|---|---|---|---|---|---|
| POST | `/auth/register` | None | `{"username": "...", "password": "..."}` | `{"user": {"id": "...", "username": "..."}}` | 201 | 400: user exists | backend/api/auth.py:19 |
| POST | `/auth/login` | None | `{"username": "...", "password": "..."}` | `{"access_token": "...", "token_type": "bearer"}` | 200 | 401: bad creds; 500: server error | backend/api/auth.py:28 |
| POST | `/chat` | Bearer | `{"message": "...", "session_id": "..."}` (session_id optional) | `{"session_id": "...", "answer": "...", "escalate": bool, "sources": [...]}` | 200 | 401: missing/invalid token; 404: session not found; 500: error | backend/api/chat.py:39 |
| POST | `/conversations` | None | `{"user_id": "...", "session_id": "...", "metadata": {...}}` (all optional) | `{"session_id": "...", "user_id": "...", "created_at": "...", "updated_at": "...", "messages": [...], "metadata": {...}}` | 201 | 500: db error | backend/api/conversations.py:8 |
| GET | `/conversations/{session_id}` | None | None | `{"session_id": "...", "user_id": "...", "created_at": "...", "updated_at": "...", "messages": [...], "metadata": {...}}` | 200 | 404: not found; 500: error | backend/api/conversations.py:29 |
| POST | `/conversations/{session_id}/messages` | None | `{"sender": "...", "text": "...", "metadata": {...}}` | `{"message": {"id": "...", "sender": "...", "text": "...", "timestamp": "...", "metadata": {...}}}` | 201 | 404: session not found; 500: error | backend/api/conversations.py:17 |
| GET | `/conversations/{session_id}/history` | None | Query: `max_messages=N` (default 20, range 1-200) | `{"messages": [...]}` (trimmed to last N) | 200 | 404: session not found; 500: error | backend/api/conversations.py:40 |
| GET | `/conversations/user/{user_id}` | None | None | `{"conversations": [...]}` | 200 | 500: error | backend/api/conversations.py:51 |
| GET | `/health` | None | None | `{"status": "ok"}` | 200 | Never | backend/app/main.py:16 |

---

## 3. Frontend ↔ Backend Contract Analysis

### 3.1 Login Flow

**Frontend sends** (frontend/lib/api.js:20-23):
```javascript
POST /auth/login
Body: { username, password }
```

**Backend expects** (backend/api/auth.py:28):
```python
POST /auth/login
Body: LoginReq(username: str, password: str)
Returns: {"access_token": token, "token_type": "bearer"}
```

✅ **MATCH**: Contract is correct.

**Frontend usage** (frontend/pages/login.js:15-19):
```javascript
const data = await api.login(username, password)
const token = data.access_token
login(token, { username })
api.setAuthToken(token)
```

✅ **CORRECT**: Extracts access_token, calls login() context method, sets Axios header.

---

### 3.2 Registration Flow

**Frontend sends** (frontend/lib/api.js:16-18):
```javascript
POST /auth/register
Body: { username, password }
```

**Backend expects** (backend/api/auth.py:19):
```python
POST /auth/register
Body: RegisterReq(username: str, password: str)
Returns: {"user": {"id": "...", "username": "..."}}
```

✅ **ENDPOINT MATCHES**: But...

❌ **MISSING FEATURE**: 
- Frontend has no `/register` page
- Frontend has only a link to `/register` on the login page
- No page or form component handles registration UI
- `api.register()` function exists but never called

**Required fix**: Create `frontend/pages/register.js` that mirrors login.js logic.

---

### 3.3 Chat Flow

**Frontend sends** (frontend/lib/api.js:30-32):
```javascript
POST /chat
Body: { message, session_id }
Headers: Authorization: Bearer {token}
```

**Backend expects** (backend/api/chat.py:39):
```python
POST /chat
Body: ChatRequest(message: str, session_id: Optional[str])
Dependency: get_current_user (requires Authorization header with Bearer token)
Returns: ChatResponse(session_id, answer, escalate, sources)
```

✅ **ENDPOINT MATCHES**: Contract is correct.

❌ **MISSING FEATURE**:
- Frontend has no `/chat` page
- `sendChat()` function exists but never called
- No UI to render chat messages or send input

**Required fix**: Create `frontend/pages/chat.js` with message input, display, and call to `api.sendChat()`.

---

### 3.4 Conversation History

**Frontend sends** (frontend/lib/api.js:44-46):
```javascript
GET /conversations/{session_id}/history?max_messages=max_messages
```

**Backend expects** (backend/api/conversations.py:40):
```python
GET /conversations/{session_id}/history?max_messages=N
Returns: {"messages": [...]}
```

✅ **ENDPOINT MATCHES**: Contract is correct.

❌ **MISSING FEATURE**:
- Frontend `getHistory()` function exists but never called
- No UI displays conversation history
- No pagination or message list component

**Required fix**: Create UI component to display `getHistory()` results.

---

### 3.5 Conversation Creation

**Frontend sends** (frontend/lib/api.js:25-27):
```javascript
POST /conversations
Body: payload (arbitrary object)
```

**Backend expects** (backend/api/conversations.py:8):
```python
POST /conversations
Body: ConversationCreate(user_id: Optional[str], session_id: Optional[str], metadata: Optional[Dict])
Returns: Conversation (full object with session_id, user_id, created_at, updated_at, messages, metadata)
```

✅ **ENDPOINT MATCHES**: Contract is correct.

❌ **MISSING FEATURE**:
- Frontend `createConversation()` function exists but never called
- Chat page does not create new conversations before sending messages
- ChatService creates conversations automatically if session_id not provided, but frontend never initiates

**Required fix**: Chat page should call `createConversation({ user_id })` at init and store session_id.

---

### 3.6 AuthContext & Token Storage

**Frontend** (frontend/pages/_app.js:12-26):
```javascript
- localStorage.setItem('auth_token', token)
- localStorage.setItem('auth_user', JSON.stringify(user))
- Loads on mount: const t = localStorage.getItem('auth_token')
- Provides: { token, user, login, logout }
```

✅ **CORRECT**: Token persists across page reloads; login(token, user) updates context and storage.

⚠️ **ISSUE**: No token refresh mechanism; no expiry handling.

---

### 3.7 Axios Authorization Header

**Frontend** (frontend/lib/api.js:11-12):
```javascript
export function setAuthToken(token) {
    if (token) client.defaults.headers.common['Authorization'] = `Bearer ${token}`
    else delete client.defaults.headers.common['Authorization']
}
```

✅ **CORRECT**: Called after login to set Authorization header.

⚠️ **ISSUE**: Not called on page load after localStorage restore; Axios will not have token on initial app render.

**Fix required**: Call `setAuthToken(token)` in useEffect on _app.js when token is loaded from localStorage.

---

## 4. Auth Flow Trace

```
User fills login form
         ↓
frontend/pages/login.js calls api.login(username, password)
         ↓
frontend/lib/api.js: client.post('/auth/login', { username, password })
         ↓
backend/api/auth.py: POST /auth/login
         ↓
backend/services/auth_service.py: AuthService.login(username, password)
         ├─ get_user_by_username(username) → InMemoryUserStore
         ├─ compare hashed password
         ├─ generate token (secrets.token_urlsafe(32))
         ├─ store in self._tokens[token] = (user_id, expires_at)
         └─ return token
         ↓
backend/api/auth.py: return {"access_token": token, "token_type": "bearer"}
         ↓
frontend/pages/login.js receives { access_token: "..." }
         ├─ context.login(token, { username })
         │  ├─ localStorage.setItem('auth_token', token)
         │  ├─ localStorage.setItem('auth_user', JSON.stringify(user))
         │  ├─ setToken(token)
         │  └─ setUser(user)
         ├─ api.setAuthToken(token)
         │  └─ client.defaults.headers.common['Authorization'] = `Bearer ${token}`
         └─ router.push('/chat')
         
User navigates to any protected endpoint (e.g., /chat)
         ↓
frontend/lib/api.js: Axios includes Authorization header automatically
         ↓
backend/api/chat.py: get_current_user(authorization: str) dependency
         ├─ extract token from "Bearer TOKEN"
         ├─ backend/services/auth_service.py: verify_token(token)
         │  ├─ check if token in self._tokens
         │  ├─ check if expired
         │  └─ return user_id or None
         ├─ backend/app/users/store.py: get_user_by_id(user_id)
         └─ return User or raise HTTPException(401)
         
Logout:
         ↓
frontend/pages/_app.js: context.logout()
         ├─ localStorage.removeItem('auth_token')
         ├─ localStorage.removeItem('auth_user')
         ├─ setToken(null)
         ├─ setUser(null)
         └─ router.push('/login')
```

### Auth Flow Status:

✅ **Token generation**: Works (SHA256 hash with salt)  
✅ **Token storage**: Works (in-memory dict in AuthService)  
✅ **Token verification**: Works (checks expiry, raises AuthError)  
✅ **Axios header setup**: Works after login  
⚠️ **Header setup on page reload**: Missing (token in localStorage but not set in Axios)  
✅ **Logout**: Works (clears localStorage)  
❌ **Protected routes**: Not implemented (no route guard middleware in Next.js)  
❌ **Register page**: Not implemented  

---

## 5. Chat Flow Trace

```
User is on /chat page (MISSING)
         ↓
User types message and clicks Send
         ↓
frontend/pages/chat.js calls api.sendChat(message, session_id)  (NO CHAT PAGE)
         ↓
frontend/lib/api.js: client.post('/chat', { message, session_id })
         ↓
Axios includes Authorization header (set after login)
         ↓
backend/api/chat.py: POST /chat (line 39)
         ├─ Depends: get_current_user(authorization)
         │  ├─ extract token
         │  ├─ verify_token(token) via AuthService
         │  └─ get_user_by_id(user_id) from UserStore
         ├─ Receives: ChatRequest(message, session_id)
         └─ Calls: chat_service.default_chat_service.chat(user_id, message, session_id)
         
backend/app/services/chat_service.py: ChatService.chat() (line 42)
         ├─ _load_or_create_conversation(session_id, user_id)
         │  └─ If session_id: get_conversation(session_id)
         │     Else: create_conversation({ user_id: user_id })
         │        → Stored in InMemoryConversationStore
         ├─ conversation_store.add_message(session_id, "user", message)
         │  └─ Message object added to conv.messages list
         ├─ IntentDetector().detect(message)
         │  └─ Simple regex pattern matching (PARTIALLY IMPLEMENTED)
         │     Returns: { intents: [...], confidence, requires_multiple_agents }
         ├─ AgentRouter().route(message)
         │  ├─ Takes intent, maps to agent names
         │  ├─ Returns: { intents, agents, requires_escalation, reason }
         │  └─ Agents list: ["billing"], ["faq"], ["technical_support"], etc.
         ├─ ATTEMPT: RAG retrieval (wrapped in try/except, SILENTLY FAILS)
         │  └─ RAGPipeline() requires source_folder, index_path (UNDEFINED)
         │     semantic_search(message, top_k=3) → Exception caught
         ├─ execute_agents(agents, message, rag_context=None) (line 34)
         │  └─ ⚠️ DUMMY IMPLEMENTATION:
         │     Returns: List of Message(sender="assistant", text=f"[{a}] response to: {user_text}")
         │     ❌ Does NOT instantiate real Agent objects
         │     ❌ Does NOT call any Agent.handle()
         │     ❌ Does NOT use RAG or LLM
         ├─ Convert agent outputs to AgentOutput list
         │  └─ Since execute_agents returns Message objects (not AgentOutput):
         │     Creates AgentOutput(agent="assistant", answer=msg.text, confidence=0.7, ...)
         ├─ aggregator.aggregate_agent_responses(ao_list)
         │  ├─ Deduplicates sentences
         │  ├─ Resolves numeric conflicts in responses
         │  ├─ Marks escalation if any agent requires it
         │  └─ Returns: { final_answer, escalate, sources, confidence }
         ├─ conversation_store.add_message(session_id, "assistant", final_answer)
         │  └─ Stored in conv.messages list
         └─ Returns: ChatResult(final_answer, escalate, sources)

backend/api/chat.py: return ChatResponse (line 52)
         ├─ session_id (stored or fetched from last conversation)
         ├─ answer (final_answer from aggregator)
         ├─ escalate (bool)
         └─ sources (list)

frontend receives { session_id, answer, escalate, sources }
         ↓
frontend/pages/chat.js DISPLAYS RESPONSE  (NO CHAT PAGE)
         ↓
User continues conversation
         ↓
Next api.sendChat(message, session_id) reuses same session
```

### Chat Flow Status:

✅ **Endpoint routing**: Correct  
✅ **Authentication**: Token verified  
✅ **Conversation storage**: Stored in InMemoryConversationStore  
✅ **Intent detection**: Implemented (regex-based)  
✅ **Agent routing**: Implemented (INTENT_TO_AGENT mapping)  
❌ **Agent instantiation**: MISSING (dummy execute_agents returns fake Message objects)  
❌ **RAG retrieval**: Not initialized (RAGPipeline fails silently)  
❌ **LLM call**: Not reached (agents not instantiated)  
✅ **Aggregation**: Implemented (deduplicates, resolves conflicts)  
✅ **Response storage**: Stored in InMemoryConversationStore  
❌ **Chat page**: Not implemented  
❌ **Message display**: Not implemented  

**Key issue**: Agent instantiation is missing. ChatService.execute_agents() is a placeholder that returns dummy Message objects instead of calling real agents.

---

## 6. Multi-Agent Architecture

### 6.1 Agent Base Class

**File**: backend/app/agents/base.py

```python
class AgentBase:
    name: str = "base"
    system_instructions: str = "..."
    
    def __init__(self, rag, llm_service):
        self.rag = rag
        self.llm = llm_service
    
    def handle(self, payload: AgentInput) -> AgentOutput:
        # 1. Retrieve RAG context
        # 2. Call LLM with system_instructions + retrieved chunks
        # 3. Return AgentOutput(agent, answer, confidence, escalate, sources)
```

✅ **Status**: IMPLEMENTED  
✅ **Flow**: Receives AgentInput → retrieves RAG → calls LLM → returns AgentOutput  
✅ **Error handling**: Catches RAG/LLM failures, returns AgentOutput with requires_escalation=True  

---

### 6.2 Concrete Agents

| Agent | File | System Instructions | Role | RAG | LLM | Instantiation |
|---|---|---|---|---|---|---|
| **Billing** | backend/app/agents/billing_agent.py | "Answer about payments, subscriptions, invoices, refunds" | Handle billing inquiries; prioritize invoice numbers | Uses inherited handle() | Uses inherited handle() | ❌ NOT instantiated |
| **FAQ** | backend/app/agents/faq_agent.py | "Provide short factual answers to general questions using retrieved content" | Answer FAQs; point to support email | Uses inherited handle() | Uses inherited handle() | ❌ NOT instantiated |
| **Technical** | backend/app/agents/technical_agent.py | "Assist with login, password reset, installation, errors, bugs" | Handle tech support; numbered steps; escalate if needed; adds instruction not to ask for passwords | Uses inherited handle() | Uses inherited handle() | ❌ NOT instantiated |
| **Complaint** | backend/app/agents/complaint_agent.py | "Handle complaints sensitively; acknowledge issue; offer steps; escalate when needed" | Handle complaints; escalate on "angry", "unacceptable", "sue", "refund now" keywords | Uses inherited handle() | Uses inherited handle() | ❌ NOT instantiated |
| **Product** | backend/app/agents/product_agent.py | "Answer about product features, pricing, comparisons, availability" | Handle product queries; be factual; reference specs; recommend contacting support if stock unknown | Uses inherited handle() | Uses inherited handle() | ❌ NOT instantiated |

**All agents**:
- ✅ Inherit from AgentBase
- ✅ Define name and system_instructions
- ✅ Override handle() for agent-specific logic (billing, technical, complaint)
- ❌ **NEVER INSTANTIATED** in ChatService
- ❌ **NEVER CALLED** during chat flow

---

### 6.3 Router

**File**: backend/app/router/router.py

```python
class AgentRouter:
    INTENT_TO_AGENT = {
        "billing": ["billing"],
        "refund": ["billing"],
        "product": ["product"],
        "technical_support": ["technical_support"],
        "complaint": ["complaint"],
        "general_faq": ["faq"],
    }
    
    def route(self, text: str) -> Dict[str, Any]:
        # Detect intent
        # Map to agents
        # Handle low confidence, unknown intents
        # Return { intents, agents, requires_escalation, reason }
```

✅ **Status**: IMPLEMENTED  
✅ **Input**: User text  
✅ **Output**: List of agent names to execute  
⚠️ **Issue**: Returns agent names but ChatService.execute_agents() ignores them and returns dummy responses  

---

### 6.4 Orchestrator / Aggregator

**File**: backend/app/orchestrator/aggregator.py

```python
def aggregate_agent_responses(agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
    # Accept multiple AgentOutput objects
    # Deduplicate sentences
    # Resolve numeric conflicts (prefer evidence-backed answers)
    # Group by topics (billing, shipping, etc.)
    # Mark escalation if any agent requires it
    # Return: { final_answer, escalate, sources, confidence }
```

✅ **Status**: IMPLEMENTED  
✅ **Input**: List of AgentOutput  
✅ **Output**: Single customer-facing response with escalation flag  
✅ **Deduplication**: Removes duplicate sentences while preserving order  
✅ **Conflict resolution**: When multiple sources disagree on numbers, prefers evidence-backed answers  
⚠️ **Current usage**: Receives dummy Message-derived objects from ChatService.execute_agents(), not real AgentOutput  

---

### 6.5 Integration Points

**Integration Status**:

```
ChatService.chat()
    ├─ IntentDetector.detect() ✅ WORKS
    ├─ AgentRouter.route() ✅ WORKS
    ├─ ChatService.execute_agents() ❌ DUMMY (returns Message, not AgentOutput)
    │  ├─ Should instantiate agents based on router output
    │  ├─ Should call Agent.handle(AgentInput)
    │  ├─ Should collect AgentOutput list
    │  └─ Should pass to aggregator
    └─ aggregator.aggregate_agent_responses() ✅ WORKS (but receives wrong input)
```

**Missing connection**: ChatService does not instantiate or call the Agent classes.

---

## 7. Dataset Integration

### Current Status

None of the datasets are actually used by the backend.

| Dataset | Location | Type | Size | Actually Used? | Where? | Purpose |
|---|---|---|---|---|---|---|
| **Banking77** | datasets/banking77/ | Labeled intents (CSV) | train.csv (4,000 rows), test.csv (1,000 rows) | ❌ NO | — | Intended for intent detection training/evaluation; IntentDetector uses hardcoded regex patterns instead |
| **MS MARCO** | datasets/*.json (train/dev v1.1/v2.0) | Questions + passages (JSON) | Large (~100k passages) | ❌ NO | — | Intended for RAG training/evaluation; RAG pipeline not initialized; FAISS index not built |
| **SQuAD** | datasets/train-v1.1.json, dev-v1.1.json | QA pairs (JSON) | ~100k training examples | ❌ NO | — | Intended for QA evaluation; not referenced in codebase |
| **Complaints** | datasets/complaints.csv | Customer complaints (CSV) | ~1,000 rows | ❌ NO | — | Intended for complaint agent training; not loaded or used |
| **Dialogues** | datasets/data/*.txt | Multilingual conversations | 12 files (DE/EN/IT/ZH, train/dev/test) | ❌ NO | — | Intended for conversation evaluation; not loaded or used |
| **Queries** | datasets/queries*.tsv | Search queries | 3 files (dev/eval/train) | ❌ NO | — | Intended for retrieval evaluation; not used |
| **Qrels** | datasets/qrels.dev.tsv | Query-relevance judgments | ~4k rows | ❌ NO | — | Intended for retrieval evaluation; not used |
| **Collection** | datasets/collection.tsv | Document corpus | ~200k rows | ❌ NO | — | Intended for retrieval corpus; not loaded |

### Detailed Analysis

**Banking77** (Intent Detection):
- ❌ Not used by IntentDetector (backend/app/intent/detector.py)
- IntentDetector uses hardcoded regex patterns:
  ```python
  "billing": [r"invoice", r"payment", r"subscription", ...],
  "technical_support": [r"login", r"password", r"install", r"error", ...],
  ```
- **Fix required**: Integrate Banking77 dataset for training an intent classifier (e.g., using transformers library)

**MS MARCO** (RAG Training):
- ❌ Not used by RAGPipeline (backend/app/rag/pipeline.py)
- RAGPipeline.build_index() calls load_documents_from_folder(source_folder)
- source_folder is undefined in chat_service.py
- RAGPipeline instantiation fails silently in try/except
- **Fix required**: Point RAGPipeline to datasets/data or create a proper document corpus from MS MARCO

**SQuAD** (QA Evaluation):
- ❌ Not referenced in codebase
- Could be used for evaluating answer quality but not currently integrated

**Complaints** (Complaint Agent Training):
- ❌ Not used by ComplaintAgent
- ComplaintAgent uses only system_instructions and inherits RAG/LLM from base
- **Fix required**: Load complaints.csv for fine-tuning or few-shot examples

**Dialogues** (Conversation Evaluation):
- ❌ Not referenced
- Could be used for evaluating multi-turn conversation quality
- Multilingual support (DE/EN/IT/ZH) suggests production internationalization intent but no i18n in code

**Queries / Qrels / Collection** (Retrieval Evaluation):
- ❌ Not used
- Could be used for evaluating RAG retrieval quality (precision, recall, MRR)
- Standard IR evaluation format but not integrated

### Conclusion

The datasets folder is **organized but disconnected from the backend**. To integrate datasets:

1. **Intent Detection**: Train or fine-tune a classifier on Banking77
2. **RAG**: Build a FAISS index from MS MARCO or a subset of documents
3. **Evaluation**: Set up an evaluation pipeline using SQuAD, queries/qrels, and dialogues
4. **Domain data**: Load complaints.csv into few-shot examples or fine-tuning corpus

---

## 8. Test Execution Results

### Attempt 1: Run existing tests

**Command**:
```bash
cd D:\customer-support-ai
.\.venv\Scripts\python.exe -m pytest backend/tests/test_api_chat.py backend/tests/test_conversations.py -q
```

**Result**: ❌ FAILED

**Error**:
```
D:\customer-support-ai\.venv\Scripts\python.exe: No module named pytest
```

**Cause**: pytest is not in backend/requirements.txt

**Status**: Tests cannot run.

### Test Files Exist

✅ backend/tests/test_api_chat.py (50 lines)
- 3 test functions defined (test_register_login_and_chat_success, test_chat_unauthorized, test_chat_invalid_session)
- Uses TestClient(app) from FastAPI
- Uses monkeypatch to mock ChatService.execute_agents()
- Tests expect /auth/register, /auth/login, /chat endpoints

✅ backend/tests/test_conversations.py (80 lines)
- 6 test functions defined
- Tests /conversations endpoints
- Tests conversation creation, message addition, history retrieval, user listing
- Tests error handling (404, 500)

### Test Quality

✅ Fixtures: TestClient(app) is correct for FastAPI  
✅ Mocking: monkeypatch.setattr() used properly  
✅ Assertions: status_code and response body checked  
✅ Coverage: Auth, chat, conversations, error cases  
⚠️ Issue: Tests assume real agent execution but mock execute_agents()  
⚠️ Issue: No tests for RAG pipeline  
⚠️ Issue: No tests for LLM service  
⚠️ Issue: No tests for intent detection  

### Recommendation

Add pytest to requirements.txt:
```
pytest==7.4.0
pytest-asyncio==0.21.0
```

Then run:
```bash
cd D:\customer-support-ai
pip install -r backend/requirements.txt
python -m pytest backend/tests/ -v
```

---

## 9. Frontend Status

### Pages Implemented

| Page | File | Status | Features |
|---|---|---|---|
| **Home** | frontend/pages/index.js | ✅ IMPLEMENTED | Displays backend /health status; no real functionality |
| **Login** | frontend/pages/login.js | ✅ IMPLEMENTED | AuthForm component; calls api.login(); stores token; redirects to /chat |
| **Register** | frontend/pages/register.js | ❌ NOT IMPLEMENTED | Missing; link on login page present but no target |
| **Chat** | frontend/pages/chat.js | ❌ NOT IMPLEMENTED | Missing; login redirects here but page doesn't exist |
| **Layout** | frontend/pages/_app.js | ✅ IMPLEMENTED | Global AuthContext; token/user state; login/logout methods |

### Components Implemented

| Component | File | Status | Usage |
|---|---|---|---|
| **AuthForm** | frontend/components/AuthForm.jsx | ✅ IMPLEMENTED | Used by login.js; accepts mode (login/register) and onSubmit handler |

### Features by Category

#### Authentication
- ✅ Login form and submission
- ❌ Register form (component exists but no page)
- ✅ Token storage (localStorage)
- ✅ Token restoration on page load (useEffect in _app.js)
- ⚠️ Axios header setup (missing on page reload)
- ✅ Logout (clears localStorage, redirects to /login)
- ❌ Protected routes (no route guards)
- ❌ Token refresh/expiry handling
- ❌ 401 error recovery

#### Chat Interface
- ❌ Chat page
- ❌ Message input form
- ❌ Message list display
- ❌ Loading indicators
- ❌ Error messages
- ❌ Conversation switcher
- ❌ New conversation button

#### Conversation Management
- ❌ Conversation list
- ❌ Conversation history display
- ❌ Conversation search/filter
- ❌ Delete conversation
- ❌ Rename conversation

#### User Experience
- ✅ Form validation (required fields in AuthForm)
- ✅ Loading state (button disabled during submission)
- ⚠️ Error display (login.js shows error detail)
- ❌ Toast notifications
- ❌ Confirmation dialogs
- ❌ Mobile responsiveness (Tailwind configured but not tested)

### API Calls Implemented (But Not Used)

**frontend/lib/api.js** defines:
- ✅ `register(username, password)` → POST /auth/register
- ✅ `login(username, password)` → POST /auth/login
- ✅ `createConversation(payload)` → POST /conversations
- ✅ `sendChat(message, session_id)` → POST /chat
- ✅ `getConversationsForUser(user_id)` → GET /conversations/user/{user_id}
- ✅ `getHistory(session_id, max_messages)` → GET /conversations/{session_id}/history

**Actual usage**:
- ✅ login() called from login.js
- ❌ register() never called (no register page)
- ❌ createConversation() never called
- ❌ sendChat() never called
- ❌ getConversationsForUser() never called
- ❌ getHistory() never called

### Issue: Axios Header Not Set on Page Load

**Problem**: When user navigates back to app and page reloads, token is restored from localStorage but Axios header is not set.

**Location**: frontend/pages/_app.js

**Current code**:
```javascript
useEffect(() => {
    const t = localStorage.getItem('auth_token')
    const u = localStorage.getItem('auth_user')
    if (t) setToken(t)  // ← Sets React state
    if (u) setUser(JSON.parse(u))
    // ← Missing: api.setAuthToken(t)
}, [])
```

**Fix required**:
```javascript
useEffect(() => {
    const t = localStorage.getItem('auth_token')
    const u = localStorage.getItem('auth_user')
    if (t) {
        setToken(t)
        api.setAuthToken(t)  // ← Add this line
    }
    if (u) setUser(JSON.parse(u))
}, [])
```

---

## 10. Architecture Diagram

### Actual Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (User)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │    Next.js Frontend         │
        │  (React 19, Tailwind CSS)   │
        ├──────────────────────────────┤
        │ Pages:                       │
        │  ✅ index.js (health check)  │
        │  ✅ login.js (auth)          │
        │  ❌ register.js (missing)    │
        │  ❌ chat.js (missing)        │
        └──────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │   React Context              │
        │   (_app.js: AuthContext)     │
        │   {token, user, login, logout}
        └──────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────┐
        │   Axios HTTP Client          │
        │   (frontend/lib/api.js)      │
        │  - setAuthToken()            │
        │  - login()                   │
        │  - register()                │
        │  - sendChat()                │
        │  - getHistory()              │
        │  - createConversation()      │
        └──────────────────────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ↓                ↓                ↓
POST /auth/login  POST /chat      POST /conversations
GET /health       GET /history    GET /conversations/*
                                  
      └────────────────┼────────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    FastAPI Backend           │
        │  (uvicorn on port 8000)      │
        ├──────────────────────────────┤
        │ API Routes:                  │
        │  ✅ /auth/register           │
        │  ✅ /auth/login              │
        │  ✅ /chat                    │
        │  ✅ /conversations/*         │
        │  ✅ /health                  │
        └──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ↓              ↓              ↓
    Services       Storage         Auth
    ├─ ChatService ├─ Users    ├─ AuthService
    │  ├─ intent   │  ├─ Store │  ├─ register()
    │  ├─ route    │  │  ├─ get │  ├─ login()
    │  ├─ ❌agents │  │  └─ id  │  ├─ verify_token()
    │  ├─ ❌rag    │  │         │  └─ revoke_token()
    │  └─ aggregate│ Conversations
    │              │  ├─ Store
    │              │  ├─ create
    │              │  ├─ add_msg
    │              │  ├─ get
    │              │  └─ list
    │              │
    │         InMemory
    │         (no DB)
    │
    └─→ ❌ AGENTS NOT INSTANTIATED
        ❌ RAG NOT INITIALIZED
        ✅ Aggregator works
        ✅ Intent detection (regex)
        ✅ Router (INTENT_TO_AGENT mapping)
        ⚠️ LLM (dummy provider only)
```

### Missing/Incomplete Pieces

**Frontend**:
- ❌ register.js page
- ❌ chat.js page
- ❌ Protected route guards
- ❌ Chat UI components
- ⚠️ Axios header on page reload

**Backend**:
- ❌ Agent instantiation (agents defined but not used)
- ❌ RAG initialization (RAGPipeline not called)
- ❌ Real LLM integration (dummy provider only)
- ❌ Database layer (InMemory only; MongoDB placeholder exists)
- ❌ Intent classifier training (regex patterns only)

---

## 11. ARCHITECTURE_AUDIT.md (This File)

This document is the audit report. Key sections:

1. ✅ Implementation Status Matrix
2. ✅ Actual API Contract
3. ✅ Frontend/Backend Contract Mismatches
4. ✅ Auth Flow Trace
5. ✅ Chat Flow Trace
6. ✅ Multi-Agent Architecture
7. ✅ Dataset Integration Analysis
8. ✅ Test Execution Results
9. ✅ Frontend Status
10. ✅ Architecture Diagram
11. ✅ Recommended Implementation Order (below)

---

## 12. Recommended Implementation Order

### Phase 1: Fix Immediate Contract Gaps (Days 1-2)

These are critical blockers that prevent the frontend from working at all.

1. **Fix Axios header on page reload** (5 min)
   - File: `frontend/pages/_app.js`
   - Add: `api.setAuthToken(t)` in useEffect
   - Impact: Frontend will keep auth token after page reload

2. **Create register page** (30 min)
   - File: `frontend/pages/register.js`
   - Copy: login.js structure
   - Change: mode="register", call api.register instead of api.login
   - Impact: Users can create accounts

3. **Create chat page** (2-3 hours)
   - File: `frontend/pages/chat.js`
   - Implement: Message input form
   - Implement: Message list display (local state)
   - Implement: Call api.sendChat() on submit
   - Implement: Call api.createConversation() on mount if no session_id
   - Implement: Display response in UI
   - Impact: Users can send messages (even if responses are dummy)

4. **Install pytest and run tests** (15 min)
   - Add pytest to requirements.txt
   - Run: `pytest backend/tests/ -v`
   - Impact: Understand actual test status

5. **Add protected route guard** (30 min)
   - File: `frontend/pages/chat.js`
   - Add: useEffect redirect to /login if no token
   - Impact: Unauthenticated users can't access /chat

---

### Phase 2: Wire Agents & RAG (Days 3-4)

Once frontend works with dummy responses, connect real agents and RAG.

6. **Initialize RAG pipeline** (3-4 hours)
   - File: `backend/app/services/chat_service.py`
   - Define: source_folder (e.g., datasets/data/)
   - Define: index_path for FAISS
   - Build: RAGPipeline().build_index() on service init
   - Impact: RAG retrieval works

7. **Instantiate agents in ChatService** (2-3 hours)
   - File: `backend/app/services/chat_service.py`
   - Create: Agent instances (BillingAgent, FAQAgent, etc.)
   - Call: Agent.handle(AgentInput) instead of dummy execute_agents()
   - Collect: AgentOutput list
   - Impact: Real agents are called

8. **Fix LLM initialization** (1 hour)
   - File: `backend/app/services/chat_service.py`
   - Initialize: LLMService (currently not initialized)
   - Pass: to Agent constructors
   - Impact: Agents can call LLM

---

### Phase 3: Training & Evaluation (Days 5-7)

Improve quality with real models and datasets.

9. **Train intent classifier** (4-6 hours)
   - Dataset: Banking77
   - Replace: Regex patterns with trained model
   - Impact: Better intent detection accuracy

10. **Build FAISS index from MS MARCO** (2-3 hours)
    - Load: MS MARCO documents
    - Embed: Using sentence-transformers
    - Build: FAISS index
    - Save: To disk
    - Impact: Better retrieval quality

11. **Integrate complaint examples** (1-2 hours)
    - Load: complaints.csv
    - Use: As few-shot examples or fine-tuning data
    - Impact: Better complaint handling

12. **Setup evaluation pipeline** (3-4 hours)
    - Use: SQuAD for QA eval
    - Use: queries/qrels for retrieval eval
    - Use: dialogues for conversation eval
    - Impact: Measure system performance

---

### Phase 4: Production Readiness (Days 8+)

Deploy and monitor.

13. **Implement MongoDB for persistence** (4-5 hours)
    - File: `backend/app/conversations/store.py`
    - Complete: MongoConversationStore methods
    - Switch: default_store from InMemory to Mongo
    - Impact: Data persists across restarts

14. **Add token refresh mechanism** (2 hours)
    - File: `backend/services/auth_service.py`
    - Add: Refresh token generation
    - File: `frontend/lib/api.js`
    - Intercept: 401 responses, refresh token, retry
    - Impact: Sessions don't expire mid-conversation

15. **Add error handling & logging** (3-4 hours)
    - Frontend: Toast notifications for errors
    - Backend: Structured logging (JSON)
    - Impact: Better debugging and UX

16. **Deploy to Cloud Run / GKE** (2-3 hours)
    - Create: Dockerfile, docker-compose.yml
    - Set: Environment variables (OPENAI_API_KEY, DB_URL)
    - Deploy: Backend and frontend separately
    - Impact: Production deployment

---

## Priority Order Summary

**Critical (Days 1-2)**:
1. Fix Axios header on page reload
2. Create register page
3. Create chat page
4. Install pytest and verify tests pass
5. Add protected route guard

**High (Days 3-4)**:
6. Initialize RAG pipeline
7. Instantiate agents in ChatService
8. Fix LLM initialization

**Medium (Days 5-7)**:
9. Train intent classifier on Banking77
10. Build FAISS index from MS MARCO
11. Integrate complaint examples
12. Setup evaluation pipeline

**Nice-to-have (Days 8+)**:
13. Switch to MongoDB
14. Add token refresh
15. Add error/logging
16. Deploy to production

---

## Key Gaps Summary

| Layer | Issue | Impact | Fix Effort |
|---|---|---|---|
| **Frontend** | No register page | Can't create accounts | 30 min |
| **Frontend** | No chat page | Can't send messages | 2-3 hours |
| **Frontend** | Axios header lost on reload | Logout happens on F5 | 5 min |
| **Frontend** | No protected routes | Unauthenticated access to /chat | 30 min |
| **Backend** | Agents not instantiated | Dummy responses only | 2-3 hours |
| **Backend** | RAG not initialized | No retrieval | 3-4 hours |
| **Backend** | LLM not initialized | No LLM calls | 1 hour |
| **Backend** | Intent detection regex only | Poor intent accuracy | 4-6 hours (training) |
| **Backend** | InMemory storage only | Data lost on restart | 4-5 hours |
| **Backend** | No token refresh | Sessions expire mid-chat | 2 hours |
| **Tests** | Pytest not installed | Can't run tests | 15 min |
| **Datasets** | Not integrated | No training data used | 6-10 hours |

---

## File Checklist

### Files that need creation:
- [ ] `frontend/pages/register.js`
- [ ] `frontend/pages/chat.js`
- [ ] `frontend/components/ChatMessage.jsx` (optional)
- [ ] `frontend/components/MessageInput.jsx` (optional)

### Files that need changes:
- [ ] `frontend/pages/_app.js` (add api.setAuthToken in useEffect)
- [ ] `backend/requirements.txt` (add pytest)
- [ ] `backend/app/services/chat_service.py` (instantiate agents, initialize RAG)
- [ ] `backend/app/services/auth_service.py` (add refresh token support)
- [ ] `backend/app/conversations/store.py` (complete MongoConversationStore)

### Files that are complete:
- ✅ `backend/app/api/auth.py`
- ✅ `backend/app/api/chat.py`
- ✅ `backend/app/api/conversations.py`
- ✅ `backend/app/agents/*.py`
- ✅ `backend/app/router/router.py`
- ✅ `backend/app/orchestrator/aggregator.py`
- ✅ `frontend/lib/api.js`
- ✅ `frontend/pages/_app.js` (except one line)
- ✅ `frontend/pages/login.js`

---

## Conclusion

**The system has a solid foundation but is incomplete.**

- ✅ **Authentication**: Functional (register, login, logout, token verification)
- ✅ **API Layer**: Well-defined contracts with FastAPI
- ✅ **Data Storage**: In-memory stores for users and conversations
- ✅ **Agent Architecture**: All 5 agents defined with proper base class
- ✅ **Response Aggregation**: Deduplication and conflict resolution implemented
- ❌ **Agent Execution**: Not wired in ChatService
- ❌ **RAG Pipeline**: Not initialized or used
- ❌ **LLM Integration**: Only dummy provider active
- ❌ **Frontend UI**: Chat and register pages missing
- ❌ **Dataset Integration**: No datasets used
- ⚠️ **Tests**: Can't run without pytest

**Next immediate step**: Create register and chat pages on frontend, then wire agent instantiation and RAG retrieval on backend. This will establish a working end-to-end flow before optimization.

