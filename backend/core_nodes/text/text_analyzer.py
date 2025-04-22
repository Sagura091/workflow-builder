"""
Text Analyzer Node

This node analyzes text and provides various metrics.
"""

from backend.core_nodes.base_node import BaseNode
import re

class TextAnalyzer(BaseNode):
    """
    Analyzes text and provides various metrics.
    """
    
    def __init__(self):
        super().__init__()
        self.id = "core.text_analyzer"
        self.name = "Text Analyzer"
        self.category = "TEXT"
        self.description = "Analyze text and extract metrics"
        self.inputs = [
            {
                "id": "text",
                "name": "Text",
                "type": "string",
                "description": "Text to analyze",
                "required": True
            }
        ]
        self.outputs = [
            {
                "id": "word_count",
                "name": "Word Count",
                "type": "number",
                "description": "Number of words in the text"
            },
            {
                "id": "character_count",
                "name": "Character Count",
                "type": "number",
                "description": "Number of characters in the text"
            },
            {
                "id": "sentence_count",
                "name": "Sentence Count",
                "type": "number",
                "description": "Number of sentences in the text"
            },
            {
                "id": "paragraph_count",
                "name": "Paragraph Count",
                "type": "number",
                "description": "Number of paragraphs in the text"
            },
            {
                "id": "average_word_length",
                "name": "Average Word Length",
                "type": "number",
                "description": "Average length of words in the text"
            },
            {
                "id": "average_sentence_length",
                "name": "Average Sentence Length",
                "type": "number",
                "description": "Average number of words per sentence"
            }
        ]
        self.config_fields = [
            {
                "name": "analyze",
                "type": "select",
                "label": "Analysis Type",
                "options": [
                    {"label": "All Metrics", "value": "all"},
                    {"label": "Word Count", "value": "word_count"},
                    {"label": "Character Count", "value": "character_count"},
                    {"label": "Sentence Count", "value": "sentence_count"},
                    {"label": "Paragraph Count", "value": "paragraph_count"},
                    {"label": "Average Word Length", "value": "average_word_length"},
                    {"label": "Average Sentence Length", "value": "average_sentence_length"}
                ],
                "default": "all"
            }
        ]
        self.ui_properties = {
            "color": "#9b59b6",
            "icon": "chart-bar",
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
        analyze = config.get("analyze", "all")
        
        # Initialize results
        results = {}
        
        # Calculate metrics based on analysis type
        if analyze in ["all", "word_count"]:
            results["word_count"] = len(text.split())
        
        if analyze in ["all", "character_count"]:
            results["character_count"] = len(text)
        
        if analyze in ["all", "sentence_count"]:
            # Simple sentence detection (not perfect but works for most cases)
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            results["sentence_count"] = len(sentences)
        
        if analyze in ["all", "paragraph_count"]:
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            results["paragraph_count"] = len(paragraphs)
        
        if analyze in ["all", "average_word_length"]:
            words = [w for w in text.split() if w]
            if words:
                avg_word_length = sum(len(word) for word in words) / len(words)
                results["average_word_length"] = round(avg_word_length, 2)
            else:
                results["average_word_length"] = 0
        
        if analyze in ["all", "average_sentence_length"]:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            if sentences:
                words_per_sentence = [len(s.split()) for s in sentences]
                avg_sentence_length = sum(words_per_sentence) / len(sentences)
                results["average_sentence_length"] = round(avg_sentence_length, 2)
            else:
                results["average_sentence_length"] = 0
        
        return results
