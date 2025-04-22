from typing import Dict, Any, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class LogicOperations(BaseNode):
    """
    A core node for performing logical operations.
    
    This node can perform various logical operations like AND, OR, NOT, etc.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.logic_operations",
            name="Logic Operations",
            version="1.0.0",
            description="Perform logical operations",
            author="Workflow Builder",
            category=NodeCategory.LOGIC,
            tags=["logic", "boolean", "condition", "core"],
            inputs=[
                PortDefinition(
                    id="a",
                    name="A",
                    type="boolean",
                    description="First operand",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="b",
                    name="B",
                    type="boolean",
                    description="Second operand",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="c",
                    name="C",
                    type="boolean",
                    description="Third operand (for some operations)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="result",
                    name="Result",
                    type="boolean",
                    description="The result of the operation",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="inverted",
                    name="Inverted",
                    type="boolean",
                    description="The inverted result",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="operation",
                    name="Operation",
                    type="select",
                    description="The logical operation to perform",
                    required=True,
                    default_value="and",
                    options=[
                        {"label": "AND (A && B)", "value": "and"},
                        {"label": "OR (A || B)", "value": "or"},
                        {"label": "NOT (¬A)", "value": "not"},
                        {"label": "XOR (A ⊕ B)", "value": "xor"},
                        {"label": "NAND (¬(A && B))", "value": "nand"},
                        {"label": "NOR (¬(A || B))", "value": "nor"},
                        {"label": "XNOR (¬(A ⊕ B))", "value": "xnor"},
                        {"label": "ALL (A && B && C)", "value": "all"},
                        {"label": "ANY (A || B || C)", "value": "any"},
                        {"label": "NONE (¬A && ¬B && ¬C)", "value": "none"},
                        {"label": "MAJORITY", "value": "majority"}
                    ]
                ),
                ConfigField(
                    id="default_b",
                    name="Default B",
                    type="boolean",
                    description="Default value for B if not provided",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="default_c",
                    name="Default C",
                    type="boolean",
                    description="Default value for C if not provided",
                    required=False,
                    default_value=False
                )
            ],
            ui_properties={
                "color": "#e74c3c",
                "icon": "sitemap",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the logic operations node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The result of the operation
        """
        # Get inputs
        a = inputs.get("a")
        b = inputs.get("b")
        c = inputs.get("c")
        
        # Get configuration
        operation = config.get("operation", "and")
        default_b = config.get("default_b", False)
        default_c = config.get("default_c", False)
        
        # Use default values if inputs are not provided
        if a is None:
            return {
                "result": False,
                "inverted": True
            }
        
        if b is None:
            b = default_b
        
        if c is None:
            c = default_c
        
        # Convert inputs to booleans
        a = bool(a)
        b = bool(b)
        c = bool(c)
        
        # Perform the operation
        result = False
        
        if operation == "and":
            result = a and b
        
        elif operation == "or":
            result = a or b
        
        elif operation == "not":
            result = not a
        
        elif operation == "xor":
            result = (a or b) and not (a and b)
        
        elif operation == "nand":
            result = not (a and b)
        
        elif operation == "nor":
            result = not (a or b)
        
        elif operation == "xnor":
            result = not ((a or b) and not (a and b))
        
        elif operation == "all":
            result = a and b and c
        
        elif operation == "any":
            result = a or b or c
        
        elif operation == "none":
            result = not a and not b and not c
        
        elif operation == "majority":
            # True if majority of inputs are True
            count = sum([a, b, c])
            result = count > 1
        
        # Return the result and its inverse
        return {
            "result": result,
            "inverted": not result
        }
