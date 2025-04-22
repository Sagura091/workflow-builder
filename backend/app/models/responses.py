"""
Standard API response models.

This module provides standardized response models for API endpoints.
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic, Union
from pydantic import BaseModel, Field
import datetime
import uuid

T = TypeVar('T')

class ErrorDetail(BaseModel):
    """Error detail model."""
    field: Optional[str] = None
    code: str
    message: str
    context: Optional[Dict[str, Any]] = None

class PaginationMetadata(BaseModel):
    """Pagination metadata."""
    total: int
    page: int
    page_size: int
    total_pages: int

class ResponseMetadata(BaseModel):
    """Response metadata."""
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    pagination: Optional[PaginationMetadata] = None
    execution_time_ms: Optional[float] = None

class StandardResponse(BaseModel, Generic[T]):
    """Standard API response model."""
    status: str = Field(..., description="Response status: 'success' or 'error'")
    data: Optional[T] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Error details")
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)

    @classmethod
    def success(cls, data: Any = None, message: Optional[str] = None,
               pagination: Optional[Dict[str, int]] = None,
               execution_time_ms: Optional[float] = None) -> 'StandardResponse':
        """Create a success response."""
        metadata = ResponseMetadata()
        if pagination:
            metadata.pagination = PaginationMetadata(**pagination)
        if execution_time_ms is not None:
            metadata.execution_time_ms = execution_time_ms

        return cls(status="success", data=data, message=message, metadata=metadata)

    @classmethod
    def error(cls, message: str, errors: Optional[List[ErrorDetail]] = None,
              execution_time_ms: Optional[float] = None) -> 'StandardResponse':
        """Create an error response."""
        metadata = ResponseMetadata()
        if execution_time_ms is not None:
            metadata.execution_time_ms = execution_time_ms

        return cls(status="error", message=message, errors=errors, metadata=metadata)

    @classmethod
    def paginated(cls, data: Any, total: int, page: int, page_size: int,
                 message: Optional[str] = None,
                 execution_time_ms: Optional[float] = None) -> 'StandardResponse':
        """Create a paginated success response."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        pagination = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
        return cls.success(data=data, message=message, pagination=pagination,
                          execution_time_ms=execution_time_ms)
