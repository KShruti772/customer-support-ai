from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from backend.app.api import conversations, auth, chat
from backend.app.middleware.rate_limit import RateLimitMiddleware
from backend.app.db import mongodb

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)

app = FastAPI()

# Add rate limiting middleware for auth endpoints (only in production)
# Set DISABLE_RATE_LIMIT=true for testing
if os.getenv("DISABLE_RATE_LIMIT", "false").lower() != "true":
    app.add_middleware(RateLimitMiddleware)

# CORS Configuration
# For development: allow localhost
# For production: set CORS_ALLOW_ORIGIN to actual frontend origin
cors_origin = os.getenv("CORS_ALLOW_ORIGIN", "http://localhost:3000")
allow_origins = [cors_origin] if cors_origin != "*" else [cors_origin]

# Security: Only allow credentials with specific origins, not with wildcard
if cors_origin == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[cors_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_db_client():
    await mongodb.connect()
    if not mongodb.is_connected():
        _LOG.warning("MongoDB not connected — persistence features will use in-memory fallback")


@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.disconnect()


@app.get("/health")
async def health():
    db_status = "connected" if mongodb.is_connected() else "disconnected"
    return {"status": "ok", "mongodb": db_status}


app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)
