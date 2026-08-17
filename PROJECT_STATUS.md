# PROJECT_STATUS.md

**Last Updated**: 2026-08-17  
**Project**: Customer Support AI  
**Current Version**: 0.1.0  
**Build Status**: ✅ Frontend builds successfully | ✅ Backend tests pass (76/76)

---

## Executive Summary

### Overall Status
**~65% feature complete** for a development prototype. Core authentication, chat UI, and intent routing are functional. Agent execution, RAG integration, and real LLM connection are **not yet integrated into the production flow**. Conversations persist in memory only (lost on restart).

### Working
- ✅ User registration with password hashing (Argon2id)
- ✅ User login with token-based auth
- ✅ Protected routes (frontend and backend)
- ✅ Chat interface with message history
- ✅ Conversation listing and resumption
- ✅ Intent detection (rule-based keyword matching)
- ✅ Agent routing configuration
- ✅ Conversation ownership verification
- ✅ Response aggregation framework
- ✅ Rate limiting (5 reg/15min, 10 login/15min)
- ✅ CORS configuration
- ✅ Comprehensive security testing

### Partially Working
- 🟡 Agent system (classes exist, never instantiated or called in production flow)
- 🟡 RAG pipeline (framework exists, not connected to chat flow)
- 🟡 LLM service (DummyProvider used, OpenAI provider available but not connected)
- 🟡 Query session_id handling in chat page (implementation added, not fully verified in runtime)

### Missing / Not Implemented
- ❌ Real agent execution (agents never instantiated)
- ❌ RAG integration into chat pipeline
- ❌ Real LLM responses (dummy responses used)
- ❌ Persistent database (in-memory only, data lost on restart)
- ❌ MongoDB connection (template exists, not implemented)
- ❌ Password reset
- ❌ Logout endpoint
- ❌ Multi-factor authentication
- ❌ Session management/revocation
- ❌ Frontend testing
- ❌ API documentation (Swagger/OpenAPI)
- ❌ Deployment configuration

### Security Concerns
- ⚠️ **No HTTPS enforcement** (required for production)
- ⚠️ **In-memory token storage** (lost on restart, not shared across instances)
- ⚠️ **In-memory conversation storage** (users lose all chats on server restart)
- ⚠️ **No database encryption** (N/A for in-memory, required for production DB)
- ⚠️ **Hardcoded default environment values** (dev defaults acceptable, but production requires secrets vault)

### Biggest Technical Debt
1. **Dummy agent execution**: `execute_agents()` returns mock responses instead of calling real agents
2. **Unintegrated RAG**: RAG pipeline exists but is never called in chat flow
3. **Missing LLM connection**: LLMService has DummyProvider as default, OpenAI available but not wired
4. **In-memory persistence**: All data lost on restart; no database implementation
5. **Pydantic v1 compatibility**: Codebase uses Pydantic <2.0.0 (deprecated warning in tests)

### Immediate Next Task
**CRITICAL**: Implement real agent execution in `execute_agents()` method of [backend/app/services/chat_service.py](backend/app/services/chat_service.py). Agents are defined but never instantiated or called. This is the blocker for intelligent responses.

---

## Project Overview

### Project Name
**Customer Support AI**

### Purpose
Multi-agent customer support chatbot that routes customer inquiries to specialized agents (FAQ, Billing, Technical Support, Complaints, Product Info) using intent detection, retrieves context via RAG, and generates responses using an LLM.

### Problem Being Solved
Manual customer support requires extensive training and high-touch labor. This system aims to automate routine inquiries through specialized AI agents while escalating complex issues.

### Target Users
- **Primary**: End users (customers of AstraHome)
- **Secondary**: Support team (through escalation)

### Current Development Stage
**Alpha Prototype** - Core infrastructure complete, production features incomplete.

### Technology Stack

#### Frontend
- **Framework**: Next.js 16.3.1
- **Styling**: Tailwind CSS 4.3.3
- **HTTP Client**: Axios 1.19.0
- **Runtime**: Node.js (version not specified in package.json)

#### Backend
- **Framework**: FastAPI 0.95.2
- **Server**: Uvicorn 0.22.0
- **Auth**: python-jose 3.3.0
- **Password Hashing**: argon2-cffi 21.1.0
- **Validation**: Pydantic <2.0.0
- **Database**: MongoDB (template only; in-memory used currently)
- **ORM**: Motor 3.7.0 (async MongoDB driver, not implemented)
- **AI/ML**:
  - LangChain 0.0.200
  - OpenAI 1.0.0 (not connected)
  - Sentence Transformers 2.2.2 (embeddings)
  - FAISS 1.7.4 (vector DB)
  - PyPDF 3.10.0 (document parsing)
- **Testing**: pytest 7.4.3

#### Infrastructure
- **Backend Deployment**: (not configured, local development only)
- **Frontend Deployment**: (not configured, local development only)
- **Database**: (in-memory only, MongoDB template exists)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│                      BROWSER (User)                             │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS (TLS in production)
                           ▼
          ┌─────────────────────────────────────┐
          │  Next.js Frontend (pages/)          │
          │  ├─ /login                          │
          │  ├─ /register                       │
          │  ├─ /chat (with query params)       │
          │  ├─ /conversations                  │
          │  └─ / (index/home)                  │
          └─────────────────────────────────────┘
                           │
                           │ Axios API Client
                           │ (lib/api.js)
                           ▼
          ┌─────────────────────────────────────┐
          │   FastAPI Backend (main.py)         │
          │   ├─ CORS Middleware                │
          │   ├─ Rate Limit Middleware          │
          │   └─ Routes                         │
          └─────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
    │ Auth Routes │  │ Chat Routes │  │ Conversation │
    │ /auth/*     │  │ /chat       │  │ /conversations│
    └─────────────┘  └─────────────┘  └──────────────┘
          │                │                │
          ▼                ▼                ▼
    ┌─────────────────────────────────────────────────┐
    │            Authentication Layer                  │
    │  ├─ get_current_user() - Token validation       │
    │  ├─ User Store - password hashing (Argon2id)    │
    │  └─ Token Service - generation & expiration     │
    └─────────────────────────────────────────────────┘
          │
          ▼
    ┌─────────────────────────────────────────────────┐
    │          Chat Service (chat_service.py)         │
    │  ├─ Conversation Loading/Creation               │
    │  ├─ Message Storage                             │
    │  ├─ Intent Detection ──────────────────┐        │
    │  ├─ Agent Routing                      │        │
    │  ├─ Agent Execution [DUMMY] ◄──────────┘        │
    │  ├─ RAG Retrieval [NOT CALLED]                  │
    │  └─ Response Aggregation                        │
    └─────────────────────────────────────────────────┘
          │
          ├─────────────┬──────────────┬──────────────┐
          │             │              │              │
          ▼             ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Intent   │  │ Router   │  │ Agents   │  │ LLM      │
    │ Detector │  │ (Rule    │  │ [NOT     │  │ Service  │
    │ [RULE]   │  │ Based)   │  │ USED]    │  │ [DUMMY]  │
    └──────────┘  └──────────┘  └──────────┘  └──────────┘
          │
          └───────────────────┐
                              ▼
                    ┌──────────────────┐
                    │  RAG Pipeline    │
                    │  [NOT CONNECTED] │
                    │  ├─ Doc Loader   │
                    │  ├─ Embeddings   │
                    │  ├─ FAISS Index  │
                    │  └─ Search       │
                    └──────────────────┘
                    
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE                                       │
│  ├─ User Store (in-memory) - users, hashed passwords            │
│  ├─ Conversation Store (in-memory) - all conversations & msgs   │
│  ├─ Token Store (in-memory) - active tokens & expiration        │
│  └─ MongoDB (template only, not used)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Frontend Status

### Pages

#### `/` (index.js)
- **Status**: ✅ COMPLETE
- **Purpose**: Home page / redirect
- **Implementation**: Redirects to /chat if authenticated, else /login
- **Files**: `frontend/pages/index.js`

#### `/login` (login.js)
- **Status**: ✅ COMPLETE
- **Purpose**: User authentication
- **Implementation**: 
  - Form-based login with username/password
  - Calls `api.login()` 
  - Sets auth token via `api.setAuthToken()`
  - Redirects to /chat on success
  - Shows error banner on failure
- **Files**: `frontend/pages/login.js`, `frontend/components/AuthForm.jsx`
- **API**: `POST /auth/login`
- **Auth**: None (public page)
- **Error Handling**: Generic error message from server

#### `/register` (register.js)
- **Status**: ✅ COMPLETE
- **Purpose**: New user registration
- **Implementation**:
  - Form-based registration (username/password)
  - Calls `api.register()`
  - Redirects to /login with success notification
  - Shows validation errors
- **Files**: `frontend/pages/register.js`, `frontend/components/AuthForm.jsx`
- **API**: `POST /auth/register`
- **Auth**: None (public page)
- **Validation**: Frontend only (basic, server validates)

#### `/chat` (chat.js)
- **Status**: ✅ COMPLETE (query param handling added)
- **Purpose**: Main chat interface
- **Implementation**:
  - Protected route (withAuth HOC)
  - Displays conversation history
  - Sends messages and displays responses
  - Can continue existing conversations via `session_id` query param
  - Loads conversations in sidebar
  - Creates new conversations
- **Files**: `frontend/pages/chat.js`, `frontend/components/ChatWindow.jsx`, `frontend/components/ChatInput.jsx`
- **API Calls**:
  - `api.getConversationsForUser()` - load sidebar
  - `api.getHistory(session_id)` - load conversation history
  - `api.sendChat()` - send message and get response
- **Auth**: Required (Bearer token in Authorization header)
- **Query Params**: `session_id` - loads specific conversation
- **Features**:
  - ✅ Message history loaded on mount (if session_id provided)
  - ✅ New conversations created if no session_id
  - ✅ Messages displayed with timestamps
  - ✅ Loading states while sending
  - ✅ Error banner for failures
  - ✅ Conversation sidebar
  - ✅ New chat button

#### `/conversations` (conversations.js)
- **Status**: ✅ COMPLETE
- **Purpose**: Browse and manage all user conversations
- **Implementation**:
  - Protected route (withAuth HOC)
  - Fetches all conversations for current user
  - Displays in grid/list format
  - Shows conversation preview (first user message)
  - Shows date (Today/Yesterday/Mon/Jan 15 format)
  - Click to open conversation
  - New conversation button
- **Files**: `frontend/pages/conversations.js`
- **API Calls**: 
  - `api.getConversationsForUser(user.id)` - load all conversations
- **Auth**: Required
- **Features**:
  - ✅ Loading spinner
  - ✅ Empty state with CTA
  - ✅ Error handling (403/404/network)
  - ✅ Responsive design
  - ✅ Navigation to /chat?session_id=X
  - ✅ Smart date formatting
  - ✅ Message count displayed

### Components

#### AuthForm.jsx
- **Purpose**: Reusable login/register form
- **Props**: `mode` (login|register), `onSubmit`, `error`
- **Fields**: username, password (and confirm password for register)
- **Validation**: Frontend only
- **Status**: ✅ COMPLETE

#### ChatWindow.jsx
- **Purpose**: Display conversation history
- **Props**: `messages`, `loading`
- **Features**: Message bubbles, sender labels, timestamps
- **Status**: ✅ COMPLETE

#### ChatInput.jsx
- **Purpose**: Message input form
- **Props**: `onSend`, `disabled`, `placeholder`
- **Features**: Text input, send button, auto-focus
- **Status**: ✅ COMPLETE

#### MessageBubble.jsx
- **Purpose**: Individual message display
- **Props**: `message`, `isSent`
- **Features**: Styling based on sender (user vs assistant)
- **Status**: ✅ COMPLETE

#### ConversationSidebar.jsx
- **Purpose**: Sidebar showing conversation list
- **Props**: `conversations`, `onSelectConversation`, `onNewChat`
- **Features**: Grouped by date, click handlers
- **Status**: ✅ COMPLETE

#### ConversationList.jsx
- **Purpose**: Reusable conversation list component
- **Props**: `conversations`, `onSelectConversation`
- **Features**: Groups by date, shows titles/times
- **Status**: ✅ COMPLETE

#### ErrorBanner.jsx
- **Purpose**: Display errors
- **Props**: `message`, `onDismiss`
- **Status**: ✅ COMPLETE

#### LoadingIndicator.jsx
- **Purpose**: Show loading spinner
- **Props**: `message`
- **Status**: ✅ COMPLETE

#### Header.jsx
- **Purpose**: Top navigation bar
- **Props**: `user`, `onLogout`, `onOpenSidebar`
- **Features**: User info, logout button, menu toggle
- **Status**: ✅ COMPLETE

### Frontend API Service Layer

**File**: `frontend/lib/api.js`

**Methods**:
- `register(username, password)` → `POST /auth/register`
- `login(username, password)` → `POST /auth/login`
- `setAuthToken(token)` → Sets Authorization header
- `createConversation(session_id)` → `POST /conversations`
- `sendChat(message, session_id)` → `POST /chat`
- `getConversationsForUser(user_id)` → `GET /conversations/user/{user_id}`
- `getHistory(session_id, max_messages=20)` → `GET /conversations/{session_id}/history`

**Auth Handling**:
- Axios interceptor: 401 errors clear token and redirect to /login
- Token stored in localStorage (key: `auth_token`)
- Bearer token sent in `Authorization: Bearer <token>` header

### Frontend Authentication Context

**File**: `frontend/pages/_app.js`

**AuthContext**:
- `user` - current user object {id, username}
- `token` - auth token
- `isInitialized` - whether auth state loaded
- `login(token, userInfo)` - set auth state
- `logout()` - clear auth state and redirect to /login

**withAuth HOC**: 
- Wraps protected pages
- Redirects to /login if not authenticated
- Prevents render flicker by checking isInitialized

**Storage**:
- Token: localStorage (`auth_token`)
- User info: AuthContext (in-memory)

### Frontend Build Status
✅ **SUCCESS** - Compiles without errors
```
Next.js 16.3.1
Routes: /, /404, /chat, /conversations, /login, /register
Build time: ~0.7s
```

---

## Authentication & Security

### Password Handling

**Storage**: ✅ SECURE
- Passwords hashed with Argon2id
- Plaintext never stored
- File: `backend/app/users/store.py::InMemoryUserStore._hash_password()`

**Verification**: ✅ SECURE
- Constant-time comparison via argon2 library
- File: `backend/app/users/store.py::InMemoryUserStore.verify_password()`

**Hashing Algorithm**: ✅ ARGON2ID
- Library: `argon2-cffi>=21.1.0`
- Algorithm: Argon2id (GPU/ASIC resistant)
- Hash Format: `$argon2id$v=19$m=102400,t=2,p=8$...(salt)...(hash)`
- Parameters: Memory=102400, Time=2, Parallelism=8

**Password Policy**:
- Minimum 8 characters
- Must contain at least one letter and one number
- Maximum 256 characters
- Enforced in `backend/app/api/auth.py::RegisterReq`

### Token Generation & Validation

**Generation**: ✅ SECURE
- Algorithm: `secrets.token_urlsafe(32)` (cryptographically secure random)
- File: `backend/app/services/auth_service.py::AuthService.login()`
- Storage: In-memory map `{token: (user_id, expires_at)}`

**Expiration**: ✅ IMPLEMENTED
- Default: 24 hours (configurable via `TOKEN_EXP_HOURS` env var)
- Checked on every protected request
- Expired tokens auto-deleted from store
- File: `backend/app/services/auth_service.py::AuthService.verify_token()`

**Validation**: ✅ IMPLEMENTED
- Extracted from `Authorization: Bearer <token>` header
- Checked on every protected endpoint
- File: `backend/app/api/chat.py::get_current_user()`

**Transmission**: ✅ DESIGNED FOR HTTPS
- Sent via Bearer token in Authorization header
- Frontend stores in localStorage (vulnerable to XSS but acceptable for dev)
- Requires HTTPS in production

### Authorization

**Conversation Ownership**: ✅ VERIFIED
- Every endpoint checks `conv.user_id == current_user.id`
- Test: `test_user_cannot_continue_other_user_conversation()` - PASS
- Files:
  - `backend/app/api/chat.py` - ownership check before chat
  - `backend/app/api/conversations.py` - ownership check on all endpoints

**Error Responses**: ✅ GENERIC
- Login: "Invalid username or password" (doesn't reveal which)
- Authorization: "Access denied" (no details)
- Token: "Invalid or expired token"
- Prevents user enumeration

### CORS Configuration

**Development**: `http://localhost:3000` (default)
**Production**: Set via `CORS_ALLOW_ORIGIN` env var
**Security**: Never uses wildcard with credentials
- File: `backend/app/main.py`

### Rate Limiting

**Endpoints**:
- `/auth/register`: 5 requests per 15 minutes per IP
- `/auth/login`: 10 requests per 15 minutes per IP

**Implementation**: In-memory per-instance middleware
**Status**: ✅ Implemented but not distributed (issue for multi-instance)
**File**: `backend/app/middleware/rate_limit.py`

### Environment Variables

| Variable | Default | Type | Purpose |
|----------|---------|------|---------|
| `TOKEN_EXP_HOURS` | 24 | int | Token expiration time |
| `CORS_ALLOW_ORIGIN` | http://localhost:3000 | string | CORS allowed origin |
| `OPENAI_API_KEY` | (none) | string | OpenAI API key (optional) |
| `LOG_LEVEL` | INFO | string | Logging level |
| `DISABLE_RATE_LIMIT` | false | bool | Disable rate limiting (testing) |
| `RATE_LIMIT_REGISTER` | 5 | int | Registration attempts limit |
| `RATE_LIMIT_LOGIN` | 10 | int | Login attempts limit |

**Security**: ✅ No hardcoded secrets in code

### Security Tests

**File**: `backend/tests/test_security.py`

**Tests**: 29 total
- ✅ Password hashing (not plaintext) - 4 tests
- ✅ Password verification (correct/incorrect) - 3 tests
- ✅ Authorization (cross-user access denied) - 3 tests
- ✅ Input validation (format, length, complexity) - 5 tests
- ✅ Duplicate registration handling - 2 tests
- ✅ Error message safety - 2 tests
- ✅ Rate limiting - 2 tests
- ✅ Passwords not in responses - 2 tests
- ✅ Token validation (expiration, invalid, malformed) - 6 tests

**Result**: ✅ 29/29 PASS

### Known Security Issues

**Critical** (for production):
- ⚠️ No HTTPS/TLS enforcement (currently HTTP only)
- ⚠️ In-memory token storage (lost on restart, not distributed)
- ⚠️ In-memory conversation storage (data loss on restart)
- ⚠️ No secrets vault (environment variables used)

**Medium** (low risk for dev):
- ⚠️ Rate limiting not distributed (per-instance only)
- ⚠️ localStorage used for token (vulnerable to XSS)

---

## Backend Status

### FastAPI Application

**File**: `backend/app/main.py`

**Middleware**:
- ✅ CORS (configurable origin)
- ✅ Rate limiting (in-memory)

**Routes**:
- ✅ `GET /health` - health check
- ✅ Auth routes (`/auth/register`, `/auth/login`)
- ✅ Chat route (`/post /chat`)
- ✅ Conversation routes (`/conversations/*`)

### Authentication Service

**File**: `backend/app/services/auth_service.py`

**Purpose**: Token generation, validation, and user authentication

**Methods**:
- `register(username, password)` - creates user via user store
- `login(username, password)` - validates password, generates token
- `verify_token(token)` - returns user_id or None
- `revoke_token(token)` - removes token (not exposed in API)

**Status**: ✅ COMPLETE

### User Store

**File**: `backend/app/users/store.py`

**Current Implementation**: `InMemoryUserStore`

**Features**:
- ✅ User creation with password hashing (Argon2id)
- ✅ Password verification (constant-time)
- ✅ User lookup by username and ID
- ✅ Detects duplicate usernames

**Persistence**: ❌ NOT PERSISTENT (in-memory only)

**Available**: `MongoConversationStore` template (not implemented)

**Status**: ✅ Functional but not persistent

### Chat Service

**File**: `backend/app/services/chat_service.py`

**Purpose**: Handle chat messages, detect intent, route to agents, aggregate responses

**Flow**:
1. Load or create conversation
2. Store user message
3. Detect intent (IntentDetector)
4. Route to agents (AgentRouter)
5. Execute agents (❌ DUMMY - returns mock responses)
6. Retrieve RAG context (🟡 NOT CALLED in production)
7. Aggregate responses (aggregator)
8. Store assistant response

**Issue**: `execute_agents()` is a dummy stub that returns `[{sender: "assistant", text: "[{agent}] response to: {message}"}]`

**Real agents** are defined but:
- Never instantiated
- Never called
- Receive no LLM output
- Receive no RAG context

**Status**: 🟡 PARTIALLY IMPLEMENTED (framework complete, execution missing)

### Conversation Service/Store

**File**: `backend/app/conversations/store.py` & `models.py`

**Current Implementation**: `InMemoryConversationStore`

**Features**:
- ✅ Create conversation
- ✅ Add message
- ✅ Get conversation
- ✅ List conversations for user
- ✅ Get trimmed history (last N messages)

**Persistence**: ❌ NOT PERSISTENT (data lost on restart)

**Data Model**:
```python
Conversation:
  - session_id: UUID
  - user_id: str (optional)
  - created_at: datetime
  - updated_at: datetime
  - messages: List[Message]
  - metadata: dict

Message:
  - id: UUID
  - sender: str ("user" or "assistant")
  - text: str
  - timestamp: datetime
  - metadata: dict (optional)
```

**Status**: ✅ Functional for session but not persistent

### API Endpoints

#### Authentication Endpoints

| Method | Endpoint | Auth | Status | Purpose |
|--------|----------|------|--------|---------|
| POST | `/auth/register` | None | ✅ | Create new user |
| POST | `/auth/login` | None | ✅ | Authenticate and get token |

**Missing**:
- POST `/auth/logout` - token revocation
- POST `/auth/refresh` - token refresh
- POST `/auth/password-reset` - password recovery

#### Chat Endpoint

| Method | Endpoint | Auth | Status | Purpose |
|--------|----------|------|--------|---------|
| POST | `/chat` | Bearer | ✅ | Send message and get response |

**Request**:
```json
{
  "message": "user query",
  "session_id": "optional-uuid"  // Continue existing conversation
}
```

**Response**:
```json
{
  "session_id": "uuid",
  "answer": "mock response: [agent_name] response to: ...",
  "escalate": false,
  "sources": []
}
```

**Note**: `answer` currently contains dummy responses like `[faq] response to: ...`

#### Conversation Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/conversations/user/{user_id}` | Bearer | List all conversations for user |
| GET | `/conversations/{session_id}` | Bearer | Get specific conversation |
| GET | `/conversations/{session_id}/history` | Bearer | Get conversation history |
| POST | `/conversations` | Bearer | Create new conversation |

**Features**:
- ✅ Ownership verification on all endpoints
- ✅ Returns 403 if user doesn't own resource
- ✅ Filters conversations by user

---

## Multi-Agent System Status

### Agent Classes

| Agent | File | Exists | Instantiated | Called | LLM | RAG | Tested | Status |
|-------|------|--------|--------------|--------|-----|-----|--------|--------|
| AgentBase | `agents/base.py` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Base class only |
| FAQ Agent | `agents/faq_agent.py` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Subclass only |
| Billing Agent | `agents/billing_agent.py` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Subclass only |
| Technical Agent | `agents/technical_agent.py` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Subclass only |
| Complaint Agent | `agents/complaint_agent.py` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Subclass only |
| Product Agent | `agents/product_agent.py` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Subclass only |

**Status**: ❌ **NOT IMPLEMENTED IN PRODUCTION**

**Evidence**: 
- `chat_service.py::execute_agents()` never instantiates any agent classes
- Returns hardcoded Message objects: `f"[{a}] response to: {user_text}"`
- Agents appear only in routing decision, never in execution

**What needs to be done**:
```python
# Current (dummy):
def execute_agents(self, agents: List[str], user_text: str, rag_context=None):
    outputs = []
    for a in agents:
        outputs.append(
            conv_models.Message(sender="assistant", text=f"[{a}] response to: {user_text}")
        )
    return outputs

# Needs to be (real):
def execute_agents(self, agents: List[str], user_text: str, rag_context=None):
    outputs = []
    for agent_name in agents:
        agent_class = {
            "faq": FAQAgent,
            "billing": BillingAgent,
            "technical_support": TechnicalAgent,
            "complaint": ComplaintAgent,
            "product": ProductAgent,
        }.get(agent_name)
        if agent_class:
            agent = agent_class(rag=self.rag, llm_service=self.llm)
            output = agent.handle(AgentInput(...))
            outputs.append(output)
    return outputs
```

---

## Intent Detection

**File**: `backend/app/intent/detector.py`

**Type**: Rule-based keyword matching (not ML-based)

**Implementation**:
- Regex keywords per intent category
- Confidence = min(1.0, keyword_matches / 2.0)
  - 1 match = 0.5 confidence
  - 2+ matches = 1.0 confidence
- Multiple intents supported

**Intent Categories**:
| Intent | Example Keywords | Mapped Agent |
|--------|------------------|--------------|
| billing | bill, charge, payment, invoice, subscription | billing |
| refund | refund, return, money back, reimburse | billing |
| product | price, feature, spec, discount | product |
| technical_support | login, password, error, bug, install | technical_support |
| complaint | angry, complain, escalate, bad service | complaint |
| general_faq | warranty, shipping, how to, contact | faq |

**Confidence Thresholds**:
- Minimum confidence: 0.4 (configurable)
- Low confidence queries default to FAQ

**Multi-intent Support**: ✅
- If top 2 intents both >= 0.4 confidence, routes to both agents
- Maximum 3 agents per query (hardcoded limit)

**Tests**: ✅ 12 tests in `test_routing.py`

**Status**: ✅ COMPLETE

---

## Routing

**File**: `backend/app/router/router.py`

**Type**: Rule-based intent → agent mapping

**Mapping**:
```python
INTENT_TO_AGENT = {
    "billing": ["billing"],
    "refund": ["billing"],
    "product": ["product"],
    "technical_support": ["technical_support"],
    "complaint": ["complaint"],
    "general_faq": ["faq"],
}
```

**Logic**:
1. Detect intent
2. Map to agents (supports multiple)
3. Enforce max_agents limit (default 3)
4. Handle unknown intents (default to FAQ)
5. Flag for escalation if confidence very low (<0.1)

**Tests**: ✅ 12 tests

**Status**: ✅ COMPLETE

**Note**: Routing works correctly, but agents are never executed.

---

## RAG Status

**File**: `backend/app/rag/pipeline.py`

**Components**:
- ✅ Document loader (`doc_loader.py`) - Supports PDF, TXT, MD
- ✅ Text processing (`text_processing.py`) - Cleaning, chunking
- ✅ Embeddings (`embeddings.py`) - Sentence Transformers (all-MiniLM-L6-v2)
- ✅ FAISS index (`faiss_index.py`) - Vector database
- ✅ Pipeline (`pipeline.py`) - Orchestration

**Initialization**:
```python
RAGPipeline(
    source_folder="path/to/docs",
    index_path="path/to/index",
    embedding_model_name="all-MiniLM-L6-v2",
    chunk_size=1000,
    chunk_overlap=200,
)
```

**Methods**:
- `build_index(rebuild=False)` - Create or load index
- `semantic_search(query, top_k=5)` - Retrieve relevant chunks

**Called From**:
- `chat_service.py::chat()` tries to call RAG but wrapped in try/except
- If RAG fails or unavailable, chat continues without context
- Status: ❌ **NOT INTEGRATED** (call exists but silently fails)

**Index Status**: ❌ **NOT BUILT**
- No index files found in repo
- No code that calls `build_index()`
- Would require documents to be provided

**Dataset Integration**: ❌ **NOT USED**
- Datasets exist in `datasets/` folder
- No code loads datasets into RAG pipeline
- No documents loaded for indexing

**Status**: 🟡 FRAMEWORK EXISTS, NOT INTEGRATED

**What needs to be done**:
1. Load dataset documents into RAG pipeline
2. Build index from documents
3. Connect to chat flow properly (error handling instead of try/except)
4. Pass retrieved context to agents

---

## Dataset Status

**Location**: `datasets/` directory

| Dataset | Type | Present | Used by App | Status |
|---------|------|---------|-------------|--------|
| **BANKING77** | Intent classification | ✅ | ❌ | CSV files only |
| **MS MARCO** | Retrieval ranking | ✅ | ❌ | TSV files only |
| **SQuAD** | QA pairs | ✅ | ❌ | JSON files only |
| **Complaints** | Customer complaints | ✅ | ❌ | CSV only |
| **Dialogues** | Multi-lingual | ✅ | ❌ | TXT files only |
| **Customer Support** | Custom domain | ✅ | ❌ | Not inspected |
| **QA Datasets** | Question-answer | ✅ | ❌ | Not inspected |

### Dataset Organization

```
datasets/
├── ORGANIZATION_REPORT.md        # Dataset inventory
├── README.md                      # Overview
├── banking77/
│   ├── train.csv                  # 10660 samples
│   └── test.csv                   # 3080 samples
├── data/
│   ├── en_train_human.txt        # English dialogues
│   ├── en_dev_human.txt
│   ├── en_test_human.txt
│   ├── de_train_human.txt        # German dialogues
│   ├── it_train_human.txt        # Italian dialogues
│   ├── zh_train_human.txt        # Chinese dialogues
│   └── 1k_part_data/
│       ├── dialogues_topic.txt
│       ├── dialogues_action.txt
│       ├── dialogues_emotion.txt
│       ├── dialogues_text_En.txt
│       ├── dialogues_text_De.txt
│       ├── dialogues_text_It.txt
│       └── dialogues_text_Zh.txt
├── collection.tsv                # MS MARCO collection
├── queries.*.tsv                  # MS MARCO queries
├── qrels.*.tsv                    # MS MARCO relevance judgments
├── train-v*.json                  # SQuAD datasets
├── dev-v*.json                    # SQuAD datasets
└── retrieval/ & qa_datasets/      # Other datasets
```

**Size**: ~1GB (mostly datasets, not tracked by git)

**Usage in Application**: ❌ **ZERO**
- No code loads any dataset
- No code references dataset files
- No preprocessing pipeline
- No training pipeline

**Recommendation**: Datasets appear collected for future ML-based intent detection or RAG indexing, but not yet integrated.

---

## Database / Storage

### Current Implementation

**Type**: In-memory (data lost on restart)

**Stores**:
- User store: `backend/app/users/store.py::InMemoryUserStore`
- Conversation store: `backend/app/conversations/store.py::InMemoryConversationStore`
- Token store: `backend/app/services/auth_service.py::AuthService._tokens`

**Persistence**: ❌ ZERO

**Production Limitation**: ⚠️ CRITICAL
- All user data lost when server restarts
- All conversation history lost
- All tokens invalidated
- Users see blank conversation history after restart

### Available but Not Implemented

**MongoDB Templates**:
- `MongoConversationStore` in `backend/app/conversations/store.py`
- All methods raise `NotImplementedError`
- Requires async Motor driver
- No initialization code

**Requirements**:
- `motor>=3.7.0` (async MongoDB driver) - present
- MongoDB server - not configured
- Database connection - not implemented

**Status**: 🟡 TEMPLATE EXISTS, NOT IMPLEMENTED

---

## Test Status

### Test Execution

**Command**: `pytest backend/tests/ --ignore=test_agents.py --ignore=test_rag_pipeline.py -q`

**Result**: ✅ **76/76 PASS**

```
============================== 76 passed in 15.92s ========================
```

### Test Breakdown

| Module | Tests | Status | Notes |
|--------|-------|--------|-------|
| test_api_chat.py | 3 | ✅ | Chat endpoint, auth, 404 handling |
| test_conversations.py | 20 | ✅ | Conversation CRUD, ownership checks |
| test_routing.py | 12 | ✅ | Intent detection, agent routing |
| test_aggregator.py | 12 | ✅ | Response aggregation logic |
| test_security.py | 29 | ✅ | Password hashing, auth, authorization |
| **SUBTOTAL** | **76** | ✅ | **Runnable tests** |
| test_agents.py | 2 | ⚠️ | IGNORED - langchain import error |
| test_rag_pipeline.py | ? | ⚠️ | IGNORED - langchain import error |

### Blocked Tests

**test_agents.py**: Cannot run due to langchain API change
- Error: `from langchain.text_splitter import ...`
- Reason: Langchain reorganized text splitting API
- Impact: Agent execution never tested

**test_rag_pipeline.py**: Cannot run (similar langchain issue)
- Impact: RAG pipeline never tested

### Test Coverage

**Coverage**: Reasonable but incomplete
- ✅ Auth system well tested (29 security tests)
- ✅ Conversation CRUD tested
- ✅ Authorization verified
- ❌ Agent execution not tested (code never runs)
- ❌ RAG not tested (not integrated)
- ❌ LLM not tested (dummy only)
- ❌ Frontend not tested

---

## Build Status

### Frontend Build

**Command**: `npm run build`

**Result**: ✅ **SUCCESS**

```
Next.js 16.3.1
Compiled successfully in 729ms
Routes generated: /, /login, /register, /chat, /conversations
```

**Files Generated**: `.next/` directory (production bundle)

### Backend Tests

**Command**: `pytest backend/tests/...`

**Result**: ✅ **76/76 PASS**

**Warnings**: 
- Pydantic v1 deprecation (15 warnings)
  - Issue: Using `model.dict()` instead of `model.model_dump()`
  - File: `backend/app/orchestrator/aggregator.py:45`
  - Impact: Low (warning only, functionality works)

### Build Prerequisites

**Frontend**:
- Node.js (version not specified, assume 18+)
- npm or yarn

**Backend**:
- Python 3.10+ (verified with 3.10.9)
- Virtual environment: `.venv/`
- pip install -r requirements.txt

---

## Known Issues

### Critical

#### 1. Agents Never Executed ❌ CRITICAL
- **Problem**: `execute_agents()` returns hardcoded responses `[{agent}] response to: ...` instead of calling real agents
- **Evidence**: 
  - File: `backend/app/services/chat_service.py::execute_agents()`
  - Returns `Message(sender="assistant", text=f"[{a}] response to: {user_text}")`
- **Impact**: Users never get intelligent responses, only echoes of agent names
- **Recommended Fix**: Implement real agent instantiation and execution
- **Files**: 
  - `backend/app/services/chat_service.py` - execute_agents()
  - `backend/app/agents/*` - all agent classes

#### 2. RAG Not Integrated ❌ CRITICAL
- **Problem**: RAG pipeline framework exists but is never called in production chat flow
- **Evidence**: 
  - `chat_service.py::chat()` has try/except around RAG call
  - Silently fails if RAG unavailable
  - Retrieved context never passed to agents
- **Impact**: No context-aware responses, agents only use query text
- **Recommended Fix**: Integrate RAG into agent input pipeline
- **Files**: 
  - `backend/app/services/chat_service.py` - chat() method
  - `backend/app/agents/base.py` - agent input includes RAG context

#### 3. No Persistent Database ❌ CRITICAL
- **Problem**: All data stored in-memory, lost on restart
- **Evidence**: 
  - `InMemoryConversationStore` - uses dict, not database
  - `InMemoryUserStore` - users and passwords in memory
  - No database configuration in code
- **Impact**: Users lose all conversations on server restart, users must re-register
- **Recommended Fix**: Implement MongoDB store (template exists, just needs implementation)
- **Files**: 
  - `backend/app/conversations/store.py` - MongoConversationStore
  - `backend/app/users/store.py` - Create MongoUserStore

### High

#### 4. LLM Always Uses Dummy Provider ⚠️ HIGH
- **Problem**: OpenAI provider configured but default is DummyProvider, never switched
- **Evidence**: 
  - `backend/app/llm/service.py::LLMService._get_provider()` - defaults to DummyProvider
  - OpenAI provider available but not used
  - No code instantiates LLMService with provider="openai"
- **Impact**: LLM responses always dummy, no integration with OpenAI
- **Recommended Fix**: 
  1. Set environment variable `OPENAI_API_KEY`
  2. Pass provider="openai" to LLMService initialization
- **Files**: 
  - `backend/app/llm/service.py`
  - `backend/app/agents/base.py` - agent initialization

#### 5. Pydantic v1 Deprecated ⚠️ HIGH
- **Problem**: Using `pydantic<2.0.0`, deprecated `.dict()` method
- **Evidence**: 
  - `requirements.txt`: `pydantic<2.0.0`
  - `aggregator.py:45`: `o.dict()` generates deprecation warning
  - 15 warnings in test output
- **Impact**: Low immediate risk, but will break on Pydantic v2 upgrade
- **Recommended Fix**: 
  1. Upgrade to Pydantic v2
  2. Replace `.dict()` with `.model_dump()`
- **Files**: 
  - `backend/app/orchestrator/aggregator.py:45`
  - `requirements.txt`

#### 6. Langchain API Changed ⚠️ HIGH
- **Problem**: Test files import from old langchain API that no longer exists
- **Evidence**: 
  - `test_agents.py` and `test_rag_pipeline.py` fail to import
  - Error: `from langchain.text_splitter import ...`
  - New API: `from langchain_text_splitters import ...`
- **Impact**: Agent and RAG tests cannot run, code untested
- **Recommended Fix**: 
  1. Update langchain requirement to >=0.1.0
  2. Update imports in test files
- **Files**: 
  - `backend/tests/test_agents.py`
  - `backend/tests/test_rag_pipeline.py`
  - `requirements.txt`

### Medium

#### 7. No HTTPS in Development ⚠️ MEDIUM
- **Problem**: No TLS/HTTPS enforcement
- **Impact**: Passwords sent in plaintext over HTTP (dev only, acceptable)
- **Recommended Fix**: Configure HTTPS in production deployment

#### 8. In-Memory Rate Limiting Not Distributed ⚠️ MEDIUM
- **Problem**: Rate limiting is per-instance, shared across requests to different instances
- **Impact**: Can be bypassed by round-robin to different instances
- **Recommended Fix**: Use Redis-backed rate limiting for production
- **Files**: `backend/app/middleware/rate_limit.py`

#### 9. No Logout Endpoint ⚠️ MEDIUM
- **Problem**: No way to revoke tokens, users cannot logout gracefully
- **Impact**: Tokens stay valid until expiration (24 hours)
- **Recommended Fix**: Implement POST /auth/logout to add token to blacklist
- **Files**: `backend/app/api/auth.py`, `backend/app/services/auth_service.py`

#### 10. No Password Reset ⚠️ MEDIUM
- **Problem**: Users with forgotten passwords cannot recover account
- **Impact**: Must contact admin (manual recovery)
- **Recommended Fix**: Implement secure password reset flow (email link)
- **Files**: `backend/app/api/auth.py`

### Low

#### 11. Dataset Not Integrated ℹ️ LOW
- **Problem**: Datasets collected but not loaded, not used for training or RAG
- **Impact**: No personalization or domain knowledge
- **Recommended Fix**: Load datasets into RAG pipeline when ready
- **Files**: `backend/app/rag/pipeline.py`, dataset loaders

#### 12. No Frontend Tests ℹ️ LOW
- **Problem**: Frontend has no automated tests
- **Impact**: UI changes not verified, regressions possible
- **Recommended Fix**: Add Jest/React Testing Library tests
- **Files**: `frontend/pages/**`, `frontend/components/**`

#### 13. No API Documentation ℹ️ LOW
- **Problem**: No Swagger/OpenAPI documentation
- **Impact**: Developers must read code to understand API
- **Recommended Fix**: Add FastAPI automatic documentation or external OpenAPI spec
- **Files**: `backend/app/main.py`

---

## Completed Work

### Authentication (Fully Implemented)
- ✅ User registration with password hashing (Argon2id)
- ✅ User login with token generation
- ✅ Token validation on protected endpoints
- ✅ Password complexity enforcement
- ✅ Error message safety (no user enumeration)
- ✅ Rate limiting (register & login)

### Frontend (Fully Implemented)
- ✅ Login page
- ✅ Register page
- ✅ Chat page with message history
- ✅ Conversations page (browser & management)
- ✅ Protected route guards (withAuth HOC)
- ✅ Authentication context
- ✅ Axios API client with auth interceptors
- ✅ Error handling and display
- ✅ Loading states
- ✅ Responsive design
- ✅ Query parameter handling for session_id

### Backend Services (Partially Implemented)
- ✅ Conversation CRUD (in-memory)
- ✅ Message storage
- ✅ Conversation ownership verification
- ✅ User authentication
- 🟡 Agent system (defined, not executed)
- 🟡 Intent detection (working, tested)
- 🟡 Routing (working, tested)

### Security (Fully Tested)
- ✅ Password hashing (Argon2id)
- ✅ Password verification (constant-time)
- ✅ Authorization checks (ownership)
- ✅ Security test suite (29 tests)
- ✅ CORS configuration
- ✅ Rate limiting

### DevOps
- ✅ Frontend build pipeline (Next.js)
- ✅ Backend test pipeline (pytest)
- ✅ Development environment (.venv)
- ❌ Deployment configuration
- ❌ Docker configuration
- ❌ CI/CD pipeline

---

## Current Development State

### End-to-End Flow (What Actually Works)

```
1. USER REGISTRATION
   ✅ User goes to /register
   ✅ Enters username & password
   ✅ Frontend validates format
   ✅ POST /auth/register sent to backend
   ✅ Backend hashes password with Argon2id
   ✅ User created in in-memory store
   ✅ Redirect to /login
   
2. USER LOGIN
   ✅ User goes to /login
   ✅ Enters credentials
   ✅ POST /auth/login sent to backend
   ✅ Password verified against hash
   ✅ Token generated (32-byte random)
   ✅ Token stored in in-memory token store
   ✅ Frontend stores token in localStorage
   ✅ Redirect to /chat
   
3. PROTECTED ROUTE ACCESS
   ✅ User at /chat (protected page)
   ✅ withAuth HOC checks token exists
   ✅ Page renders ChatWindow + ChatInput
   ✅ Loads conversation sidebar
   ✅ Loads history if session_id in URL
   
4. SENDING A MESSAGE
   ✅ User types message in ChatInput
   ✅ Click Send button
   ✅ POST /chat {message, session_id} sent
   ✅ Backend validates token (Bearer header)
   ✅ Creates or loads conversation
   ✅ Stores user message
   
5. INTENT DETECTION ✅
   ✅ Backend calls IntentDetector.detect(message)
   ✅ Matches keywords (rule-based)
   ✅ Returns intent with confidence
   
6. AGENT ROUTING ✅
   ✅ Backend calls AgentRouter.route(message)
   ✅ Maps intent → agent name
   ✅ Returns agent list (e.g., ["faq"])
   
7. AGENT EXECUTION ❌ DUMMY
   ❌ Backend calls execute_agents(agents, message)
   ❌ SHOULD: Instantiate agent, call handle()
   ❌ ACTUALLY: Returns "[faq] response to: {message}"
   
8. RAG CONTEXT RETRIEVAL ❌ NOT CALLED
   ❌ SHOULD: Retrieve relevant documents
   ❌ ACTUALLY: Wrapped in try/except, silently fails
   
9. LLM GENERATION ❌ DUMMY
   ❌ SHOULD: Call OpenAI API
   ❌ ACTUALLY: DummyProvider returns empty response
   
10. RESPONSE AGGREGATION ✅
    ✅ Aggregates agent outputs
    ✅ Combines answers from multiple agents
    ✅ Detects escalation needs
    
11. RESPONSE STORAGE & RETURN ✅
    ✅ Stores assistant message in conversation
    ✅ Returns ChatResponse {session_id, answer, escalate, sources}
    ✅ Frontend displays answer in ChatWindow
    
12. CONVERSATION BROWSER ✅
    ✅ User can go to /conversations
    ✅ Loads all their conversations
    ✅ Shows preview, date, message count
    ✅ Click to resume in /chat
    
13. PERSISTENCE ❌ NONE
    ❌ On server restart:
       ❌ All users deleted
       ❌ All conversations deleted
       ❌ All tokens invalidated
       ❌ Users must re-register
```

### Summary

**What Works**:
- Full authentication flow (register → login → token)
- Chat UI with message display
- Conversation management
- Intent detection & routing configuration
- Basic security (password hashing, auth checks)

**What's Missing**:
- Real agent execution
- RAG integration
- LLM connection
- Database persistence
- Production deployment features

**User Experience**:
> Users can register, login, send messages to a chatbot, and see responses. But all responses are dummy echoes of agent names, and conversations disappear when the server restarts.

---

## Next Task Ranking

### Ranked by Priority

1. **[CRITICAL] Implement Real Agent Execution** (Priority: 1)
   - **Why**: Core system blocker - agents never run
   - **What**: Replace `execute_agents()` dummy with real instantiation
   - **Effort**: 4-6 hours
   - **Files**: 
     - `backend/app/services/chat_service.py`
     - `backend/app/agents/*` (all agent classes)
     - `backend/app/llm/service.py` (for LLM integration)
   - **Verify**: 
     - Chat response no longer contains "[agent_name]" prefix
     - Actual LLM output returned (even from DummyProvider)
     - Test: `test_api_chat.py::test_register_login_and_chat_success` should not contain `[faq]` in response

2. **[CRITICAL] Implement Persistent Database** (Priority: 2)
   - **Why**: Data loss on restart is unacceptable
   - **What**: Implement MongoDB store or use SQLite
   - **Effort**: 8-10 hours
   - **Files**:
     - `backend/app/conversations/store.py` (MongoConversationStore)
     - `backend/app/users/store.py` (MongoUserStore)
     - Database initialization & migration
   - **Verify**:
     - Conversations survive server restart
     - Users persist across sessions
     - All tests still pass

3. **[HIGH] Integrate RAG into Chat Pipeline** (Priority: 3)
   - **Why**: Agents need context to provide intelligent responses
   - **What**: Load documents, build index, pass to agents
   - **Effort**: 6-8 hours
   - **Files**:
     - `backend/app/services/chat_service.py`
     - `backend/app/rag/pipeline.py`
     - Dataset loading
   - **Verify**:
     - Retrieved documents appear in LLM context
     - Sources returned in API response
     - Test: Verify retrieved context relevant to query

4. **[HIGH] Connect OpenAI LLM** (Priority: 4)
   - **Why**: DummyProvider doesn't scale
   - **What**: Configure OpenAI API key, instantiate OpenAI provider
   - **Effort**: 2-3 hours
   - **Files**:
     - `backend/app/services/chat_service.py` (LLMService initialization)
     - `backend/app/agents/base.py` (agent initialization)
     - `.env` (OPENAI_API_KEY)
   - **Verify**:
     - API key properly set
     - OpenAI responses returned
     - Cost tracking (avoid surprises)

5. **[HIGH] Fix Langchain Imports** (Priority: 5)
   - **Why**: Tests blocked, code untested
   - **What**: Update imports to new langchain API
   - **Effort**: 2-3 hours
   - **Files**:
     - `backend/tests/test_agents.py`
     - `backend/tests/test_rag_pipeline.py`
     - `requirements.txt`
   - **Verify**:
     - Tests run and pass
     - No import errors

6. **[MEDIUM] Implement Logout Endpoint** (Priority: 6)
   - **Why**: Users can't revoke tokens
   - **What**: Add POST /auth/logout, add token blacklist
   - **Effort**: 2-3 hours
   - **Files**:
     - `backend/app/api/auth.py`
     - `backend/app/services/auth_service.py`
   - **Verify**:
     - POST /auth/logout revokes token
     - Revoked token rejected on next request

7. **[MEDIUM] Add Password Reset** (Priority: 7)
   - **Why**: Users need account recovery
   - **What**: Email-based password reset flow
   - **Effort**: 4-6 hours
   - **Files**:
     - `backend/app/api/auth.py`
     - Email service integration
   - **Verify**:
     - Reset email sent
     - Link works, password updated
     - Old password no longer works

8. **[MEDIUM] Upgrade Pydantic to v2** (Priority: 8)
   - **Why**: Remove deprecation warnings
   - **What**: Update requirements, replace `.dict()` with `.model_dump()`
   - **Effort**: 2-3 hours
   - **Files**:
     - `requirements.txt`
     - `backend/app/orchestrator/aggregator.py`
     - Other files using `.dict()`
   - **Verify**:
     - No warnings in test output
     - All tests pass

9. **[LOW] Add Frontend Tests** (Priority: 9)
   - **Why**: UI changes not verified
   - **What**: Add Jest/React Testing Library tests
   - **Effort**: 8-12 hours
   - **Files**:
     - `frontend/pages/**` (new test files)
     - `frontend/components/**` (new test files)
   - **Verify**:
     - Test coverage >80%
     - All tests pass

10. **[LOW] Add API Documentation** (Priority: 10)
    - **Why**: No documentation
    - **What**: FastAPI auto-generates at /docs
    - **Effort**: 1 hour
    - **Files**: `backend/app/main.py` (already supported by FastAPI)
    - **Verify**: Navigate to /docs, see all endpoints

---

## Instructions for the Next Coding Agent

### 1. READ FIRST
- [ ] Read this PROJECT_STATUS.md completely
- [ ] Read original project README.md (if exists)
- [ ] Read SECURITY_AUDIT_REPORT.md
- [ ] Read any other REPORT.md files in repo root

### 2. UNDERSTAND BEFORE CODING
- [ ] Understand current architecture (use diagram above)
- [ ] Identify what's implemented vs. what's dummy
- [ ] Read relevant source files before modifying
- [ ] Never assume functionality exists just because a file exists

### 3. PRESERVE EXISTING CODE
- [ ] Do NOT rewrite working components
- [ ] Do NOT refactor unless explicitly requested
- [ ] Preserve API contracts (endpoint paths, request/response formats)
- [ ] Preserve function signatures
- [ ] Preserve file organization

### 4. BEFORE MAKING CHANGES
- [ ] Run existing test suite: `pytest backend/tests/ -q`
- [ ] Build frontend: `npm run build`
- [ ] Verify baseline: all tests pass, build succeeds
- [ ] Document your understanding in comments

### 5. IMPLEMENTATION RULES
- [ ] Make small, focused changes (one feature per PR)
- [ ] Write tests BEFORE code (TDD)
- [ ] Do not modify tests to hide failures
- [ ] Do not commit secrets or credentials
- [ ] Do not commit datasets
- [ ] Do not modify `.env` values (document requirements instead)

### 6. TESTING REQUIREMENTS
- [ ] Run tests BEFORE committing
- [ ] Report: test command, total tests, passed, failed
- [ ] Fix test failures (do not hide them)
- [ ] Verify no regression in existing tests
- [ ] Verify new feature has test coverage

### 7. DOCUMENTATION
- [ ] Update PROJECT_STATUS.md after architectural changes
- [ ] Document any API changes
- [ ] Document any new dependencies
- [ ] Document any environment variables
- [ ] Report every file changed (via git or manually)

### 8. CODE QUALITY
- [ ] Follow existing code style
- [ ] Add docstrings to new functions
- [ ] Add comments for non-obvious logic
- [ ] Keep functions small (<50 lines)
- [ ] Use type hints (Python) or TypeScript (JavaScript)

### 9. SECURITY
- [ ] Never expose passwords or tokens in logs
- [ ] Never commit `.env` with real values
- [ ] Use environment variables for secrets
- [ ] Validate user input
- [ ] Verify authorization checks

### 10. REPORTING
- [ ] Report exactly what changed
- [ ] Report test results (pass/fail counts)
- [ ] Report build status (success/failure)
- [ ] Report any blockers or issues
- [ ] Do NOT claim "production ready" without evidence

### 11. GIT WORKFLOW
- Use meaningful commit messages
- One feature per commit
- Include test updates in same commit
- Reference issue numbers if applicable

### 12. COMMON PITFALLS
- ❌ DO NOT assume agents are called (they aren't)
- ❌ DO NOT assume RAG is used (it isn't)
- ❌ DO NOT assume LLM is real (it's dummy)
- ❌ DO NOT assume data persists (it doesn't)
- ❌ DO NOT trust file names (verify in code)
- ❌ DO NOT skip tests (run them)
- ❌ DO NOT refactor without tests
- ❌ DO NOT commit without testing

---

## File Map

### Frontend

```
frontend/
├── package.json                   # Dependencies, scripts
├── tailwind.config.js            # Tailwind CSS config
├── postcss.config.js             # PostCSS config
├── next.config.js                # Next.js config
├── pages/
│   ├── _app.js                   # App wrapper, AuthContext
│   ├── index.js                  # Home (redirect)
│   ├── login.js                  # Login page
│   ├── register.js               # Register page
│   ├── chat.js                   # Main chat interface
│   └── conversations.js          # Conversation browser
├── components/
│   ├── AuthForm.jsx              # Login/Register form
│   ├── Header.jsx                # Top nav bar
│   ├── ChatWindow.jsx            # Message display
│   ├── ChatInput.jsx             # Message input
│   ├── MessageBubble.jsx         # Single message
│   ├── ConversationSidebar.jsx   # Sidebar list
│   ├── ConversationList.jsx      # Grouped list
│   ├── ErrorBanner.jsx           # Error display
│   └── LoadingIndicator.jsx      # Loading spinner
├── lib/
│   ├── api.js                    # Axios client + routes
│   └── withAuth.js               # Protected route HOC
└── styles/
    └── globals.css               # Global styles
```

### Backend

```
backend/
├── requirements.txt              # Python dependencies
├── app/
│   ├── main.py                   # FastAPI app, middleware
│   ├── __init__.py
│   ├── api/
│   │   ├── auth.py               # /auth/register, /auth/login
│   │   ├── chat.py               # /chat endpoint
│   │   ├── conversations.py      # /conversations/* endpoints
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py       # Token generation/validation
│   │   ├── chat_service.py       # Chat flow orchestration
│   │   └── __init__.py
│   ├── users/
│   │   ├── models.py             # User pydantic models
│   │   ├── store.py              # User storage (in-memory)
│   │   └── __init__.py
│   ├── conversations/
│   │   ├── models.py             # Conversation/Message models
│   │   ├── store.py              # Conversation storage
│   │   └── __init__.py
│   ├── agents/
│   │   ├── base.py               # AgentBase class
│   │   ├── faq_agent.py          # FAQ Agent
│   │   ├── billing_agent.py      # Billing Agent
│   │   ├── technical_agent.py    # Technical Support Agent
│   │   ├── complaint_agent.py    # Complaint Agent
│   │   ├── product_agent.py      # Product Agent
│   │   └── __init__.py
│   ├── intent/
│   │   ├── detector.py           # Rule-based intent detection
│   │   └── __init__.py
│   ├── router/
│   │   ├── router.py             # Intent → Agent mapping
│   │   └── __init__.py
│   ├── orchestrator/
│   │   ├── aggregator.py         # Response aggregation
│   │   └── __init__.py
│   ├── rag/
│   │   ├── pipeline.py           # RAG orchestration
│   │   ├── doc_loader.py         # Load documents
│   │   ├── text_processing.py    # Chunk text
│   │   ├── embeddings.py         # Generate embeddings
│   │   ├── faiss_index.py        # Vector DB
│   │   └── __init__.py
│   ├── llm/
│   │   ├── service.py            # LLM service
│   │   ├── providers/
│   │   │   ├── dummy_provider.py # Dummy responses
│   │   │   ├── openai_provider.py # OpenAI wrapper
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── middleware/
│   │   ├── rate_limit.py         # Rate limiting
│   │   └── __init__.py
│   └── __pycache__/
├── tests/
│   ├── test_api_chat.py          # Chat endpoint tests
│   ├── test_conversations.py     # Conversation CRUD tests
│   ├── test_routing.py           # Routing logic tests
│   ├── test_aggregator.py        # Aggregation tests
│   ├── test_security.py          # Security tests (29)
│   ├── test_agents.py            # Agent tests [BLOCKED]
│   ├── test_rag_pipeline.py      # RAG tests [BLOCKED]
│   └── __pycache__/
├── __init__.py
└── __pycache__/
```

### Data

```
datasets/
├── README.md                     # Dataset overview
├── ORGANIZATION_REPORT.md        # Dataset inventory
├── banking77/                    # BANKING77 intent classification
├── data/                         # Multi-lingual dialogues
├── retrieval/                    # MS MARCO retrieval
├── qa_datasets/                  # QA datasets
└── customer_support/             # Custom domain data
```

### Documentation

```
docs/                            # (if exists)
README.md                        # (if exists)
SECURITY_AUDIT_REPORT.md        # Security findings
PROJECT_STATUS.md               # THIS FILE
```

---

## Environment

### Version Requirements

| Component | Version | Status |
|-----------|---------|--------|
| Python | 3.10+ | Verified 3.10.9 |
| Node.js | 18+ | Not specified, assume latest |
| Next.js | 16.3.1 | ✅ |
| FastAPI | 0.95.2 | ✅ |
| React | 19.2.8 | ✅ |
| Pydantic | <2.0.0 | ⚠️ Deprecated |

### Environment Variables

| Variable | Default | Example | Purpose |
|----------|---------|---------|---------|
| `TOKEN_EXP_HOURS` | 24 | 24 | Token expiration time |
| `CORS_ALLOW_ORIGIN` | http://localhost:3000 | https://app.example.com | CORS allowed origin |
| `OPENAI_API_KEY` | (none) | sk-... | OpenAI API key |
| `LOG_LEVEL` | INFO | DEBUG | Logging level |
| `DISABLE_RATE_LIMIT` | false | true | Disable rate limiting (dev) |
| `RATE_LIMIT_REGISTER` | 5 | 10 | Registration attempts limit |
| `RATE_LIMIT_LOGIN` | 10 | 20 | Login attempts limit |
| `MONGODB_URI` | (none) | mongodb://localhost:27017 | MongoDB connection (if used) |

### Setup Instructions

**Backend**:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest backend/tests/  # Verify setup
```

**Frontend**:
```bash
cd frontend
npm install
npm run build  # Verify setup
npm run dev    # Start dev server
```

---

## Final Summary

| Aspect | Status | % Complete |
|--------|--------|-----------|
| **Authentication** | ✅ Complete | 100% |
| **Frontend UI** | ✅ Complete | 100% |
| **Conversation Management** | ✅ Complete | 100% |
| **Intent Detection & Routing** | ✅ Complete | 100% |
| **Agent System** | 🟡 Defined, not used | 10% |
| **RAG Pipeline** | 🟡 Framework exists | 30% |
| **LLM Integration** | 🟡 DummyProvider only | 20% |
| **Database Persistence** | ❌ Not implemented | 0% |
| **Deployment** | ❌ Not configured | 0% |
| **Testing** | ✅ Core tests | 75% |
| **Documentation** | ✅ This report | 100% |
| **OVERALL** | 🟡 Prototype | ~65% |

### Executive Recommendation

**This project is a well-structured prototype with solid foundations.** Core authentication, UI, and infrastructure are production-quality. However, **the core intelligence system (agents + RAG + LLM) is not yet integrated**, making responses dummy echoes.

**Immediate action required**: Implement real agent execution (Priority 1) to make the system functional beyond a demo.

**Biggest risk**: Data loss on server restart (in-memory storage only). Implement persistent database (Priority 2) before any user-facing deployment.

**Timeline to MVP**: 
- Agent execution: 4-6 hours
- Database persistence: 8-10 hours
- RAG integration: 6-8 hours
- **Total: 18-24 hours for functional intelligent chatbot**

---

**Document Version**: 1.0  
**Last Review**: 2026-08-17  
**Prepared for**: Next AI coding agent handoff
