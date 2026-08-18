from __future__ import annotations

import os
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

_LOG = logging.getLogger(__name__)


class MongoDB:
    """Reusable MongoDB client for the application.

    One client instance shared across all stores.
    Initialized via FastAPI lifespan.
    """

    def __init__(self) -> None:
        self.uri: str = os.getenv("MONGODB_URI", "")
        self.database_name: str = os.getenv("MONGODB_DATABASE", "astrahome")
        self.client: Optional[MotorClient] = None
        self.database = None  # type: ignore

    async def connect(self) -> None:
        if not self.uri:
            _LOG.warning("MONGODB_URI not set; MongoDB features disabled")
            return

        try:
            self.client = MotorClient(self.uri, serverSelectionTimeoutMS=5000)
            # Force a small command to verify connectivity early
            await self.client.admin.command("ping")
            self.database = self.client[self.database_name]
            _LOG.info("MongoDB connected: %s -> %s", self.uri, self.database_name)
        except Exception as e:
            _LOG.exception("Failed to connect to MongoDB: %s", e)
            self.client = None
            self.database = None

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            _LOG.info("MongoDB disconnected")
            self.client = None
            self.database = None

    def is_connected(self) -> bool:
        return self.client is not None and self.database is not None


# Global instance — initialized once via FastAPI lifespan
mongodb = MongoDB()