"""Module for adjusting validation based on discipline levels."""
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class ValidationLevel(Enum):
    """Enum representing different levels of validation rigor."""
    MINIMAL = 1
    LIGHT = 2
    STANDARD = 5
    COMPREHENSIVE = 7
    RIGOROUS = 9


@dataclass
class ValidationProfile:
    """Profile containing validation settings for a specific discipline level."""
    name: str
    enabled_checks: List[str]
    thresholds: Dict[str, Any]
    timeouts: Dict[str, int]
    severity_levels: Dict[str, str]


class ValidationAdjuster:
    """Adjusts validation processes based on discipline level."""

    def __init__(self):
        """Initialize the validation adjuster."""
        self.validation_rules = {
            'syntax_check': ['fast', 'balanced', 'strict'],
            'style_check': ['balanced', 'strict'],
            'security_scan': ['balanced', 'strict'],
            'dependency_check': ['balanced', 'strict'],
            'complexity_analysis': ['balanced', 'strict'],
            'performance_check': ['strict'],
            'license_compliance': ['strict'],
            'code_duplication': ['balanced', 'strict'],
            'api_conformance': ['strict']
        }

        self.custom_rules = {}

    def adjust_validation_for_level(self, discipline_level: 'DisciplineLevel') -> List[str]:
        """
        Adjust validation rules based on discipline level.

        Args:
            discipline_level: The discipline level to adjust for

        Returns:
            List of validation checks to run
        """
        level_str = discipline_level.value

        enabled_checks = []
        for check, levels in self.validation_rules.items():
            if level_str in levels:
                enabled_checks.append(check)

        return enabled_checks

    def get_validation_parameters(self, discipline_level: 'DisciplineLevel') -> Dict[str, Any]:
        """
        Get validation parameters for a specific discipline level.

        Args:
            discipline_level: The discipline level to get parameters for

        Returns:
            Dictionary of validation parameters
        """
        level_value = discipline_level.value

        if level_value == 'fast':
            return {
                'max_line_length': 120,
                'min_test_coverage': 0.60,
                'security_threshold': 'medium',
                'timeout_seconds': 10,
                'complexity_limit': 10,
                'duplicate_code_threshold': 0.10
            }
        elif level_value == 'balanced':
            return {
                'max_line_length': 100,
                'min_test_coverage': 0.80,
                'security_threshold': 'low',
                'timeout_seconds': 30,
                'complexity_limit': 8,
                'duplicate_code_threshold': 0.05
            }
        elif level_value == 'strict':
            return {
                'max_line_length': 80,
                'min_test_coverage': 0.90,
                'security_threshold': 'high',
                'timeout_seconds': 60,
                'complexity_limit': 5,
                'duplicate_code_threshold': 0.02
            }
        else:
            # Default to balanced
            return self.get_validation_parameters(type(discipline_level).BALANCED)

    def prepare_settings(self, discipline_level: 'DisciplineLevel') -> Dict[str, Any]:
        """
        Prepare validation settings for application.

        Args:
            discipline_level: The discipline level to prepare settings for

        Returns:
            Dictionary of prepared validation settings
        """
        checks = self.adjust_validation_for_level(discipline_level)
        parameters = self.get_validation_parameters(discipline_level)

        return {
            'enabled_checks': checks,
            'thresholds': parameters,
            'timeouts': {
                'syntax_check': parameters.get('timeout_seconds', 30),
                'security_scan': parameters.get('timeout_seconds', 60) * 2,
                'performance_check': parameters.get('timeout_seconds', 60) * 3
            }
        }

    def create_validation_profile(self, discipline_level: 'DisciplineLevel') -> ValidationProfile:
        """
        Create a validation profile for a discipline level.

        Args:
            discipline_level: The discipline level to create profile for

        Returns:
            ValidationProfile object
        """
        checks = self.adjust_validation_for_level(discipline_level)
        parameters = self.get_validation_parameters(discipline_level)

        return ValidationProfile(
            name=f"{discipline_level.value}_validation_profile",
            enabled_checks=checks,
            thresholds=parameters,
            timeouts={
                'syntax_check': parameters.get('timeout_seconds', 30),
                'security_scan': parameters.get('timeout_seconds', 60) * 2,
                'performance_check': parameters.get('timeout_seconds', 60) * 3
            },
            severity_levels={
                'security': parameters.get('security_threshold', 'medium'),
                'style': 'medium',
                'performance': 'medium' if discipline_level.value != 'strict' else 'high'
            }
        )

    def update_custom_config(self, custom_config: Dict[str, Any]):
        """
        Update with custom validation configuration.

        Args:
            custom_config: Dictionary of custom validation rules
        """
        self.custom_rules.update(custom_config)