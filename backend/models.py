# backend/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.database import Base
from constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    API_KEY_MAX_LENGTH,
    PROFILE_NAME_MAX_LENGTH,
    LANG_CODE_MAX_LENGTH,
    SEARCH_TERM_MAX_LENGTH,
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(EMAIL_MAX_LENGTH), unique=True, index=True, nullable=False)
    name = Column(String(USERNAME_MAX_LENGTH), nullable=False)
    password = Column(String(PASSWORD_MAX_LENGTH), nullable=False)
    api_key = Column(String(API_KEY_MAX_LENGTH), nullable=True)

    profiles = relationship("Profile", back_populates="user", cascade="all, delete")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(PROFILE_NAME_MAX_LENGTH), nullable=False)
    result_lang = Column(String(LANG_CODE_MAX_LENGTH), nullable=False)
    source_lang = Column(String(LANG_CODE_MAX_LENGTH), nullable=False)
    target_lang = Column(String(LANG_CODE_MAX_LENGTH), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="profiles")
    history = relationship("History", back_populates="profile", cascade="all, delete")

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    term = Column(String(SEARCH_TERM_MAX_LENGTH), nullable=False)
    source_lang = Column(String(LANG_CODE_MAX_LENGTH), nullable=False)
    target_lang = Column(String(LANG_CODE_MAX_LENGTH), nullable=False)
    json_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="history")