"""Tests for performance statistics functionality."""
import unittest
import tempfile
import os
from datetime import datetime, timedelta
from src.dcae.performance_statistics import StatisticsCollector, PerformanceRecord
from src.dcae.performance_dashboard import PerformanceDashboard


class TestPerformanceStatistics(unittest.TestCase):
    """Test cases for performance statistics functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.collector = StatisticsCollector(stats_file_path=self.temp_file.name)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_record_operation_success(self):
        """Test recording a successful operation."""
        result = self.collector.record_operation(
            operation_type="test_operation",
            project_name="test_project",
            duration_seconds=1.5,
            success=True
        )

        self.assertTrue(result)
        self.assertEqual(len(self.collector.records), 1)
        record = self.collector.records[0]
        self.assertEqual(record.operation_type, "test_operation")
        self.assertEqual(record.project_name, "test_project")
        self.assertEqual(record.duration_seconds, 1.5)
        self.assertTrue(record.success)

    def test_record_operation_failure(self):
        """Test recording a failed operation."""
        result = self.collector.record_operation(
            operation_type="test_operation",
            project_name="test_project",
            duration_seconds=2.0,
            success=False,
            error_message="Test error occurred"
        )

        self.assertTrue(result)
        self.assertEqual(len(self.collector.records), 1)
        record = self.collector.records[0]
        self.assertFalse(record.success)
        self.assertEqual(record.error_message, "Test error occurred")

    def test_get_statistics_empty(self):
        """Test getting statistics when no records exist."""
        stats = self.collector.get_statistics()

        self.assertEqual(stats.total_operations, 0)
        self.assertEqual(stats.successful_operations, 0)
        self.assertEqual(stats.failed_operations, 0)
        self.assertEqual(stats.average_duration, 0.0)
        self.assertEqual(stats.total_duration, 0.0)
        self.assertEqual(len(stats.operation_types), 0)
        self.assertEqual(len(stats.projects), 0)
        self.assertEqual(len(stats.recent_operations), 0)

    def test_get_statistics_with_data(self):
        """Test getting statistics with sample data."""
        # Add some test records
        self.collector.record_operation(
            operation_type="create_project",
            project_name="project1",
            duration_seconds=1.0,
            success=True
        )
        self.collector.record_operation(
            operation_type="create_project",
            project_name="project2",
            duration_seconds=2.0,
            success=False,
            error_message="Failed"
        )
        self.collector.record_operation(
            operation_type="generate_code",
            project_name="project1",
            duration_seconds=5.0,
            success=True
        )

        stats = self.collector.get_statistics()

        self.assertEqual(stats.total_operations, 3)
        self.assertEqual(stats.successful_operations, 2)
        self.assertEqual(stats.failed_operations, 1)
        self.assertEqual(stats.total_duration, 8.0)
        self.assertAlmostEqual(stats.average_duration, 8.0/3, places=2)
        self.assertEqual(len(stats.operation_types), 2)  # create_project, generate_code
        self.assertEqual(len(stats.projects), 2)  # project1, project2
        self.assertLessEqual(len(stats.recent_operations), 3)

    def test_get_statistics_filtered_days(self):
        """Test getting statistics filtered by date range."""
        # Add records with specific timestamps
        past_date = datetime.now() - timedelta(days=10)
        recent_date = datetime.now()

        # Record from 10 days ago (should be excluded with days=5)
        self.collector.record_operation(
            operation_type="old_op",
            project_name="project1",
            duration_seconds=1.0,
            success=True,
            start_time=past_date,
            end_time=past_date + timedelta(seconds=1.0)
        )

        # Record from today (should be included with days=5)
        self.collector.record_operation(
            operation_type="recent_op",
            project_name="project2",
            duration_seconds=2.0,
            success=True,
            start_time=recent_date,
            end_time=recent_date + timedelta(seconds=2.0)
        )

        # Get stats for last 5 days (should exclude old_op)
        stats = self.collector.get_statistics(days=5)

        self.assertEqual(stats.total_operations, 1)
        self.assertEqual(list(stats.operation_types.keys()), ["recent_op"])

    def test_get_operation_breakdown(self):
        """Test getting breakdown by operation type."""
        self.collector.record_operation(
            operation_type="test_op",
            project_name="project1",
            duration_seconds=1.0,
            success=True
        )
        self.collector.record_operation(
            operation_type="test_op",
            project_name="project2",
            duration_seconds=2.0,
            success=False
        )
        self.collector.record_operation(
            operation_type="other_op",
            project_name="project1",
            duration_seconds=3.0,
            success=True
        )

        breakdown = self.collector.get_operation_breakdown("test_op")

        self.assertEqual(len(breakdown), 2)
        self.assertTrue(all(r.operation_type == "test_op" for r in breakdown))

    def test_get_project_statistics(self):
        """Test getting statistics for a specific project."""
        self.collector.record_operation(
            operation_type="op1",
            project_name="target_project",
            duration_seconds=1.0,
            success=True
        )
        self.collector.record_operation(
            operation_type="op1",
            project_name="target_project",
            duration_seconds=2.0,
            success=False
        )
        self.collector.record_operation(
            operation_type="op2",
            project_name="other_project",
            duration_seconds=3.0,
            success=True
        )

        project_stats = self.collector.get_project_statistics("target_project")

        self.assertEqual(project_stats.total_operations, 2)
        self.assertEqual(project_stats.successful_operations, 1)
        self.assertEqual(project_stats.failed_operations, 1)
        self.assertEqual(project_stats.total_duration, 3.0)
        self.assertAlmostEqual(project_stats.average_duration, 1.5, places=2)
        self.assertIn("target_project", project_stats.projects)

    def test_export_statistics(self):
        """Test exporting statistics to file."""
        temp_export_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_export_file.close()

        try:
            self.collector.record_operation(
                operation_type="test_op",
                project_name="test_project",
                duration_seconds=1.0,
                success=True
            )

            self.collector.export_statistics(temp_export_file.name)

            # Verify the file was created and has content
            self.assertTrue(os.path.exists(temp_export_file.name))

            with open(temp_export_file.name, 'r') as f:
                content = f.read()
                self.assertIn("test_op", content)
                self.assertIn("test_project", content)

        finally:
            if os.path.exists(temp_export_file.name):
                os.remove(temp_export_file.name)

    def test_time_operation_decorator(self):
        """Test the time_operation utility method."""
        def test_func(x, y):
            # Simulate some work
            return x + y

        result, duration = self.collector.time_operation(test_func, 5, 3)

        self.assertEqual(result, 8)
        self.assertGreater(duration, 0)  # Should take some time, even if tiny

    def test_time_operation_with_exception(self):
        """Test the time_operation utility with an exception."""
        def failing_func():
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            self.collector.time_operation(failing_func)


class TestPerformanceDashboard(unittest.TestCase):
    """Test cases for performance dashboard functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.collector = StatisticsCollector(stats_file_path=self.temp_file.name)
        self.dashboard = PerformanceDashboard(collector=self.collector)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_generate_summary_report(self):
        """Test generating a summary report."""
        self.collector.record_operation(
            operation_type="create_project",
            project_name="test_project",
            duration_seconds=1.5,
            success=True
        )

        report = self.dashboard.generate_summary_report()

        self.assertIn("DCAE Performance Statistics Report", report)
        self.assertIn("create_project", report)
        self.assertIn("test_project", report)
        self.assertIn("Total Operations: 1", report)

    def test_generate_project_report(self):
        """Test generating a project-specific report."""
        self.collector.record_operation(
            operation_type="create_project",
            project_name="specific_project",
            duration_seconds=2.0,
            success=True
        )

        report = self.dashboard.generate_project_report("specific_project")

        self.assertIn("DCAE Performance Report for Project: specific_project", report)
        self.assertIn("specific_project", report)
        self.assertIn("Total Operations: 1", report)

    def test_get_top_slow_operations(self):
        """Test getting the slowest operations."""
        # Add operations with different durations
        self.collector.record_operation(
            operation_type="fast_op",
            project_name="project",
            duration_seconds=0.1,
            success=True
        )
        self.collector.record_operation(
            operation_type="slow_op",
            project_name="project",
            duration_seconds=5.0,
            success=True
        )
        self.collector.record_operation(
            operation_type="medium_op",
            project_name="project",
            duration_seconds=2.0,
            success=True
        )

        top_slow = self.dashboard.get_top_slow_operations(top_n=2)

        # Should return the slowest operations first
        self.assertEqual(len(top_slow), 2)
        self.assertEqual(top_slow[0].duration_seconds, 5.0)
        self.assertEqual(top_slow[0].operation_type, "slow_op")

    def test_get_failure_rate_by_operation_type(self):
        """Test getting failure rates by operation type."""
        # Add some successful and failed operations
        self.collector.record_operation(
            operation_type="flaky_op",
            project_name="project",
            duration_seconds=1.0,
            success=False
        )
        self.collector.record_operation(
            operation_type="flaky_op",
            project_name="project",
            duration_seconds=1.0,
            success=True
        )
        self.collector.record_operation(
            operation_type="reliable_op",
            project_name="project",
            duration_seconds=1.0,
            success=True
        )
        self.collector.record_operation(
            operation_type="reliable_op",
            project_name="project",
            duration_seconds=1.0,
            success=True
        )

        failure_rates = self.dashboard.get_failure_rate_by_operation_type()

        self.assertIn("flaky_op", failure_rates)
        self.assertIn("reliable_op", failure_rates)
        self.assertEqual(failure_rates["flaky_op"], 50.0)  # 1 out of 2 failed
        self.assertEqual(failure_rates["reliable_op"], 0.0)  # 0 out of 2 failed

    def test_get_efficiency_trend(self):
        """Test getting efficiency trend."""
        # Add operations (first batch is slower, second batch is faster)
        for i in range(3):
            self.collector.record_operation(
                operation_type=f"batch1_op_{i}",
                project_name="project",
                duration_seconds=5.0,  # Slower operations
                success=True
            )
        for i in range(3):
            self.collector.record_operation(
                operation_type=f"batch2_op_{i}",
                project_name="project",
                duration_seconds=1.0,  # Faster operations
                success=True
            )

        trend = self.dashboard.get_efficiency_trend()

        # Should show improvement since second batch was faster
        self.assertIn("improvement_percentage", trend)
        self.assertIn("trend", trend)
        if trend["improvement_percentage"] > 0:
            self.assertEqual(trend["trend"], "improving")


if __name__ == '__main__':
    unittest.main()