import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

_HAS_LETTER  = re.compile(r"[A-Za-z]")
_HAS_DIGIT   = re.compile(r"\d")
_HAS_SPECIAL = re.compile(r"[^A-Za-z0-9\s]")   # any symbol/punctuation, not space

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)   # bcrypt caps at 72 bytes
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_policy(cls, v: str) -> str:
        if not _HAS_LETTER.search(v):
            raise ValueError("Password must contain at least one letter")
        if not _HAS_DIGIT.search(v):
            raise ValueError("Password must contain at least one number")
        if not _HAS_SPECIAL.search(v):
            raise ValueError("Password must contain at least one special character (e.g. !@#$%)")
        if " " in v:
            raise ValueError("Password must not contain spaces")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}