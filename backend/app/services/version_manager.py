"""
Version Manager

This module provides a service for managing different versions of components
in the workflow builder, allowing for backward compatibility while
encouraging migration to enhanced versions.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum

# Configure logger
logger = logging.getLogger("workflow_builder")


class ComponentType(str, Enum):
    """Types of components that can be versioned."""
    CORE_NODE = "core_node"
    PLUGIN = "plugin"
    SERVICE = "service"
    CONTROLLER = "controller"
    MODEL = "model"


class VersionManager:
    """
    Service for managing component versions.
    
    This service allows the system to maintain backward compatibility
    while providing enhanced versions of components.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super(VersionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the version manager."""
        if self._initialized:
            return
        
        # Version mappings
        self.legacy_to_enhanced: Dict[str, Dict[str, str]] = {
            ComponentType.CORE_NODE: {},
            ComponentType.PLUGIN: {},
            ComponentType.SERVICE: {},
            ComponentType.CONTROLLER: {},
            ComponentType.MODEL: {}
        }
        
        # Component preferences
        self.component_preferences: Dict[str, Dict[str, str]] = {
            ComponentType.CORE_NODE: {},
            ComponentType.PLUGIN: {},
            ComponentType.SERVICE: {},
            ComponentType.CONTROLLER: {},
            ComponentType.MODEL: {}
        }
        
        # Default preferences
        self.default_preferences: Dict[str, str] = {
            ComponentType.CORE_NODE: "enhanced",
            ComponentType.PLUGIN: "enhanced",
            ComponentType.SERVICE: "enhanced",
            ComponentType.CONTROLLER: "enhanced",
            ComponentType.MODEL: "enhanced"
        }
        
        # Load configuration
        self._load_config()
        
        self._initialized = True
        logger.info("Version manager initialized")
    
    def _load_config(self) -> None:
        """Load version configuration from file."""
        try:
            # Get the path to the backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(backend_dir, "config", "version_config.json")
            
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                
                # Load mappings
                if "mappings" in config:
                    for component_type, mappings in config["mappings"].items():
                        if component_type in self.legacy_to_enhanced:
                            self.legacy_to_enhanced[component_type] = mappings
                
                # Load preferences
                if "preferences" in config:
                    for component_type, preferences in config["preferences"].items():
                        if component_type in self.component_preferences:
                            self.component_preferences[component_type] = preferences
                
                # Load default preferences
                if "default_preferences" in config:
                    for component_type, preference in config["default_preferences"].items():
                        if component_type in self.default_preferences:
                            self.default_preferences[component_type] = preference
                
                logger.info(f"Loaded version configuration from {config_path}")
            else:
                # Create default mappings
                self._create_default_mappings()
                
                # Save configuration
                self._save_config()
                
                logger.info(f"Created default version configuration at {config_path}")
        except Exception as e:
            logger.error(f"Error loading version configuration: {str(e)}")
            
            # Create default mappings
            self._create_default_mappings()
    
    def _save_config(self) -> None:
        """Save version configuration to file."""
        try:
            # Get the path to the backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_dir = os.path.join(backend_dir, "config")
            
            # Create config directory if it doesn't exist
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            config_path = os.path.join(config_dir, "version_config.json")
            
            # Create configuration
            config = {
                "mappings": self.legacy_to_enhanced,
                "preferences": self.component_preferences,
                "default_preferences": self.default_preferences
            }
            
            # Save configuration
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Saved version configuration to {config_path}")
        except Exception as e:
            logger.error(f"Error saving version configuration: {str(e)}")
    
    def _create_default_mappings(self) -> None:
        """Create default mappings for core nodes and other components."""
        # Core node mappings
        self.legacy_to_enhanced[ComponentType.CORE_NODE] = {
            "core.begin": "core.enhanced_begin",
            "core.end": "core.enhanced_end",
            "core.conditional": "core.enhanced_conditional",
            "core.loop": "core.enhanced_loop",
            "core.variable": "core.enhanced_variable"
        }
        
        # Service mappings
        self.legacy_to_enhanced[ComponentType.SERVICE] = {
            "plugin_manager": "enhanced_plugin_manager",
            "core_node_registry": "enhanced_core_node_registry"
        }
    
    def register_mapping(self, component_type: str, legacy_id: str, enhanced_id: str) -> None:
        """
        Register a mapping between legacy and enhanced components.
        
        Args:
            component_type: The type of component
            legacy_id: The ID of the legacy component
            enhanced_id: The ID of the enhanced component
        """
        if component_type not in self.legacy_to_enhanced:
            logger.warning(f"Unknown component type: {component_type}")
            return
        
        self.legacy_to_enhanced[component_type][legacy_id] = enhanced_id
        logger.debug(f"Registered mapping: {legacy_id} -> {enhanced_id} ({component_type})")
        
        # Save configuration
        self._save_config()
    
    def get_enhanced_id(self, component_type: str, legacy_id: str) -> Optional[str]:
        """
        Get the enhanced component ID for a legacy component.
        
        Args:
            component_type: The type of component
            legacy_id: The ID of the legacy component
            
        Returns:
            The ID of the enhanced component, or None if not found
        """
        if component_type not in self.legacy_to_enhanced:
            return None
        
        return self.legacy_to_enhanced[component_type].get(legacy_id)
    
    def get_legacy_id(self, component_type: str, enhanced_id: str) -> Optional[str]:
        """
        Get the legacy component ID for an enhanced component.
        
        Args:
            component_type: The type of component
            enhanced_id: The ID of the enhanced component
            
        Returns:
            The ID of the legacy component, or None if not found
        """
        if component_type not in self.legacy_to_enhanced:
            return None
        
        for legacy_id, mapped_enhanced_id in self.legacy_to_enhanced[component_type].items():
            if mapped_enhanced_id == enhanced_id:
                return legacy_id
        
        return None
    
    def set_preference(self, component_type: str, component_id: str, preference: str) -> None:
        """
        Set the preference for a component.
        
        Args:
            component_type: The type of component
            component_id: The ID of the component
            preference: The preference ("legacy" or "enhanced")
        """
        if component_type not in self.component_preferences:
            logger.warning(f"Unknown component type: {component_type}")
            return
        
        if preference not in ["legacy", "enhanced"]:
            logger.warning(f"Invalid preference: {preference}")
            return
        
        self.component_preferences[component_type][component_id] = preference
        logger.debug(f"Set preference for {component_id} ({component_type}): {preference}")
        
        # Save configuration
        self._save_config()
    
    def get_preference(self, component_type: str, component_id: str) -> str:
        """
        Get the preference for a component.
        
        Args:
            component_type: The type of component
            component_id: The ID of the component
            
        Returns:
            The preference ("legacy" or "enhanced")
        """
        if component_type not in self.component_preferences:
            return self.default_preferences.get(component_type, "enhanced")
        
        return self.component_preferences[component_type].get(
            component_id, 
            self.default_preferences.get(component_type, "enhanced")
        )
    
    def set_default_preference(self, component_type: str, preference: str) -> None:
        """
        Set the default preference for a component type.
        
        Args:
            component_type: The type of component
            preference: The preference ("legacy" or "enhanced")
        """
        if component_type not in self.default_preferences:
            logger.warning(f"Unknown component type: {component_type}")
            return
        
        if preference not in ["legacy", "enhanced"]:
            logger.warning(f"Invalid preference: {preference}")
            return
        
        self.default_preferences[component_type] = preference
        logger.debug(f"Set default preference for {component_type}: {preference}")
        
        # Save configuration
        self._save_config()
    
    def get_default_preference(self, component_type: str) -> str:
        """
        Get the default preference for a component type.
        
        Args:
            component_type: The type of component
            
        Returns:
            The preference ("legacy" or "enhanced")
        """
        return self.default_preferences.get(component_type, "enhanced")
    
    def get_component_id(self, component_type: str, component_id: str) -> str:
        """
        Get the appropriate component ID based on preferences.
        
        This method determines whether to use the legacy or enhanced version
        of a component based on the configured preferences.
        
        Args:
            component_type: The type of component
            component_id: The ID of the component (either legacy or enhanced)
            
        Returns:
            The appropriate component ID to use
        """
        # Check if this is a legacy ID with an enhanced version
        enhanced_id = self.get_enhanced_id(component_type, component_id)
        
        if enhanced_id:
            # This is a legacy ID
            preference = self.get_preference(component_type, component_id)
            return enhanced_id if preference == "enhanced" else component_id
        
        # Check if this is an enhanced ID with a legacy version
        legacy_id = self.get_legacy_id(component_type, component_id)
        
        if legacy_id:
            # This is an enhanced ID
            preference = self.get_preference(component_type, legacy_id)
            return component_id if preference == "enhanced" else legacy_id
        
        # No mapping found, return the original ID
        return component_id
    
    def get_all_mappings(self, component_type: str) -> Dict[str, str]:
        """
        Get all mappings for a component type.
        
        Args:
            component_type: The type of component
            
        Returns:
            Dictionary of legacy to enhanced mappings
        """
        if component_type not in self.legacy_to_enhanced:
            return {}
        
        return self.legacy_to_enhanced[component_type].copy()
    
    def get_all_preferences(self, component_type: str) -> Dict[str, str]:
        """
        Get all preferences for a component type.
        
        Args:
            component_type: The type of component
            
        Returns:
            Dictionary of component preferences
        """
        if component_type not in self.component_preferences:
            return {}
        
        return self.component_preferences[component_type].copy()
