import json
import re
from typing import Dict, Any, List, Optional
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory
from backend.core_nodes.base_node import BaseNode

class PromptTemplate(BaseNode):
    """
    A core node for creating prompts for LLMs.
    
    This node allows users to create structured prompts for language models.
    """
    
    def get_metadata(self) -> PluginMetadata:
        """Get the node metadata."""
        return PluginMetadata(
            id="core.prompt_template",
            name="Prompt Template",
            version="1.0.0",
            description="Create prompts for LLMs",
            author="Workflow Builder",
            category=NodeCategory.AI_ML,
            tags=["prompt", "template", "llm", "ai", "core"],
            inputs=[
                PortDefinition(
                    id="variables",
                    name="Variables",
                    type="object",
                    description="Variables to use in the template",
                    required=True,
                    ui_properties={
                        "position": "left-top"
                    }
                ),
                PortDefinition(
                    id="system_message",
                    name="System Message",
                    type="string",
                    description="System message (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-center"
                    }
                ),
                PortDefinition(
                    id="user_message",
                    name="User Message",
                    type="string",
                    description="User message (overrides config)",
                    required=False,
                    ui_properties={
                        "position": "left-bottom"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="prompt",
                    name="Prompt",
                    type="string",
                    description="The generated prompt text",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="messages",
                    name="Messages",
                    type="array",
                    description="The prompt as a messages array",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="token_estimate",
                    name="Token Estimate",
                    type="number",
                    description="Estimated token count",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="template_type",
                    name="Template Type",
                    type="select",
                    description="Type of prompt template",
                    required=True,
                    default_value="chat",
                    options=[
                        {"label": "Chat", "value": "chat"},
                        {"label": "Completion", "value": "completion"},
                        {"label": "Custom", "value": "custom"}
                    ]
                ),
                ConfigField(
                    id="system_message",
                    name="System Message",
                    type="text",
                    description="System message for chat templates",
                    required=False,
                    default_value="You are a helpful assistant."
                ),
                ConfigField(
                    id="user_message",
                    name="User Message",
                    type="text",
                    description="User message template",
                    required=True,
                    default_value="Hello, I need help with {topic}."
                ),
                ConfigField(
                    id="custom_template",
                    name="Custom Template",
                    type="text",
                    description="Custom prompt template",
                    required=False
                ),
                ConfigField(
                    id="include_examples",
                    name="Include Examples",
                    type="boolean",
                    description="Whether to include example exchanges",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="examples",
                    name="Examples",
                    type="text",
                    description="Example exchanges (JSON array)",
                    required=False,
                    default_value="[]"
                ),
                ConfigField(
                    id="model",
                    name="Model",
                    type="select",
                    description="Target model for token estimation",
                    required=False,
                    default_value="gpt-3.5-turbo",
                    options=[
                        {"label": "GPT-3.5 Turbo", "value": "gpt-3.5-turbo"},
                        {"label": "GPT-4", "value": "gpt-4"},
                        {"label": "Claude", "value": "claude"},
                        {"label": "Llama", "value": "llama"},
                        {"label": "Other", "value": "other"}
                    ]
                )
            ],
            ui_properties={
                "color": "#2ecc71",
                "icon": "comment-alt",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the prompt template node.
        
        Args:
            config: The node configuration
            inputs: The input values
            
        Returns:
            The generated prompt
        """
        import json
        import re
        
        # Get inputs
        variables = inputs.get("variables", {})
        input_system_message = inputs.get("system_message")
        input_user_message = inputs.get("user_message")
        
        # Get configuration
        template_type = config.get("template_type", "chat")
        config_system_message = config.get("system_message", "You are a helpful assistant.")
        config_user_message = config.get("user_message", "Hello, I need help with {topic}.")
        custom_template = config.get("custom_template", "")
        include_examples = config.get("include_examples", False)
        examples_json = config.get("examples", "[]")
        model = config.get("model", "gpt-3.5-turbo")
        
        # Use input values if provided, otherwise use config
        system_message = input_system_message if input_system_message is not None else config_system_message
        user_message = input_user_message if input_user_message is not None else config_user_message
        
        # Initialize outputs
        prompt = ""
        messages = []
        token_estimate = 0
        
        try:
            # Apply variables to messages
            for key, value in variables.items():
                placeholder = "{" + key + "}"
                if placeholder in system_message:
                    system_message = system_message.replace(placeholder, str(value))
                if placeholder in user_message:
                    user_message = user_message.replace(placeholder, str(value))
                if custom_template and placeholder in custom_template:
                    custom_template = custom_template.replace(placeholder, str(value))
            
            # Parse examples
            examples = []
            if include_examples and examples_json:
                try:
                    examples = json.loads(examples_json)
                    if not isinstance(examples, list):
                        examples = []
                except:
                    examples = []
            
            # Generate prompt based on template type
            if template_type == "chat":
                # Create messages array
                messages.append({"role": "system", "content": system_message})
                
                # Add examples if included
                for example in examples:
                    if isinstance(example, dict):
                        role = example.get("role", "user")
                        content = example.get("content", "")
                        messages.append({"role": role, "content": content})
                
                # Add user message
                messages.append({"role": "user", "content": user_message})
                
                # Create text prompt for output
                prompt = f"System: {system_message}\n\n"
                
                for example in examples:
                    if isinstance(example, dict):
                        role = example.get("role", "user").capitalize()
                        content = example.get("content", "")
                        prompt += f"{role}: {content}\n\n"
                
                prompt += f"User: {user_message}"
            
            elif template_type == "completion":
                # Create simple completion prompt
                prompt = user_message
                
                # Create messages array for compatibility
                messages.append({"role": "user", "content": user_message})
            
            elif template_type == "custom":
                # Use custom template
                prompt = custom_template if custom_template else user_message
                
                # Create messages array for compatibility
                messages.append({"role": "user", "content": prompt})
            
            # Estimate token count
            token_estimate = self._estimate_tokens(prompt, model)
        
        except Exception as e:
            prompt = f"Error generating prompt: {str(e)}"
            messages = [{"role": "user", "content": prompt}]
            token_estimate = 0
        
        return {
            "prompt": prompt,
            "messages": messages,
            "token_estimate": token_estimate
        }
    
    def _estimate_tokens(self, text: str, model: str) -> int:
        """Estimate the number of tokens in a text."""
        # Very rough estimation based on words
        # In reality, tokenization is more complex and model-dependent
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Different models have different tokenization ratios
        if model in ["gpt-4", "claude"]:
            # These models tend to have slightly more efficient tokenization
            return int(word_count * 1.3)
        else:
            # Default ratio for most models
            return int(word_count * 1.5)
    
    def validate_config(self, config: Dict[str, Any]) -> Optional[str]:
        """Validate the node configuration."""
        template_type = config.get("template_type", "")
        if not template_type:
            return "Template type is required"
        
        if template_type == "chat" and not config.get("system_message", ""):
            return "System message is required for chat templates"
        
        if not config.get("user_message", ""):
            return "User message is required"
        
        if template_type == "custom" and not config.get("custom_template", ""):
            return "Custom template is required for custom template type"
        
        # Validate examples JSON
        if config.get("include_examples", False):
            examples_json = config.get("examples", "[]")
            try:
                examples = json.loads(examples_json)
                if not isinstance(examples, list):
                    return "Examples must be a JSON array"
            except json.JSONDecodeError:
                return "Examples must be valid JSON"
        
        return None
