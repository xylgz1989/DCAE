import unittest
import os
import tempfile
from pathlib import Path
from src.dcae.llm_management import (
    ProviderConfig, ProviderType, LLMProviderManager,
    TaskAnalyzer, LLMSelector, TaskType,
    ManualLLMSelector,
    MultiLLMComparison,
    UsageTracker
)


class TestEpic6Integration(unittest.TestCase):
    """Integration tests for Epic #6: LLM Management & Integration."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "providers.json")
        self.stats_file = os.path.join(self.temp_dir, "usage_stats.json")

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_llm_management_workflow(self):
        """Test a complete workflow of configuring providers, selecting, and tracking usage."""
        # 1. Configure providers
        manager = LLMProviderManager(config_file_path=self.config_file)

        openai_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test_openai_key",
            name="openai-gpt4",
            model="gpt-4o"
        )

        anthropic_config = ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key="test_anthropic_key",
            name="anthropic-claude",
            model="claude-3-5-sonnet-20241022"
        )

        manager.add_provider(openai_config)
        manager.add_provider(anthropic_config)

        # Verify providers are configured
        self.assertEqual(len(manager.list_providers()), 2)
        self.assertIsNotNone(manager.get_provider("openai-gpt4"))
        self.assertIsNotNone(manager.get_provider("anthropic-claude"))

        # 2. Test intelligent selection
        selector = LLMSelector(manager.providers)

        coding_task = "Generate Python code for a REST API endpoint with authentication"
        selected_provider = selector.select_best_provider(coding_task)

        # Should select one of the available providers for coding
        self.assertIn(selected_provider.name, ["openai-gpt4", "anthropic-claude"])

        # 3. Test manual selection override
        manual_selector = ManualLLMSelector(manager.providers)
        manual_choice = manual_selector.select_provider("anthropic-claude")
        self.assertEqual(manual_choice.name, "anthropic-claude")

        # 4. Test usage tracking
        tracker = UsageTracker(stats_file_path=self.stats_file)

        # Record usage
        tracker.record_usage(
            provider_name="openai-gpt4",
            task_type="coding",
            tokens_used=1000,
            cost_incurred=0.05,
            project_name="test-project"
        )

        # Verify tracking worked
        stats = tracker.get_statistics()
        self.assertEqual(stats.total_requests, 1)
        self.assertEqual(stats.total_tokens, 1000)
        self.assertEqual(stats.provider_stats["openai-gpt4"]["requests"], 1)

    def test_provider_configuration_with_intelligent_selection(self):
        """Test configuring providers and using intelligent selection together."""
        # Set up provider manager
        manager = LLMProviderManager(config_file_path=self.config_file)

        providers_data = [
            (ProviderType.OPENAI, "test_key", "fast-model", "gpt-3.5-turbo"),
            (ProviderType.ANTHROPIC, "test_key", "smart-model", "claude-3-5-sonnet-20241022"),
            (ProviderType.BIGMODEL, "test_key", "local-model", "qwen-max")
        ]

        for provider_type, api_key, name, model in providers_data:
            config = ProviderConfig(
                provider_type=provider_type,
                api_key=api_key,
                name=name,
                model=model
            )
            manager.add_provider(config)

        # Test selection with different task types
        selector = LLMSelector(manager.providers)

        # Coding task should favor capable models
        coding_task = "Write a Python function to sort a list of dictionaries by a specific key"
        coding_provider = selector.select_best_provider(coding_task)
        self.assertIsNotNone(coding_provider)

        # Creative writing task
        writing_task = "Write a creative story about the future of AI"
        writing_provider = selector.select_best_provider(writing_task)
        self.assertIsNotNone(writing_provider)

        # Analysis task
        analysis_task = "Analyze this algorithm for time and space complexity: def bubble_sort(arr)"
        analysis_provider = selector.select_best_provider(analysis_task)
        self.assertIsNotNone(analysis_provider)

        # Each task should get a valid provider
        self.assertIn(coding_provider.name, manager.list_providers())
        self.assertIn(writing_provider.name, manager.list_providers())
        self.assertIn(analysis_provider.name, manager.list_providers())

    def test_multi_llm_comparison_with_usage_tracking(self):
        """Test comparing LLMs and tracking usage of comparisons."""
        # Mock LLM clients (just return predefined responses)
        class MockLLMClient:
            def __init__(self, response):
                self.response = response

            def generate(self, prompt):
                return self.response

        # Set up mock clients
        llm_clients = {
            "model_a": MockLLMClient("Response from Model A"),
            "model_b": MockLLMClient("Response from Model B"),
            "model_c": MockLLMClient("Response from Model A")  # Same as A
        }

        comparator = MultiLLMComparison(llm_clients)

        # Perform comparison
        results = comparator.submit_to_multiple("Test prompt", ["model_a", "model_b", "model_c"])
        consistency_check = comparator.compare_consistency(results)

        # Track the comparison activity as usage
        tracker = UsageTracker(stats_file_path=self.stats_file)

        # Record each model usage individually
        for model_name in results.keys():
            tracker.record_usage(
                provider_name=model_name,
                task_type="comparison",
                tokens_used=50,  # Estimation
                cost_incurred=0.0025,  # Estimation
                project_name="comparison-test"
            )

        # Verify tracking
        stats = tracker.get_statistics()
        self.assertGreaterEqual(stats.total_requests, 3)  # At least 3 model calls

        # Verify comparison results
        self.assertEqual(len(results), 3)
        self.assertGreaterEqual(consistency_check.agreement_percentage, 0.0)
        self.assertIsInstance(consistency_check.discrepancies, list)

    def test_manual_vs_automatic_selection_integration(self):
        """Test integration between manual and automatic selection methods."""
        # Set up providers
        manager = LLMProviderManager(config_file_path=self.config_file)

        providers = [
            ProviderConfig(ProviderType.OPENAI, "key", "primary", "gpt-4o"),
            ProviderConfig(ProviderType.ANTHROPIC, "key", "secondary", "claude-3-5-sonnet-20241022"),
            ProviderConfig(ProviderType.BIGMODEL, "key", "fallback", "qwen-max")
        ]

        for provider in providers:
            manager.add_provider(provider)

        # Set up selectors
        auto_selector = LLMSelector(manager.providers)
        manual_selector = ManualLLMSelector(manager.providers)

        task = "Generate documentation for a Python class"

        # Get auto-selected provider
        auto_selected = auto_selector.select_best_provider(task)

        # Get manually selected provider
        manual_selected = manual_selector.select_provider("secondary")

        # Both should return valid providers
        self.assertIsNotNone(auto_selected)
        self.assertIsNotNone(manual_selected)

        # They might be different depending on the task analysis
        self.assertIn(auto_selected.name, ["primary", "secondary", "fallback"])
        self.assertEqual(manual_selected.name, "secondary")

    def test_end_to_end_scenario_with_statistics(self):
        """End-to-end scenario testing full LLM management workflow."""
        # 1. Initialize all components
        manager = LLMProviderManager(config_file_path=self.config_file)
        tracker = UsageTracker(stats_file_path=self.stats_file)

        # 2. Configure multiple providers
        configs = [
            ProviderConfig(ProviderType.OPENAI, "openai_key", "openai-fast", "gpt-3.5-turbo"),
            ProviderConfig(ProviderType.ANTHROPIC, "anthropic_key", "anthropic-smart", "claude-3-5-sonnet-20241022")
        ]

        for config in configs:
            manager.add_provider(config)

        # 3. Set up selectors
        auto_selector = LLMSelector(manager.providers)
        manual_selector = ManualLLMSelector(manager.providers)

        # 4. Define tasks
        tasks = [
            ("coding", "Write a Python function to calculate fibonacci sequence"),
            ("writing", "Write a blog post about software architecture"),
            ("analysis", "Analyze this code snippet for potential bugs")
        ]

        # 5. Process each task
        for task_type, task_desc in tasks:
            # Auto-select provider
            auto_provider = auto_selector.select_best_provider(task_desc)

            # Manually select for sensitive task
            if "analysis" in task_desc.lower():
                manual_provider = manual_selector.select_provider("anthropic-smart")
                selected_provider = manual_provider
            else:
                selected_provider = auto_provider

            # Record usage
            tracker.record_usage(
                provider_name=selected_provider.name,
                task_type=task_type,
                tokens_used=750,  # Estimated
                cost_incurred=0.0375,  # Estimated
                project_name="end-to-end-test"
            )

            # Verify selection worked
            self.assertIsNotNone(selected_provider)
            self.assertIn(selected_provider.name, manager.list_providers())

        # 6. Verify tracking
        final_stats = tracker.get_statistics()
        self.assertEqual(final_stats.total_requests, 3)  # 3 tasks
        self.assertGreaterEqual(final_stats.total_tokens, 2000)  # 3 * 750

        # 7. Export for analysis
        export_path = os.path.join(self.temp_dir, "exported_stats.json")
        tracker.export_statistics(export_path)

        self.assertTrue(os.path.exists(export_path))


if __name__ == '__main__':
    unittest.main()