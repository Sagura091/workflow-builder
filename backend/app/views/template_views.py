from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional

from backend.app.controllers.template_controller import TemplateController
from backend.app.dependencies import get_template_controller

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.get("/")
async def get_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = None,
    controller: TemplateController = Depends(get_template_controller)
) -> Dict[str, Any]:
    """
    Get all templates with optional filtering.
    
    Args:
        category: Filter by category
        difficulty: Filter by difficulty
        tags: Filter by tags
        search: Search by name or description
        
    Returns:
        List of templates
    """
    templates = controller.get_all_templates(category, difficulty, tags, search)
    return {"templates": templates}

@router.get("/recommend")
async def recommend_templates(
    controller: TemplateController = Depends(get_template_controller)
) -> Dict[str, Any]:
    """
    Recommend templates based on user history.
    
    Returns:
        List of recommended templates
    """
    templates = controller.recommend_templates()
    return {"templates": templates}

@router.get("/{template_id}")
async def get_template(
    template_id: str,
    controller: TemplateController = Depends(get_template_controller)
) -> Dict[str, Any]:
    """
    Get a template by ID.
    
    Args:
        template_id: Template ID
        
    Returns:
        Template data
    """
    template = controller.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    return template

@router.post("/")
async def create_template(
    template: Dict[str, Any],
    controller: TemplateController = Depends(get_template_controller)
) -> Dict[str, Any]:
    """
    Create a new template.
    
    Args:
        template: Template data
        
    Returns:
        Created template
    """
    return controller.create_template(template)

@router.put("/{template_id}")
async def update_template(
    template_id: str,
    template: Dict[str, Any],
    controller: TemplateController = Depends(get_template_controller)
) -> Dict[str, Any]:
    """
    Update an existing template.
    
    Args:
        template_id: Template ID
        template: Template data
        
    Returns:
        Updated template
    """
    updated_template = controller.update_template(template_id, template)
    
    if not updated_template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    return updated_template

@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    controller: TemplateController = Depends(get_template_controller)
) -> Dict[str, Any]:
    """
    Delete a template.
    
    Args:
        template_id: Template ID
        
    Returns:
        Success message
    """
    success = controller.delete_template(template_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    
    return {"message": f"Template '{template_id}' deleted successfully"}
