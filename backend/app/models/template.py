from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TemplateDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class TemplateCategory(str, Enum):
    DATA_PROCESSING = "data_processing"
    MACHINE_LEARNING = "machine_learning"
    TEXT_ANALYSIS = "text_analysis"
    IMAGE_PROCESSING = "image_processing"
    VISUALIZATION = "visualization"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    OTHER = "other"

class WorkflowTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: TemplateCategory
    difficulty: TemplateDifficulty
    tags: List[str] = Field(default_factory=list)
    preview_image_url: Optional[str] = None
    workflow: Dict[str, Any]
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    usage_count: int = 0
