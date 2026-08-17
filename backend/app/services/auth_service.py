import secrets
from typing import Optional
from datetime import datetime, timedelta
import os
from backend.app.users import store as user_store

TOK_EXP_HOURS = int(os.getenv("TOKEN_EXP_HOURS", "24"))


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self):
        # token -> (user_id, expires_at)
        self._tokens = {}

    def register(self, username: str, password: str):
        return user_store.default_user_store.create_user(username, password)

    def login(self, username: str, password: str) -> str:
        user = user_store.default_user_store.get_user_by_username(username)
        if not user:
            raise AuthError("invalid credentials")
        
        # Use the new password verification method
        if not user_store.default_user_store.verify_password(password, user.hashed_password):
            raise AuthError("invalid credentials")
        
        token = secrets.token_urlsafe(32)
        self._tokens[token] = (user.id, datetime.utcnow() + timedelta(hours=TOK_EXP_HOURS))
        return token

    def verify_token(self, token: str) -> Optional[str]:
        entry = self._tokens.get(token)
        if not entry:
            return None
        user_id, expires = entry
        if datetime.utcnow() > expires:
            del self._tokens[token]
            return None
        return user_id

    def revoke_token(self, token: str):
        self._tokens.pop(token, None)


default_auth_service = AuthService()
