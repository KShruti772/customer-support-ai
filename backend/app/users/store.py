from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from typing import Optional, Dict
from .models import User


class UserAlreadyExists(Exception):
    pass


class UserStore:
    def create_user(self, username: str, password: str) -> User:
        raise NotImplementedError()

    def get_user_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError()

    def verify_password(self, password: str, password_hash: str) -> bool:
        raise NotImplementedError()


class InMemoryUserStore(UserStore):
    def __init__(self):
        self._by_username: Dict[str, User] = {}
        self._by_id: Dict[str, User] = {}
        self._password_hasher = PasswordHasher()

    def _hash_password(self, password: str) -> str:
        """Hash password using Argon2id"""
        return self._password_hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash using Argon2id"""
        try:
            self._password_hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, VerificationError):
            return False

    def create_user(self, username: str, password: str) -> User:
        if username in self._by_username:
            raise UserAlreadyExists()
        hashed = self._hash_password(password)
        user = User(username=username, hashed_password=hashed)
        self._by_username[username] = user
        self._by_id[user.id] = user
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self._by_username.get(username)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self._by_id.get(user_id)


default_user_store = InMemoryUserStore()
