from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from datetime import datetime
from typing import Optional, Dict, List
from uuid import uuid4

from pymongo.errors import DuplicateKeyError

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

    def list_usernames(self) -> List[str]:
        raise NotImplementedError()

    def detect_duplicate(self, username: str) -> bool:
        raise NotImplementedError()


class MongoUserStore(UserStore):
    def __init__(self, database):
        """database is a MotorDatabase instance."""
        self._col = database.get_collection("users")
        # Ensure unique index on username; created once on init
        try:
            self._col.create_index("username", unique=True)
        except Exception:
            # Index may already exist; that's fine
            pass

    async def _hash_password(self, password: str) -> str:
        """Hash password using Argon2id"""
        PHP = __import__("argon2").PasswordHasher()
        return PHP.hash(password)

    async def create_user(self, username: str, password: str) -> User:
        # Database-level uniqueness guard (prevents race conditions)
        existing = await self._col.find_one({"username": username})
        if existing:
            raise UserAlreadyExists()

        hashed = await self._hash_password(password)
        user_id = str(uuid4())
        user = User(id=user_id, username=username, hashed_password=hashed, created_at=datetime.utcnow())
        # Insert as dict; User.model_dump gives us a dict with proper fields
        doc = user.model_dump()
        doc["id"] = user_id
        await self._col.insert_one(doc)
        # Return user from DB
        return await self.get_user_by_username(username)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        doc = await self._col.find_one({"username": username})
        if not doc:
            return None
        # Remove _id and convert to User
        doc.pop("_id", None)
        return User(**doc)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        doc = await self._col.find_one({"id": user_id})
        if not doc:
            return None
        doc.pop("_id", None)
        return User(**doc)

    async def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            PHP = __import__("argon2").PasswordHasher()
            PHP.verify(password_hash, password)
            return True
        except Exception:
            return False

    async def list_usernames(self) -> List[str]:
        docs = self._col.find({}, {"username": 1, "_id": 0})
        return [doc["username"] async for doc in docs]

    async def detect_duplicate(self, username: str) -> bool:
        count = await self._col.count_documents({"username": username})
        return count > 0


# Keep the in-memory default for backward compatibility when MongoDB unavailable
class InMemoryUserStore(UserStore):
    def __init__(self):
        self._by_username: Dict[str, User] = {}
        self._by_id: Dict[str, User] = {}
        self._password_hasher = __import__("argon2").PasswordHasher()

    def _hash_password(self, password: str) -> str:
        return self._password_hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            self._password_hasher.verify(password_hash, password)
            return True
        except Exception:
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


# Global — set from FastAPI startup if MongoDB available
default_user_store = InMemoryUserStore()  # type: ignore