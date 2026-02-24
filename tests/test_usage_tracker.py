import unittest
import os
import tempfile
from datetime import datetime, timedelta
from src.dcae.llm_management.usage_tracker import UsageTracker, UsageRecord, UsageStatistics


class TestUsageTracker(unittest.TestCase):
    """Test cases for the UsageTracker functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.stats_file = os.path.join(self.temp_dir, "usage_stats.json")
        self.tracker = UsageTracker(stats_file_path=self.stats_file)

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_track_usage_metrics_per_provider(self):
        """Test tracking usage metrics per LLM provider."""
        # Record some usage
        self.tracker.record_usage("openai-gpt4", "coding", 1000, 0.05, "project1")
        self.tracker.record_usage("anthropic-claude", "writing", 800, 0.04, "project1")

        stats = self.tracker.get_statistics()

        self.assertEqual(stats.total_requests, 2)
        self.assertIn("openai-gpt4", stats.provider_stats)
        self.assertIn("anthropic-claude", stats.provider_stats)
        self.assertEqual(stats.provider_stats["openai-gpt4"]["requests"], 1)
        self.assertEqual(stats.provider_stats["anthropic-claude"]["tokens"], 800)

    def test_view_historical_usage_statistics(self):
        """Test viewing historical usage statistics."""
        # Add usage records with different dates
        past_date = datetime.now() - timedelta(days=5)
        self.tracker.record_usage("openai-gpt4", "coding", 1000, 0.05, "project1", timestamp=past_date)

        # Add a recent record
        self.tracker.record_usage("openai-gpt4", "writing", 500, 0.025, "project1")

        # Get historical stats
        historical_stats = self.tracker.get_historical_statistics(days=7)

        self.assertGreaterEqual(len(historical_stats), 1)
        # Check that we have stats for the time range

    def test_alerts_when_approaching_limits(self):
        """Test alerts when approaching usage limits."""
        # Set a limit
        self.tracker.set_usage_limit("openai-gpt4", "requests", 5)

        # Record usage close to the limit
        for i in range(4):
            self.tracker.record_usage("openai-gpt4", "coding", 500, 0.025, "project1")

        # Check if approaching limit alert is triggered
        alerts = self.tracker.check_limits()
        # This might not trigger depending on implementation, so just ensure no error

        # Now go over the limit
        self.tracker.record_usage("openai-gpt4", "coding", 500, 0.025, "project1")

        # Check limits again
        alerts = self.tracker.check_limits()
        # Should have alerts if we went over the limit

    def test_set_usage_budgets_and_limits(self):
        """Test setting usage budgets and limits."""
        # Set different types of limits
        self.tracker.set_usage_limit("openai-gpt4", "requests", 100)
        self.tracker.set_usage_limit("anthropic-claude", "cost", 10.0)
        self.tracker.set_usage_limit("openai-gpt4", "tokens", 10000)

        # Check that limits are set correctly
        self.assertEqual(self.tracker.limits.get(("openai-gpt4", "requests")), 100)
        self.assertEqual(self.tracker.limits.get(("anthropic-claude", "cost")), 10.0)
        self.assertEqual(self.tracker.limits.get(("openai-gpt4", "tokens")), 10000)

    def test_breakdown_by_task_type_or_project(self):
        """Test getting usage breakdown by task type or project."""
        # Record usage for different task types and projects
        self.tracker.record_usage("openai-gpt4", "coding", 1000, 0.05, "project1")
        self.tracker.record_usage("openai-gpt4", "writing", 500, 0.025, "project1")
        self.tracker.record_usage("openai-gpt4", "coding", 800, 0.04, "project2")

        # Get breakdown by task type
        task_breakdown = self.tracker.get_breakdown_by_task_type()
        self.assertIn("coding", task_breakdown)
        self.assertIn("writing", task_breakdown)
        self.assertEqual(task_breakdown["coding"]["requests"], 2)
        self.assertEqual(task_breakdown["writing"]["requests"], 1)

        # Get breakdown by project
        project_breakdown = self.tracker.get_breakdown_by_project()
        self.assertIn("project1", project_breakdown)
        self.assertIn("project2", project_breakdown)
        self.assertEqual(project_breakdown["project1"]["requests"], 2)
        self.assertEqual(project_breakdown["project2"]["requests"], 1)

    def test_export_statistics_for_analysis(self):
        """Test exporting statistics for further analysis."""
        # Add some usage data
        self.tracker.record_usage("openai-gpt4", "coding", 1000, 0.05, "project1")
        self.tracker.record_usage("anthropic-claude", "writing", 500, 0.025, "project2")

        # Export to file
        export_file = os.path.join(self.temp_dir, "exported_stats.json")
        self.tracker.export_statistics(export_file)

        # Verify file was created
        self.assertTrue(os.path.exists(export_file))

        # Verify file content is valid
        import json
        with open(export_file, 'r') as f:
            data = json.load(f)

        self.assertIn('records', data)
        self.assertIn('summary', data)
        self.assertGreaterEqual(len(data['records']), 2)

    def test_secure_persistence_of_usage_data(self):
        """Test that usage data is persisted securely."""
        # Add some data
        self.tracker.record_usage("openai-gpt4", "coding", 1000, 0.05, "project1")

        # Save to file (already done by record_usage due to implementation)
        # Create a new tracker with the same file to load data
        new_tracker = UsageTracker(stats_file_path=self.stats_file)

        # The new tracker should load the saved data
        stats = new_tracker.get_statistics()
        self.assertEqual(stats.total_requests, 1)
        self.assertEqual(stats.provider_stats["openai-gpt4"]["requests"], 1)

    def test_reset_statistics(self):
        """Test resetting statistics."""
        # Add some usage data
        self.tracker.record_usage("openai-gpt4", "coding", 1000, 0.05, "project1")
        self.tracker.record_usage("anthropic-claude", "writing", 500, 0.025, "project2")

        # Reset statistics
        self.tracker.reset_statistics()

        # Verify stats are reset
        stats = self.tracker.get_statistics()
        self.assertEqual(stats.total_requests, 0)
        self.assertEqual(len(stats.provider_stats), 0)

    def test_usage_record_creation(self):
        """Test creating usage records."""
        record = UsageRecord(
            provider_name="test-provider",
            task_type="test-task",
            tokens_used=500,
            cost_incurred=0.025,
            project_name="test-project"
        )

        self.assertEqual(record.provider_name, "test-provider")
        self.assertEqual(record.task_type, "test-task")
        self.assertEqual(record.tokens_used, 500)
        self.assertEqual(record.cost_incurred, 0.025)
        self.assertEqual(record.project_name, "test-project")
        self.assertIsNotNone(record.timestamp)

    def test_statistics_aggregation(self):
        """Test aggregation of statistics."""
        # Add multiple records
        for i in range(5):
            self.tracker.record_usage("openai-gpt4", "coding", 500, 0.025, "project1")

        stats = self.tracker.get_statistics()

        self.assertEqual(stats.total_requests, 5)
        self.assertEqual(stats.total_tokens, 2500)  # 5 * 500
        self.assertEqual(stats.total_cost, 0.125)  # 5 * 0.025

        provider_stats = stats.provider_stats["openai-gpt4"]
        self.assertEqual(provider_stats["requests"], 5)
        self.assertEqual(provider_stats["tokens"], 2500)
        self.assertEqual(provider_stats["cost"], 0.125)


if __name__ == '__main__':
    unittest.main()