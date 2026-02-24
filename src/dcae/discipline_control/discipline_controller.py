"""Module for controlling discipline levels and methodology enforcement."""
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
import os


class DisciplineLevel(Enum):
    """Enum representing different discipline levels."""
    FAST = "fast"
    BALANCED = "balanced"
    STRICT = "strict"


@dataclass
class DisciplineSettings:
    """Settings configuration for a specific discipline level."""
    validation_level: int  # 1-10 scale, higher = more validation
    review_frequency: int  # 1-10 scale, higher = more frequent review
    testing_requirement: str  # 'none', 'minimal', 'standard', 'strict'
    documentation_requirement: str  # 'none', 'minimal', 'standard', 'strict'
    approval_required: bool  # Whether approvals are required
    automated_checks: List[str]  # List of automated checks to run
    time_limits: Dict[str, int]  # Time limits for various operations in minutes

    @classmethod
    def for_level(cls, level: DisciplineLevel) -> 'DisciplineSettings':
        """Create settings appropriate for a discipline level."""
        if level == DisciplineLevel.FAST:
            return cls(
                validation_level=2,
                review_frequency=2,
                testing_requirement='minimal',
                documentation_requirement='minimal',
                approval_required=False,
                automated_checks=['syntax_check'],
                time_limits={'code_generation': 5, 'review': 2}
            )
        elif level == DisciplineLevel.BALANCED:
            return cls(
                validation_level=5,
                review_frequency=5,
                testing_requirement='standard',
                documentation_requirement='standard',
                approval_required=True,
                automated_checks=['syntax_check', 'style_check'],
                time_limits={'code_generation': 15, 'review': 10}
            )
        elif level == DisciplineLevel.STRICT:
            return cls(
                validation_level=8,
                review_frequency=8,
                testing_requirement='strict',
                documentation_requirement='strict',
                approval_required=True,
                automated_checks=['syntax_check', 'style_check', 'security_scan', 'dependency_check'],
                time_limits={'code_generation': 30, 'review': 20}
            )
        else:
            # Default to balanced
            return cls.for_level(DisciplineLevel.BALANCED)


@dataclass
class DisciplineHistoryEntry:
    """Represents a change in discipline level."""
    level: DisciplineLevel
    timestamp: str
    reason: str = ""


class DisciplineController:
    """Controls discipline levels and methodology enforcement."""

    def __init__(self, project_path: str = ".dcae/discipline_settings.json"):
        """
        Initialize the discipline controller.

        Args:
            project_path: Path to the discipline settings file
        """
        self.settings_file_path = Path(project_path)
        self.current_level: DisciplineLevel = DisciplineLevel.BALANCED  # Default to balanced
        self.settings: DisciplineSettings = DisciplineSettings.for_level(self.current_level)
        self.history: List[DisciplineHistoryEntry] = []

        # Create directory if it doesn't exist
        self.settings_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing settings if available
        self.load_settings()

    def set_level(self, level: DisciplineLevel, reason: str = "") -> bool:
        """
        Set the discipline level for the project.

        Args:
            level: The discipline level to set
            reason: Reason for changing the discipline level

        Returns:
            True if the level was set successfully
        """
        old_level = self.current_level
        self.current_level = level
        self.settings = DisciplineSettings.for_level(level)

        # Add to history
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        entry = DisciplineHistoryEntry(
            level=level,
            timestamp=timestamp,
            reason=reason
        )
        self.history.append(entry)

        # Save settings
        self.save_settings()

        return True

    def get_current_level(self) -> DisciplineLevel:
        """
        Get the current discipline level.

        Returns:
            The current discipline level
        """
        return self.current_level

    def get_settings_for_level(self, level: DisciplineLevel) -> Dict[str, Any]:
        """
        Get settings appropriate for a specific discipline level.

        Args:
            level: The discipline level to get settings for

        Returns:
            Dictionary of settings for the level
        """
        settings = DisciplineSettings.for_level(level)
        return {
            'validation_level': settings.validation_level,
            'review_frequency': settings.review_frequency,
            'testing_requirement': settings.testing_requirement,
            'documentation_requirement': settings.documentation_requirement,
            'approval_required': settings.approval_required,
            'automated_checks': settings.automated_checks,
            'time_limits': settings.time_limits
        }

    def preview_settings_for_level(self, level: DisciplineLevel) -> Dict[str, Any]:
        """
        Preview what settings would be applied for a discipline level without changing.

        Args:
            level: The discipline level to preview settings for

        Returns:
            Dictionary of settings for the level
        """
        return self.get_settings_for_level(level)

    def save_settings(self, project_name: str = "default"):
        """
        Save the current discipline settings to file.

        Args:
            project_name: Name of the project for identification
        """
        data = {
            'current_level': self.current_level.value,
            'settings': {
                'validation_level': self.settings.validation_level,
                'review_frequency': self.settings.review_frequency,
                'testing_requirement': self.settings.testing_requirement,
                'documentation_requirement': self.settings.documentation_requirement,
                'approval_required': self.settings.approval_required,
                'automated_checks': self.settings.automated_checks,
                'time_limits': self.settings.time_limits
            },
            'history': [
                {
                    'level': entry.level.value,
                    'timestamp': entry.timestamp,
                    'reason': entry.reason
                }
                for entry in self.history
            ]
        }

        with open(self.settings_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_settings(self, project_name: str = "default") -> bool:
        """
        Load discipline settings from file.

        Args:
            project_name: Name of the project for identification

        Returns:
            True if settings were loaded successfully, False otherwise
        """
        if not self.settings_file_path.exists():
            # Create default settings file
            self.save_settings(project_name)
            return True

        try:
            with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load current level
            level_value = data.get('current_level', 'balanced')
            self.current_level = DisciplineLevel(level_value)

            # Load settings
            settings_data = data.get('settings', {})
            self.settings = DisciplineSettings(
                validation_level=settings_data.get('validation_level', 5),
                review_frequency=settings_data.get('review_frequency', 5),
                testing_requirement=settings_data.get('testing_requirement', 'standard'),
                documentation_requirement=settings_data.get('documentation_requirement', 'standard'),
                approval_required=settings_data.get('approval_required', True),
                automated_checks=settings_data.get('automated_checks', ['syntax_check', 'style_check']),
                time_limits=settings_data.get('time_limits', {'code_generation': 15, 'review': 10})
            )

            # Load history
            self.history = []
            for entry_data in data.get('history', []):
                entry = DisciplineHistoryEntry(
                    level=DisciplineLevel(entry_data['level']),
                    timestamp=entry_data['timestamp'],
                    reason=entry_data.get('reason', '')
                )
                self.history.append(entry)

            return True

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading discipline settings: {e}")
            # Create default settings file if there's an error
            self.save_settings(project_name)
            return False