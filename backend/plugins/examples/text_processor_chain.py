"""
Text Processor Chain Plugin

This plugin demonstrates how to use core nodes within a plugin.
It chains together multiple text processing operations.
"""

from backend.plugins.base_plugin import BasePlugin

class TextProcessorChain(BasePlugin):
    """
    A plugin that chains together multiple text processing core nodes.
    """

    __plugin_meta__ = {
        "name": "Text Processor Chain",
        "category": "TEXT_PROCESSING",
        "description": "Process text through multiple transformations",
        "editable": True,
        "inputs": {
            "text": {"type": "string", "description": "Text to process"}
        },
        "outputs": {
            "processed_text": {"type": "string", "description": "Processed text"},
            "word_count": {"type": "number", "description": "Word count"},
            "character_count": {"type": "number", "description": "Character count"}
        },
        "configFields": [
            {
                "name": "uppercase",
                "type": "boolean",
                "label": "Convert to Uppercase",
                "default": False
            },
            {
                "name": "trim_whitespace",
                "type": "boolean",
                "label": "Trim Whitespace",
                "default": True
            },
            {
                "name": "count_words",
                "type": "boolean",
                "label": "Count Words",
                "default": True
            }
        ]
    }

    @classmethod
    def run(cls, inputs, config):
        """
        Execute the plugin with the given inputs and configuration.

        Args:
            inputs (dict): Input values from connected nodes
            config (dict): Configuration values set by the user

        Returns:
            dict: Output values to be passed to connected nodes
        """
        text = inputs.get("text", "")
        results = {"processed_text": text, "word_count": 0, "character_count": 0}

        # Use string operations core node if available
        if text:
            # Apply uppercase transformation if configured
            if config.get("uppercase", False):
                string_ops_result = cls.execute_core_node(
                    "core.string_operations",
                    {"text": text},
                    {"operation": "uppercase"}
                )
                if string_ops_result and "result" in string_ops_result:
                    text = string_ops_result["result"]

            # Apply trim whitespace transformation if configured
            if config.get("trim_whitespace", True):
                string_ops_result = cls.execute_core_node(
                    "core.string_operations",
                    {"text": text},
                    {"operation": "trim"}
                )
                if string_ops_result and "result" in string_ops_result:
                    text = string_ops_result["result"]

            results["processed_text"] = text
            results["character_count"] = len(text)

        # Use text analyzer core node if available and configured
        if config.get("count_words", True) and text:
            text_analyzer_result = cls.execute_core_node(
                "core.text_analyzer",
                {"text": text},
                {"analyze": "word_count"}
            )
            if text_analyzer_result and "word_count" in text_analyzer_result:
                results["word_count"] = text_analyzer_result["word_count"]
            else:
                # Fallback word count implementation
                results["word_count"] = len(text.split())

        return results

    @classmethod
    def generate_code(cls, config):
        """
        Generate code for the plugin.

        Args:
            config (dict): Configuration values set by the user

        Returns:
            str: Generated code
        """
        code = [
            "# Text Processor Chain",
            "def process_text(text):",
            "    # Process the input text"
        ]

        if config.get("trim_whitespace", True):
            code.append("    text = text.strip()")

        if config.get("uppercase", False):
            code.append("    text = text.upper()")

        code.append("    result = {}")
        code.append("    result['processed_text'] = text")
        code.append("    result['character_count'] = len(text)")

        if config.get("count_words", True):
            code.append("    result['word_count'] = len(text.split())")

        code.append("    return result")

        return "\n".join(code)
