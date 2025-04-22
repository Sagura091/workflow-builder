from typing import Dict, Any, List, Optional
from backend.app.services.template_service import TemplateService
from backend.app.models.template import WorkflowTemplate, TemplateCategory, TemplateDifficulty

class TemplateController:
    def __init__(self, template_service: TemplateService):
        self.template_service = template_service
    
    def get_all_templates(self, 
                         category: Optional[str] = None,
                         difficulty: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         search: Optional[str] = None) -> List[Dict[str, Any]]:
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
        # Get all templates
        templates = self.template_service.get_all_templates()
        
        # Apply filters
        if category:
            try:
                category_enum = TemplateCategory(category)
                templates = [t for t in templates if t.category == category_enum]
            except ValueError:
                # Invalid category, ignore filter
                pass
        
        if difficulty:
            try:
                difficulty_enum = TemplateDifficulty(difficulty)
                templates = [t for t in templates if t.difficulty == difficulty_enum]
            except ValueError:
                # Invalid difficulty, ignore filter
                pass
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        if search:
            search = search.lower()
            templates = [t for t in templates if search in t.name.lower() or search in t.description.lower()]
        
        # Format templates for API response
        return [self._format_template_summary(t) for t in templates]
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template data or None if not found
        """
        template = self.template_service.get_template(template_id)
        
        if not template:
            return None
        
        # Increment usage count
        self.template_service.increment_usage_count(template_id)
        
        # Format template for API response
        return self._format_template_detail(template)
    
    def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new template.
        
        Args:
            template_data: Template data
            
        Returns:
            Created template
        """
        template = self.template_service.create_template(template_data)
        return self._format_template_detail(template)
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing template.
        
        Args:
            template_id: Template ID
            template_data: Template data
            
        Returns:
            Updated template or None if not found
        """
        template = self.template_service.update_template(template_id, template_data)
        
        if not template:
            return None
        
        return self._format_template_detail(template)
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.template_service.delete_template(template_id)
    
    def recommend_templates(self, user_history: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Recommend templates based on user history.
        
        Args:
            user_history: Optional user history data
            
        Returns:
            List of recommended templates
        """
        templates = self.template_service.recommend_templates(user_history)
        return [self._format_template_summary(t) for t in templates]
    
    def _format_template_summary(self, template: WorkflowTemplate) -> Dict[str, Any]:
        """Format template for summary API response."""
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "difficulty": template.difficulty,
            "tags": template.tags,
            "preview_image_url": template.preview_image_url,
            "created_by": template.created_by,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            "usage_count": template.usage_count,
            "node_count": len(template.workflow.get("nodes", [])),
            "connection_count": len(template.workflow.get("connections", []))
        }
    
    def _format_template_detail(self, template: WorkflowTemplate) -> Dict[str, Any]:
        """Format template for detailed API response."""
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "difficulty": template.difficulty,
            "tags": template.tags,
            "preview_image_url": template.preview_image_url,
            "workflow": template.workflow,
            "created_by": template.created_by,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            "usage_count": template.usage_count
        }
