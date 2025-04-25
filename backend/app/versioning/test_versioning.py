"""
Test Script for Versioning System

This script tests the versioning system by registering versions,
creating components, and checking compatibility.
"""

import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def test_version_manager():
    """Test the version manager functionality."""
    from backend.app.versioning import (
        version_manager,
        VersionedFeature,
        VersionMetadata
    )
    
    logger.info("Testing Version Manager...")
    
    # Register a new version
    version_manager.register_version(
        "0.2.0",
        VersionMetadata(
            version="0.2.0",
            release_date="2023-02-01",
            features={
                VersionedFeature.TYPE_SYSTEM: "0.2.0",
                VersionedFeature.CORE_NODES: "0.2.0",
                VersionedFeature.PLUGIN_SYSTEM: "0.1.0",
                VersionedFeature.WORKFLOW_ENGINE: "0.2.0",
                VersionedFeature.API: "0.2.0",
                VersionedFeature.EXECUTION_ENGINE: "0.2.0",
                VersionedFeature.VALIDATION_SYSTEM: "0.1.0"
            },
            description="Enhanced version with improved type system and core nodes",
            new_features=["Enhanced type system", "Additional core nodes"],
            deprecated_features=["Legacy validation system"]
        )
    )
    
    # Check available versions
    versions = version_manager.list_available_versions()
    logger.info(f"Available versions: {versions}")
    
    # Check feature versions
    for feature in VersionedFeature:
        version = version_manager.get_feature_version(feature, "0.2.0")
        logger.info(f"Feature {feature.value} version in 0.2.0: {version}")
    
    # Check compatibility
    compatibility = version_manager.check_compatibility("0.1.0", "0.2.0")
    logger.info(f"Compatibility from 0.1.0 to 0.2.0: {compatibility.compatible}")
    logger.info(f"Upgrade path: {compatibility.upgrade_path}")
    
    logger.info("Version Manager tests completed successfully")

def test_core_node_registry():
    """Test the core node registry functionality."""
    from backend.app.versioning import (
        core_node_registry,
        VersionedCoreNode
    )
    
    logger.info("Testing Core Node Registry...")
    
    # Register a test node
    test_node = VersionedCoreNode(
        id="test.node",
        name="Test Node",
        version="0.2.0",
        introduced_in="0.2.0",
        category="Test",
        description="A test node",
        inputs={"input": "string"},
        outputs={"output": "string"},
        config_schema={}
    )
    
    core_node_registry.register_node(test_node)
    
    # Get the node
    retrieved_node = core_node_registry.get_node("test.node", system_version="0.2.0")
    logger.info(f"Retrieved node: {retrieved_node.name} (version {retrieved_node.version})")
    
    # List nodes
    nodes = core_node_registry.list_nodes(system_version="0.2.0")
    logger.info(f"Found {len(nodes)} nodes in version 0.2.0")
    
    # List categories
    categories = core_node_registry.list_categories(system_version="0.2.0")
    logger.info(f"Categories in version 0.2.0: {categories}")
    
    logger.info("Core Node Registry tests completed successfully")

def test_type_registry():
    """Test the type registry functionality."""
    from backend.app.versioning import (
        type_registry,
        VersionedType
    )
    
    logger.info("Testing Type Registry...")
    
    # Register a test type
    test_type = VersionedType(
        id="test.type",
        name="Test Type",
        version="0.2.0",
        introduced_in="0.2.0",
        base_type="string",
        validators=[],
        converters={}
    )
    
    type_registry.register_type(test_type)
    
    # Get the type
    retrieved_type = type_registry.get_type("test.type", system_version="0.2.0")
    logger.info(f"Retrieved type: {retrieved_type.name} (version {retrieved_type.version})")
    
    # List types
    types = type_registry.list_types(system_version="0.2.0")
    logger.info(f"Found {len(types)} types in version 0.2.0")
    
    logger.info("Type Registry tests completed successfully")

def test_migration_registry():
    """Test the migration registry functionality."""
    from backend.app.versioning.migration import (
        migration_registry,
        WorkflowMigrationStep
    )
    
    logger.info("Testing Migration Registry...")
    
    # Create a test migration step
    class TestMigrationStep(WorkflowMigrationStep):
        def __init__(self):
            super().__init__(
                source_version="0.1.0",
                target_version="0.2.0",
                description="Test migration step",
                breaking=False
            )
        
        def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
            result = data.copy()
            result["migrated"] = True
            return result
    
    # Register the migration step
    migration_registry.register_step(TestMigrationStep())
    
    # Create a migration plan
    plan = migration_registry.create_migration_plan("0.1.0", "0.2.0")
    logger.info(f"Migration plan has {len(plan.steps)} steps")
    
    # Apply the migration
    test_data = {"version": "0.1.0", "data": "test"}
    migrated_data = migration_registry.migrate_workflow(test_data, "0.1.0", "0.2.0")
    logger.info(f"Migrated data: {migrated_data}")
    
    logger.info("Migration Registry tests completed successfully")

def run_all_tests():
    """Run all versioning system tests."""
    logger.info("Starting versioning system tests...")
    
    try:
        # Initialize the versioning system
        from backend.app.versioning import initialize_versioning
        initialize_versioning()
        
        # Run tests
        test_version_manager()
        test_core_node_registry()
        test_type_registry()
        test_migration_registry()
        
        logger.info("All tests completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
