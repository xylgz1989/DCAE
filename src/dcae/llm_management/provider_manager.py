"""Module for managing multiple LLM providers."""
import json
import os
from typing import Dict, Optional, List
from pathlib import Path

from .provider_config import ProviderConfig


class LLMProviderManager:
    """Manages multiple LLM provider configurations."""

    def __init__(self, config_file_path: str = ".dcae/providers.json"):
        """
        Initialize the LLM provider manager.

        Args:
            config_file_path: Path to the configuration file for storing provider configs
        """
        self.config_file_path = Path(config_file_path)
        self.providers: Dict[str, ProviderConfig] = {}
        self.default_provider_name: Optional[str] = None

        # Create directory if it doesn't exist
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing configurations
        self.load_configs()

    def add_provider(self, provider_config: ProviderConfig) -> bool:
        """
        Add a new provider configuration.

        Args:
            provider_config: The provider configuration to add

        Returns:
            True if the provider was added successfully, False if a provider with the same name already exists
        """
        if provider_config.name in self.providers:
            return False  # Provider with this name already exists

        self.providers[provider_config.name] = provider_config
        self.save_configs()
        return True

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """
        Get a provider configuration by name.

        Args:
            name: The name of the provider to retrieve

        Returns:
            The provider configuration if found, None otherwise
        """
        return self.providers.get(name)

    def remove_provider(self, name: str) -> bool:
        """
        Remove a provider configuration by name.

        Args:
            name: The name of the provider to remove

        Returns:
            True if the provider was removed successfully, False if the provider doesn't exist
        """
        if name not in self.providers:
            return False

        del self.providers[name]

        # If this was the default provider, unset the default
        if self.default_provider_name == name:
            self.default_provider_name = None

        self.save_configs()
        return True

    def list_providers(self) -> List[str]:
        """
        List all provider names.

        Returns:
            A list of provider names
        """
        return list(self.providers.keys())

    def set_default_provider(self, name: str) -> bool:
        """
        Set a provider as the default.

        Args:
            name: The name of the provider to set as default

        Returns:
            True if the provider exists and was set as default, False otherwise
        """
        if name not in self.providers:
            return False

        self.default_provider_name = name
        self.save_configs()
        return True

    def get_default_provider(self) -> Optional[ProviderConfig]:
        """
        Get the default provider.

        Returns:
            The default provider configuration if set, None otherwise
        """
        if self.default_provider_name is None:
            return None

        return self.providers.get(self.default_provider_name)

    def save_configs(self):
        """Save the provider configurations to the config file."""
        config_data = {
            "default_provider": self.default_provider_name,
            "providers": {
                name: config.to_dict()
                for name, config in self.providers.items()
            }
        }

        with open(self.config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)

    def load_configs(self):
        """Load provider configurations from the config file."""
        if not self.config_file_path.exists():
            # Create a default empty config file
            self.save_configs()
            return

        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Load providers
            self.providers = {}
            for name, config_dict in config_data.get("providers", {}).items():
                provider_config = ProviderConfig.from_dict(config_dict)
                self.providers[name] = provider_config

            # Set default provider
            self.default_provider_name = config_data.get("default_provider")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading provider configs: {e}")
            # Create a default empty config file if there's an error
            self.save_configs()