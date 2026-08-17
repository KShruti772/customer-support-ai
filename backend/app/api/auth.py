from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from backend.app.services import auth_service
from backend.app.users import store as user_store
from backend.app.users import models as user_models

router = APIRouter(prefix="/auth")


class RegisterReq(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=8, max_length=256)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        # Allow alphanumeric, underscore, hyphen
        if not all(c.isalnum() or c in '_-' for c in v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Require at least one letter and one number
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        if not (has_letter and has_number):
            raise ValueError('Password must contain at least one letter and one number')
        return v


class LoginReq(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str


class RegisterResponse(BaseModel):
    user: UserResponse


@router.post("/register", status_code=201, response_model=RegisterResponse)
def register(req: RegisterReq):
    """
    Register a new user.
    
    - Username: 1-128 characters, alphanumeric + underscore + hyphen only
    - Password: 8-256 characters, must contain letters and numbers
    
    Returns 201 on success, 400 on invalid input or duplicate username.
    """
    try:
        user = auth_service.default_auth_service.register(req.username, req.password)
        return RegisterResponse(user=UserResponse(id=user.id, username=user.username))
    except user_store.UserAlreadyExists:
        raise HTTPException(status_code=400, detail="Username already exists")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log error but don't expose details
        raise HTTPException(status_code=400, detail="Registration failed")


@router.post("/login", response_model=LoginResponse)
def login(req: LoginReq):
    """
    Authenticate user and return access token.
    
    Token is valid for TOKEN_EXP_HOURS (default 24 hours).
    Use 'Bearer {access_token}' in Authorization header for authenticated requests.
    
    Returns 200 on success, 401 on invalid credentials.
    """
    try:
        token = auth_service.default_auth_service.login(req.username, req.password)
        return LoginResponse(access_token=token, token_type="bearer")
    except auth_service.AuthError:
        # Generic error message - don't reveal if username exists
        raise HTTPException(status_code=401, detail="Invalid username or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")
