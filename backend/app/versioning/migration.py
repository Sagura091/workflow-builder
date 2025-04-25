"""
Version Migration Utilities

This module provides utilities for migrating workflows and components
between different versions.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from .version_manager import version_manager

logger = logging.getLogger(__name__)


class MigrationStep(BaseModel):
    """Model for a single migration step."""
    source_version: str
    target_version: str
    description: str
    breaking: bool = False
    
    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply this migration step to the data.
        
        This method should be overridden by subclasses.
        
        Args:
            data: The data to migrate
            
        Returns:
            The migrated data
        """
        # Default implementation just returns the data unchanged
        return data


class WorkflowMigrationStep(MigrationStep):
    """Migration step for workflows."""
    component_type: str = "workflow"


class NodeMigrationStep(MigrationStep):
    """Migration step for nodes."""
    component_type: str = "node"
    node_type: str


class TypeMigrationStep(MigrationStep):
    """Migration step for types."""
    component_type: str = "type"
    type_id: str


class MigrationPlan(BaseModel):
    """Model for a migration plan."""
    source_version: str
    target_version: str
    steps: List[MigrationStep] = Field(default_factory=list)
    
    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all migration steps to the data.
        
        Args:
            data: The data to migrate
            
        Returns:
            The migrated data
        """
        result = data.copy()
        
        for step in self.steps:
            try:
                result = step.apply(result)
                logger.info(
                    f"Applied migration step from {step.source_version} to {step.target_version}: {step.description}"
                )
            except Exception as e:
                logger.error(f"Error applying migration step: {e}")
                if step.breaking:
                    raise ValueError(
                        f"Failed to apply breaking migration step: {step.description}"
                    ) from e
        
        return result


class MigrationRegistry:
    """
    Registry for migration steps.
    
    This registry manages migration steps and provides utilities for
    creating migration plans.
    """
    
    def __init__(self):
        self.steps: List[MigrationStep] = []
    
    def register_step(self, step: MigrationStep):
        """Register a migration step."""
        self.steps.append(step)
        logger.info(
            f"Registered migration step from {step.source_version} to {step.target_version}: {step.description}"
        )
    
    def create_migration_plan(self, 
                             source_version: str, 
                             target_version: str) -> MigrationPlan:
        """
        Create a migration plan from source to target version.
        
        Args:
            source_version: The source version
            target_version: The target version
            
        Returns:
            A migration plan with all necessary steps
        """
        # Check compatibility
        compatibility = version_manager.check_compatibility(source_version, target_version)
        if not compatibility.compatible and not compatibility.upgrade_path:
            raise ValueError(
                f"Cannot create migration plan from {source_version} to {target_version}: "
                f"Versions are incompatible and no upgrade path exists"
            )
        
        # Create the plan
        plan = MigrationPlan(
            source_version=source_version,
            target_version=target_version
        )
        
        # If versions are the same, return empty plan
        if source_version == target_version:
            return plan
        
        # Find all steps that apply to this migration
        applicable_steps = []
        
        # If we have an upgrade path, use it
        if compatibility.upgrade_path:
            # Add source version to the beginning
            versions = [source_version] + compatibility.upgrade_path
            
            # For each version transition, find applicable steps
            for i in range(len(versions) - 1):
                from_version = versions[i]
                to_version = versions[i + 1]
                
                for step in self.steps:
                    if step.source_version == from_version and step.target_version == to_version:
                        applicable_steps.append(step)
        else:
            # Direct migration
            for step in self.steps:
                if step.source_version == source_version and step.target_version == target_version:
                    applicable_steps.append(step)
        
        # Add steps to the plan
        plan.steps = applicable_steps
        
        return plan
    
    def migrate_workflow(self, 
                        workflow: Dict[str, Any], 
                        source_version: str,
                        target_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Migrate a workflow from source to target version.
        
        Args:
            workflow: The workflow data to migrate
            source_version: The source version
            target_version: The target version (defaults to current)
            
        Returns:
            The migrated workflow
        """
        target_version = target_version or version_manager.current_version
        
        # Create migration plan
        plan = self.create_migration_plan(source_version, target_version)
        
        # Apply the plan
        migrated_workflow = plan.apply(workflow)
        
        # Update version information
        if "version" in migrated_workflow:
            migrated_workflow["version"] = target_version
        else:
            migrated_workflow["version"] = target_version
        
        return migrated_workflow
    
    def discover_migrations(self, base_path: str = "backend/app/migrations"):
        """
        Discover and register migration steps from the filesystem.
        
        This method scans the migrations directory for migration steps
        and registers them.
        
        Args:
            base_path: Base path to scan for migrations
        """
        import os
        import importlib
        
        # Normalize path
        base_path = os.path.normpath(base_path)
        
        # Check if the directory exists
        if not os.path.exists(base_path):
            logger.warning(f"Migrations directory {base_path} does not exist")
            return
        
        # Walk through the directory structure
        for root, dirs, files in os.walk(base_path):
            # Skip __pycache__ directories
            if "__pycache__" in root:
                continue
            
            # Look for migration files
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    # Import the module
                    relative_path = os.path.relpath(root, os.path.dirname(base_path))
                    module_name = os.path.splitext(file)[0]
                    module_path = f"backend.app.migrations.{relative_path.replace(os.path.sep, '.')}.{module_name}"
                    
                    try:
                        module = importlib.import_module(module_path)
                        
                        # Look for MIGRATION_STEPS list
                        if hasattr(module, "MIGRATION_STEPS"):
                            for step in module.MIGRATION_STEPS:
                                self.register_step(step)
                    except Exception as e:
                        logger.error(f"Error importing {module_path}: {e}")


# Create singleton instance
migration_registry = MigrationRegistry()
