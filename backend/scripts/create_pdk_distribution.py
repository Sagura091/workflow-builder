"""
Create PDK Distribution

This script creates a standalone distribution of the Plugin Development Kit (PDK).
"""

import os
import sys
import shutil
import argparse
import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("pdk_distribution")

def create_pdk_distribution(output_dir: str):
    """
    Create a standalone distribution of the PDK.
    
    Args:
        output_dir: Directory to store the distribution
    """
    # Get the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the directory structure
    os.makedirs(os.path.join(output_dir, "pdk"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "pdk", "testing"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "pdk", "examples"), exist_ok=True)
    
    # Copy the PDK files
    files_to_copy = [
        # PDK base files
        ("plugins/pdk/__init__.py", "pdk/__init__.py"),
        ("plugins/pdk/README.md", "pdk/README.md"),
        
        # Standalone plugin base
        ("plugins/standalone_plugin_base.py", "pdk/standalone_plugin_base.py"),
        
        # Testing framework
        ("plugins/testing/__init__.py", "pdk/testing/__init__.py"),
        ("plugins/testing/plugin_test_case.py", "pdk/testing/plugin_test_case.py"),
        ("plugins/testing/test_runner.py", "pdk/testing/test_runner.py"),
        ("plugins/testing/quality_checker.py", "pdk/testing/quality_checker.py"),
        ("plugins/testing/production_validator.py", "pdk/testing/production_validator.py"),
        ("plugins/testing/certification.py", "pdk/testing/certification.py"),
        ("plugins/testing/test_generator.py", "pdk/testing/test_generator.py"),
        ("plugins/testing/validator.py", "pdk/testing/validator.py"),
        ("plugins/testing/importer.py", "pdk/testing/importer.py"),
        ("plugins/testing/cli.py", "pdk/testing/cli.py"),
        
        # Examples
        ("plugins/examples/standalone_plugin_example.py", "pdk/examples/standalone_plugin_example.py"),
        ("plugins/examples/test_standalone_plugin_example.py", "pdk/examples/test_standalone_plugin_example.py"),
    ]
    
    # Copy the files
    for src, dst in files_to_copy:
        src_path = os.path.join(backend_dir, src)
        dst_path = os.path.join(output_dir, dst)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            logger.info(f"Copied {src_path} to {dst_path}")
        else:
            logger.warning(f"File not found: {src_path}")
            
    # Copy required models
    models_dir = os.path.join(output_dir, "pdk", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    models_to_copy = [
        ("app/models/plugin_interface.py", "plugin_interface.py"),
        ("app/models/plugin_metadata.py", "plugin_metadata.py"),
        ("app/models/node.py", "node.py"),
        ("app/models/connection.py", "connection.py"),
        ("app/models/workflow.py", "workflow.py"),
    ]
    
    for src, dst in models_to_copy:
        src_path = os.path.join(backend_dir, src)
        dst_path = os.path.join(models_dir, dst)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            logger.info(f"Copied {src_path} to {dst_path}")
        else:
            logger.warning(f"File not found: {src_path}")
            
    # Create an __init__.py file for the models directory
    with open(os.path.join(models_dir, "__init__.py"), "w") as f:
        f.write('"""Models for the Plugin Development Kit."""\n\n')
        f.write("from .plugin_interface import PluginInterface\n")
        f.write("from .plugin_metadata import PluginMetadata, PortDefinition, ConfigField\n")
        f.write("from .node import Node\n")
        f.write("from .connection import Edge\n")
        f.write("from .workflow import NodeExecutionResult, NodeExecutionStatus\n\n")
        f.write('__all__ = [\n')
        f.write('    "PluginInterface",\n')
        f.write('    "PluginMetadata",\n')
        f.write('    "PortDefinition",\n')
        f.write('    "ConfigField",\n')
        f.write('    "Node",\n')
        f.write('    "Edge",\n')
        f.write('    "NodeExecutionResult",\n')
        f.write('    "NodeExecutionStatus"\n')
        f.write(']\n')
        
    # Create a setup.py file
    with open(os.path.join(output_dir, "setup.py"), "w") as f:
        f.write('"""Setup script for the Plugin Development Kit."""\n\n')
        f.write("from setuptools import setup, find_packages\n\n")
        f.write("setup(\n")
        f.write('    name="workflow-builder-pdk",\n')
        f.write('    version="1.0.0",\n')
        f.write('    description="Plugin Development Kit for Workflow Builder",\n')
        f.write('    author="Workflow Builder Team",\n')
        f.write('    packages=find_packages(),\n')
        f.write('    install_requires=[\n')
        f.write('        "pydantic>=2.0.0",\n')
        f.write('    ],\n')
        f.write('    entry_points={\n')
        f.write('        "console_scripts": [\n')
        f.write('            "pdk-test=pdk.testing.cli:main",\n')
        f.write('        ],\n')
        f.write('    },\n')
        f.write(')\n')
        
    # Create a README.md file
    with open(os.path.join(output_dir, "README.md"), "w") as f:
        f.write("# Workflow Builder Plugin Development Kit (PDK)\n\n")
        f.write("This package provides tools and utilities for developing plugins for the Workflow Builder.\n\n")
        f.write("## Installation\n\n")
        f.write("```bash\n")
        f.write("pip install -e .\n")
        f.write("```\n\n")
        f.write("## Usage\n\n")
        f.write("### Creating a Plugin\n\n")
        f.write("```python\n")
        f.write("from pdk import StandalonePluginBase, PluginMetadata, PortDefinition, ConfigField\n\n")
        f.write("class MyPlugin(StandalonePluginBase):\n")
        f.write('    """My plugin."""\n\n')
        f.write("    # Plugin metadata\n")
        f.write("    __plugin_meta__ = PluginMetadata(\n")
        f.write('        id="my_plugin",\n')
        f.write('        name="My Plugin",\n')
        f.write('        version="1.0.0",\n')
        f.write('        description="My plugin",\n')
        f.write('        category="examples",\n')
        f.write('        tags=["example"],\n')
        f.write("        inputs=[\n")
        f.write("            PortDefinition(\n")
        f.write('                id="input1",\n')
        f.write('                name="Input 1",\n')
        f.write('                type="string",\n')
        f.write('                description="Input 1",\n')
        f.write("                required=True\n")
        f.write("            )\n")
        f.write("        ],\n")
        f.write("        outputs=[\n")
        f.write("            PortDefinition(\n")
        f.write('                id="output1",\n')
        f.write('                name="Output 1",\n')
        f.write('                type="string",\n')
        f.write('                description="Output 1",\n')
        f.write("                required=True\n")
        f.write("            )\n")
        f.write("        ],\n")
        f.write("        config_fields=[\n")
        f.write("            ConfigField(\n")
        f.write('                id="config1",\n')
        f.write('                name="Config 1",\n')
        f.write('                type="string",\n')
        f.write('                description="Config 1",\n')
        f.write("                required=False,\n")
        f.write('                default_value=""\n')
        f.write("            )\n")
        f.write("        ]\n")
        f.write("    )\n\n")
        f.write("    def execute(self, inputs, config):\n")
        f.write('        """Execute the plugin."""\n')
        f.write("        # Get inputs\n")
        f.write('        input1 = inputs.get("input1", "")\n\n')
        f.write("        # Get config\n")
        f.write('        config1 = config.get("config1", "")\n\n')
        f.write("        # Process inputs\n")
        f.write("        result = f\"{input1} - {config1}\"\n\n")
        f.write("        # Return outputs\n")
        f.write("        return {\n")
        f.write('            "output1": result\n')
        f.write("        }\n")
        f.write("```\n\n")
        f.write("### Testing a Plugin\n\n")
        f.write("```bash\n")
        f.write("pdk-test test my_plugin.py --output-dir test_results\n")
        f.write("```\n\n")
        f.write("### Checking Plugin Quality\n\n")
        f.write("```bash\n")
        f.write("pdk-test quality my_plugin.py --output-dir test_results\n")
        f.write("```\n\n")
        f.write("### Generating Tests for a Plugin\n\n")
        f.write("```bash\n")
        f.write("pdk-test generate my_plugin.py test_results\n")
        f.write("```\n\n")
        f.write("## Documentation\n\n")
        f.write("For more information, see the [PDK documentation](pdk/README.md).\n")
        
    logger.info(f"PDK distribution created in {output_dir}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Create PDK Distribution")
    parser.add_argument("output_dir", help="Directory to store the distribution")
    
    args = parser.parse_args()
    
    create_pdk_distribution(args.output_dir)

if __name__ == "__main__":
    main()
