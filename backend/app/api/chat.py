from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from backend.app.services import auth_service, chat_service
from backend.app.services.auth_service import default_auth_service
from backend.app.users import store as user_store
from backend.app.conversations import store as conv_store

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    escalate: bool
    sources: list


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    user_id = default_auth_service.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = user_store.default_user_store.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, current_user=Depends(get_current_user)):
    try:
        # Ownership check: if session_id provided, verify user owns it
        if req.session_id:
            conv = chat_service.default_chat_service.conversation_store.get_conversation(req.session_id)
            if conv.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        res = chat_service.default_chat_service.chat(current_user.id, req.message, session_id=req.session_id)
        # ensure we return session id
        session_id = req.session_id or ""
        if not session_id:
            # attempt to find last conversation for user
            convs = chat_service.default_chat_service.conversation_store.list_conversations_for_user(current_user.id)
            if convs:
                session_id = convs[-1].session_id
        return {"session_id": session_id, "answer": res.final_answer, "escalate": res.escalate, "sources": res.sources}
    except conv_store.ConversationNotFound:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except HTTPException:
        raise  # Re-raise HTTP exceptions (including our 403)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
