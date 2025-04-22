"""
Authentication Service

This module provides services for user authentication and authorization.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.app.models.user import User, UserRole, UserStatus, TokenData

# Configure logger
logger = logging.getLogger("workflow_builder")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

class AuthService:
    """Service for user authentication and authorization."""
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(AuthService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the authentication service."""
        if self._initialized:
            return
            
        # JWT settings
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # User storage
        self.users: Dict[str, User] = {}
        self.username_to_id: Dict[str, str] = {}
        self.email_to_id: Dict[str, str] = {}
        
        # Data storage path
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self.users_file = os.path.join(self.data_dir, "users.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load users from file
        self._load_users()
        
        # Create admin user if no users exist
        if not self.users:
            self._create_admin_user()
        
        self._initialized = True
    
    def _load_users(self) -> None:
        """Load users from file."""
        if not os.path.exists(self.users_file):
            return
            
        try:
            with open(self.users_file, "r") as f:
                users_data = json.load(f)
                
            for user_data in users_data:
                try:
                    user = User.parse_obj(user_data)
                    self.users[user.id] = user
                    self.username_to_id[user.username] = user.id
                    self.email_to_id[user.email] = user.id
                except Exception as e:
                    logger.error(f"Error loading user: {str(e)}")
                    
            logger.info(f"Loaded {len(self.users)} users")
        except Exception as e:
            logger.error(f"Error loading users from file: {str(e)}")
    
    def _save_users(self) -> None:
        """Save users to file."""
        try:
            users_data = [user.dict() for user in self.users.values()]
            
            with open(self.users_file, "w") as f:
                json.dump(users_data, f, default=str)
                
            logger.info(f"Saved {len(self.users)} users to file")
        except Exception as e:
            logger.error(f"Error saving users to file: {str(e)}")
    
    def _create_admin_user(self) -> None:
        """Create an admin user if no users exist."""
        try:
            # Default admin credentials
            username = os.getenv("ADMIN_USERNAME", "admin")
            password = os.getenv("ADMIN_PASSWORD", "admin")
            email = os.getenv("ADMIN_EMAIL", "admin@example.com")
            
            # Create admin user
            self.create_user(
                username=username,
                email=email,
                password=password,
                role=UserRole.ADMIN
            )
            
            logger.info(f"Created admin user: {username}")
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}")
    
    def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.USER,
                   first_name: Optional[str] = None, last_name: Optional[str] = None) -> User:
        """Create a new user."""
        # Check if username or email already exists
        if username in self.username_to_id:
            raise ValueError(f"Username '{username}' already exists")
            
        if email in self.email_to_id:
            raise ValueError(f"Email '{email}' already exists")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # Add to storage
        self.users[user.id] = user
        self.username_to_id[user.username] = user.id
        self.email_to_id[user.email] = user.id
        
        # Save users
        self._save_users()
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        user_id = self.username_to_id.get(username)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        user_id = self.email_to_id.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_users(self) -> List[User]:
        """Get all users."""
        return list(self.users.values())
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update a user."""
        user = self.users.get(user_id)
        
        if not user:
            return None
        
        # Handle email update
        if "email" in updates and updates["email"] != user.email:
            # Check if email already exists
            if updates["email"] in self.email_to_id and self.email_to_id[updates["email"]] != user_id:
                raise ValueError(f"Email '{updates['email']}' already exists")
                
            # Update email mapping
            del self.email_to_id[user.email]
            self.email_to_id[updates["email"]] = user_id
        
        # Update fields
        for field, value in updates.items():
            if hasattr(user, field) and field != "password_hash":
                setattr(user, field, value)
        
        # Update timestamp
        user.updated_at = datetime.now()
        
        # Save users
        self._save_users()
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = self.users.get(user_id)
        
        if not user:
            return False
        
        # Remove from storage
        del self.users[user_id]
        del self.username_to_id[user.username]
        del self.email_to_id[user.email]
        
        # Save users
        self._save_users()
        
        return True
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change a user's password."""
        user = self.users.get(user_id)
        
        if not user:
            return False
        
        # Verify current password
        if not self._verify_password(current_password, user.password_hash):
            return False
        
        # Hash new password
        password_hash = self._hash_password(new_password)
        
        # Update password
        user.password_hash = password_hash
        user.updated_at = datetime.now()
        
        # Save users
        self._save_users()
        
        return True
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """Reset a user's password (admin only)."""
        user = self.users.get(user_id)
        
        if not user:
            return False
        
        # Hash new password
        password_hash = self._hash_password(new_password)
        
        # Update password
        user.password_hash = password_hash
        user.updated_at = datetime.now()
        
        # Save users
        self._save_users()
        
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = self.get_user_by_username(username)
        
        if not user:
            return None
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            return None
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        self._save_users()
        
        return user
    
    def create_access_token(self, user: User) -> Dict[str, Any]:
        """Create an access token for a user."""
        # Token expiration
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        expires_at = datetime.now() + expires_delta
        
        # Token data
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role,
            "exp": expires_at.timestamp()
        }
        
        # Create JWT token
        access_token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": expires_at,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "last_login": user.last_login
            }
        }
    
    def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """Get the current user from a token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Extract token data
            user_id = payload.get("sub")
            username = payload.get("username")
            role = payload.get("role")
            
            if user_id is None or username is None:
                raise credentials_exception
                
            token_data = TokenData(sub=user_id, username=username, role=role, exp=payload.get("exp"))
        except JWTError:
            raise credentials_exception
        
        # Get user
        user = self.get_user(token_data.sub)
        
        if user is None:
            raise credentials_exception
            
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
            )
        
        return user
    
    def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        """Get the current active user."""
        if current_user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
            )
        return current_user
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        # Generate salt
        salt = bcrypt.gensalt()
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), salt)
        
        return password_hash.decode()
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password."""
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
