from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("username cannot be empty")
        if len(v) > 30:
            raise ValueError("username cannot exceed 30 characters")
        return v

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class LoginSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("password cannot be empty")
        return v.strip()


class EditAccountSchema(BaseModel):
    username:   Optional[str]   = None
    email:      Optional[EmailStr] = None
    password:   Optional[str]   = None
    avatar_url: Optional[str]   = None
    bio:        Optional[str]   = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("username cannot be empty")
        if len(v) > 30:
            raise ValueError("username cannot exceed 30 characters")
        return v

    @field_validator("email")
    @classmethod
    def email_to_lower(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v

    @field_validator("bio")
    @classmethod
    def bio_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 160:
            raise ValueError("bio cannot exceed 160 characters")
        return v
