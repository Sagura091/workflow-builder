import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.models.template import WorkflowTemplate, TemplateCategory, TemplateDifficulty

class TemplateService:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self):
        """Ensure the templates directory exists."""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def get_all_templates(self) -> List[WorkflowTemplate]:
        """Get all templates."""
        templates = []
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                template_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(template_path, "r") as f:
                        template_data = json.load(f)
                        # Convert to WorkflowTemplate
                        template = WorkflowTemplate(
                            id=template_data.get("id", filename[:-5]),
                            name=template_data.get("name", "Unnamed Template"),
                            description=template_data.get("description", ""),
                            category=template_data.get("category", TemplateCategory.OTHER),
                            difficulty=template_data.get("difficulty", TemplateDifficulty.INTERMEDIATE),
                            tags=template_data.get("tags", []),
                            preview_image_url=template_data.get("preview_image_url"),
                            workflow=template_data.get("workflow", {}),
                            created_by=template_data.get("created_by", "system"),
                            created_at=datetime.fromisoformat(template_data.get("created_at", datetime.now().isoformat())),
                            updated_at=datetime.fromisoformat(template_data.get("updated_at")) if template_data.get("updated_at") else None,
                            usage_count=template_data.get("usage_count", 0)
                        )
                        templates.append(template)
                except Exception as e:
                    print(f"Error loading template {filename}: {str(e)}")
        
        return templates
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a template by ID."""
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        
        if not os.path.exists(template_path):
            return None
        
        try:
            with open(template_path, "r") as f:
                template_data = json.load(f)
                # Convert to WorkflowTemplate
                return WorkflowTemplate(
                    id=template_data.get("id", template_id),
                    name=template_data.get("name", "Unnamed Template"),
                    description=template_data.get("description", ""),
                    category=template_data.get("category", TemplateCategory.OTHER),
                    difficulty=template_data.get("difficulty", TemplateDifficulty.INTERMEDIATE),
                    tags=template_data.get("tags", []),
                    preview_image_url=template_data.get("preview_image_url"),
                    workflow=template_data.get("workflow", {}),
                    created_by=template_data.get("created_by", "system"),
                    created_at=datetime.fromisoformat(template_data.get("created_at", datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(template_data.get("updated_at")) if template_data.get("updated_at") else None,
                    usage_count=template_data.get("usage_count", 0)
                )
        except Exception as e:
            print(f"Error loading template {template_id}: {str(e)}")
            return None
    
    def create_template(self, template: Dict[str, Any]) -> WorkflowTemplate:
        """Create a new template."""
        # Generate ID if not provided
        template_id = template.get("id", str(uuid.uuid4()))
        
        # Create template object
        template_obj = WorkflowTemplate(
            id=template_id,
            name=template.get("name", "Unnamed Template"),
            description=template.get("description", ""),
            category=template.get("category", TemplateCategory.OTHER),
            difficulty=template.get("difficulty", TemplateDifficulty.INTERMEDIATE),
            tags=template.get("tags", []),
            preview_image_url=template.get("preview_image_url"),
            workflow=template.get("workflow", {}),
            created_by=template.get("created_by", "system"),
            created_at=datetime.now(),
            usage_count=0
        )
        
        # Save template
        self._save_template(template_obj)
        
        return template_obj
    
    def update_template(self, template_id: str, template: Dict[str, Any]) -> Optional[WorkflowTemplate]:
        """Update an existing template."""
        existing_template = self.get_template(template_id)
        
        if not existing_template:
            return None
        
        # Update template
        updated_template = WorkflowTemplate(
            id=template_id,
            name=template.get("name", existing_template.name),
            description=template.get("description", existing_template.description),
            category=template.get("category", existing_template.category),
            difficulty=template.get("difficulty", existing_template.difficulty),
            tags=template.get("tags", existing_template.tags),
            preview_image_url=template.get("preview_image_url", existing_template.preview_image_url),
            workflow=template.get("workflow", existing_template.workflow),
            created_by=existing_template.created_by,
            created_at=existing_template.created_at,
            updated_at=datetime.now(),
            usage_count=existing_template.usage_count
        )
        
        # Save template
        self._save_template(updated_template)
        
        return updated_template
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        
        if not os.path.exists(template_path):
            return False
        
        try:
            os.remove(template_path)
            return True
        except Exception as e:
            print(f"Error deleting template {template_id}: {str(e)}")
            return False
    
    def increment_usage_count(self, template_id: str) -> bool:
        """Increment the usage count of a template."""
        template = self.get_template(template_id)
        
        if not template:
            return False
        
        # Increment usage count
        template.usage_count += 1
        
        # Save template
        self._save_template(template)
        
        return True
    
    def _save_template(self, template: WorkflowTemplate) -> None:
        """Save a template to disk."""
        template_path = os.path.join(self.templates_dir, f"{template.id}.json")
        
        # Convert to dict
        template_dict = template.dict()
        
        # Convert datetime objects to ISO format
        template_dict["created_at"] = template_dict["created_at"].isoformat()
        if template_dict["updated_at"]:
            template_dict["updated_at"] = template_dict["updated_at"].isoformat()
        
        # Save to file
        with open(template_path, "w") as f:
            json.dump(template_dict, f, indent=2)
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[WorkflowTemplate]:
        """Get templates by category."""
        templates = self.get_all_templates()
        return [t for t in templates if t.category == category]
    
    def get_templates_by_difficulty(self, difficulty: TemplateDifficulty) -> List[WorkflowTemplate]:
        """Get templates by difficulty."""
        templates = self.get_all_templates()
        return [t for t in templates if t.difficulty == difficulty]
    
    def get_templates_by_tags(self, tags: List[str]) -> List[WorkflowTemplate]:
        """Get templates by tags."""
        templates = self.get_all_templates()
        return [t for t in templates if any(tag in t.tags for tag in tags)]
    
    def search_templates(self, query: str) -> List[WorkflowTemplate]:
        """Search templates by name or description."""
        templates = self.get_all_templates()
        query = query.lower()
        return [t for t in templates if query in t.name.lower() or query in t.description.lower()]
    
    def recommend_templates(self, user_history: Optional[Dict[str, Any]] = None) -> List[WorkflowTemplate]:
        """Recommend templates based on user history."""
        templates = self.get_all_templates()
        
        # Sort by usage count (most popular first)
        templates.sort(key=lambda t: t.usage_count, reverse=True)
        
        # If user history is provided, we could implement more sophisticated recommendations
        if user_history:
            # This is a placeholder for more sophisticated recommendation logic
            pass
        
        return templates[:5]  # Return top 5 templates
