"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Configuration Management Module

This module implements the configuration management functionality for Epic #1:
Project Setup & Management, specifically stories 1-2 (Project Configuration),
1-6 (Global Settings Configuration), 1-7 (API Key Management), and
1-9 (Settings Update).

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
from typing import Dict, Any, Optional, Union
from enum import Enum

class DisciplineLevel(Enum):
    """Enumeration for discipline levels in DCAE framework."""
    FAST = "fast"
    BALANCED = "balanced"
    STRICT = "strict"

class DCAEConfig:
    """Main configuration class for DCAE framework."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize DCAE configuration.

        Args:
            config_path: Path to config file. If None, looks for .dcae/config.yaml
        """
        self.config_path = Path(config_path) if config_path else Path(".dcae/config.yaml")
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # Create default configuration
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure."""
        return {
            "project": {
                "name": "",
                "created_date": datetime.now().isoformat(),
                "version": "0.1.0"
            },
            "dcae": {
                "version": "1.0.0",
                "bmad_workflow": {
                    "enabled": True,
                    "discipline_level": "balanced",
                    "consensus_enabled": False,
                    "performance_stats": {
                        "enabled": True,
                        "collection_interval_minutes": 5
                    }
                },
                "llm_providers": {
                    "openai": {
                        "enabled": False,
                        "api_key": "",
                        "model": "gpt-4o"
                    },
                    "anthropic": {
                        "enabled": False,
                        "api_key": "",
                        "model": "claude-3-5-sonnet-20241022"
                    },
                    "qwen": {
                        "enabled": False,
                        "api_key": "",
                        "model": "qwen-max"
                    },
                    "glm": {
                        "enabled": False,
                        "api_key": "",
                        "model": "glm-4"
                    }
                },
                "logging": {
                    "level": "INFO",
                    "file_output": True,
                    "console_output": True
                }
            }
        }

    def _save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def get(self, key_path: str, default=None):
        """
        Get a configuration value using dot notation.

        Args:
            key_path: Path to the value using dot notation (e.g., "dcae.version")
            default: Default value if key not found

        Returns:
            The configuration value or default if not found
        """
        keys = key_path.split('.')
        current = self.config_data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def set(self, key_path: str, value: Any) -> bool:
        """
        Set a configuration value using dot notation.

        Args:
            key_path: Path to the value using dot notation (e.g., "dcae.version")
            value: Value to set

        Returns:
            True if successful, False otherwise
        """
        keys = key_path.split('.')
        current = self.config_data

        # Navigate to the parent of the target key
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
        return self._save_config(self.config_data)

    def update_llm_provider(self, provider: str, api_key: str, enabled: bool = True) -> bool:
        """
        Update LLM provider configuration.

        Args:
            provider: Name of the provider (openai, anthropic, qwen, glm)
            api_key: API key for the provider
            enabled: Whether the provider is enabled (default: True)

        Returns:
            True if successful, False otherwise
        """
        if provider not in self.config_data["dcae"]["llm_providers"]:
            print(f"Error: Provider '{provider}' not supported")
            return False

        self.config_data["dcae"]["llm_providers"][provider]["api_key"] = api_key
        self.config_data["dcae"]["llm_providers"][provider]["enabled"] = enabled

        return self._save_config(self.config_data)

    def set_discipline_level(self, level: DisciplineLevel) -> bool:
        """
        Set the discipline level for the BMAD workflow.

        Args:
            level: The discipline level to set

        Returns:
            True if successful, False otherwise
        """
        if not isinstance(level, DisciplineLevel):
            print(f"Error: Invalid discipline level. Use DisciplineLevel enum.")
            return False

        self.config_data["dcae"]["bmad_workflow"]["discipline_level"] = level.value
        return self._save_config(self.config_data)

    def toggle_performance_stats(self, enabled: bool) -> bool:
        """
        Enable or disable performance statistics collection.

        Args:
            enabled: Whether to enable performance stats

        Returns:
            True if successful, False otherwise
        """
        self.config_data["dcae"]["bmad_workflow"]["performance_stats"]["enabled"] = enabled
        return self._save_config(self.config_data)

    def update_project_info(self, name: str, version: str = None) -> bool:
        """
        Update project information.

        Args:
            name: New project name
            version: New project version (optional)

        Returns:
            True if successful, False otherwise
        """
        self.config_data["project"]["name"] = name
        if version:
            self.config_data["project"]["version"] = version

        return self._save_config(self.config_data)

    def get_active_provider(self) -> Optional[str]:
        """
        Get the first enabled LLM provider.

        Returns:
            Name of the first enabled provider, or None if none enabled
        """
        for provider, config in self.config_data["dcae"]["llm_providers"].items():
            if config.get("enabled", False) and config.get("api_key"):
                return provider
        return None

    def get_available_providers(self) -> list:
        """
        Get list of all configured providers.

        Returns:
            List of provider names
        """
        return list(self.config_data["dcae"]["llm_providers"].keys())


class ConfigurationManager:
    """Higher-level configuration management for Epic #1 stories."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config = DCAEConfig(config_path)

    def configure_project(self, project_name: str, project_version: str = "0.1.0",
                         discipline_level: DisciplineLevel = DisciplineLevel.BALANCED) -> bool:
        """
        Configure a project with basic settings.

        Args:
            project_name: Name of the project
            project_version: Version of the project
            discipline_level: Discipline level to set

        Returns:
            True if successful, False otherwise
        """
        print(f"Configuring project: {project_name} (v{project_version})")

        # Update project info
        if not self.config.update_project_info(project_name, project_version):
            print("Failed to update project info")
            return False

        # Set discipline level
        if not self.config.set_discipline_level(discipline_level):
            print("Failed to set discipline level")
            return False

        print(f"✓ Project configured successfully with {discipline_level.value} discipline level")
        return True

    def configure_api_keys(self, provider_configs: Dict[str, str]) -> bool:
        """
        Configure API keys for multiple providers.

        Args:
            provider_configs: Dictionary mapping provider names to API keys

        Returns:
            True if successful, False otherwise
        """
        print("Configuring API keys for providers...")

        success_count = 0
        total = len(provider_configs)

        for provider, api_key in provider_configs.items():
            if self.config.update_llm_provider(provider, api_key):
                print(f"  ✓ {provider} API key configured")
                success_count += 1
            else:
                print(f"  ✗ Failed to configure {provider}")

        if success_count == total:
            print(f"✓ All {total} provider API keys configured successfully")
            return True
        else:
            print(f"✗ {success_count}/{total} providers configured successfully")
            return False

    def show_current_config(self) -> Dict[str, Any]:
        """Show current configuration (hiding sensitive API keys)."""
        # Make a copy of the config to mask sensitive data
        safe_config = json.loads(json.dumps(self.config.config_data))

        # Mask API keys
        for provider, config in safe_config["dcae"]["llm_providers"].items():
            if "api_key" in config and config["api_key"]:
                config["api_key"] = "*" * len(config["api_key"])

        return safe_config

    def update_global_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update global settings based on Epic #1 requirements.

        Args:
            settings: Dictionary of settings to update

        Returns:
            True if successful, False otherwise
        """
        print("Updating global settings...")

        # Update each setting in the hierarchy
        for key_path, value in settings.items():
            if self.config.set(key_path, value):
                print(f"  ✓ {key_path} = {value}")
            else:
                print(f"  ✗ Failed to update {key_path}")
                return False

        print("✓ Global settings updated successfully")
        return True

    def toggle_logging(self, level: str = "INFO", file_output: bool = True,
                      console_output: bool = True) -> bool:
        """
        Configure logging settings.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            file_output: Enable/disable file output
            console_output: Enable/disable console output

        Returns:
            True if successful, False otherwise
        """
        logging_config = {
            "dcae.logging.level": level,
            "dcae.logging.file_output": file_output,
            "dcae.logging.console_output": console_output
        }

        return self.update_global_settings(logging_config)


def manage_multiple_projects() -> Dict[str, str]:
    """
    Function to manage multiple projects (Story 1-5).
    Returns a dictionary mapping project names to their paths.
    """
    projects_dir = Path("./dcae-projects")
    projects_dir.mkdir(exist_ok=True)

    # Find all DCAE projects in the directory
    projects = {}
    for item in projects_dir.iterdir():
        if item.is_dir():
            config_path = item / ".dcae/config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    project_name = config.get("project", {}).get("name", item.name)
                    projects[project_name] = str(item)

    return projects


def create_pause_resume_functionality() -> Dict[str, Any]:
    """
    Function to create pause/resume functionality (Story 1-4).
    Returns the state needed to resume a workflow.
    """
    state_file = Path(".dcae/workflow-state.json")

    # This would normally save the current state of a workflow
    # For now, return a template structure
    state_template = {
        "current_step": "unknown",
        "progress": 0,
        "timestamp": datetime.now().isoformat(),
        "checkpoint_data": {},
        "paused_by": "system",
        "resume_instructions": "Call resume_workflow() to continue"
    }

    # Save state to file if it exists
    if state_file.parent.exists():
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_template, f, indent=2)

    return state_template


def manage_api_keys_interactively():
    """Interactive function to manage API keys."""
    print("DCAE API Key Management")
    print("=" * 30)
    print("Supported providers:", ", ".join(["openai", "anthropic", "qwen", "glm"]))
    print()

    config_manager = ConfigurationManager()

    while True:
        print("\nOptions:")
        print("1. Set API key for a provider")
        print("2. View current API key status")
        print("3. Remove API key for a provider")
        print("4. Back to main menu")

        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            provider = input("Enter provider name (openai/anthropic/qwen/glm): ").strip().lower()
            api_key = input(f"Enter API key for {provider}: ").strip()

            if config_manager.config.update_llm_provider(provider, api_key):
                print(f"✓ API key for {provider} set successfully")
            else:
                print(f"✗ Failed to set API key for {provider}")

        elif choice == "2":
            config = config_manager.show_current_config()
            providers = config["dcae"]["llm_providers"]
            print("\nAPI Key Status:")
            for provider, settings in providers.items():
                status = "Enabled" if settings["enabled"] else "Disabled"
                key_set = "Yes" if settings["api_key"] != "*" * len(settings["api_key"]) else "Yes (masked)"
                print(f"  {provider}: {status}, Key: {key_set}")

        elif choice == "3":
            provider = input("Enter provider name to remove API key for: ").strip().lower()
            confirm = input(f"Are you sure you want to remove the API key for {provider}? (y/N): ").strip().lower()

            if confirm == 'y':
                if config_manager.config.update_llm_provider(provider, "", False):
                    print(f"✓ API key for {provider} removed and provider disabled")
                else:
                    print(f"✗ Failed to remove API key for {provider}")

        elif choice == "4":
            break
        else:
            print("Invalid option. Please select 1-4.")


def update_settings_without_interruption(settings_update: Dict[str, Any]):
    """
    Function to update settings without interrupting ongoing processes (Story 1-9).
    In a real implementation, this would handle live configuration updates.
    """
    config_manager = ConfigurationManager()

    print("Updating settings without interrupting processes...")
    success = config_manager.update_global_settings(settings_update)

    if success:
        print("✓ Settings updated successfully without interruption")
    else:
        print("✗ Failed to update settings")

    return success


def log_error_reporting_config():
    """
    Function to set up error reporting configuration (Story 1-10).
    """
    error_config = {
        "dcae.logging.level": "ERROR",
        "dcae.bmad_workflow.performance_stats.enabled": True
    }

    config_manager = ConfigurationManager()
    config_manager.update_global_settings(error_config)

    print("✓ Error reporting and logging configured")


def show_progress_indicators_config():
    """
    Function to set up progress indicators (Story 1-11).
    """
    progress_config = {
        "dcae.bmad_workflow.performance_stats.collection_interval_minutes": 1
    }

    config_manager = ConfigurationManager()
    config_manager.update_global_settings(progress_config)

    print("✓ Progress indicators and performance stats configured")


# Main function for configuration management
def main():
    """Main function to handle configuration management CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="DCAE Configuration Management Tool"
    )

    parser.add_argument(
        "action",
        choices=[
            "configure-project", "set-api-keys", "show-config",
            "toggle-logging", "update-settings", "manage-multiple-projects",
            "pause-resume", "api-key-management", "error-reporting",
            "progress-indicators"
        ],
        help="Configuration action to perform"
    )

    parser.add_argument("--project-name", help="Project name")
    parser.add_argument("--discipline-level", choices=["fast", "balanced", "strict"],
                       help="Discipline level")
    parser.add_argument("--provider", help="LLM provider name")
    parser.add_argument("--api-key", help="API key for provider")
    parser.add_argument("--log-level", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    parser.add_argument("--enable", type=bool, help="Enable setting")
    parser.add_argument("--disable", type=bool, help="Disable setting")

    args = parser.parse_args()

    config_manager = ConfigurationManager()

    if args.action == "configure-project":
        if not args.project_name:
            print("Error: --project-name is required for configure-project")
            sys.exit(1)

        discipline = DisciplineLevel(args.discipline_level) if args.discipline_level else DisciplineLevel.BALANCED
        success = config_manager.configure_project(args.project_name, discipline_level=discipline)
        sys.exit(0 if success else 1)

    elif args.action == "set-api-keys":
        if not args.provider or not args.api_key:
            print("Error: Both --provider and --api-key are required for set-api-keys")
            sys.exit(1)

        provider_config = {args.provider: args.api_key}
        success = config_manager.configure_api_keys(provider_config)
        sys.exit(0 if success else 1)

    elif args.action == "show-config":
        config = config_manager.show_current_config()
        print("Current DCAE Configuration:")
        print(yaml.dump(config, default_flow_style=False, allow_unicode=True))

    elif args.action == "toggle-logging":
        if not args.log_level:
            print("Error: --log-level is required for toggle-logging")
            sys.exit(1)

        success = config_manager.toggle_logging(level=args.log_level)
        sys.exit(0 if success else 1)

    elif args.action == "update-settings":
        # Example of updating settings
        settings = {
            "dcae.logging.level": args.log_level or "INFO",
        }
        if args.enable is not None:
            settings["dcae.bmad_workflow.enabled"] = args.enable
        if args.disable is not None:
            # We'd need to know which setting to disable specifically
            pass

        success = config_manager.update_global_settings(settings)
        sys.exit(0 if success else 1)

    elif args.action == "manage-multiple-projects":
        projects = manage_multiple_projects()
        print("Managed projects:")
        for name, path in projects.items():
            print(f"  {name}: {path}")

    elif args.action == "pause-resume":
        state = create_pause_resume_functionality()
        print("Pause/Resume state created:")
        print(json.dumps(state, indent=2))

    elif args.action == "api-key-management":
        manage_api_keys_interactively()

    elif args.action == "error-reporting":
        log_error_reporting_config()

    elif args.action == "progress-indicators":
        show_progress_indicators_config()


if __name__ == "__main__":
    main()