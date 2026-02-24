"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Project Configuration Module

This module implements project configuration functionality as specified in
Epic #1: Project Setup & Management, specifically:
- Story 1.2: Project Configuration
- Story 1.6: Global System Settings Configuration
- Story 1.7: API Key Management
- Story 1.9: Update Settings Without Interruption
- Story 1.10: Logging/Error Reporting
- Story 1.11: Progress Indicators

As a developer,
I want to configure project settings effectively,
so that I can customize the DCAE framework behavior for my specific project needs.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from enum import Enum

from .config_management import DCAEConfig, ConfigurationManager, DisciplineLevel


class ProjectConfigManager:
    """Manager class for project-specific configuration as per Story 1.2."""

    def __init__(self, project_path: Union[str, Path] = "."):
        self.project_path = Path(project_path)
        self.config_path = self.project_path / ".dcae/config.yaml"
        self.state_path = self.project_path / ".dcae/state.json"

        # Ensure .dcae directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        self.config = DCAEConfig(self.config_path)

    def configure_project_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Configure project-specific settings as per Story 1.2.

        Args:
            settings: Dictionary of project settings to configure

        Returns:
            True if successful, False otherwise
        """
        print(f"Configuring project settings for: {self.project_path.name}")

        # Validate settings
        valid_settings = self._validate_project_settings(settings)
        if not valid_settings:
            print("Invalid settings provided")
            return False

        # Apply settings
        config_manager = ConfigurationManager(self.config_path)
        return config_manager.update_global_settings(valid_settings)

    def _validate_project_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate project settings against allowed configurations.

        Args:
            settings: Settings to validate

        Returns:
            Validated settings or empty dict if invalid
        """
        # Define allowed settings for project configuration
        allowed_paths = [
            "dcae.bmad_workflow.discipline_level",
            "dcae.bmad_workflow.consensus_enabled",
            "dcae.bmad_workflow.performance_stats.enabled",
            "dcae.bmad_workflow.performance_stats.collection_interval_minutes",
            "dcae.logging.level",
            "dcae.logging.file_output",
            "dcae.logging.console_output"
        ]

        validated = {}
        for key_path, value in settings.items():
            if key_path in allowed_paths:
                validated[key_path] = value
            else:
                print(f"Warning: Setting '{key_path}' not allowed for project configuration")

        return validated

    def get_project_info(self) -> Dict[str, Any]:
        """Get current project information."""
        return {
            "name": self.config.get("project.name", ""),
            "version": self.config.get("project.version", ""),
            "created_date": self.config.get("project.created_date", ""),
            "configured_features": self._get_configured_features()
        }

    def _get_configured_features(self) -> List[str]:
        """Get list of currently configured features."""
        features = []
        if self.config.get("dcae.bmad_workflow.enabled", False):
            features.append("BMAD Workflow")
        if self.config.get("dcae.bmad_workflow.consensus_enabled", False):
            features.append("Consensus Validation")
        if self.config.get("dcae.bmad_workflow.performance_stats.enabled", False):
            features.append("Performance Stats")
        if any(provider["enabled"] and provider["api_key"]
               for provider in self.config.config_data["dcae"]["llm_providers"].values()):
            features.append("LLM Providers")

        return features

    def update_discipline_level(self, level: DisciplineLevel) -> bool:
        """Update the discipline level as per Story 1.2."""
        return self.config.set("dcae.bmad_workflow.discipline_level", level.value)

    def get_current_discipline_level(self) -> DisciplineLevel:
        """Get the current discipline level."""
        level_str = self.config.get("dcae.bmad_workflow.discipline_level", "balanced")
        return DisciplineLevel(level_str)

    def save_project_state(self, stage: str, completed: bool = True) -> bool:
        """Save project state to track progress."""
        if not self.state_path.exists():
            # Create default state if it doesn't exist
            default_state = {
                "current_stage": "initial",
                "stages": {
                    "business": {"completed": False, "timestamp": None},
                    "architecture": {"completed": False, "timestamp": None},
                    "development": {"completed": False, "timestamp": None},
                    "quality_assurance": {"completed": False, "timestamp": None}
                },
                "last_updated": datetime.now().isoformat()
            }
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(default_state, f, indent=2)

        # Load current state
        with open(self.state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # Update the specific stage
        if stage in state["stages"]:
            state["stages"][stage]["completed"] = completed
            state["stages"][stage]["timestamp"] = datetime.now().isoformat()
            state["last_updated"] = datetime.now().isoformat()
            state["current_stage"] = stage if completed else state["current_stage"]

        # Save updated state
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

        return True

    def get_project_state(self) -> Dict[str, Any]:
        """Get current project state."""
        if not self.state_path.exists():
            return {
                "current_stage": "initial",
                "stages": {
                    "business": {"completed": False, "timestamp": None},
                    "architecture": {"completed": False, "timestamp": None},
                    "development": {"completed": False, "timestamp": None},
                    "quality_assurance": {"completed": False, "timestamp": None}
                },
                "last_updated": None
            }

        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)


class GlobalSettingsManager:
    """Manager for global system settings as per Story 1.6."""

    def __init__(self, config_path: Union[str, Path] = ".dcae/config.yaml"):
        self.config = DCAEConfig(config_path)

    def configure_global_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Configure global system settings as per Story 1.6.

        Args:
            settings: Dictionary of global settings to configure

        Returns:
            True if successful, False otherwise
        """
        print("Configuring global system settings...")

        # Validate settings
        validated_settings = self._validate_global_settings(settings)
        if not validated_settings:
            print("Invalid global settings provided")
            return False

        # Apply settings
        config_manager = ConfigurationManager(self.config.config_path)
        return config_manager.update_global_settings(validated_settings)

    def _validate_global_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate global settings against allowed configurations.

        Args:
            settings: Settings to validate

        Returns:
            Validated settings or empty dict if invalid
        """
        # Define allowed global settings
        allowed_paths = [
            "dcae.bmad_workflow.discipline_level",
            "dcae.bmad_workflow.consensus_enabled",
            "dcae.bmad_workflow.performance_stats.enabled",
            "dcae.bmad_workflow.performance_stats.collection_interval_minutes",
            "dcae.logging.level",
            "dcae.logging.file_output",
            "dcae.logging.console_output",
            "project.name",
            "project.version"
        ]

        validated = {}
        for key_path, value in settings.items():
            if key_path in allowed_paths:
                validated[key_path] = value
            else:
                print(f"Warning: Global setting '{key_path}' not recognized")

        return validated

    def get_global_settings(self) -> Dict[str, Any]:
        """Get current global settings."""
        return {
            "discipline_level": self.config.get("dcae.bmad_workflow.discipline_level"),
            "consensus_enabled": self.config.get("dcae.bmad_workflow.consensus_enabled"),
            "performance_stats_enabled": self.config.get("dcae.bmad_workflow.performance_stats.enabled"),
            "log_level": self.config.get("dcae.logging.level"),
            "log_file_output": self.config.get("dcae.logging.file_output"),
            "log_console_output": self.config.get("dcae.logging.console_output")
        }


class APIKeyManager:
    """Manager for API key management as per Story 1.7."""

    def __init__(self, config_path: Union[str, Path] = ".dcae/config.yaml"):
        self.config = DCAEConfig(config_path)

    def set_api_key(self, provider: str, api_key: str, enable: bool = True) -> bool:
        """
        Set API key for a provider as per Story 1.7.

        Args:
            provider: Name of the provider (openai, anthropic, qwen, glm)
            api_key: API key value
            enable: Whether to enable the provider after setting the key

        Returns:
            True if successful, False otherwise
        """
        print(f"Setting API key for {provider}...")

        if provider not in self.config.config_data["dcae"]["llm_providers"]:
            print(f"Error: Provider '{provider}' not supported")
            return False

        # Validate API key format (basic check)
        if not api_key or len(api_key.strip()) == 0:
            print("Error: API key cannot be empty")
            return False

        # Update the configuration
        self.config.config_data["dcae"]["llm_providers"][provider]["api_key"] = api_key
        self.config.config_data["dcae"]["llm_providers"][provider]["enabled"] = enable

        # Save the updated configuration
        success = self.config._save_config(self.config.config_data)
        if success:
            status = "enabled" if enable else "disabled"
            print(f"✓ API key for {provider} set and {status}")
        else:
            print(f"✗ Failed to set API key for {provider}")

        return success

    def remove_api_key(self, provider: str) -> bool:
        """
        Remove API key for a provider.

        Args:
            provider: Name of the provider

        Returns:
            True if successful, False otherwise
        """
        print(f"Removing API key for {provider}...")

        if provider not in self.config.config_data["dcae"]["llm_providers"]:
            print(f"Error: Provider '{provider}' not supported")
            return False

        # Remove the API key and disable the provider
        self.config.config_data["dcae"]["llm_providers"][provider]["api_key"] = ""
        self.config.config_data["dcae"]["llm_providers"][provider]["enabled"] = False

        # Save the updated configuration
        success = self.config._save_config(self.config.config_data)
        if success:
            print(f"✓ API key for {provider} removed and provider disabled")
        else:
            print(f"✗ Failed to remove API key for {provider}")

        return success

    def get_api_key_status(self) -> Dict[str, Dict[str, Union[bool, str]]]:
        """Get status of all configured API keys."""
        status = {}
        for provider, config in self.config.config_data["dcae"]["llm_providers"].items():
            status[provider] = {
                "enabled": config["enabled"],
                "has_key": bool(config["api_key"]),
                "key_preview": f"{config['api_key'][:5]}..." if config["api_key"] else ""
            }
        return status

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled providers with valid API keys."""
        enabled = []
        for provider, config in self.config.config_data["dcae"]["llm_providers"].items():
            if config["enabled"] and config["api_key"]:
                enabled.append(provider)
        return enabled


class SettingsUpdater:
    """Handles updating settings without interrupting processes as per Story 1.9."""

    def __init__(self, config_path: Union[str, Path] = ".dcae/config.yaml"):
        self.config = DCAEConfig(config_path)

    def update_settings_live(self, settings: Dict[str, Any]) -> bool:
        """
        Update settings without interrupting ongoing processes as per Story 1.9.

        Args:
            settings: Dictionary of settings to update

        Returns:
            True if successful, False otherwise
        """
        print("Updating settings without interrupting processes...")

        # In a real implementation, this would:
        # 1. Check if any processes are currently running
        # 2. Queue the configuration changes
        # 3. Apply changes during safe transition points
        # 4. Update running processes with new configuration

        # For now, we'll simulate the process
        config_manager = ConfigurationManager(self.config.config_path)

        # Validate settings before applying
        validated_settings = self._validate_settings_for_live_update(settings)
        if not validated_settings:
            print("Settings not suitable for live update")
            return False

        # Apply the validated settings
        success = config_manager.update_global_settings(validated_settings)

        if success:
            print("✓ Settings updated successfully without interruption")
        else:
            print("✗ Failed to update settings")

        return success

    def _validate_settings_for_live_update(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate settings to ensure they can be updated live.

        Args:
            settings: Settings to validate

        Returns:
            Validated settings or empty dict if not suitable for live update
        """
        # Settings that are safe to update live (don't affect running processes significantly)
        live_update_safe = [
            "dcae.logging.level",
            "dcae.bmad_workflow.performance_stats.collection_interval_minutes",
            "dcae.bmad_workflow.consensus_enabled"
        ]

        validated = {}
        for key_path, value in settings.items():
            if key_path in live_update_safe:
                validated[key_path] = value
            else:
                print(f"Warning: Setting '{key_path}' may require process restart")

        return validated


class LoggingErrorReporter:
    """Handles logging and error reporting as per Story 1.10."""

    def __init__(self, config_path: Union[str, Path] = ".dcae/config.yaml"):
        self.config = DCAEConfig(config_path)

    def configure_logging(self, level: str = "INFO", file_output: bool = True,
                         console_output: bool = True) -> bool:
        """
        Configure logging as per Story 1.10.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            file_output: Enable/disable file logging
            console_output: Enable/disable console logging

        Returns:
            True if successful, False otherwise
        """
        print(f"Configuring logging: level={level}, file={file_output}, console={console_output}")

        # Validate logging level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level.upper() not in valid_levels:
            print(f"Error: Invalid log level. Valid options: {valid_levels}")
            return False

        # Update logging configuration
        logging_config = {
            "dcae.logging.level": level.upper(),
            "dcae.logging.file_output": file_output,
            "dcae.logging.console_output": console_output
        }

        config_manager = ConfigurationManager(self.config.config_path)
        success = config_manager.update_global_settings(logging_config)

        if success:
            print(f"✓ Logging configured: {level} level, file={file_output}, console={console_output}")
        else:
            print("✗ Failed to configure logging")

        return success

    def log_event(self, level: str, message: str, category: str = "general"):
        """
        Log an event with specified level and category.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Log message
            category: Category of the event
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] [{category}] {message}"

        # Output to console if enabled
        if self.config.get("dcae.logging.console_output", True):
            print(log_entry)

        # Write to file if enabled
        if self.config.get("dcae.logging.file_output", True):
            log_file = Path(".dcae/logs/dcae.log")
            log_file.parent.mkdir(parents=True, exist_ok=True)

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')

    def report_error(self, error_msg: str, error_type: str = "general",
                    component: str = "system", context: str = ""):
        """
        Report an error with context.

        Args:
            error_msg: Error message
            error_type: Type of error
            component: Component where error occurred
            context: Additional context about the error
        """
        self.log_event("ERROR",
                      f"[{component}] {error_type} error: {error_msg} - Context: {context}",
                      "error")


class ProgressIndicator:
    """Provides progress indicators as per Story 1.11."""

    def __init__(self, config_path: Union[str, Path] = ".dcae/config.yaml"):
        self.config = DCAEConfig(config_path)
        self.indicators_file = Path(".dcae/indicators.json")
        self.indicators_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize indicators file if it doesn't exist
        if not self.indicators_file.exists():
            self._initialize_indicators()

    def _initialize_indicators(self):
        """Initialize the indicators file with default values."""
        default_indicators = {
            "performance_stats": {
                "enabled": self.config.get("dcae.bmad_workflow.performance_stats.enabled", True),
                "collection_interval_minutes": self.config.get("dcae.bmad_workflow.performance_stats.collection_interval_minutes", 5),
                "stats": {}
            },
            "workflow_progress": {
                "current_stage": "initial",
                "overall_progress": 0,
                "stage_progress": {}
            }
        }

        with open(self.indicators_file, 'w', encoding='utf-8') as f:
            json.dump(default_indicators, f, indent=2)

    def update_progress(self, stage: str, progress: int, details: Dict[str, Any] = None):
        """
        Update progress for a specific stage.

        Args:
            stage: Stage name
            progress: Progress percentage (0-100)
            details: Additional details about the progress
        """
        if not self.indicators_file.exists():
            self._initialize_indicators()

        with open(self.indicators_file, 'r', encoding='utf-8') as f:
            indicators = json.load(f)

        # Update stage progress
        indicators["workflow_progress"]["stage_progress"][stage] = {
            "progress": min(max(progress, 0), 100),  # Clamp between 0-100
            "updated": datetime.now().isoformat(),
            "details": details or {}
        }

        # Calculate overall progress
        stages = indicators["workflow_progress"]["stage_progress"]
        if stages:
            total_progress = sum(stage_data["progress"] for stage_data in stages.values())
            overall_progress = total_progress / len(stages)
            indicators["workflow_progress"]["overall_progress"] = round(overall_progress, 2)

        # Update current stage
        indicators["workflow_progress"]["current_stage"] = stage

        # Save updated indicators
        with open(self.indicators_file, 'w', encoding='utf-8') as f:
            json.dump(indicators, f, indent=2)

        # Display progress if logging is enabled
        if self.config.get("dcae.logging.console_output", True):
            print(f"Progress: {stage} - {progress}% complete")

    def record_performance_stat(self, stat_name: str, value: Union[int, float, str],
                              unit: str = "", timestamp: datetime = None):
        """
        Record a performance statistic.

        Args:
            stat_name: Name of the statistic
            value: Value of the statistic
            unit: Unit of measurement
            timestamp: Timestamp for the recording (defaults to now)
        """
        if not self.indicators_file.exists():
            self._initialize_indicators()

        with open(self.indicators_file, 'r', encoding='utf-8') as f:
            indicators = json.load(f)

        if not indicators["performance_stats"]["enabled"]:
            return

        if timestamp is None:
            timestamp = datetime.now()

        # Create stats entry
        stat_entry = {
            "value": value,
            "unit": unit,
            "recorded": timestamp.isoformat()
        }

        # Add to stats collection
        if "stats" not in indicators["performance_stats"]:
            indicators["performance_stats"]["stats"] = {}

        if stat_name not in indicators["performance_stats"]["stats"]:
            indicators["performance_stats"]["stats"][stat_name] = []

        # Add the new entry
        indicators["performance_stats"]["stats"][stat_name].append(stat_entry)

        # Limit history to last 100 entries per stat
        if len(indicators["performance_stats"]["stats"][stat_name]) > 100:
            indicators["performance_stats"]["stats"][stat_name] = \
                indicators["performance_stats"]["stats"][stat_name][-100:]

        # Save updated indicators
        with open(self.indicators_file, 'w', encoding='utf-8') as f:
            json.dump(indicators, f, indent=2)

    def get_current_indicators(self) -> Dict[str, Any]:
        """Get current progress and performance indicators."""
        if not self.indicators_file.exists():
            self._initialize_indicators()

        with open(self.indicators_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def display_progress_summary(self):
        """Display a summary of current progress indicators."""
        indicators = self.get_current_indicators()

        print("\nDCAE Progress Indicators")
        print("=" * 30)
        print(f"Overall Progress: {indicators['workflow_progress']['overall_progress']}%")
        print(f"Current Stage: {indicators['workflow_progress']['current_stage']}")

        print("\nStage Progress:")
        for stage, data in indicators["workflow_progress"]["stage_progress"].items():
            print(f"  {stage}: {data['progress']}%")

        if indicators["performance_stats"]["enabled"]:
            print("\nPerformance Stats Enabled")
            print(f"Collection Interval: {indicators['performance_stats']['collection_interval_minutes']} min")
        else:
            print("\nPerformance Stats: Disabled")


# Convenience functions for Epic #1 stories
def configure_project_management_features():
    """Configure all project management features as per Epic #1."""
    print("Configuring Project Management Features (Epic #1)...")

    # Initialize managers
    project_config = ProjectConfigManager()
    global_settings = GlobalSettingsManager()
    api_manager = APIKeyManager()
    settings_updater = SettingsUpdater()
    logger = LoggingErrorReporter()
    progress = ProgressIndicator()

    print("✓ All Epic #1 managers initialized")

    # Example configuration
    project_settings = {
        "dcae.bmad_workflow.discipline_level": "balanced",
        "dcae.bmad_workflow.consensus_enabled": False,
        "dcae.bmad_workflow.performance_stats.enabled": True
    }

    success = project_config.configure_project_settings(project_settings)
    if success:
        print("✓ Project configuration applied")
    else:
        print("✗ Project configuration failed")

    # Configure logging
    logger.configure_logging(level="INFO", file_output=True, console_output=True)

    # Update progress indicator
    progress.update_progress("project_setup", 100, {"feature": "configuration"})

    return {
        "project_config": project_config,
        "global_settings": global_settings,
        "api_manager": api_manager,
        "settings_updater": settings_updater,
        "logger": logger,
        "progress": progress
    }


def pause_project_workflow():
    """Function to pause the project workflow as per Story 1.4."""
    state_manager = ProjectConfigManager()

    # Save current state before pausing
    current_stage = state_manager.config.get("dcae.bmad_workflow.current_stage", "unknown")
    state_manager.save_project_state(current_stage, completed=False)

    print(f"✓ Workflow paused at stage: {current_stage}")
    return current_stage


def resume_project_workflow():
    """Function to resume the project workflow as per Story 1.4."""
    state_manager = ProjectConfigManager()

    state = state_manager.get_project_state()
    current_stage = state.get("current_stage", "initial")

    print(f"✓ Resuming workflow from stage: {current_stage}")
    return current_stage


def manage_multiple_projects():
    """Function to manage multiple projects as per Story 1.5."""
    projects_dir = Path("./dcae-projects")
    projects_dir.mkdir(exist_ok=True)

    projects = []
    for item in projects_dir.iterdir():
        if item.is_dir():
            config_path = item / ".dcae/config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    project_name = config.get("project", {}).get("name", item.name)
                    projects.append({
                        "name": project_name,
                        "path": str(item),
                        "version": config.get("project", {}).get("version", "unknown")
                    })

    return projects


if __name__ == "__main__":
    # Example usage
    managers = configure_project_management_features()

    # Example: Set an API key
    api_manager = managers["api_manager"]
    api_manager.set_api_key("openai", "sk-...your-api-key...", enable=True)

    # Example: Update progress
    progress = managers["progress"]
    progress.update_progress("requirements_analysis", 45, {"items_completed": 3, "items_total": 7})

    # Example: Log an event
    logger = managers["logger"]
    logger.log_event("INFO", "Project configuration completed", "setup")