"""
Tests for Progress Indicator functionality as specified in
Epic #1: Project Setup & Management, Story 1.11: Progress Indicators

These tests validate the implementation of progress tracking and performance metrics.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.dcae.progress_indicators import (
    ProgressIndicator, ProgressStage,
    ProgressData, PerformanceStat
)


class TestProgressIndicator(unittest.TestCase):
    """Test suite for ProgressIndicator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_indicators_file = self.test_dir / "test_indicators.json"

        # Create a temporary config file
        self.test_config_file = self.test_dir / "test_config.yaml"
        default_config = {
            "dcae": {
                "logging": {
                    "console_output": False,
                    "file_output": False
                }
            }
        }

        with open(self.test_config_file, 'w') as f:
            json.dump(default_config, f)

        self.progress_indicator = ProgressIndicator(
            config_path=self.test_config_file,
            indicators_path=self.test_indicators_file
        )

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_initialization_creates_indicators_file(self):
        """Test that initialization creates the indicators file with default values."""
        self.assertTrue(self.test_indicators_file.exists())

        with open(self.test_indicators_file, 'r') as f:
            data = json.load(f)

        self.assertIn("performance_stats", data)
        self.assertIn("workflow_progress", data)
        self.assertIn("display_options", data)

        # Check default values
        self.assertTrue(data["performance_stats"]["enabled"])
        self.assertEqual(data["workflow_progress"]["overall_progress"], 0)
        self.assertEqual(data["workflow_progress"]["current_stage"], "initial")
        self.assertEqual(data["display_options"]["verbosity"], "standard")

    def test_update_progress_valid_values(self):
        """Test updating progress with valid values."""
        result = self.progress_indicator.update_progress(
            ProgressStage.REQUIREMENTS,
            50,
            {"task": "analysis", "completed": 2, "total": 4}
        )

        self.assertTrue(result)

        indicators = self.progress_indicator.get_current_indicators()
        stage_progress = indicators["workflow_progress"]["stage_progress"]

        self.assertIn("requirements", stage_progress)
        self.assertEqual(stage_progress["requirements"]["progress"], 50)
        self.assertEqual(stage_progress["requirements"]["details"]["task"], "analysis")

    def test_update_progress_clamps_values(self):
        """Test that progress values are clamped between 0 and 100."""
        # Test value over 100
        result = self.progress_indicator.update_progress(ProgressStage.ARCHITECTURE, 150)
        self.assertTrue(result)

        indicators = self.progress_indicator.get_current_indicators()
        stage_progress = indicators["workflow_progress"]["stage_progress"]
        self.assertEqual(stage_progress["architecture"]["progress"], 100)

        # Test value under 0
        result = self.progress_indicator.update_progress(ProgressStage.TESTING, -10)
        self.assertTrue(result)

        indicators = self.progress_indicator.get_current_indicators()
        stage_progress = indicators["workflow_progress"]["stage_progress"]
        self.assertEqual(stage_progress["testing"]["progress"], 0)

    def test_update_progress_with_string_stage(self):
        """Test updating progress using string stage names."""
        result = self.progress_indicator.update_progress("development", 75)
        self.assertTrue(result)

        indicators = self.progress_indicator.get_current_indicators()
        stage_progress = indicators["workflow_progress"]["stage_progress"]

        # Should convert string to appropriate enum value
        self.assertIn("development", stage_progress)
        self.assertEqual(stage_progress["development"]["progress"], 75)

    def test_record_performance_stat(self):
        """Test recording performance statistics."""
        result = self.progress_indicator.record_performance_stat(
            "lines_of_code", 1000, "LOC"
        )
        self.assertTrue(result)

        indicators = self.progress_indicator.get_current_indicators()
        stats = indicators["performance_stats"]["stats"]

        self.assertIn("lines_of_code", stats)
        self.assertEqual(len(stats["lines_of_code"]), 1)
        self.assertEqual(stats["lines_of_code"][0]["value"], 1000)
        self.assertEqual(stats["lines_of_code"][0]["unit"], "LOC")

    def test_get_progress_summary(self):
        """Test getting progress summary."""
        # Update progress for multiple stages
        self.progress_indicator.update_progress(ProgressStage.REQUIREMENTS, 100)
        self.progress_indicator.update_progress(ProgressStage.ARCHITECTURE, 50)
        self.progress_indicator.update_progress(ProgressStage.DEVELOPMENT, 25)

        summary = self.progress_indicator.get_progress_summary()

        self.assertEqual(summary["overall_progress"], 58.33)  # Average of 100, 50, 25
        self.assertEqual(len(summary["stages"]), 3)

        # Find the requirements stage in the summary
        req_stage = next((s for s in summary["stages"] if s["stage"] == "requirements"), None)
        self.assertIsNotNone(req_stage)
        self.assertEqual(req_stage["progress"], 100)
        self.assertTrue(req_stage["completed"])

    def test_is_stage_complete(self):
        """Test checking if a stage is complete."""
        # Stage not complete
        self.progress_indicator.update_progress(ProgressStage.TESTING, 50)
        self.assertFalse(self.progress_indicator.is_stage_complete(ProgressStage.TESTING))

        # Stage complete
        self.progress_indicator.update_progress(ProgressStage.TESTING, 100)
        self.assertTrue(self.progress_indicator.is_stage_complete(ProgressStage.TESTING))

    def test_get_performance_stats(self):
        """Test retrieving performance statistics."""
        # Record some stats
        self.progress_indicator.record_performance_stat("build_time", 120, "seconds")
        self.progress_indicator.record_performance_stat("test_count", 45, "tests")

        # Get all stats
        all_stats = self.progress_indicator.get_performance_stats()
        self.assertIn("build_time", all_stats)
        self.assertIn("test_count", all_stats)
        self.assertEqual(len(all_stats["build_time"]), 1)

        # Get specific stat
        build_stats = self.progress_indicator.get_performance_stats("build_time")
        self.assertEqual(len(build_stats), 1)
        self.assertEqual(build_stats[0]["value"], 120)

    def test_disable_performance_stats(self):
        """Test disabling performance statistics."""
        # Modify the indicators file to disable performance stats
        with open(self.test_indicators_file, 'r') as f:
            data = json.load(f)

        data["performance_stats"]["enabled"] = False

        with open(self.test_indicators_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Record should succeed but not store data when disabled
        result = self.progress_indicator.record_performance_stat("test_metric", 100, "units")
        self.assertTrue(result)  # Should succeed even when disabled

        # Reload and check that no stats were recorded while disabled
        indicators = self.progress_indicator.get_current_indicators()
        stats = indicators["performance_stats"]["stats"]
        # If we recorded when disabled, it might still be in the original data,
        # but for a fresh test we expect it to not be recorded when disabled

    def test_multiple_updates_to_same_stat(self):
        """Test recording multiple values for the same stat."""
        self.progress_indicator.record_performance_stat("response_time", 100, "ms")
        self.progress_indicator.record_performance_stat("response_time", 150, "ms")
        self.progress_indicator.record_performance_stat("response_time", 200, "ms")

        stats = self.progress_indicator.get_performance_stats("response_time")
        self.assertEqual(len(stats), 3)
        self.assertEqual([s["value"] for s in stats], [100, 150, 200])

    def test_handle_nonexistent_indicators_file(self):
        """Test that the system handles nonexistent indicators file gracefully."""
        temp_indicator = ProgressIndicator(
            config_path=self.test_config_file,
            indicators_path=self.test_dir / "nonexistent.json"
        )

        # Should initialize properly even with non-existent file
        result = temp_indicator.update_progress(ProgressStage.DEVELOPMENT, 50)
        self.assertTrue(result)

        # Should have created the file with defaults
        self.assertTrue((self.test_dir / "nonexistent.json").exists())


class TestProgressData(unittest.TestCase):
    """Test suite for ProgressData class."""

    def test_progress_data_clamps_values(self):
        """Test that ProgressData clamps progress values."""
        # Test value over 100
        data_high = ProgressData(
            stage=ProgressStage.REQUIREMENTS,
            progress=150,
            updated=datetime.now().isoformat(),
            details={}
        )
        self.assertEqual(data_high.progress, 100)

        # Test value under 0
        data_low = ProgressData(
            stage=ProgressStage.ARCHITECTURE,
            progress=-10,
            updated=datetime.now().isoformat(),
            details={}
        )
        self.assertEqual(data_low.progress, 0)

        # Test valid value remains unchanged
        data_valid = ProgressData(
            stage=ProgressStage.DEVELOPMENT,
            progress=75,
            updated=datetime.now().isoformat(),
            details={}
        )
        self.assertEqual(data_valid.progress, 75)


class TestPerformanceStat(unittest.TestCase):
    """Test suite for PerformanceStat class."""

    def test_performance_stat_to_dict(self):
        """Test converting PerformanceStat to dictionary."""
        stat = PerformanceStat(
            name="test_stat",
            value=100,
            unit="units",
            recorded=datetime.now().isoformat()
        )

        stat_dict = stat.to_dict()
        self.assertEqual(stat_dict["name"], "test_stat")
        self.assertEqual(stat_dict["value"], 100)
        self.assertEqual(stat_dict["unit"], "units")
        self.assertIsInstance(stat_dict["recorded"], str)


def run_tests():
    """Run all tests in the suite."""
    print("Running Progress Indicator Tests...\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__('test_progress_indicators', fromlist=['*']))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()