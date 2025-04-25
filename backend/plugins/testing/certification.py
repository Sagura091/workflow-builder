"""
Plugin Certification System

This module provides a certification system for plugins.
"""

import logging
import os
import json
from typing import Dict, Any, Type, Optional, List, Tuple, Union
from datetime import datetime

from backend.app.models.plugin_interface import PluginInterface
from backend.plugins.testing.quality_checker import PluginQualityChecker
from backend.plugins.testing.plugin_test_case import PluginTestCase
from backend.plugins.testing.test_runner import PluginTestRunner
from backend.plugins.testing.production_validator import ProductionValidator

logger = logging.getLogger("workflow_builder")

class CertificationLevel:
    """Certification levels for plugins."""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

class PluginCertifier:
    """
    Certifier for plugins.
    
    This class provides methods for certifying plugins.
    """
    
    def __init__(self, plugin_class: Type[PluginInterface], test_cases: Optional[List[PluginTestCase]] = None):
        """
        Initialize the certifier.
        
        Args:
            plugin_class: The plugin class to certify
            test_cases: List of test cases for the plugin (optional)
        """
        self.plugin_class = plugin_class
        self.test_cases = test_cases or []
        self.quality_checker = PluginQualityChecker(plugin_class)
        self.production_validator = ProductionValidator(plugin_class, test_cases)
        
    def certify(self) -> Dict[str, Any]:
        """
        Certify the plugin.
        
        Returns:
            Dictionary containing the certification results
        """
        # Check quality
        quality_result = self.quality_checker.check_quality()
        
        # Validate production readiness
        production_result = self.production_validator.validate()
        
        # Determine certification level
        certification_level, reasons = self._determine_certification_level(quality_result, production_result)
        
        # Create result
        return {
            "plugin": self.plugin_class.__name__,
            "certification_level": certification_level,
            "reasons": reasons,
            "quality": quality_result,
            "production": production_result,
            "timestamp": datetime.now().isoformat()
        }
        
    def _determine_certification_level(self, quality_result: Dict[str, Any],
                                      production_result: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Determine the certification level for the plugin.
        
        Args:
            quality_result: Quality check results
            production_result: Production validation results
            
        Returns:
            Tuple of (certification_level, reasons)
        """
        reasons = []
        
        # Get quality score
        quality_score = quality_result["quality_score"]
        
        # Get production readiness
        is_production_ready = production_result["is_ready"]
        
        # Get test coverage
        test_coverage = production_result["test_coverage"]["overall_coverage"]
        
        # Determine certification level
        if quality_score < 0.6:
            certification_level = CertificationLevel.NONE
            reasons.append(f"Quality score is too low: {quality_score:.2f} (minimum 0.6)")
        elif quality_score >= 0.6 and quality_score < 0.7:
            certification_level = CertificationLevel.BASIC
            reasons.append(f"Quality score is {quality_score:.2f} (basic level)")
        elif quality_score >= 0.7 and quality_score < 0.8:
            certification_level = CertificationLevel.STANDARD
            reasons.append(f"Quality score is {quality_score:.2f} (standard level)")
        elif quality_score >= 0.8:
            certification_level = CertificationLevel.PREMIUM
            reasons.append(f"Quality score is {quality_score:.2f} (premium level)")
        else:
            certification_level = CertificationLevel.NONE
            reasons.append(f"Quality score is unknown: {quality_score}")
            
        # Check production readiness
        if not is_production_ready:
            if certification_level == CertificationLevel.PREMIUM:
                certification_level = CertificationLevel.STANDARD
                reasons.append("Plugin is not production ready (downgraded from premium to standard)")
            elif certification_level == CertificationLevel.STANDARD:
                certification_level = CertificationLevel.BASIC
                reasons.append("Plugin is not production ready (downgraded from standard to basic)")
                
        # Check test coverage
        if test_coverage < 0.5:
            if certification_level == CertificationLevel.PREMIUM:
                certification_level = CertificationLevel.STANDARD
                reasons.append(f"Test coverage is too low: {test_coverage:.2f} (downgraded from premium to standard)")
            elif certification_level == CertificationLevel.STANDARD:
                certification_level = CertificationLevel.BASIC
                reasons.append(f"Test coverage is too low: {test_coverage:.2f} (downgraded from standard to basic)")
                
        return certification_level, reasons
        
    def generate_certificate(self, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a certificate for the plugin.
        
        Args:
            output_dir: Directory to store the certificate (optional)
            
        Returns:
            Dictionary containing the certificate
        """
        # Certify the plugin
        result = self.certify()
        
        # Save the certificate
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            plugin_name = self.plugin_class.__name__
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{plugin_name}_certificate_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w") as f:
                json.dump(result, f, indent=4)
                
            logger.info(f"Saved certificate to {filepath}")
            
        return result
