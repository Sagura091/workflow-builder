"""
Revolutionary Version Manager for Workflow Builder

This module provides a sophisticated version management system that enables:
1. Dynamic version resolution
2. Semantic versioning with feature flags
3. Automatic compatibility detection
4. Version-aware dependency injection
5. Time-travel debugging capabilities
"""

import importlib
import inspect
import logging
import re
import semver
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union, Callable
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class VersionedFeature(str, Enum):
    """Enum of features that can be versioned independently."""
    TYPE_SYSTEM = "type_system"
    CORE_NODES = "core_nodes"
    PLUGIN_SYSTEM = "plugin_system"
    WORKFLOW_ENGINE = "workflow_engine"
    API = "api"
    EXECUTION_ENGINE = "execution_engine"
    VALIDATION_SYSTEM = "validation_system"


class FeatureVersion(BaseModel):
    """Model representing a specific feature version."""
    feature: VersionedFeature
    version: str
    introduced_in: str
    deprecated_in: Optional[str] = None
    removed_in: Optional[str] = None

    def is_active(self, system_version: str) -> bool:
        """Check if this feature version is active in the given system version."""
        if semver.compare(system_version, self.introduced_in) < 0:
            return False
        if self.removed_in and semver.compare(system_version, self.removed_in) >= 0:
            return False
        return True

    def is_deprecated(self, system_version: str) -> bool:
        """Check if this feature version is deprecated in the given system version."""
        if not self.deprecated_in:
            return False
        return (semver.compare(system_version, self.deprecated_in) >= 0 and
                (not self.removed_in or semver.compare(system_version, self.removed_in) < 0))


class VersionCompatibility(BaseModel):
    """Model for version compatibility information."""
    source_version: str
    target_version: str
    compatible: bool
    upgrade_path: List[str] = Field(default_factory=list)
    breaking_changes: List[str] = Field(default_factory=list)

    @property
    def requires_migration(self) -> bool:
        """Check if migration is required between versions."""
        return len(self.upgrade_path) > 0 or len(self.breaking_changes) > 0


class VersionMetadata(BaseModel):
    """Metadata for a specific system version."""
    version: str
    release_date: str
    features: Dict[VersionedFeature, str]
    description: str
    breaking_changes: List[str] = Field(default_factory=list)
    deprecated_features: List[str] = Field(default_factory=list)
    new_features: List[str] = Field(default_factory=list)
    sunset_date: Optional[str] = None  # Date when this version will be removed


class VersionManager:
    """
    Revolutionary Version Manager for the Workflow Builder.

    This class manages component versions, compatibility, and provides
    version-aware dependency injection.
    """

    def __init__(self, config_file: Optional[str] = None):
        self.current_version = "0.1.0"  # Default starting version
        self.available_versions: List[str] = ["0.1.0"]
        self.feature_versions: Dict[VersionedFeature, List[FeatureVersion]] = {}
        self.version_metadata: Dict[str, VersionMetadata] = {}
        self.compatibility_matrix: Dict[str, Dict[str, VersionCompatibility]] = {}
        self.config_file = config_file or "version_config.json"

        # Initialize with default feature versions
        self._initialize_feature_versions()

        # Load saved version data if available
        self._load_version_data()

    def _initialize_feature_versions(self):
        """Initialize the feature versions with default values."""
        # Initial versions for all features
        initial_features = [
            FeatureVersion(
                feature=feature,
                version="0.1.0",
                introduced_in="0.1.0"
            ) for feature in VersionedFeature
        ]

        # Group by feature
        for feature_version in initial_features:
            if feature_version.feature not in self.feature_versions:
                self.feature_versions[feature_version.feature] = []
            self.feature_versions[feature_version.feature].append(feature_version)

    def register_version(self, version: str, metadata: VersionMetadata, save: bool = True):
        """
        Register a new system version with metadata.

        Args:
            version: The version string (e.g., "0.2.0")
            metadata: The version metadata
            save: Whether to save the version data to disk (default: True)
        """
        if version in self.version_metadata:
            logger.warning(f"Version {version} already registered, updating metadata")

        self.version_metadata[version] = metadata
        if version not in self.available_versions:
            self.available_versions.append(version)
            # Sort versions semantically
            self.available_versions.sort(key=lambda v: semver.VersionInfo.parse(v))

        # Save the version data if requested
        if save:
            self.save_version_data()

    def register_feature_version(self, feature_version: FeatureVersion, save: bool = True):
        """
        Register a new feature version.

        Args:
            feature_version: The feature version to register
            save: Whether to save the version data to disk (default: True)
        """
        if feature_version.feature not in self.feature_versions:
            self.feature_versions[feature_version.feature] = []

        # Check if this version already exists
        for existing in self.feature_versions[feature_version.feature]:
            if existing.version == feature_version.version:
                logger.warning(
                    f"Feature version {feature_version.feature}:{feature_version.version} "
                    f"already registered, updating"
                )
                # Remove the existing version
                self.feature_versions[feature_version.feature].remove(existing)
                break

        self.feature_versions[feature_version.feature].append(feature_version)
        # Sort by semantic version
        self.feature_versions[feature_version.feature].sort(
            key=lambda fv: semver.VersionInfo.parse(fv.version)
        )

        # Save the version data if requested
        if save:
            self.save_version_data()

    def get_feature_version(self,
                           feature: VersionedFeature,
                           system_version: Optional[str] = None) -> str:
        """
        Get the appropriate feature version for a given system version.

        Args:
            feature: The feature to get the version for
            system_version: The system version to check against (defaults to current)

        Returns:
            The appropriate feature version string
        """
        system_version = system_version or self.current_version

        if feature not in self.feature_versions:
            raise ValueError(f"Feature {feature} not registered")

        # Find the latest feature version that's active in the given system version
        active_versions = [
            fv for fv in self.feature_versions[feature]
            if fv.is_active(system_version)
        ]

        if not active_versions:
            raise ValueError(
                f"No active version of {feature} found for system version {system_version}"
            )

        # Return the latest active version
        return max(active_versions, key=lambda fv: semver.VersionInfo.parse(fv.version)).version

    def get_component(self,
                     feature: VersionedFeature,
                     component_name: str,
                     system_version: Optional[str] = None) -> Any:
        """
        Dynamically import and return the appropriate version of a component.

        This is the core of the version-aware dependency injection system.

        Args:
            feature: The feature area the component belongs to
            component_name: The name of the component to import
            system_version: The system version to use (defaults to current)

        Returns:
            The imported component (class, function, or module)
        """
        system_version = system_version or self.current_version
        feature_version = self.get_feature_version(feature, system_version)

        # Construct the import path
        import_path = f"backend.app.{feature.value}.v{feature_version.replace('.', '_')}.{component_name}"

        try:
            module = importlib.import_module(import_path)
            # If the component name is capitalized, assume it's a class
            if component_name[0].isupper() and hasattr(module, component_name):
                return getattr(module, component_name)
            return module
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import {import_path}: {e}")
            # Try fallback to the base module without version
            try:
                fallback_path = f"backend.app.{feature.value}.{component_name}"
                return importlib.import_module(fallback_path)
            except ImportError:
                raise ImportError(
                    f"Could not import {import_path} or fallback {fallback_path}"
                )

    def check_compatibility(self,
                           source_version: str,
                           target_version: str) -> VersionCompatibility:
        """
        Check compatibility between two system versions.

        Args:
            source_version: The source version
            target_version: The target version

        Returns:
            A VersionCompatibility object with compatibility information
        """
        # Check if we've already computed this
        if (source_version in self.compatibility_matrix and
            target_version in self.compatibility_matrix[source_version]):
            return self.compatibility_matrix[source_version][target_version]

        # If both versions are the same, they're compatible
        if source_version == target_version:
            return VersionCompatibility(
                source_version=source_version,
                target_version=target_version,
                compatible=True
            )

        # If either version is not registered, we can't determine compatibility
        if (source_version not in self.version_metadata or
            target_version not in self.version_metadata):
            return VersionCompatibility(
                source_version=source_version,
                target_version=target_version,
                compatible=False,
                breaking_changes=["Unknown version"]
            )

        # Check if we're downgrading
        if semver.compare(source_version, target_version) > 0:
            return VersionCompatibility(
                source_version=source_version,
                target_version=target_version,
                compatible=False,
                breaking_changes=["Downgrading not supported"]
            )

        # Collect all breaking changes between the versions
        breaking_changes = []
        upgrade_path = []

        # Find all versions between source and target
        versions_between = [
            v for v in self.available_versions
            if semver.compare(v, source_version) > 0 and semver.compare(v, target_version) <= 0
        ]

        for version in versions_between:
            metadata = self.version_metadata[version]
            if metadata.breaking_changes:
                breaking_changes.extend(metadata.breaking_changes)
            upgrade_path.append(version)

        # Determine compatibility
        compatible = len(breaking_changes) == 0

        # Create and cache the compatibility result
        result = VersionCompatibility(
            source_version=source_version,
            target_version=target_version,
            compatible=compatible,
            upgrade_path=upgrade_path,
            breaking_changes=breaking_changes
        )

        if source_version not in self.compatibility_matrix:
            self.compatibility_matrix[source_version] = {}
        self.compatibility_matrix[source_version][target_version] = result

        return result

    def set_current_version(self, version: str, save: bool = True):
        """
        Set the current system version.

        Args:
            version: The version to set as current
            save: Whether to save the version data to disk (default: True)
        """
        if version not in self.available_versions:
            raise ValueError(f"Version {version} is not registered")
        self.current_version = version
        logger.info(f"Current system version set to {version}")

        # Save the version data if requested
        if save:
            self.save_version_data()

    def get_latest_version(self) -> str:
        """Get the latest available system version."""
        if not self.available_versions:
            return self.current_version
        return self.available_versions[-1]  # Already sorted

    def get_version_metadata(self, version: str) -> VersionMetadata:
        """Get metadata for a specific version."""
        if version not in self.version_metadata:
            raise ValueError(f"Version {version} not registered")
        return self.version_metadata[version]

    def list_available_versions(self) -> List[str]:
        """List all available system versions."""
        return self.available_versions.copy()

    def get_sunset_date(self, version: str) -> Optional[str]:
        """
        Get the sunset date for a specific version.

        Args:
            version: The version to get the sunset date for

        Returns:
            The sunset date as a string, or None if no sunset date is set
        """
        if version not in self.version_metadata:
            return None

        return self.version_metadata[version].sunset_date

    def set_sunset_date(self, version: str, sunset_date: str, save: bool = True):
        """
        Set the sunset date for a specific version.

        Args:
            version: The version to set the sunset date for
            sunset_date: The sunset date as a string (ISO format recommended)
            save: Whether to save the version data to disk (default: True)
        """
        if version not in self.version_metadata:
            raise ValueError(f"Version {version} not registered")

        self.version_metadata[version].sunset_date = sunset_date
        logger.info(f"Set sunset date for version {version} to {sunset_date}")

        # Save the version data if requested
        if save:
            self.save_version_data()

    def get_deprecated_features(self, system_version: Optional[str] = None) -> List[Tuple[VersionedFeature, str]]:
        """Get a list of deprecated features in the given system version."""
        system_version = system_version or self.current_version
        deprecated = []

        for feature, versions in self.feature_versions.items():
            for version in versions:
                if version.is_deprecated(system_version):
                    deprecated.append((feature, version.version))

        return deprecated

    def _load_version_data(self):
        """Load version data from the config file."""
        import os
        import json

        if not os.path.exists(self.config_file):
            logger.info(f"Version config file {self.config_file} not found, using defaults")
            return

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)

            # Load current version
            if "current_version" in data:
                self.current_version = data["current_version"]

            # Load available versions
            if "available_versions" in data:
                self.available_versions = data["available_versions"]

            # Load version metadata
            if "version_metadata" in data:
                for version, metadata_dict in data["version_metadata"].items():
                    self.version_metadata[version] = VersionMetadata(**metadata_dict)

            # Load feature versions
            if "feature_versions" in data:
                for feature_name, versions in data["feature_versions"].items():
                    feature = VersionedFeature(feature_name)
                    if feature not in self.feature_versions:
                        self.feature_versions[feature] = []

                    for version_dict in versions:
                        version_dict["feature"] = feature
                        self.feature_versions[feature].append(FeatureVersion(**version_dict))

            logger.info(f"Loaded version data from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading version data: {e}")

    def save_version_data(self):
        """Save version data to the config file."""
        import json

        data = {
            "current_version": self.current_version,
            "available_versions": self.available_versions,
            "version_metadata": {},
            "feature_versions": {}
        }

        # Save version metadata
        for version, metadata in self.version_metadata.items():
            # Use model_dump instead of dict (which is deprecated)
            data["version_metadata"][version] = metadata.model_dump()

        # Save feature versions
        for feature, versions in self.feature_versions.items():
            feature_name = feature.value
            if feature_name not in data["feature_versions"]:
                data["feature_versions"][feature_name] = []

            for version in versions:
                # Use model_dump instead of dict (which is deprecated)
                version_dict = version.model_dump()
                # Remove the feature field since it's already the key
                version_dict.pop("feature")
                data["feature_versions"][feature_name].append(version_dict)

        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved version data to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving version data: {e}")

    def version_decorator(self,
                         feature: VersionedFeature,
                         introduced_in: str,
                         deprecated_in: Optional[str] = None,
                         removed_in: Optional[str] = None):
        """
        Decorator to mark a function or class with version information.

        Example:
            @version_manager.version_decorator(
                feature=VersionedFeature.API,
                introduced_in="0.2.0",
                deprecated_in="0.3.0"
            )
            def my_api_function():
                pass
        """
        def decorator(func_or_class):
            # Add version metadata to the function or class
            func_or_class.__version_info__ = {
                "feature": feature,
                "introduced_in": introduced_in,
                "deprecated_in": deprecated_in,
                "removed_in": removed_in
            }

            # For functions, we can add a wrapper to check version compatibility
            if inspect.isfunction(func_or_class):
                original_func = func_or_class

                def wrapper(*args, **kwargs):
                    # Check if this function is available in the current version
                    if semver.compare(self.current_version, introduced_in) < 0:
                        raise NotImplementedError(
                            f"Function {original_func.__name__} is not available in version {self.current_version}"
                        )

                    if removed_in and semver.compare(self.current_version, removed_in) >= 0:
                        raise NotImplementedError(
                            f"Function {original_func.__name__} was removed in version {removed_in}"
                        )

                    if deprecated_in and semver.compare(self.current_version, deprecated_in) >= 0:
                        logger.warning(
                            f"Function {original_func.__name__} is deprecated since version {deprecated_in}"
                        )

                    return original_func(*args, **kwargs)

                # Copy metadata from the original function
                wrapper.__name__ = original_func.__name__
                wrapper.__doc__ = original_func.__doc__
                wrapper.__module__ = original_func.__module__
                wrapper.__version_info__ = original_func.__version_info__

                return wrapper

            # For classes, we return the original class with metadata
            return func_or_class

        return decorator


# Create a singleton instance
version_manager = VersionManager()
