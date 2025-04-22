"""
Schedule Routes

This module provides routes for managing workflow schedules.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User

from backend.app.models.schedule import (
    Schedule,
    ScheduleRequest,
    ScheduleResponse,
    ScheduleType,
    ScheduleStatus,
    ScheduleExecutionLog
)
from backend.app.services.schedule_service import ScheduleService
from backend.app.models.responses import StandardResponse

router = APIRouter(prefix="/api/schedules", tags=["schedules"])

@router.post("")
async def create_schedule(request: ScheduleRequest, current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Create a new schedule."""
    try:
        schedule_service = ScheduleService()
        schedule = schedule_service.create_schedule(request)
        return StandardResponse.success(
            message="Schedule created successfully",
            data=schedule.dict()
        )
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.get("")
async def get_schedules(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """Get schedules with optional filtering."""
    try:
        schedule_service = ScheduleService()
        schedules = schedule_service.get_schedules(workflow_id, status, tag)
        return StandardResponse.success(
            data=[schedule.dict() for schedule in schedules]
        )
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str, current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Get a schedule by ID."""
    try:
        schedule_service = ScheduleService()
        schedule = schedule_service.get_schedule(schedule_id)

        if not schedule:
            return StandardResponse.error(
                message="Schedule not found",
                errors=[{
                    "code": "NOT_FOUND",
                    "message": f"Schedule with ID {schedule_id} not found"
                }]
            )

        return StandardResponse.success(data=schedule.dict())
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.put("/{schedule_id}")
async def update_schedule(schedule_id: str, updates: Dict[str, Any], current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Update a schedule."""
    try:
        schedule_service = ScheduleService()
        schedule = schedule_service.update_schedule(schedule_id, updates)

        if not schedule:
            return StandardResponse.error(
                message="Schedule not found",
                errors=[{
                    "code": "NOT_FOUND",
                    "message": f"Schedule with ID {schedule_id} not found"
                }]
            )

        return StandardResponse.success(
            message="Schedule updated successfully",
            data=schedule.dict()
        )
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str, current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Delete a schedule."""
    try:
        schedule_service = ScheduleService()
        success = schedule_service.delete_schedule(schedule_id)

        if not success:
            return StandardResponse.error(
                message="Schedule not found",
                errors=[{
                    "code": "NOT_FOUND",
                    "message": f"Schedule with ID {schedule_id} not found"
                }]
            )

        return StandardResponse.success(message="Schedule deleted successfully")
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.post("/{schedule_id}/pause")
async def pause_schedule(schedule_id: str, current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Pause a schedule."""
    try:
        schedule_service = ScheduleService()
        schedule = schedule_service.pause_schedule(schedule_id)

        if not schedule:
            return StandardResponse.error(
                message="Schedule not found",
                errors=[{
                    "code": "NOT_FOUND",
                    "message": f"Schedule with ID {schedule_id} not found"
                }]
            )

        return StandardResponse.success(
            message="Schedule paused successfully",
            data=schedule.dict()
        )
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.post("/{schedule_id}/resume")
async def resume_schedule(schedule_id: str, current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Resume a schedule."""
    try:
        schedule_service = ScheduleService()
        schedule = schedule_service.resume_schedule(schedule_id)

        if not schedule:
            return StandardResponse.error(
                message="Schedule not found",
                errors=[{
                    "code": "NOT_FOUND",
                    "message": f"Schedule with ID {schedule_id} not found"
                }]
            )

        return StandardResponse.success(
            message="Schedule resumed successfully",
            data=schedule.dict()
        )
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.get("/logs")
async def get_execution_logs(
    schedule_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """Get execution logs with optional filtering."""
    try:
        schedule_service = ScheduleService()
        logs = schedule_service.get_execution_logs(schedule_id, limit)
        return StandardResponse.success(
            data=[log.dict() for log in logs]
        )
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.get("/logs/{log_id}")
async def get_execution_log(log_id: str, current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Get an execution log by ID."""
    try:
        schedule_service = ScheduleService()
        log = schedule_service.get_execution_log(log_id)

        if not log:
            return StandardResponse.error(
                message="Execution log not found",
                errors=[{
                    "code": "NOT_FOUND",
                    "message": f"Execution log with ID {log_id} not found"
                }]
            )

        return StandardResponse.success(data=log.dict())
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.delete("/logs")
async def clear_execution_logs(
    schedule_id: Optional[str] = None,
    days: Optional[int] = Query(None, ge=1),
    current_user: User = Depends(AuthService().get_current_active_user)
) -> StandardResponse:
    """Clear execution logs with optional filtering."""
    try:
        schedule_service = ScheduleService()
        count = schedule_service.clear_execution_logs(schedule_id, days)
        return StandardResponse.success(
            message=f"Cleared {count} execution logs",
            data={"count": count}
        )
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.post("/start-scheduler")
async def start_scheduler(current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Start the scheduler."""
    try:
        schedule_service = ScheduleService()
        schedule_service.start_scheduler()
        return StandardResponse.success(message="Scheduler started successfully")
    except Exception as e:
        return StandardResponse.error(message=str(e))

@router.post("/stop-scheduler")
async def stop_scheduler(current_user: User = Depends(AuthService().get_current_active_user)) -> StandardResponse:
    """Stop the scheduler."""
    try:
        schedule_service = ScheduleService()
        schedule_service.stop_scheduler()
        return StandardResponse.success(message="Scheduler stopped successfully")
    except Exception as e:
        return StandardResponse.error(message=str(e))
