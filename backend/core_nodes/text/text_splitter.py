"""
Text Splitter Node

This node splits text into chunks.
"""

from backend.core_nodes.base_node import BaseNode

class TextSplitter(BaseNode):
    """
    Splits text into chunks.
    """
    
    def __init__(self):
        super().__init__()
        self.id = "core.text_splitter"
        self.name = "Text Splitter"
        self.category = "TEXT"
        self.description = "Split text into chunks"
        self.inputs = [
            {
                "id": "text",
                "name": "Text",
                "type": "string",
                "description": "Text to split",
                "required": True
            }
        ]
        self.outputs = [
            {
                "id": "chunks",
                "name": "Chunks",
                "type": "array",
                "description": "Text chunks"
            },
            {
                "id": "chunk_count",
                "name": "Chunk Count",
                "type": "number",
                "description": "Number of chunks"
            }
        ]
        self.config_fields = [
            {
                "name": "chunk_size",
                "type": "number",
                "label": "Chunk Size",
                "default": 1000
            },
            {
                "name": "chunk_overlap",
                "type": "number",
                "label": "Chunk Overlap",
                "default": 200
            },
            {
                "name": "split_by",
                "type": "select",
                "label": "Split By",
                "options": [
                    {"label": "Characters", "value": "characters"},
                    {"label": "Words", "value": "words"},
                    {"label": "Sentences", "value": "sentences"},
                    {"label": "Paragraphs", "value": "paragraphs"}
                ],
                "default": "characters"
            }
        ]
        self.ui_properties = {
            "color": "#2ecc71",
            "icon": "cut",
            "width": 240
        }
    
    def execute(self, inputs, config):
        """
        Execute the node.
        
        Args:
            inputs (dict): The input values.
            config (dict): The node configuration.
            
        Returns:
            dict: The output values.
        """
        text = inputs.get("text", "")
        chunk_size = config.get("chunk_size", 1000)
        chunk_overlap = config.get("chunk_overlap", 200)
        split_by = config.get("split_by", "characters")
        
        if not text:
            return {"chunks": [], "chunk_count": 0}
        
        chunks = []
        
        if split_by == "characters":
            # Split by characters
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunk = text[i:i + chunk_size]
                if chunk:
                    chunks.append(chunk)
        
        elif split_by == "words":
            # Split by words
            words = text.split()
            current_chunk = []
            current_size = 0
            
            for word in words:
                word_size = len(word) + 1  # +1 for space
                
                if current_size + word_size > chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    # Keep overlap words
                    overlap_words = current_chunk[-int(chunk_overlap / 5):]  # Approximate word count for overlap
                    current_chunk = overlap_words
                    current_size = sum(len(w) + 1 for w in current_chunk)
                
                current_chunk.append(word)
                current_size += word_size
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
        
        elif split_by == "sentences":
            import re
            # Split by sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                sentence_size = len(sentence) + 1  # +1 for space
                
                if current_size + sentence_size > chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    # Keep overlap sentences
                    overlap_sentences = current_chunk[-int(chunk_overlap / 50):]  # Approximate sentence count for overlap
                    current_chunk = overlap_sentences
                    current_size = sum(len(s) + 1 for s in current_chunk)
                
                current_chunk.append(sentence)
                current_size += sentence_size
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
        
        elif split_by == "paragraphs":
            # Split by paragraphs
            paragraphs = text.split("\n\n")
            current_chunk = []
            current_size = 0
            
            for paragraph in paragraphs:
                paragraph_size = len(paragraph) + 2  # +2 for newlines
                
                if current_size + paragraph_size > chunk_size and current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    # Keep overlap paragraphs
                    overlap_paragraphs = current_chunk[-int(chunk_overlap / 100):]  # Approximate paragraph count for overlap
                    current_chunk = overlap_paragraphs
                    current_size = sum(len(p) + 2 for p in current_chunk)
                
                current_chunk.append(paragraph)
                current_size += paragraph_size
            
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
        
        return {
            "chunks": chunks,
            "chunk_count": len(chunks)
        }
