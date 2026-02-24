import unittest
from src.dcae.llm_management.manual_selector import ManualLLMSelector
from src.dcae.llm_management.provider_config import ProviderConfig, ProviderType


class TestManualLLMSelector(unittest.TestCase):
    """Test cases for the ManualLLMSelector."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create some test provider configs
        self.providers = {
            "openai-gpt4": ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test_key",
                name="openai-gpt4",
                model="gpt-4o"
            ),
            "anthropic-claude": ProviderConfig(
                provider_type=ProviderType.ANTHROPIC,
                api_key="test_key",
                name="anthropic-claude",
                model="claude-3-5-sonnet-20241022"
            ),
            "bigmodel-qwen": ProviderConfig(
                provider_type=ProviderType.BIGMODEL,
                api_key="test_key",
                name="bigmodel-qwen",
                model="qwen-max"
            )
        }
        self.selector = ManualLLMSelector(self.providers)

    def test_manual_selection_with_valid_provider(self):
        """Test manually selecting a valid provider."""
        selected = self.selector.select_provider("openai-gpt4")

        self.assertIsNotNone(selected)
        self.assertEqual(selected.name, "openai-gpt4")
        self.assertEqual(selected.model, "gpt-4o")

    def test_manual_selection_with_invalid_provider(self):
        """Test manually selecting an invalid provider."""
        selected = self.selector.select_provider("nonexistent-provider")

        self.assertIsNone(selected)

    def test_project_level_preference_setting(self):
        """Test setting project-level provider preferences."""
        self.selector.set_project_preference("test-project", "anthropic-claude")

        selected = self.selector.select_provider_for_project("test-project", "some-task")

        self.assertIsNotNone(selected)
        self.assertEqual(selected.name, "anthropic-claude")

    def test_project_level_preference_for_nonexistent_project(self):
        """Test selecting provider for a project without preferences."""
        selected = self.selector.select_provider_for_project("nonexistent-project", "some-task")

        self.assertIsNone(selected)

    def test_task_level_preference_setting(self):
        """Test setting task-level provider preferences."""
        self.selector.set_task_preference("test-project", "critical-task", "bigmodel-qwen")

        selected = self.selector.select_provider_for_task("test-project", "critical-task")

        self.assertIsNotNone(selected)
        self.assertEqual(selected.name, "bigmodel-qwen")

    def test_task_level_preference_override(self):
        """Test that task-level preferences override project-level preferences."""
        # Set both project and task preferences
        self.selector.set_project_preference("test-project", "anthropic-claude")
        self.selector.set_task_preference("test-project", "sensitive-task", "openai-gpt4")

        # Task should use task-level preference
        selected = self.selector.select_provider_for_task("test-project", "sensitive-task")

        self.assertIsNotNone(selected)
        self.assertEqual(selected.name, "openai-gpt4")

    def test_available_providers_list(self):
        """Test getting list of available providers."""
        providers_list = self.selector.list_available_providers()

        self.assertEqual(len(providers_list), 3)
        self.assertIn("openai-gpt4", providers_list)
        self.assertIn("anthropic-claude", providers_list)
        self.assertIn("bigmodel-qwen", providers_list)

    def test_validate_provider_availability(self):
        """Test validating provider availability."""
        is_available = self.selector.validate_provider("openai-gpt4")

        self.assertTrue(is_available)

        is_not_available = self.selector.validate_provider("nonexistent")

        self.assertFalse(is_not_available)

    def test_provider_availability_notification(self):
        """Test notification when manually selected provider is unavailable."""
        # This should return None since the provider doesn't exist
        selected = self.selector.select_provider("unavailable-provider")

        # Should return None for unavailable provider
        self.assertIsNone(selected)

    def test_temporary_manual_override(self):
        """Test temporary manual override functionality."""
        # Set a default preference
        self.selector.set_project_preference("test-project", "anthropic-claude")

        # Override temporarily
        overridden = self.selector.select_with_temporary_override("openai-gpt4")

        self.assertIsNotNone(overridden)
        self.assertEqual(overridden.name, "openai-gpt4")

    def test_permanent_preference_storage(self):
        """Test that preferences are properly stored and retrieved."""
        # Set preferences
        self.selector.set_project_preference("proj1", "openai-gpt4")
        self.selector.set_project_preference("proj2", "bigmodel-qwen")

        # Retrieve preferences
        proj1_pref = self.selector.get_project_preference("proj1")
        proj2_pref = self.selector.get_project_preference("proj2")

        self.assertEqual(proj1_pref, "openai-gpt4")
        self.assertEqual(proj2_pref, "bigmodel-qwen")


if __name__ == '__main__':
    unittest.main()