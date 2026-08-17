from fastapi import APIRouter, HTTPException, Query, Depends, Header
from typing import Optional
from backend.app.conversations import models, store
from backend.app.users import store as user_store
from backend.app.services.auth_service import default_auth_service

router = APIRouter()


def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and verify the current user from Authorization header."""
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


@router.post("/conversations", status_code=201)
def create_conversation(payload: models.ConversationCreate, current_user=Depends(get_current_user)):
    """Create a new conversation. Requires authentication."""
    try:
        # Set user_id to current user if not provided
        if not payload.user_id:
            payload.user_id = current_user.id
        conv = store.default_store.create_conversation(payload)
        return conv
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.post("/conversations/{session_id}/messages", status_code=201)
def add_message(session_id: str, req: models.AddMessageRequest, current_user=Depends(get_current_user)):
    """Add a message to a conversation. Requires authentication and ownership."""
    try:
        # Verify the user owns this conversation
        conv = store.default_store.get_conversation(session_id)
        if conv.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        msg = store.default_store.add_message(session_id, req.sender, req.text, req.metadata)
        return {"message": msg}
    except store.ConversationNotFound:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add message")


@router.get("/conversations/{session_id}")
def get_conversation(session_id: str, current_user=Depends(get_current_user)):
    """Get a conversation. Requires authentication and ownership."""
    try:
        conv = store.default_store.get_conversation(session_id)
        # Verify the user owns this conversation
        if conv.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        return conv
    except store.ConversationNotFound:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@router.get("/conversations/{session_id}/history")
def get_history(session_id: str, max_messages: Optional[int] = Query(20, ge=1, le=200), current_user=Depends(get_current_user)):
    """Get conversation history. Requires authentication and ownership."""
    try:
        conv = store.default_store.get_conversation(session_id)
        # Verify the user owns this conversation
        if conv.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        msgs = store.default_store.get_trimmed_history(session_id, max_messages=max_messages)
        return {"messages": msgs}
    except store.ConversationNotFound:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@router.get("/conversations/user/{user_id}")
def list_user_conversations(user_id: str, current_user=Depends(get_current_user)):
    """
    List conversations for a user.
    
    SECURITY: Users can only list their own conversations.
    Attempting to access another user's conversations returns 403.
    """
    # Verify the user is requesting their own conversations
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        convs = store.default_store.list_conversations_for_user(user_id)
        return {"conversations": convs}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")
