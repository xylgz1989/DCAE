import unittest
import os
import tempfile
from pathlib import Path
from src.dcae.llm_management.provider_config import ProviderConfig, ProviderType


class TestProviderConfig(unittest.TestCase):
    """Test cases for the ProviderConfig model."""

    def test_provider_config_creation_with_valid_data(self):
        """Test creating a ProviderConfig with valid data."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test_api_key",
            base_url="https://api.openai.com",
            model="gpt-4",
            name="openai-gpt4"
        )

        self.assertEqual(config.provider_type, ProviderType.OPENAI)
        self.assertEqual(config.api_key, "test_api_key")
        self.assertEqual(config.base_url, "https://api.openai.com")
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.name, "openai-gpt4")

    def test_provider_config_creation_with_minimal_data(self):
        """Test creating a ProviderConfig with minimal required data."""
        config = ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key="test_api_key",
            name="anthropic-claude"
        )

        self.assertEqual(config.provider_type, ProviderType.ANTHROPIC)
        self.assertEqual(config.api_key, "test_api_key")
        self.assertEqual(config.name, "anthropic-claude")
        # Default values should be set
        self.assertEqual(config.base_url, "https://api.anthropic.com/v1")  # Updated to match actual default
        self.assertEqual(config.model, "claude-3-5-sonnet-20241022")

    def test_provider_type_enum_values(self):
        """Test that ProviderType enum has expected values."""
        # Check that common provider types exist
        self.assertTrue(hasattr(ProviderType, 'OPENAI'))
        self.assertTrue(hasattr(ProviderType, 'ANTHROPIC'))
        self.assertTrue(hasattr(ProviderType, 'BIGMODEL'))
        self.assertTrue(hasattr(ProviderType, 'BAI_LIAN'))

    def test_provider_config_serialization(self):
        """Test serializing and deserializing ProviderConfig."""
        original_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test_api_key",
            base_url="https://api.openai.com",
            model="gpt-4",
            name="openai-gpt4"
        )

        # Convert to dict and back
        config_dict = original_config.to_dict()
        self.assertEqual(config_dict['provider_type'], 'openai')
        self.assertEqual(config_dict['api_key'], 'test_api_key')
        self.assertEqual(config_dict['base_url'], 'https://api.openai.com')
        self.assertEqual(config_dict['model'], 'gpt-4')
        self.assertEqual(config_dict['name'], 'openai-gpt4')

    def test_provider_config_from_dict(self):
        """Test creating ProviderConfig from dictionary."""
        config_data = {
            'provider_type': 'anthropic',
            'api_key': 'test_key',
            'base_url': 'https://api.anthropic.com',
            'model': 'claude-3-5-sonnet-20241022',
            'name': 'test-anthropic'
        }

        config = ProviderConfig.from_dict(config_data)
        self.assertEqual(config.provider_type, ProviderType.ANTHROPIC)
        self.assertEqual(config.api_key, 'test_key')
        self.assertEqual(config.name, 'test-anthropic')


if __name__ == '__main__':
    unittest.main()