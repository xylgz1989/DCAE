"""Module for manual LLM selection."""
from typing import Dict, Optional, List
from .provider_config import ProviderConfig


class ManualLLMSelector:
    """Allows users to manually specify which LLM to use for specific tasks."""

    def __init__(self, available_providers: Dict[str, ProviderConfig]):
        """
        Initialize the manual LLM selector.

        Args:
            available_providers: Dictionary of available provider configs
        """
        self.available_providers = available_providers
        self.project_preferences: Dict[str, str] = {}  # project_name -> provider_name
        self.task_preferences: Dict[str, Dict[str, str]] = {}  # project_name -> {task_name -> provider_name}

    def select_provider(self, provider_name: str) -> Optional[ProviderConfig]:
        """
        Manually select a provider by name.

        Args:
            provider_name: Name of the provider to select

        Returns:
            The ProviderConfig if available, None otherwise
        """
        return self.available_providers.get(provider_name)

    def set_project_preference(self, project_name: str, provider_name: str) -> bool:
        """
        Set a provider preference for an entire project.

        Args:
            project_name: Name of the project
            provider_name: Name of the provider to use for the project

        Returns:
            True if the provider exists and preference was set, False otherwise
        """
        if provider_name not in self.available_providers:
            return False

        self.project_preferences[project_name] = provider_name
        return True

    def get_project_preference(self, project_name: str) -> Optional[str]:
        """
        Get the preferred provider for a project.

        Args:
            project_name: Name of the project

        Returns:
            The preferred provider name if set, None otherwise
        """
        return self.project_preferences.get(project_name)

    def set_task_preference(self, project_name: str, task_name: str, provider_name: str) -> bool:
        """
        Set a provider preference for a specific task within a project.

        Args:
            project_name: Name of the project
            task_name: Name of the task
            provider_name: Name of the provider to use for the task

        Returns:
            True if the provider exists and preference was set, False otherwise
        """
        if provider_name not in self.available_providers:
            return False

        if project_name not in self.task_preferences:
            self.task_preferences[project_name] = {}

        self.task_preferences[project_name][task_name] = provider_name
        return True

    def select_provider_for_project(self, project_name: str, task_name: Optional[str] = None) -> Optional[ProviderConfig]:
        """
        Select a provider for a project, optionally considering a specific task.

        Args:
            project_name: Name of the project
            task_name: Optional name of the specific task

        Returns:
            The appropriate ProviderConfig, or None if no preference set
        """
        # Check if there's a specific task preference
        if project_name in self.task_preferences and task_name and task_name in self.task_preferences[project_name]:
            provider_name = self.task_preferences[project_name][task_name]
            return self.available_providers.get(provider_name)

        # Otherwise, check project preference
        provider_name = self.project_preferences.get(project_name)
        return self.available_providers.get(provider_name)

    def select_provider_for_task(self, project_name: str, task_name: str) -> Optional[ProviderConfig]:
        """
        Select a provider for a specific task within a project.

        Args:
            project_name: Name of the project
            task_name: Name of the task

        Returns:
            The appropriate ProviderConfig, or None if no preference set
        """
        return self.select_provider_for_project(project_name, task_name)

    def list_available_providers(self) -> List[str]:
        """
        Get a list of all available provider names.

        Returns:
            List of available provider names
        """
        return list(self.available_providers.keys())

    def validate_provider(self, provider_name: str) -> bool:
        """
        Validate if a provider is available.

        Args:
            provider_name: Name of the provider to validate

        Returns:
            True if provider is available, False otherwise
        """
        return provider_name in self.available_providers

    def select_with_temporary_override(self, provider_name: str) -> Optional[ProviderConfig]:
        """
        Select a provider with temporary override, bypassing stored preferences.

        Args:
            provider_name: Name of the provider to temporarily select

        Returns:
            The ProviderConfig if available, None otherwise
        """
        return self.available_providers.get(provider_name)