"""
WebSocket Models

This module provides models for WebSocket communication.
"""

from typing import Dict, Any, Optional, List, Set, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class ConnectionStatus(str, Enum):
    """Connection status enum."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"


class MessageType(str, Enum):
    """WebSocket message type enum."""
    # System messages
    CONNECTION_ESTABLISHED = "connection_established"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    RECONNECT = "reconnect"
    
    # Subscription messages
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    
    # Execution messages
    EXECUTION_SUBSCRIBE = "execution_subscribe"
    EXECUTION_UNSUBSCRIBE = "execution_unsubscribe"
    EXECUTION_SUBSCRIBED = "execution_subscribed"
    EXECUTION_UNSUBSCRIBED = "execution_unsubscribed"
    EXECUTION_UPDATE = "execution_update"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_PROGRESS = "execution_progress"
    
    # Workflow messages
    WORKFLOW_UPDATE = "workflow_update"
    WORKFLOW_SAVED = "workflow_saved"
    
    # Authentication messages
    AUTH_REQUEST = "auth_request"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    
    # Custom messages
    CUSTOM = "custom"


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: Union[MessageType, str]
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    message_id: str = Field(default_factory=lambda: f"msg-{datetime.now().timestamp()}")
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class ConnectionInfo(BaseModel):
    """Connection information model."""
    client_id: str
    user_id: Optional[str] = None
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    connected_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    groups: Set[str] = Field(default_factory=set)
    executions: Set[str] = Field(default_factory=set)
    is_authenticated: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class ConnectionStatistics(BaseModel):
    """Connection statistics model."""
    total_connections: int = 0
    authenticated_connections: int = 0
    unauthenticated_connections: int = 0
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_errors: int = 0
    uptime_seconds: float = 0
    start_time: datetime = Field(default_factory=datetime.now)
    
    def calculate_uptime(self) -> float:
        """Calculate uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def update_uptime(self) -> None:
        """Update uptime."""
        self.uptime_seconds = self.calculate_uptime()


class RateLimitConfig(BaseModel):
    """Rate limit configuration model."""
    enabled: bool = True
    max_connections_per_ip: int = 10
    max_messages_per_minute: int = 100
    max_errors_before_ban: int = 5
    ban_duration_minutes: int = 10
