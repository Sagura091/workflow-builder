from typing import Dict, Any, List
import re
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class TextSplitter:
    """
    A plugin for splitting text into chunks.
    
    This plugin can split text by paragraphs, sentences, words, or custom delimiters.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="text_splitter",
            name="Text Splitter",
            version="1.0.0",
            description="Split text into chunks",
            author="Workflow Builder",
            category=NodeCategory.PROCESSING,
            tags=["text", "split", "processing", "chunks"],
            inputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The text to split",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="chunks",
                    name="Chunks",
                    type="array",
                    description="The text chunks",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="chunk_count",
                    name="Chunk Count",
                    type="number",
                    description="The number of chunks",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="joined_text",
                    name="Joined Text",
                    type="string",
                    description="The chunks joined with the specified delimiter",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="split_by",
                    name="Split By",
                    type="select",
                    description="How to split the text",
                    required=True,
                    default_value="paragraph",
                    options=[
                        {"label": "Paragraph", "value": "paragraph"},
                        {"label": "Sentence", "value": "sentence"},
                        {"label": "Word", "value": "word"},
                        {"label": "Character", "value": "character"},
                        {"label": "Custom", "value": "custom"}
                    ]
                ),
                ConfigField(
                    id="custom_delimiter",
                    name="Custom Delimiter",
                    type="string",
                    description="Custom delimiter for splitting (when Split By is 'Custom')",
                    required=False,
                    default_value=","
                ),
                ConfigField(
                    id="max_chunk_size",
                    name="Max Chunk Size",
                    type="number",
                    description="Maximum size of each chunk (0 for no limit)",
                    required=False,
                    default_value=0
                ),
                ConfigField(
                    id="include_empty",
                    name="Include Empty Chunks",
                    type="boolean",
                    description="Whether to include empty chunks",
                    required=False,
                    default_value=False
                ),
                ConfigField(
                    id="join_delimiter",
                    name="Join Delimiter",
                    type="string",
                    description="Delimiter to use when joining chunks",
                    required=False,
                    default_value="\n"
                )
            ],
            ui_properties={
                "color": "#e67e22",
                "icon": "cut",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the text splitting operation.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The split text chunks
        """
        # Get input text
        text = inputs.get("text", "")
        
        if not isinstance(text, str):
            text = str(text)
        
        # Get configuration
        split_by = config.get("split_by", "paragraph")
        custom_delimiter = config.get("custom_delimiter", ",")
        max_chunk_size = config.get("max_chunk_size", 0)
        include_empty = config.get("include_empty", False)
        join_delimiter = config.get("join_delimiter", "\n")
        
        # Split text
        chunks = []
        
        if split_by == "paragraph":
            chunks = text.split("\n\n")
        elif split_by == "sentence":
            # Split by sentence endings
            chunks = re.split(r'(?<=[.!?])\s+', text)
        elif split_by == "word":
            # Split by words
            chunks = re.findall(r'\b\w+\b', text)
        elif split_by == "character":
            # Split by characters
            chunks = list(text)
        elif split_by == "custom":
            # Split by custom delimiter
            chunks = text.split(custom_delimiter)
        
        # Filter empty chunks if needed
        if not include_empty:
            chunks = [chunk.strip() for chunk in chunks]
            chunks = [chunk for chunk in chunks if chunk]
        
        # Apply max chunk size if specified
        if max_chunk_size > 0:
            new_chunks = []
            for chunk in chunks:
                if len(chunk) <= max_chunk_size:
                    new_chunks.append(chunk)
                else:
                    # Split large chunks
                    for i in range(0, len(chunk), max_chunk_size):
                        new_chunks.append(chunk[i:i+max_chunk_size])
            chunks = new_chunks
        
        # Join chunks with the specified delimiter
        joined_text = join_delimiter.join(chunks)
        
        return {
            "chunks": chunks,
            "chunk_count": len(chunks),
            "joined_text": joined_text
        }
