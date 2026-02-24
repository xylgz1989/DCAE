"""Module for adjusting review processes based on discipline levels."""
from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class ReviewFrequency(Enum):
    """Enum representing different levels of review frequency and thoroughness."""
    LOW = 1
    MEDIUM = 5
    HIGH = 9


@dataclass
class ReviewProfile:
    """Profile containing review settings for a specific discipline level."""
    name: str
    enabled_reviews: List[str]
    parameters: Dict[str, Any]
    time_limits: Dict[str, int]
    approval_requirements: Dict[str, int]


class ReviewAdjuster:
    """Adjusts review processes based on discipline level."""

    def __init__(self):
        """Initialize the review adjuster."""
        self.review_criteria = {
            'quick_syntax_check': ['fast', 'balanced', 'strict'],
            'syntax_check': ['balanced', 'strict'],
            'style_check': ['balanced', 'strict'],
            'security_review': ['balanced', 'strict'],
            'performance_review': ['balanced', 'strict'],
            'architecture_review': ['balanced', 'strict'],
            'code_quality_review': ['balanced', 'strict'],
            'peer_review': ['balanced', 'strict'],
            'senior_approval': ['strict'],
            'compliance_check': ['strict']
        }

        self.custom_reviews = {}

    def adjust_review_for_level(self, discipline_level: 'DisciplineLevel') -> List[str]:
        """
        Adjust review criteria based on discipline level.

        Args:
            discipline_level: The discipline level to adjust for

        Returns:
            List of review checks to perform
        """
        level_str = discipline_level.value

        enabled_reviews = []
        for check, levels in self.review_criteria.items():
            if level_str in levels:
                enabled_reviews.append(check)

        return enabled_reviews

    def get_review_parameters(self, discipline_level: 'DisciplineLevel') -> Dict[str, Any]:
        """
        Get review parameters for a specific discipline level.

        Args:
            discipline_level: The discipline level to get parameters for

        Returns:
            Dictionary of review parameters
        """
        level_value = discipline_level.value

        if level_value == 'fast':
            return {
                'max_review_time': 10,  # minutes
                'review_depth': 'surface',
                'approval_steps': 1,
                'comments_required': 1,
                'reviewer_expertise': 'junior',
                'automated_percent': 90
            }
        elif level_value == 'balanced':
            return {
                'max_review_time': 30,  # minutes
                'review_depth': 'moderate',
                'approval_steps': 2,
                'comments_required': 3,
                'reviewer_expertise': 'mid-level',
                'automated_percent': 70
            }
        elif level_value == 'strict':
            return {
                'max_review_time': 60,  # minutes
                'review_depth': 'deep',
                'approval_steps': 3,
                'comments_required': 5,
                'reviewer_expertise': 'senior',
                'automated_percent': 50
            }
        else:
            # Default to balanced
            return self.get_review_parameters(type(discipline_level).BALANCED)

    def prepare_settings(self, discipline_level: 'DisciplineLevel') -> Dict[str, Any]:
        """
        Prepare review settings for application.

        Args:
            discipline_level: The discipline level to prepare settings for

        Returns:
            Dictionary of prepared review settings
        """
        reviews = self.adjust_review_for_level(discipline_level)
        parameters = self.get_review_parameters(discipline_level)

        return {
            'enabled_reviews': reviews,
            'time_limits': {
                'initial_review': parameters.get('max_review_time', 30),
                'revisions': parameters.get('max_review_time', 15),
                'final_approval': parameters.get('max_review_time', 10)
            },
            'approvals_needed': parameters.get('approval_steps', 2),
            'requirements': {
                'min_comments': parameters.get('comments_required', 3),
                'reviewer_level': parameters.get('reviewer_expertise', 'mid-level'),
                'automated_check_percent': parameters.get('automated_percent', 70)
            }
        }

    def create_review_profile(self, discipline_level: 'DisciplineLevel') -> ReviewProfile:
        """
        Create a review profile for a discipline level.

        Args:
            discipline_level: The discipline level to create profile for

        Returns:
            ReviewProfile object
        """
        reviews = self.adjust_review_for_level(discipline_level)
        parameters = self.get_review_parameters(discipline_level)

        return ReviewProfile(
            name=f"{discipline_level.value}_review_profile",
            enabled_reviews=reviews,
            parameters=parameters,
            time_limits={
                'initial_review': parameters.get('max_review_time', 30),
                'revisions': parameters.get('max_review_time', 15),
                'final_approval': parameters.get('max_review_time', 10)
            },
            approval_requirements={
                'steps': parameters.get('approval_steps', 2),
                'comments_min': parameters.get('comments_required', 3)
            }
        )

    def update_custom_config(self, custom_config: Dict[str, Any]):
        """
        Update with custom review configuration.

        Args:
            custom_config: Dictionary of custom review rules
        """
        self.custom_reviews.update(custom_config)