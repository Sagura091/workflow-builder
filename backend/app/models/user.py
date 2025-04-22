"""
User Models

This module defines models for user authentication and authorization.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

class UserRole(str, Enum):
    """User roles for authorization."""
    ADMIN = "admin"  # Full access to all features
    USER = "user"  # Standard user with limited access
    VIEWER = "viewer"  # Read-only access

class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"  # Account is active
    INACTIVE = "inactive"  # Account is inactive
    PENDING = "pending"  # Account is pending activation
    LOCKED = "locked"  # Account is locked

class User(BaseModel):
    """User model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        orm_mode = True

class UserCreate(BaseModel):
    """Request model for creating a user."""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    """Request model for updating a user."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    """Response model for user operations."""
    id: str
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        orm_mode = True

class Token(BaseModel):
    """Token model for authentication."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse

class TokenData(BaseModel):
    """Token data model for JWT payload."""
    sub: str  # User ID
    username: str
    role: str
    exp: int  # Expiration timestamp
