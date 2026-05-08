import uuid
from typing import Literal
from pydantic import BaseModel, EmailStr, field_validator, Field
from ..model.User_model import UserRole

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=120)
    role: UserRole = UserRole.EMPLOYEE

    @field_validator("password")
    @classmethod
    def validate_password(cls ,v: str) -> str:
        error = []

        if len(v) < 6:
            error.append("Password must be at least 6 character")
        if not any(c.isupper() for c in v):
            error.append("Must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            error.append("Must contain at least one number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            error.append("at least one special character (!@#$%^&*...)")

        if error:
            raise ValueError(f"Password must contain: {', '.join(error)}")

        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, _ and -")
        return v.lower()

    model_config = {
        "extra": "forbid",
    }

class token(BaseModel):
    access_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int

class UserResponse(BaseModel):
    UUid: uuid.UUID
    username: str
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}

class UserWrapper(BaseModel):
    message: str
    token: token
    user: UserResponse



class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls ,v: str) -> str:
        error = []

        if len(v) < 6:
            error.append("Password must be at least 6 character")
        if not any(c.isupper() for c in v):
            error.append("Must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            error.append("Must contain at least one number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            error.append("at least one special character (!@#$%^&*...)")

        if error:
            raise ValueError(f"Password must contain: {', '.join(error)}")

        return v

    model_config = {
        "extra": "forbid",
    }

