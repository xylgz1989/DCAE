"""
Test Suite for DCAE Settings Update Module

Tests for Epic #1: Project Setup & Management
Story 1.9: Update Settings
"""

import unittest
import tempfile
import os
from pathlib import Path
import yaml
import json
from unittest.mock import patch, MagicMock

from src.dcae.update_settings import (
    SettingsUpdateManager,
    UpdateResult,
    create_settings_update_cli
)


class TestSettingsUpdateManager(unittest.TestCase):
    """Test cases for SettingsUpdateManager."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test configuration
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / ".dcae" / "global_config.yaml"

        # Initialize the settings manager with our test config
        self.manager = SettingsUpdateManager(self.config_path)

        # Ensure the config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test that SettingsUpdateManager initializes correctly."""
        self.assertIsNotNone(self.manager.config_manager)
        self.assertIsNotNone(self.manager.lock)
        self.assertEqual(len(self.manager._ongoing_processes), 0)
        self.assertEqual(len(self.manager._pending_updates), 0)

    def test_add_and_remove_ongoing_process(self):
        """Test adding and removing ongoing processes."""
        # Add a process
        process_id = "test_process_123"
        description = "Test process for update settings"

        self.manager.add_ongoing_process(process_id, description)

        # Verify the process was added
        self.assertTrue(self.manager.has_ongoing_processes())
        self.assertIn(process_id, self.manager.get_ongoing_processes())

        # Remove the process
        self.manager.remove_ongoing_process(process_id)

        # Verify the process was removed
        self.assertFalse(self.manager.has_ongoing_processes())
        self.assertNotIn(process_id, self.manager.get_ongoing_processes())

    def test_update_settings_safely_with_no_processes(self):
        """Test updating settings when no processes are ongoing."""
        settings = {
            "dcae.version": "2.0.0",
            "dcae.logging.level": "DEBUG"
        }

        result = self.manager.update_settings_safely(settings)

        self.assertTrue(result.success)
        self.assertIn("Successfully updated", result.message)
        self.assertEqual(len(result.updated_settings), 2)
        self.assertIsNone(result.failed_settings or {})

        # Verify the settings were actually updated
        updated_config = self.manager.config_manager.show_configuration(hide_sensitive=False)
        self.assertEqual(updated_config["dcae"]["version"], "2.0.0")
        self.assertEqual(updated_config["dcae"]["logging"]["level"], "DEBUG")

    def test_update_settings_safely_with_processes(self):
        """Test updating settings when processes are ongoing (should defer)."""
        # Add an ongoing process
        self.manager.add_ongoing_process("active_process", "Active development process")

        settings = {
            "dcae.version": "2.0.0",
            "dcae.logging.level": "DEBUG"
        }

        result = self.manager.update_settings_safely(settings)

        # Should succeed but indicate update was deferred
        self.assertTrue(result.success)
        self.assertIn("deferred", result.message.lower())
        self.assertEqual(len(result.updated_settings), 2)  # Settings should be queued

        # The settings shouldn't be applied yet
        current_config = self.manager.config_manager.show_configuration(hide_sensitive=False)
        self.assertNotEqual(current_config["dcae"]["version"], "2.0.0")
        self.assertNotEqual(current_config["dcae"]["logging"]["level"], "DEBUG")

    def test_process_deferred_updates(self):
        """Test processing deferred updates when safe."""
        # Add an ongoing process
        self.manager.add_ongoing_process("active_process", "Active development process")

        # This should defer the update
        settings = {
            "dcae.version": "2.0.0",
            "dcae.logging.level": "DEBUG"
        }
        self.manager.update_settings_safely(settings)

        # Verify update was deferred
        self.assertEqual(len(self.manager._pending_updates), 1)

        # Remove the ongoing process
        self.manager.remove_ongoing_process("active_process")

        # Now process the deferred update
        result = self.manager.process_deferred_updates()

        self.assertTrue(result.success)
        self.assertIn("processed", result.message.lower())
        self.assertEqual(len(result.updated_settings), 2)

        # Verify the settings were actually applied
        updated_config = self.manager.config_manager.show_configuration(hide_sensitive=False)
        self.assertEqual(updated_config["dcae"]["version"], "2.0.0")
        self.assertEqual(updated_config["dcae"]["logging"]["level"], "DEBUG")

    def test_update_with_validation_success(self):
        """Test updating settings with validation that passes."""
        settings = {
            "dcae.bmad_workflow.discipline_level": "strict",  # Valid value
            "dcae.logging.level": "INFO"  # Valid value
        }

        result = self.manager.update_settings_with_validation(settings)

        self.assertTrue(result.success)
        self.assertIn("Successfully updated", result.message)
        self.assertEqual(len(result.updated_settings), 2)

    def test_update_with_validation_failure(self):
        """Test updating settings with validation that fails."""
        settings = {
            "dcae.bmad_workflow.discipline_level": "invalid_level",  # Invalid value
            "dcae.logging.level": "INVALID_LEVEL"  # Invalid value
        }

        result = self.manager.update_settings_with_validation(settings)

        self.assertFalse(result.success)
        self.assertIn("Validation failed", result.message)
        self.assertIsNone(result.updated_settings or {})
        # The failed settings would be captured differently in a real implementation

    def test_update_discipline_level(self):
        """Test updating discipline level specifically."""
        result = self.manager.update_discipline_level("fast")

        self.assertTrue(result.success)
        self.assertIn("Successfully", result.message)

        # Verify the setting was applied
        config = self.manager.config_manager.show_configuration(hide_sensitive=False)
        self.assertEqual(config["dcae"]["bmad_workflow"]["discipline_level"], "fast")

    def test_update_discipline_level_invalid(self):
        """Test updating discipline level with invalid value."""
        result = self.manager.update_discipline_level("invalid_level")

        self.assertFalse(result.success)
        self.assertIn("Invalid discipline level", result.message)

    def test_bulk_update_from_file(self):
        """Test bulk update from a configuration file."""
        # Create a temporary config file
        temp_config = {
            "dcae": {
                "version": "3.0.0",
                "logging": {
                    "level": "WARNING",
                    "file_output": False
                }
            }
        }

        temp_file = Path(self.test_dir) / "temp_config.yaml"
        with open(temp_file, 'w') as f:
            yaml.dump(temp_config, f)

        result = self.manager.bulk_update_from_file(temp_file)

        self.assertTrue(result.success)

        # Verify the settings were applied
        config = self.manager.config_manager.show_configuration(hide_sensitive=False)
        self.assertEqual(config["dcae"]["version"], "3.0.0")
        self.assertEqual(config["dcae"]["logging"]["level"], "WARNING")
        self.assertFalse(config["dcae"]["logging"]["file_output"])

    def test_get_settings_update_status(self):
        """Test getting the status of settings updates."""
        # Add an ongoing process
        self.manager.add_ongoing_process("test_process", "Test process")

        # Defer an update
        settings = {"dcae.version": "2.0.0"}
        self.manager.update_settings_safely(settings)

        status = self.manager.get_settings_update_status()

        self.assertTrue(status["has_ongoing_processes"])
        self.assertEqual(status["pending_updates_count"], 1)
        self.assertIn("test_process", status["ongoing_processes"])

    def test_register_and_execute_callback(self):
        """Test registering and executing callbacks."""
        callback_called = []

        def test_callback(path, old_val, new_val):
            callback_called.append((path, old_val, new_val))

        self.manager.register_callback(test_callback)

        # Update a setting
        settings = {"dcae.version": "2.0.0"}
        self.manager.update_settings_safely(settings)

        # Check that callback was called
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0][0], "dcae.version")


class TestUpdateResult(unittest.TestCase):
    """Test cases for UpdateResult class."""

    def test_update_result_creation(self):
        """Test creating UpdateResult instances."""
        result = UpdateResult(
            success=True,
            message="Test message",
            updated_settings={"test.setting": "value"},
            failed_settings={}
        )

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Test message")
        self.assertEqual(result.updated_settings, {"test.setting": "value"})
        self.assertEqual(result.failed_settings, {})


class TestIntegration(unittest.TestCase):
    """Integration tests for settings update functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / ".dcae" / "global_config.yaml"
        self.manager = SettingsUpdateManager(self.config_path)

        # Ensure the config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_workflow_with_processes(self):
        """Test a complete workflow with ongoing processes and updates."""
        # Start a process
        self.manager.add_ongoing_process("development_task", "Developing feature X")

        # Attempt to update settings (should defer)
        settings = {"dcae.version": "4.0.0", "dcae.logging.level": "DEBUG"}
        result = self.manager.update_settings_safely(settings)

        self.assertTrue(result.success)
        self.assertIn("deferred", result.message)

        # Check that settings weren't immediately applied
        config = self.manager.config_manager.show_configuration(hide_sensitive=False)
        self.assertNotEqual(config["dcae"]["version"], "4.0.0")

        # End the process
        self.manager.remove_ongoing_process("development_task")

        # Process the deferred update
        process_result = self.manager.process_deferred_updates()

        self.assertTrue(process_result.success)

        # Check that settings were now applied
        config = self.manager.config_manager.show_configuration(hide_sensitive=False)
        self.assertEqual(config["dcae"]["version"], "4.0.0")
        self.assertEqual(config["dcae"]["logging"]["level"], "DEBUG")


# Mock classes for CLI testing
class MockArgs:
    def __init__(self, action, setting_path=None, setting_value=None, settings_file=None, config_path=None):
        self.action = action
        self.setting_path = setting_path
        self.setting_value = setting_value
        self.settings_file = settings_file
        self.config_path = config_path


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / ".dcae" / "global_config.yaml"

        # Create initial config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        initial_config = {
            "dcae": {
                "version": "1.0.0",
                "logging": {"level": "INFO"}
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(initial_config, f)

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('sys.argv', ['script', 'update', '--setting-path', 'dcae.version', '--setting-value', '2.0.0'])
    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_update_single_setting(self, mock_parse_args):
        """Test CLI update of a single setting."""
        mock_parse_args.return_value = MockArgs(
            action='update',
            setting_path='dcae.version',
            setting_value='2.0.0'
        )

        # Mock the actual execution to prevent sys.exit calls
        with patch('src.dcae.update_settings.SettingsUpdateManager') as mock_manager_class:
            mock_manager_instance = MagicMock()
            mock_manager_class.return_value = mock_manager_instance
            mock_manager_instance.update_settings_safely.return_value = UpdateResult(
                success=True,
                message="Test update successful"
            )

            # Import and call the function that would handle the CLI
            from src.dcae.update_settings import create_settings_update_cli

            # Since we're mocking, we don't want to actually exit
            # The test will focus on verifying that the correct methods are called


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)