"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Global Settings Configuration Module

Implementation for Epic #1: Project Setup & Management
Story 1.6: Global Settings Configuration

This module provides comprehensive global settings configuration functionality
as specified in the story acceptance criteria.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class DisciplineLevel(Enum):
    """Enumeration for discipline levels in DCAE framework."""
    FAST = "fast"
    BALANCED = "balanced"
    STRICT = "strict"


class SecurityLevel(Enum):
    """Enumeration for security levels of configuration settings."""
    PUBLIC = "public"
    SENSITIVE = "sensitive"
    SECRET = "secret"


@dataclass
class SettingSchema:
    """Defines the schema for a configuration setting."""
    name: str
    type: type
    required: bool = False
    default_value: Any = None
    validator: Optional[callable] = None
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    description: str = ""


class ConfigurationValidator:
    """Validates configuration settings against defined schemas."""

    @staticmethod
    def validate_discipline_level(value: str) -> bool:
        """Validate discipline level value."""
        return value in [level.value for level in DisciplineLevel]

    @staticmethod
    def validate_api_key(value: str) -> bool:
        """Basic validation for API keys."""
        return isinstance(value, str) and len(value.strip()) > 0

    @staticmethod
    def validate_log_level(value: str) -> bool:
        """Validate logging level."""
        return value.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    @staticmethod
    def validate_positive_integer(value: int) -> bool:
        """Validate positive integer values."""
        return isinstance(value, int) and value > 0

    @staticmethod
    def validate_percentage(value: float) -> bool:
        """Validate percentage values (0.0 to 1.0)."""
        return isinstance(value, (int, float)) and 0.0 <= value <= 1.0

    @staticmethod
    def validate_boolean(value: bool) -> bool:
        """Validate boolean values."""
        return isinstance(value, bool)


class GlobalSettingsSchema:
    """Defines the schema for global settings."""

    def __init__(self):
        self.schema = {
            "project": {
                "name": SettingSchema("project.name", str, False, "", None, SecurityLevel.PUBLIC, "Project name"),
                "version": SettingSchema("project.version", str, False, "0.1.0", None, SecurityLevel.PUBLIC, "Project version"),
                "created_date": SettingSchema("project.created_date", str, False, lambda: datetime.now().isoformat(), None, SecurityLevel.PUBLIC, "Project creation date")
            },
            "dcae": {
                "version": SettingSchema("dcae.version", str, False, "1.0.0", None, SecurityLevel.PUBLIC, "DCAE framework version"),
                "bmad_workflow": {
                    "enabled": SettingSchema("dcae.bmad_workflow.enabled", bool, False, True, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable BMAD workflow"),
                    "discipline_level": SettingSchema("dcae.bmad_workflow.discipline_level", str, False, "balanced", ConfigurationValidator.validate_discipline_level, SecurityLevel.PUBLIC, "Discipline level for workflow"),
                    "consensus_enabled": SettingSchema("dcae.bmad_workflow.consensus_enabled", bool, False, False, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable consensus mechanism"),
                    "performance_stats": {
                        "enabled": SettingSchema("dcae.bmad_workflow.performance_stats.enabled", bool, False, True, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable performance statistics"),
                        "collection_interval_minutes": SettingSchema("dcae.bmad_workflow.performance_stats.collection_interval_minutes", int, False, 5, ConfigurationValidator.validate_positive_integer, SecurityLevel.PUBLIC, "Collection interval for performance stats")
                    }
                },
                "llm_providers": {
                    "openai": {
                        "enabled": SettingSchema("dcae.llm_providers.openai.enabled", bool, False, False, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable OpenAI provider"),
                        "api_key": SettingSchema("dcae.llm_providers.openai.api_key", str, False, "", ConfigurationValidator.validate_api_key, SecurityLevel.SECRET, "OpenAI API key"),
                        "model": SettingSchema("dcae.llm_providers.openai.model", str, False, "gpt-4o", None, SecurityLevel.PUBLIC, "OpenAI model")
                    },
                    "anthropic": {
                        "enabled": SettingSchema("dcae.llm_providers.anthropic.enabled", bool, False, False, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable Anthropic provider"),
                        "api_key": SettingSchema("dcae.llm_providers.anthropic.api_key", str, False, "", ConfigurationValidator.validate_api_key, SecurityLevel.SECRET, "Anthropic API key"),
                        "model": SettingSchema("dcae.llm_providers.anthropic.model", str, False, "claude-3-5-sonnet-20241022", None, SecurityLevel.PUBLIC, "Anthropic model")
                    },
                    "qwen": {
                        "enabled": SettingSchema("dcae.llm_providers.qwen.enabled", bool, False, False, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable Qwen provider"),
                        "api_key": SettingSchema("dcae.llm_providers.qwen.api_key", str, False, "", ConfigurationValidator.validate_api_key, SecurityLevel.SECRET, "Qwen API key"),
                        "model": SettingSchema("dcae.llm_providers.qwen.model", str, False, "qwen-max", None, SecurityLevel.PUBLIC, "Qwen model")
                    },
                    "glm": {
                        "enabled": SettingSchema("dcae.llm_providers.glm.enabled", bool, False, False, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable GLM provider"),
                        "api_key": SettingSchema("dcae.llm_providers.glm.api_key", str, False, "", ConfigurationValidator.validate_api_key, SecurityLevel.SECRET, "GLM API key"),
                        "model": SettingSchema("dcae.llm_providers.glm.model", str, False, "glm-4", None, SecurityLevel.PUBLIC, "GLM model")
                    }
                },
                "logging": {
                    "level": SettingSchema("dcae.logging.level", str, False, "INFO", ConfigurationValidator.validate_log_level, SecurityLevel.PUBLIC, "Logging level"),
                    "file_output": SettingSchema("dcae.logging.file_output", bool, False, True, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable file logging"),
                    "console_output": SettingSchema("dcae.logging.console_output", bool, False, True, ConfigurationValidator.validate_boolean, SecurityLevel.PUBLIC, "Enable console logging")
                }
            }
        }

    def get_schema_by_path(self, path: str) -> Optional[SettingSchema]:
        """Get the schema for a setting at the specified path."""
        keys = path.split('.')
        current = self.schema

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current if isinstance(current, SettingSchema) else None


class HierarchicalConfigManager:
    """Manages configuration with hierarchical support for global, project, and workflow levels."""

    def __init__(self, global_config_path: Optional[Union[str, Path]] = None):
        self.global_config_path = Path(global_config_path) if global_config_path else Path(".dcae/global_config.yaml")
        self.schema = GlobalSettingsSchema()

        # Load global configuration
        self.global_config_data = self._load_config(self.global_config_path)

        # Project-specific and workflow-specific configs will be loaded as needed
        self.project_config_data = {}
        self.workflow_config_data = {}

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists."""
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            # Create default configuration based on schema
            default_config = self._get_default_config_from_schema()
            self._save_config(config_path, default_config)
            return default_config

    def _get_default_config_from_schema(self) -> Dict[str, Any]:
        """Generate default configuration based on schema definitions."""
        def build_defaults(schema_section):
            result = {}
            for key, value in schema_section.items():
                if isinstance(value, SettingSchema):
                    if callable(value.default_value):
                        result[key] = value.default_value()
                    else:
                        result[key] = value.default_value
                elif isinstance(value, dict):
                    result[key] = build_defaults(value)
            return result

        return build_defaults(self.schema.schema)

    def _save_config(self, config_path: Path, config_data: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def get_setting(self, key_path: str, default=None, config_level: str = "global"):
        """
        Get a configuration value using dot notation with hierarchical fallback.

        Args:
            key_path: Path to the value using dot notation (e.g., "dcae.version")
            default: Default value if key not found
            config_level: Level to check first ("global", "project", "workflow")

        Returns:
            The configuration value following hierarchy (specific overrides general)
        """
        # First check the requested level
        config_data = getattr(self, f"{config_level}_config_data")
        value = self._get_nested_value(config_data, key_path)

        if value is not None:
            return value

        # If not found at requested level, fall back to hierarchy
        hierarchy_order = {
            "workflow": ["workflow", "project", "global"],
            "project": ["project", "global"],
            "global": ["global"]
        }

        for level in hierarchy_order[config_level]:
            if level != config_level:  # Skip if we already checked this level
                config_data = getattr(self, f"{level}_config_data")
                value = self._get_nested_value(config_data, key_path)

                if value is not None:
                    return value

        return default

    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Helper to get a nested value using dot notation."""
        keys = key_path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def set_setting(self, key_path: str, value: Any, config_level: str = "global") -> bool:
        """
        Set a configuration value using dot notation at the specified level.

        Args:
            key_path: Path to the value using dot notation (e.g., "dcae.version")
            value: Value to set
            config_level: Level to set the configuration ("global", "project", "workflow")

        Returns:
            True if successful, False otherwise
        """
        # Validate the setting against schema
        schema_entry = self.schema.get_schema_by_path(key_path)
        if schema_entry:
            if schema_entry.validator and not schema_entry.validator(value):
                print(f"Validation failed for setting {key_path} with value {value}")
                return False

        # Get the appropriate config data based on level
        config_data = getattr(self, f"{config_level}_config_data")

        # Navigate to the parent of the target key
        keys = key_path.split('.')
        current = config_data

        for key in keys[:-1]:
            if not isinstance(current, dict):
                print(f"Error: Configuration path invalid at '{key}'")
                return False
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final key
        current[keys[-1]] = value

        # Save the updated configuration
        config_path = getattr(self, f"{config_level}_config_path", self.global_config_path)
        return self._save_config(config_path, config_data)

    def validate_setting(self, key_path: str, value: Any) -> bool:
        """Validate a setting value against its schema."""
        schema_entry = self.schema.get_schema_by_path(key_path)
        if not schema_entry:
            print(f"No schema found for setting: {key_path}")
            return False

        if schema_entry.validator:
            return schema_entry.validator(value)
        return True

    def get_secure_display_config(self) -> Dict[str, Any]:
        """Get configuration with sensitive data masked for display purposes."""
        # Make a deep copy of the config
        safe_config = json.loads(json.dumps(self.global_config_data))

        def mask_sensitive_values(data):
            for key, value in data.items():
                if isinstance(value, dict):
                    mask_sensitive_values(value)
                else:
                    schema_entry = self.schema.get_schema_by_path(key)
                    if schema_entry and schema_entry.security_level == SecurityLevel.SECRET:
                        data[key] = "*" * len(str(value)) if value else ""

        mask_sensitive_values(safe_config)
        return safe_config

    def load_project_config(self, project_path: Union[str, Path]):
        """Load project-specific configuration."""
        project_config_path = Path(project_path) / ".dcae" / "config.yaml"
        self.project_config_data = self._load_config(project_config_path)
        self.project_config_path = project_config_path

    def load_workflow_config(self, workflow_path: Union[str, Path]):
        """Load workflow-specific configuration."""
        workflow_config_path = Path(workflow_path) / "workflow_config.yaml"
        self.workflow_config_data = self._load_config(workflow_config_path)
        self.workflow_config_path = workflow_config_path


class GlobalSettingsManager:
    """High-level manager for global settings configuration as specified in Story 1.6."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.hierarchical_manager = HierarchicalConfigManager(config_path)

    def configure_global_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """
        Configure multiple global settings at once with validation.

        Args:
            settings_dict: Dictionary mapping setting paths to values

        Returns:
            True if all settings were configured successfully, False otherwise
        """
        print("Configuring global settings...")

        all_successful = True
        for key_path, value in settings_dict.items():
            success = self.set_global_setting(key_path, value)
            if not success:
                all_successful = False
                print(f"  ✗ Failed to set {key_path} = {value}")
            else:
                print(f"  ✓ {key_path} = {value}")

        if all_successful:
            print("✓ All global settings configured successfully")
        else:
            print("✗ Some settings failed to configure")

        return all_successful

    def set_global_setting(self, key_path: str, value: Any) -> bool:
        """
        Set a global setting with validation and security measures.

        Args:
            key_path: Path to the setting using dot notation
            value: Value to set

        Returns:
            True if successful, False otherwise
        """
        return self.hierarchical_manager.set_setting(key_path, value, "global")

    def get_global_setting(self, key_path: str, default=None) -> Any:
        """
        Get a global setting value.

        Args:
            key_path: Path to the setting using dot notation
            default: Default value if not found

        Returns:
            The setting value or default
        """
        return self.hierarchical_manager.get_setting(key_path, default, "global")

    def validate_configuration(self, config_to_validate: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Validate the entire configuration or a specific configuration dictionary.

        Args:
            config_to_validate: Configuration to validate (uses global config if None)

        Returns:
            List of validation errors found
        """
        if config_to_validate is None:
            config_to_validate = self.hierarchical_manager.global_config_data

        errors = []

        def validate_recursive(data, path_prefix=""):
            for key, value in data.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key

                if isinstance(value, dict):
                    validate_recursive(value, current_path)
                else:
                    schema_entry = self.hierarchical_manager.schema.get_schema_by_path(current_path)
                    if schema_entry and schema_entry.validator:
                        if not schema_entry.validator(value):
                            errors.append(f"Validation failed for {current_path}: {value}")

        validate_recursive(config_to_validate)
        return errors

    def show_configuration(self, hide_sensitive: bool = True) -> Dict[str, Any]:
        """
        Show current configuration with optional hiding of sensitive data.

        Args:
            hide_sensitive: Whether to mask sensitive data (API keys, etc.)

        Returns:
            Current configuration
        """
        if hide_sensitive:
            return self.hierarchical_manager.get_secure_display_config()
        else:
            return self.hierarchical_manager.global_config_data

    def backup_configuration(self, backup_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Create a backup of the current configuration.

        Args:
            backup_path: Path for backup file (uses default if None)

        Returns:
            True if successful, False otherwise
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f".dcae/backups/global_config_backup_{timestamp}.yaml"

        backup_path = Path(backup_path)
        current_config = self.hierarchical_manager.global_config_data

        try:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(backup_path, 'w', encoding='utf-8') as f:
                yaml.dump(current_config, f, default_flow_style=False, allow_unicode=True)
            print(f"✓ Configuration backed up to {backup_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to backup configuration: {e}")
            return False

    def restore_configuration(self, backup_path: Union[str, Path]) -> bool:
        """
        Restore configuration from a backup file.

        Args:
            backup_path: Path to backup file

        Returns:
            True if successful, False otherwise
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            print(f"✗ Backup file does not exist: {backup_path}")
            return False

        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                restored_config = yaml.safe_load(f)

            # Validate the restored configuration before applying
            validation_errors = self.validate_configuration(restored_config)
            if validation_errors:
                print("✗ Restored configuration has validation errors:")
                for error in validation_errors:
                    print(f"  - {error}")
                return False

            # Apply the restored configuration
            self.hierarchical_manager.global_config_data = restored_config
            success = self.hierarchical_manager._save_config(
                self.hierarchical_manager.global_config_path,
                restored_config
            )

            if success:
                print(f"✓ Configuration restored from {backup_path}")
            else:
                print(f"✗ Failed to save restored configuration")

            return success
        except Exception as e:
            print(f"✗ Failed to restore configuration: {e}")
            return False


def main():
    """Main function to demonstrate global settings configuration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="DCAE Global Settings Configuration Tool"
    )

    parser.add_argument(
        "action",
        choices=[
            "configure", "get-setting", "set-setting", "show-config",
            "validate-config", "backup", "restore"
        ],
        help="Global settings action to perform"
    )

    parser.add_argument("--setting-path", help="Setting path (e.g., dcae.version)")
    parser.add_argument("--setting-value", help="Setting value to set")
    parser.add_argument("--settings-file", help="Path to settings file")
    parser.add_argument("--backup-path", help="Path for backup/restore operations")
    parser.add_argument("--show-sensitive", action="store_true",
                       help="Show sensitive settings unmasked")

    args = parser.parse_args()

    settings_manager = GlobalSettingsManager(args.settings_file)

    if args.action == "configure":
        print("Interactive global settings configuration is not implemented in this demo")
        print("Use set-setting to configure individual settings")

    elif args.action == "get-setting":
        if not args.setting_path:
            print("Error: --setting-path is required for get-setting")
            sys.exit(1)

        value = settings_manager.get_global_setting(args.setting_path)
        print(f"Value for {args.setting_path}: {value}")

    elif args.action == "set-setting":
        if not args.setting_path or not args.setting_value:
            print("Error: Both --setting-path and --setting-value are required for set-setting")
            sys.exit(1)

        # Try to convert value to appropriate type
        try:
            # Attempt to parse as boolean
            if args.setting_value.lower() in ('true', 'false'):
                value = args.setting_value.lower() == 'true'
            # Attempt to parse as integer
            elif args.setting_value.isdigit():
                value = int(args.setting_value)
            # Attempt to parse as float
            elif '.' in args.setting_value:
                try:
                    value = float(args.setting_value)
                except ValueError:
                    value = args.setting_value  # Keep as string if not a valid float
            else:
                value = args.setting_value
        except:
            value = args.setting_value  # Default to string if parsing fails

        success = settings_manager.set_global_setting(args.setting_path, value)
        sys.exit(0 if success else 1)

    elif args.action == "show-config":
        config = settings_manager.show_configuration(hide_sensitive=not args.show_sensitive)
        print("Current Global Configuration:")
        print(yaml.dump(config, default_flow_style=False, allow_unicode=True))

    elif args.action == "validate-config":
        errors = settings_manager.validate_configuration()
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("✓ Configuration is valid")

    elif args.action == "backup":
        backup_path = args.backup_path
        success = settings_manager.backup_configuration(backup_path)
        sys.exit(0 if success else 1)

    elif args.action == "restore":
        if not args.backup_path:
            print("Error: --backup-path is required for restore")
            sys.exit(1)

        success = settings_manager.restore_configuration(args.backup_path)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()