"""
Schedule Service

This module provides services for managing workflow schedules.
"""

import threading
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import uuid
import json
import os

from backend.app.models.schedule import (
    Schedule,
    ScheduleRequest,
    ScheduleType,
    ScheduleStatus,
    ScheduleExecutionLog
)
from backend.app.models.workflow import WorkflowRequest, WorkflowExecutionRequest, ExecutionMode
from backend.app.controllers.workflow_controller import WorkflowController

# Configure logger
logger = logging.getLogger("workflow_builder")

class ScheduleService:
    """Service for managing workflow schedules."""
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(ScheduleService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the schedule service."""
        if self._initialized:
            return
            
        # Schedules storage
        self.schedules: Dict[str, Schedule] = {}
        self.execution_logs: Dict[str, ScheduleExecutionLog] = {}
        
        # Active schedules
        self.active_schedules: Set[str] = set()
        
        # Scheduler thread
        self.scheduler_thread = None
        self.scheduler_running = False
        self.scheduler_interval = 10  # Check schedules every 10 seconds
        
        # Data storage path
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self.schedules_file = os.path.join(self.data_dir, "schedules.json")
        self.logs_file = os.path.join(self.data_dir, "schedule_logs.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load schedules from file
        self._load_schedules()
        self._load_logs()
        
        self._initialized = True
    
    def _load_schedules(self) -> None:
        """Load schedules from file."""
        if not os.path.exists(self.schedules_file):
            return
            
        try:
            with open(self.schedules_file, "r") as f:
                schedules_data = json.load(f)
                
            for schedule_data in schedules_data:
                try:
                    schedule = Schedule.parse_obj(schedule_data)
                    self.schedules[schedule.id] = schedule
                    
                    # Add to active schedules if active
                    if schedule.is_active():
                        self.active_schedules.add(schedule.id)
                except Exception as e:
                    logger.error(f"Error loading schedule: {str(e)}")
                    
            logger.info(f"Loaded {len(self.schedules)} schedules, {len(self.active_schedules)} active")
        except Exception as e:
            logger.error(f"Error loading schedules from file: {str(e)}")
    
    def _load_logs(self) -> None:
        """Load execution logs from file."""
        if not os.path.exists(self.logs_file):
            return
            
        try:
            with open(self.logs_file, "r") as f:
                logs_data = json.load(f)
                
            for log_data in logs_data:
                try:
                    log = ScheduleExecutionLog.parse_obj(log_data)
                    self.execution_logs[log.id] = log
                except Exception as e:
                    logger.error(f"Error loading execution log: {str(e)}")
                    
            logger.info(f"Loaded {len(self.execution_logs)} execution logs")
        except Exception as e:
            logger.error(f"Error loading execution logs from file: {str(e)}")
    
    def _save_schedules(self) -> None:
        """Save schedules to file."""
        try:
            schedules_data = [schedule.dict() for schedule in self.schedules.values()]
            
            with open(self.schedules_file, "w") as f:
                json.dump(schedules_data, f, default=str)
                
            logger.info(f"Saved {len(self.schedules)} schedules to file")
        except Exception as e:
            logger.error(f"Error saving schedules to file: {str(e)}")
    
    def _save_logs(self) -> None:
        """Save execution logs to file."""
        try:
            logs_data = [log.dict() for log in self.execution_logs.values()]
            
            with open(self.logs_file, "w") as f:
                json.dump(logs_data, f, default=str)
                
            logger.info(f"Saved {len(self.execution_logs)} execution logs to file")
        except Exception as e:
            logger.error(f"Error saving execution logs to file: {str(e)}")
    
    def start_scheduler(self) -> None:
        """Start the scheduler thread."""
        if self.scheduler_thread is not None and self.scheduler_thread.is_alive():
            logger.info("Scheduler already running")
            return
            
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler thread."""
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            logger.info("Scheduler not running")
            return
            
        self.scheduler_running = False
        self.scheduler_thread.join(timeout=30)
        
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        logger.info("Scheduler loop started")
        
        while self.scheduler_running:
            try:
                self._check_schedules()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                
            # Sleep for the scheduler interval
            time.sleep(self.scheduler_interval)
            
        logger.info("Scheduler loop stopped")
    
    def _check_schedules(self) -> None:
        """Check schedules for execution."""
        now = datetime.now()
        schedules_to_execute = []
        
        # Find schedules to execute
        for schedule_id in list(self.active_schedules):
            schedule = self.schedules.get(schedule_id)
            
            if not schedule:
                self.active_schedules.discard(schedule_id)
                continue
                
            if not schedule.is_active():
                self.active_schedules.discard(schedule_id)
                continue
                
            if schedule.next_execution_time is None:
                schedule.update_next_execution_time()
                continue
                
            if schedule.next_execution_time <= now:
                schedules_to_execute.append(schedule)
        
        # Execute schedules
        for schedule in schedules_to_execute:
            self._execute_schedule(schedule)
    
    def _execute_schedule(self, schedule: Schedule) -> None:
        """Execute a schedule."""
        logger.info(f"Executing schedule {schedule.id} ({schedule.name})")
        
        # Create execution log
        execution_log = ScheduleExecutionLog(
            schedule_id=schedule.id,
            workflow_id=schedule.workflow_id,
            execution_id="",
            status="pending",
            start_time=datetime.now()
        )
        
        try:
            # Get workflow
            workflow_controller = WorkflowController()
            workflow = workflow_controller.get_workflow(schedule.workflow_id)
            
            if not workflow:
                raise ValueError(f"Workflow {schedule.workflow_id} not found")
                
            # Create execution request
            execution_request = WorkflowExecutionRequest(
                workflow=WorkflowRequest(
                    id=workflow.id,
                    name=workflow.name,
                    nodes=workflow.nodes,
                    edges=[edge.dict() for edge in workflow.connections]
                ),
                execution_mode=ExecutionMode.FULL,
                execution_options=schedule.execution_options
            )
            
            # Execute workflow
            result = workflow_controller.execute_workflow(execution_request)
            
            # Update execution log
            execution_log.execution_id = result.get("execution_id", "")
            execution_log.status = result.get("status", "unknown")
            execution_log.end_time = datetime.now()
            execution_log.duration_seconds = (execution_log.end_time - execution_log.start_time).total_seconds()
            
            # Update schedule
            schedule.last_execution_time = execution_log.start_time
            schedule.last_execution_id = execution_log.execution_id
            schedule.last_execution_status = execution_log.status
            schedule.execution_count += 1
            schedule.update_next_execution_time()
            schedule.updated_at = datetime.now()
            
            logger.info(f"Schedule {schedule.id} executed successfully")
        except Exception as e:
            # Update execution log with error
            execution_log.status = "error"
            execution_log.end_time = datetime.now()
            execution_log.duration_seconds = (execution_log.end_time - execution_log.start_time).total_seconds()
            execution_log.error_message = str(e)
            
            # Update schedule
            schedule.last_execution_time = execution_log.start_time
            schedule.last_execution_status = "error"
            schedule.execution_count += 1
            schedule.update_next_execution_time()
            schedule.updated_at = datetime.now()
            
            logger.error(f"Error executing schedule {schedule.id}: {str(e)}")
        
        # Save execution log
        self.execution_logs[execution_log.id] = execution_log
        self._save_logs()
        
        # Save schedules
        self._save_schedules()
    
    def create_schedule(self, request: ScheduleRequest) -> Schedule:
        """Create a new schedule."""
        # Create schedule
        schedule = Schedule(
            workflow_id=request.workflow_id,
            name=request.name,
            description=request.description,
            schedule_type=request.schedule_type,
            cron_expression=request.cron_expression,
            interval_seconds=request.interval_seconds,
            start_time=request.start_time,
            end_time=request.end_time,
            max_executions=request.max_executions,
            execution_options=request.execution_options,
            tags=request.tags
        )
        
        # Update next execution time
        schedule.update_next_execution_time()
        
        # Add to schedules
        self.schedules[schedule.id] = schedule
        
        # Add to active schedules if active
        if schedule.is_active():
            self.active_schedules.add(schedule.id)
        
        # Save schedules
        self._save_schedules()
        
        return schedule
    
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get a schedule by ID."""
        return self.schedules.get(schedule_id)
    
    def get_schedules(self, workflow_id: Optional[str] = None, status: Optional[str] = None, tag: Optional[str] = None) -> List[Schedule]:
        """Get schedules with optional filtering."""
        schedules = list(self.schedules.values())
        
        # Filter by workflow ID
        if workflow_id:
            schedules = [s for s in schedules if s.workflow_id == workflow_id]
        
        # Filter by status
        if status:
            try:
                status_enum = ScheduleStatus(status)
                schedules = [s for s in schedules if s.status == status_enum]
            except ValueError:
                pass
        
        # Filter by tag
        if tag:
            schedules = [s for s in schedules if tag in s.tags]
        
        return schedules
    
    def update_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Optional[Schedule]:
        """Update a schedule."""
        schedule = self.schedules.get(schedule_id)
        
        if not schedule:
            return None
        
        # Update fields
        for field, value in updates.items():
            if hasattr(schedule, field):
                setattr(schedule, field, value)
        
        # Update timestamps
        schedule.updated_at = datetime.now()
        
        # Update next execution time
        schedule.update_next_execution_time()
        
        # Update active schedules
        if schedule.is_active():
            self.active_schedules.add(schedule.id)
        else:
            self.active_schedules.discard(schedule.id)
        
        # Save schedules
        self._save_schedules()
        
        return schedule
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule."""
        if schedule_id not in self.schedules:
            return False
        
        # Remove from schedules
        del self.schedules[schedule_id]
        
        # Remove from active schedules
        self.active_schedules.discard(schedule_id)
        
        # Save schedules
        self._save_schedules()
        
        return True
    
    def pause_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Pause a schedule."""
        schedule = self.schedules.get(schedule_id)
        
        if not schedule:
            return None
        
        # Update status
        schedule.status = ScheduleStatus.PAUSED
        schedule.updated_at = datetime.now()
        
        # Remove from active schedules
        self.active_schedules.discard(schedule.id)
        
        # Save schedules
        self._save_schedules()
        
        return schedule
    
    def resume_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Resume a schedule."""
        schedule = self.schedules.get(schedule_id)
        
        if not schedule:
            return None
        
        # Update status
        schedule.status = ScheduleStatus.ACTIVE
        schedule.updated_at = datetime.now()
        
        # Update next execution time
        schedule.update_next_execution_time()
        
        # Add to active schedules if active
        if schedule.is_active():
            self.active_schedules.add(schedule.id)
        
        # Save schedules
        self._save_schedules()
        
        return schedule
    
    def get_execution_logs(self, schedule_id: Optional[str] = None, limit: int = 100) -> List[ScheduleExecutionLog]:
        """Get execution logs with optional filtering."""
        logs = list(self.execution_logs.values())
        
        # Filter by schedule ID
        if schedule_id:
            logs = [log for log in logs if log.schedule_id == schedule_id]
        
        # Sort by start time (newest first)
        logs.sort(key=lambda log: log.start_time, reverse=True)
        
        # Limit results
        if limit > 0:
            logs = logs[:limit]
        
        return logs
    
    def get_execution_log(self, log_id: str) -> Optional[ScheduleExecutionLog]:
        """Get an execution log by ID."""
        return self.execution_logs.get(log_id)
    
    def clear_execution_logs(self, schedule_id: Optional[str] = None, days: Optional[int] = None) -> int:
        """Clear execution logs with optional filtering."""
        if schedule_id is None and days is None:
            return 0
        
        logs_to_remove = []
        
        # Find logs to remove
        for log_id, log in self.execution_logs.items():
            if schedule_id and log.schedule_id != schedule_id:
                continue
                
            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                if log.start_time >= cutoff_date:
                    continue
            
            logs_to_remove.append(log_id)
        
        # Remove logs
        for log_id in logs_to_remove:
            del self.execution_logs[log_id]
        
        # Save logs
        self._save_logs()
        
        return len(logs_to_remove)
