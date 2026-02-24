import unittest
import os
import tempfile
from pathlib import Path
from src.dcae.llm_management.provider_config import ProviderConfig, ProviderType
from src.dcae.llm_management.provider_manager import LLMProviderManager


class TestLLMProviderManager(unittest.TestCase):
    """Test cases for the LLMProviderManager."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "providers.json")

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_initialization(self):
        """Test initializing the LLM provider manager."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        self.assertEqual(len(manager.providers), 0)
        self.assertIsNotNone(manager.providers)
        # Check that config file is created
        self.assertTrue(os.path.exists(self.config_file))

    def test_add_provider(self):
        """Test adding a provider to the manager."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test_api_key",
            name="test-openai"
        )

        result = manager.add_provider(provider_config)

        self.assertTrue(result)
        self.assertEqual(len(manager.providers), 1)
        self.assertIn("test-openai", manager.providers)
        self.assertEqual(manager.providers["test-openai"].api_key, "test_api_key")

    def test_add_duplicate_provider(self):
        """Test that adding a duplicate provider returns False."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test_api_key",
            name="test-openai"
        )

        # Add the provider first time
        result1 = manager.add_provider(provider_config)
        self.assertTrue(result1)

        # Try to add the same provider again
        result2 = manager.add_provider(provider_config)
        self.assertFalse(result2)  # Should return False for duplicates

    def test_get_provider(self):
        """Test retrieving a provider by name."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        provider_config = ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key="test_key",
            name="test-anthropic"
        )

        manager.add_provider(provider_config)

        retrieved = manager.get_provider("test-anthropic")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.api_key, "test_key")
        self.assertEqual(retrieved.provider_type, ProviderType.ANTHROPIC)

    def test_get_nonexistent_provider(self):
        """Test retrieving a provider that doesn't exist."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        retrieved = manager.get_provider("nonexistent")

        self.assertIsNone(retrieved)

    def test_remove_provider(self):
        """Test removing a provider."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test_api_key",
            name="test-openai"
        )

        manager.add_provider(provider_config)
        self.assertEqual(len(manager.providers), 1)

        result = manager.remove_provider("test-openai")

        self.assertTrue(result)
        self.assertEqual(len(manager.providers), 0)

    def test_remove_nonexistent_provider(self):
        """Test removing a provider that doesn't exist."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        result = manager.remove_provider("nonexistent")

        self.assertFalse(result)

    def test_list_providers(self):
        """Test listing all provider names."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        # Add multiple providers
        configs = [
            ProviderConfig(ProviderType.OPENAI, "key1", "openai1"),
            ProviderConfig(ProviderType.ANTHROPIC, "key2", "anthropic1"),
            ProviderConfig(ProviderType.BIGMODEL, "key3", "bigmodel1")
        ]

        for config in configs:
            manager.add_provider(config)

        provider_names = manager.list_providers()

        self.assertEqual(len(provider_names), 3)
        self.assertIn("openai1", provider_names)
        self.assertIn("anthropic1", provider_names)
        self.assertIn("bigmodel1", provider_names)

    def test_set_default_provider(self):
        """Test setting a default provider."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test_api_key",
            name="test-openai"
        )

        manager.add_provider(provider_config)
        manager.set_default_provider("test-openai")

        self.assertEqual(manager.default_provider_name, "test-openai")

    def test_get_default_provider(self):
        """Test getting the default provider."""
        manager = LLMProviderManager(config_file_path=self.config_file)

        provider_config = ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key="test_key",
            name="test-anthropic"
        )

        manager.add_provider(provider_config)
        manager.set_default_provider("test-anthropic")

        default_provider = manager.get_default_provider()

        self.assertIsNotNone(default_provider)
        self.assertEqual(default_provider.name, "test-anthropic")
        self.assertEqual(default_provider.api_key, "test_key")


if __name__ == '__main__':
    unittest.main()