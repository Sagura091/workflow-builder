"""
Schedule Models

This module defines models for workflow scheduling.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
import uuid

class ScheduleType(str, Enum):
    """Types of schedules."""
    CRON = "cron"  # Cron-based schedule
    INTERVAL = "interval"  # Interval-based schedule
    ONE_TIME = "one_time"  # One-time schedule
    EVENT = "event"  # Event-based schedule

class ScheduleStatus(str, Enum):
    """Status of a schedule."""
    ACTIVE = "active"  # Schedule is active
    PAUSED = "paused"  # Schedule is paused
    COMPLETED = "completed"  # Schedule is completed
    FAILED = "failed"  # Schedule has failed

class ScheduleRequest(BaseModel):
    """Request model for creating a schedule."""
    workflow_id: str
    name: str
    description: Optional[str] = None
    schedule_type: ScheduleType
    cron_expression: Optional[str] = None  # For cron-based schedules
    interval_seconds: Optional[int] = None  # For interval-based schedules
    start_time: Optional[datetime] = None  # For one-time schedules
    end_time: Optional[datetime] = None
    max_executions: Optional[int] = None
    execution_options: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class Schedule(BaseModel):
    """Model for a workflow schedule."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    name: str
    description: Optional[str] = None
    schedule_type: ScheduleType
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    next_execution_time: Optional[datetime] = None
    last_execution_time: Optional[datetime] = None
    last_execution_id: Optional[str] = None
    last_execution_status: Optional[str] = None
    execution_count: int = 0
    max_executions: Optional[int] = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    execution_options: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    
    def is_active(self) -> bool:
        """Check if the schedule is active."""
        if self.status != ScheduleStatus.ACTIVE:
            return False
            
        # Check if max executions reached
        if self.max_executions is not None and self.execution_count >= self.max_executions:
            return False
            
        # Check if end time reached
        if self.end_time is not None and datetime.now() > self.end_time:
            return False
            
        return True
    
    def update_next_execution_time(self) -> None:
        """Update the next execution time based on the schedule type."""
        now = datetime.now()
        
        if self.schedule_type == ScheduleType.ONE_TIME:
            # One-time schedules only execute once
            if self.execution_count > 0:
                self.next_execution_time = None
            else:
                self.next_execution_time = self.start_time
        
        elif self.schedule_type == ScheduleType.INTERVAL:
            # Interval-based schedules
            if self.interval_seconds is None:
                self.next_execution_time = None
                return
                
            if self.next_execution_time is None:
                # First execution
                if self.start_time and self.start_time > now:
                    self.next_execution_time = self.start_time
                else:
                    self.next_execution_time = now
            else:
                # Subsequent executions
                while self.next_execution_time <= now:
                    self.next_execution_time = self.next_execution_time + timedelta(seconds=self.interval_seconds)
        
        elif self.schedule_type == ScheduleType.CRON:
            # Cron-based schedules
            if self.cron_expression is None:
                self.next_execution_time = None
                return
                
            try:
                import croniter
                
                if self.next_execution_time is None:
                    # First execution
                    base_time = max(now, self.start_time) if self.start_time else now
                else:
                    # Subsequent executions
                    base_time = self.next_execution_time
                    
                cron = croniter.croniter(self.cron_expression, base_time)
                self.next_execution_time = cron.get_next(datetime)
                
                # If next execution is before now, get the next one
                while self.next_execution_time <= now:
                    self.next_execution_time = cron.get_next(datetime)
            except Exception as e:
                # Invalid cron expression
                self.next_execution_time = None
        
        # Check if next execution is after end time
        if self.end_time is not None and self.next_execution_time is not None:
            if self.next_execution_time > self.end_time:
                self.next_execution_time = None
                
        # Check if max executions reached
        if self.max_executions is not None and self.execution_count >= self.max_executions:
            self.next_execution_time = None

class ScheduleResponse(BaseModel):
    """Response model for schedule operations."""
    id: str
    workflow_id: str
    name: str
    description: Optional[str] = None
    schedule_type: ScheduleType
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    next_execution_time: Optional[datetime] = None
    last_execution_time: Optional[datetime] = None
    last_execution_id: Optional[str] = None
    last_execution_status: Optional[str] = None
    execution_count: int
    max_executions: Optional[int] = None
    status: ScheduleStatus
    created_at: datetime
    updated_at: datetime
    tags: List[str] = Field(default_factory=list)

class ScheduleExecutionLog(BaseModel):
    """Log entry for a schedule execution."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schedule_id: str
    workflow_id: str
    execution_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
