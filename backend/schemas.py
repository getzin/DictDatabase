# backend/schemas.py
# pip install "pydantic[email]"
# pip install email-validator
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PROFILE_NAME_MAX_LENGTH,
    LANG_CODE_MAX_LENGTH,
    API_KEY_MAX_LENGTH,
    USERNAME_ALLOWED_CHARS_REGEX,
    PASSWORD_ALLOWED_CHARS_REGEX,
)

# ============================
#         USERS
# ============================

class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=EMAIL_MAX_LENGTH)
    name: str = Field(..., max_length=USERNAME_MAX_LENGTH)

    @field_validator("name")
    @classmethod
    def validate_username(cls, v):
        """Ensure username follows allowed characters"""
        if not USERNAME_ALLOWED_CHARS_REGEX.match(v):
            raise ValueError("Username contains invalid characters.")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    password_confirm: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("password", "password_confirm")
    @classmethod
    def validate_password(cls, v):
        """Ensure password follows allowed characters"""
        if not PASSWORD_ALLOWED_CHARS_REGEX.match(v):
            raise ValueError("Password contains invalid characters.")
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=EMAIL_MAX_LENGTH)
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("password")
    @classmethod
    def validate_login_password(cls, v):
        if not PASSWORD_ALLOWED_CHARS_REGEX.match(v):
            raise ValueError("Password contains invalid characters.")
        return v

class UserOut(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True

class UpdateApiKeyRequest(BaseModel):
    user_id: int
    api_key: str = Field(..., max_length=API_KEY_MAX_LENGTH)

class ChangePasswordRequest(BaseModel):
    user_id: int
    old_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    new_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    confirm_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("old_password", "new_password", "confirm_password")
    @classmethod
    def validate_new_passwords(cls, v):
        if not PASSWORD_ALLOWED_CHARS_REGEX.match(v):
            raise ValueError("Password contains invalid characters.")
        return v


# ============================
#        PROFILES
# ============================

class ProfileBase(BaseModel):
    name: str = Field(..., max_length=PROFILE_NAME_MAX_LENGTH)
    result_lang: str = Field(..., max_length=LANG_CODE_MAX_LENGTH)
    source_lang: str = Field(..., max_length=LANG_CODE_MAX_LENGTH)
    target_lang: str = Field(..., max_length=LANG_CODE_MAX_LENGTH)

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileOut(ProfileBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True