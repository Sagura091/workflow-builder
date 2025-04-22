"""
Core Node Loader

This module provides functionality to load core nodes and register them with the node registry.
"""

import os
import importlib.util
import inspect
import logging
from backend.app.services.node_registry import NodeRegistry

logger = logging.getLogger(__name__)

def load_core_nodes(core_nodes_dir):
    """
    Load all core nodes from the given directory and register them with the node registry.
    
    Args:
        core_nodes_dir (str): Path to the core nodes directory
    
    Returns:
        int: Number of core nodes loaded
    """
    registry = NodeRegistry()
    count = 0
    
    logger.info(f"Loading core nodes from {core_nodes_dir}")
    
    # Walk through the core nodes directory
    for root, dirs, files in os.walk(core_nodes_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                # Load the module
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find all classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            hasattr(obj, 'execute') and 
                            inspect.isfunction(getattr(obj, 'execute'))):
                            
                            # Create an instance to get the ID
                            try:
                                instance = obj()
                                if hasattr(instance, 'id'):
                                    node_id = instance.id
                                    registry.register_node(node_id, obj)
                                    count += 1
                                    logger.debug(f"Registered core node: {node_id}")
                            except Exception as e:
                                logger.error(f"Error instantiating node class {name} from {module_path}: {e}")
                
                except Exception as e:
                    logger.error(f"Error loading module {module_path}: {e}")
    
    logger.info(f"Loaded {count} core nodes")
    return count

def initialize_core_nodes():
    """
    Initialize all core nodes from the default core nodes directory.
    
    Returns:
        int: Number of core nodes loaded
    """
    import os
    
    # Get the path to the core_nodes directory
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    core_nodes_dir = os.path.join(current_dir, "core_nodes")
    
    return load_core_nodes(core_nodes_dir)
