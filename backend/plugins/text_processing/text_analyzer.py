from typing import Dict, Any, List
import re
from collections import Counter
from backend.app.models.plugin_metadata import PluginMetadata, PortDefinition, ConfigField, NodeCategory

class TextAnalyzer:
    """
    A plugin for analyzing text and extracting information.
    
    This plugin can count words, characters, sentences, and extract keywords.
    """
    
    def __init__(self):
        self.__plugin_meta__ = PluginMetadata(
            id="text_analyzer",
            name="Text Analyzer",
            version="1.0.0",
            description="Analyze text and extract information",
            author="Workflow Builder",
            category=NodeCategory.PROCESSING,
            tags=["text", "analysis", "processing", "nlp"],
            inputs=[
                PortDefinition(
                    id="text",
                    name="Text",
                    type="string",
                    description="The text to analyze",
                    required=True,
                    ui_properties={
                        "position": "left-center"
                    }
                )
            ],
            outputs=[
                PortDefinition(
                    id="word_count",
                    name="Word Count",
                    type="number",
                    description="The number of words in the text",
                    ui_properties={
                        "position": "right-top"
                    }
                ),
                PortDefinition(
                    id="char_count",
                    name="Character Count",
                    type="number",
                    description="The number of characters in the text",
                    ui_properties={
                        "position": "right-center-top"
                    }
                ),
                PortDefinition(
                    id="sentence_count",
                    name="Sentence Count",
                    type="number",
                    description="The number of sentences in the text",
                    ui_properties={
                        "position": "right-center"
                    }
                ),
                PortDefinition(
                    id="keywords",
                    name="Keywords",
                    type="array",
                    description="The most frequent words in the text",
                    ui_properties={
                        "position": "right-center-bottom"
                    }
                ),
                PortDefinition(
                    id="statistics",
                    name="Statistics",
                    type="object",
                    description="Various statistics about the text",
                    ui_properties={
                        "position": "right-bottom"
                    }
                )
            ],
            config_fields=[
                ConfigField(
                    id="extract_keywords",
                    name="Extract Keywords",
                    type="boolean",
                    description="Whether to extract keywords",
                    required=False,
                    default_value=True
                ),
                ConfigField(
                    id="keyword_count",
                    name="Keyword Count",
                    type="number",
                    description="The number of keywords to extract",
                    required=False,
                    default_value=10
                ),
                ConfigField(
                    id="min_word_length",
                    name="Minimum Word Length",
                    type="number",
                    description="The minimum length of words to consider",
                    required=False,
                    default_value=3
                ),
                ConfigField(
                    id="exclude_common_words",
                    name="Exclude Common Words",
                    type="boolean",
                    description="Whether to exclude common words",
                    required=False,
                    default_value=True
                )
            ],
            ui_properties={
                "color": "#9b59b6",
                "icon": "search",
                "width": 240
            }
        )
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the text analysis.
        
        Args:
            config: The plugin configuration
            inputs: The input values
            
        Returns:
            The analysis results
        """
        # Get input text
        text = inputs.get("text", "")
        
        if not isinstance(text, str):
            text = str(text)
        
        # Get configuration
        extract_keywords = config.get("extract_keywords", True)
        keyword_count = config.get("keyword_count", 10)
        min_word_length = config.get("min_word_length", 3)
        exclude_common_words = config.get("exclude_common_words", True)
        
        # Count characters
        char_count = len(text)
        
        # Count words
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # Extract keywords
        keywords = []
        if extract_keywords and words:
            # Common English stop words
            stop_words = set([
                "the", "and", "a", "to", "of", "in", "is", "that", "it", "with",
                "for", "as", "was", "on", "are", "by", "this", "be", "or", "an",
                "not", "but", "had", "has", "have", "from", "at", "which", "you",
                "his", "her", "they", "we", "she", "he", "who", "what", "where",
                "when", "why", "how", "all", "any", "both", "each", "few", "more",
                "most", "other", "some", "such", "than", "too", "very", "can",
                "will", "just", "should", "now"
            ]) if exclude_common_words else set()
            
            # Filter words
            filtered_words = [word for word in words if len(word) >= min_word_length and word not in stop_words]
            
            # Count word frequencies
            word_counts = Counter(filtered_words)
            
            # Get top keywords
            keywords = [{"word": word, "count": count} for word, count in word_counts.most_common(keyword_count)]
        
        # Calculate additional statistics
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Readability (Flesch-Kincaid Grade Level)
        syllable_count = self._count_syllables(text)
        if word_count > 0 and sentence_count > 0:
            flesch_kincaid = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
        else:
            flesch_kincaid = 0
        
        statistics = {
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "syllable_count": syllable_count,
            "readability_score": round(flesch_kincaid, 2),
            "unique_words": len(set(words)),
            "paragraphs": len(text.split("\n\n"))
        }
        
        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "keywords": keywords,
            "statistics": statistics
        }
    
    def _count_syllables(self, text: str) -> int:
        """Count the number of syllables in text."""
        # Simple syllable counting heuristic
        text = text.lower()
        text = re.sub(r'[^a-z]', ' ', text)
        words = text.split()
        
        syllable_count = 0
        for word in words:
            word = word.strip()
            if not word:
                continue
            
            # Count vowel groups
            count = len(re.findall(r'[aeiouy]+', word))
            
            # Adjust for common patterns
            if word.endswith('e'):
                count -= 1
            if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
                count += 1
            if count == 0:
                count = 1
            
            syllable_count += count
        
        return syllable_count
