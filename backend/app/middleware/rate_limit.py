"""
Simple in-memory rate limiting middleware for development.

For production, use a dedicated rate limiting solution like:
- Redis-based rate limiter
- API Gateway rate limiting
- Cloud provider rate limiting (AWS, GCP, Azure)
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
import os


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter for authentication endpoints.
    
    Limits:
    - POST /auth/register: 5 requests per 15 minutes per IP
    - POST /auth/login: 10 requests per 15 minutes per IP
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)  # IP -> list of (timestamp, endpoint)
        
        # Configuration
        self.register_limit = int(os.getenv("RATE_LIMIT_REGISTER", "5"))
        self.register_window = int(os.getenv("RATE_LIMIT_REGISTER_WINDOW", "900"))  # 15 min
        self.login_limit = int(os.getenv("RATE_LIMIT_LOGIN", "10"))
        self.login_window = int(os.getenv("RATE_LIMIT_LOGIN_WINDOW", "900"))  # 15 min

    async def dispatch(self, request: Request, call_next):
        # Only rate limit auth endpoints
        path = request.url.path
        if path not in ["/auth/register", "/auth/login"]:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        now = datetime.utcnow()
        self.requests[client_ip] = [
            (ts, ep) for ts, ep in self.requests[client_ip]
            if (now - ts).total_seconds() < 900  # Keep last 15 minutes
        ]

        # Determine limit based on endpoint
        if path == "/auth/register":
            limit = self.register_limit
            window = self.register_window
        else:  # /auth/login
            limit = self.login_limit
            window = self.login_window

        # Count requests to this endpoint in the window
        recent = [
            (ts, ep) for ts, ep in self.requests[client_ip]
            if ep == path and (now - ts).total_seconds() < window
        ]

        if len(recent) >= limit:
            return JSONResponse(
                {"detail": "Too many requests. Please try again later."},
                status_code=429
            )

        # Record this request
        self.requests[client_ip].append((now, path))

        return await call_next(request)
