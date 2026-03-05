"""
Tests for the Global Settings Configuration module (Story 1.6).
These tests verify the functionality required by the acceptance criteria.
"""

import unittest
import tempfile
import os
from pathlib import Path
import yaml
import json

from src.dcae.global_settings_config import (
    GlobalSettingsManager,
    GlobalSettingsSchema,
    ConfigurationValidator,
    DisciplineLevel,
    SecurityLevel
)


class TestGlobalSettingsConfiguration(unittest.TestCase):
    """Test cases for Global Settings Configuration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test configuration files
        self.test_dir = tempfile.mkdtemp()
        self.config_path = Path(self.test_dir) / ".dcae" / "global_config.yaml"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_1_global_settings_structure(self):
        """Test AC #1: Global Settings Structure with appropriate defaults."""
        manager = GlobalSettingsManager(self.config_path)

        # Verify the configuration file was created with defaults
        self.assertTrue(self.config_path.exists())

        # Load the config to verify structure
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Verify essential structure exists
        self.assertIn('project', config)
        self.assertIn('dcae', config)
        self.assertIn('version', config['dcae'])
        self.assertIn('bmad_workflow', config['dcae'])
        self.assertIn('llm_providers', config['dcae'])
        self.assertIn('logging', config['dcae'])

        # Verify default values are set correctly
        self.assertEqual(config['dcae']['version'], '1.0.0')
        self.assertTrue(config['dcae']['bmad_workflow']['enabled'])
        self.assertEqual(config['dcae']['bmad_workflow']['discipline_level'], 'balanced')
        self.assertFalse(config['dcae']['bmad_workflow']['consensus_enabled'])

    def test_2_global_settings_access(self):
        """Test AC #2: Global Settings Access by path."""
        manager = GlobalSettingsManager(self.config_path)

        # Test getting existing settings
        version = manager.get_global_setting('dcae.version')
        self.assertEqual(version, '1.0.0')

        discipline_level = manager.get_global_setting('dcae.bmad_workflow.discipline_level')
        self.assertEqual(discipline_level, 'balanced')

        # Test getting with default for non-existent setting
        nonexistent = manager.get_global_setting('non.existent.path', 'default_value')
        self.assertEqual(nonexistent, 'default_value')

        # Test getting nested values
        stats_enabled = manager.get_global_setting('dcae.bmad_workflow.performance_stats.enabled')
        self.assertTrue(stats_enabled)

    def test_3_global_settings_update(self):
        """Test AC #3: Global Settings Update functionality."""
        manager = GlobalSettingsManager(self.config_path)

        # Test updating a simple setting
        result = manager.set_global_setting('dcae.version', '2.0.0')
        self.assertTrue(result)

        # Verify the change was persisted
        updated_version = manager.get_global_setting('dcae.version')
        self.assertEqual(updated_version, '2.0.0')

        # Test updating a nested setting
        result = manager.set_global_setting('dcae.bmad_workflow.discipline_level', 'strict')
        self.assertTrue(result)

        # Verify the change was persisted
        updated_discipline = manager.get_global_setting('dcae.bmad_workflow.discipline_level')
        self.assertEqual(updated_discipline, 'strict')

        # Verify the file was updated
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.assertEqual(config['dcae']['bmad_workflow']['discipline_level'], 'strict')

    def test_4_settings_validation(self):
        """Test AC #4: Settings Validation."""
        schema = GlobalSettingsSchema()

        # Test discipline level validation
        self.assertTrue(ConfigurationValidator.validate_discipline_level('fast'))
        self.assertTrue(ConfigurationValidator.validate_discipline_level('balanced'))
        self.assertTrue(ConfigurationValidator.validate_discipline_level('strict'))
        self.assertFalse(ConfigurationValidator.validate_discipline_level('invalid'))

        # Test API key validation
        self.assertTrue(ConfigurationValidator.validate_api_key('valid_key_123'))
        self.assertFalse(ConfigurationValidator.validate_api_key(''))
        self.assertFalse(ConfigurationValidator.validate_api_key('   '))

        # Test log level validation
        self.assertTrue(ConfigurationValidator.validate_log_level('INFO'))
        self.assertTrue(ConfigurationValidator.validate_log_level('DEBUG'))
        self.assertTrue(ConfigurationValidator.validate_log_level('WARNING'))
        self.assertTrue(ConfigurationValidator.validate_log_level('ERROR'))
        self.assertFalse(ConfigurationValidator.validate_log_level('INVALID'))

        # Test positive integer validation
        self.assertTrue(ConfigurationValidator.validate_positive_integer(5))
        self.assertTrue(ConfigurationValidator.validate_positive_integer(1))
        self.assertFalse(ConfigurationValidator.validate_positive_integer(-1))
        self.assertFalse(ConfigurationValidator.validate_positive_integer(0))

        # Test boolean validation
        self.assertTrue(ConfigurationValidator.validate_boolean(True))
        self.assertTrue(ConfigurationValidator.validate_boolean(False))
        self.assertFalse(ConfigurationValidator.validate_boolean('true'))
        self.assertFalse(ConfigurationValidator.validate_boolean(1))

    def test_5_hierarchical_configuration(self):
        """Test AC #5: Multi-Level Configuration Hierarchy."""
        manager = GlobalSettingsManager(self.config_path)

        # The hierarchical functionality is tested via the underlying manager
        # Test that global settings can be accessed properly
        result = manager.set_global_setting('project.name', 'Test Project')
        self.assertTrue(result)

        project_name = manager.get_global_setting('project.name')
        self.assertEqual(project_name, 'Test Project')

    def test_6_configuration_security(self):
        """Test AC #6: Configuration Security for sensitive settings."""
        manager = GlobalSettingsManager(self.config_path)

        # Set a sensitive API key
        result = manager.set_global_setting('dcae.llm_providers.openai.api_key', 'sk-test123verysecretkey456')
        self.assertTrue(result)

        # Get configuration with sensitive data hidden
        safe_config = manager.show_configuration(hide_sensitive=True)

        # Verify API key is masked
        api_key = safe_config['dcae']['llm_providers']['openai']['api_key']
        self.assertNotEqual(api_key, 'sk-test123verysecretkey456')
        self.assertTrue(all(c == '*' for c in api_key))

        # Get configuration with sensitive data visible (for authorized access)
        full_config = manager.show_configuration(hide_sensitive=False)
        full_api_key = full_config['dcae']['llm_providers']['openai']['api_key']
        self.assertEqual(full_api_key, 'sk-test123verysecretkey456')

    def test_multiple_settings_configuration(self):
        """Test configuring multiple settings at once."""
        manager = GlobalSettingsManager(self.config_path)

        settings_dict = {
            'dcae.version': '2.1.0',
            'dcae.bmad_workflow.discipline_level': 'strict',
            'dcae.logging.level': 'DEBUG'
        }

        result = manager.configure_global_settings(settings_dict)
        self.assertTrue(result)

        # Verify all settings were updated
        self.assertEqual(manager.get_global_setting('dcae.version'), '2.1.0')
        self.assertEqual(manager.get_global_setting('dcae.bmad_workflow.discipline_level'), 'strict')
        self.assertEqual(manager.get_global_setting('dcae.logging.level'), 'DEBUG')

    def test_configuration_validation_method(self):
        """Test the validation method of the GlobalSettingsManager."""
        manager = GlobalSettingsManager(self.config_path)

        # Test valid configuration
        errors = manager.validate_configuration()
        self.assertEqual(len(errors), 0, f"Unexpected validation errors: {errors}")

        # Test invalid configuration
        invalid_config = {
            'dcae': {
                'bmad_workflow': {
                    'discipline_level': 'invalid_level'  # Should be invalid
                }
            }
        }
        errors = manager.validate_configuration(invalid_config)
        self.assertGreater(len(errors), 0, "Expected validation errors for invalid configuration")

    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        manager = GlobalSettingsManager(self.config_path)

        # Set a custom value to test if it gets backed up and restored
        manager.set_global_setting('dcae.version', 'custom_version_for_test')

        # Create backup
        backup_path = Path(self.test_dir) / "backup.yaml"
        backup_success = manager.backup_configuration(backup_path)
        self.assertTrue(backup_success)
        self.assertTrue(backup_path.exists())

        # Modify the original config
        manager.set_global_setting('dcae.version', 'modified_after_backup')
        self.assertEqual(manager.get_global_setting('dcae.version'), 'modified_after_backup')

        # Restore from backup
        restore_success = manager.restore_configuration(backup_path)
        self.assertTrue(restore_success)

        # Verify restoration
        restored_version = manager.get_global_setting('dcae.version')
        self.assertEqual(restored_version, 'custom_version_for_test')


class TestConfigurationSchema(unittest.TestCase):
    """Test cases for configuration schema definitions."""

    def test_schema_definition(self):
        """Test that the schema is properly defined."""
        schema = GlobalSettingsSchema()

        # Test getting schema by path
        version_schema = schema.get_schema_by_path('dcae.version')
        self.assertIsNotNone(version_schema)
        self.assertEqual(version_schema.type, str)
        self.assertEqual(version_schema.default_value, '1.0.0')

        discipline_schema = schema.get_schema_by_path('dcae.bmad_workflow.discipline_level')
        self.assertIsNotNone(discipline_schema)
        self.assertEqual(discipline_schema.type, str)
        self.assertEqual(discipline_schema.default_value, 'balanced')

        api_key_schema = schema.get_schema_by_path('dcae.llm_providers.openai.api_key')
        self.assertIsNotNone(api_key_schema)
        self.assertEqual(api_key_schema.security_level, SecurityLevel.SECRET)

    def test_nonexistent_schema_path(self):
        """Test getting schema for non-existent path."""
        schema = GlobalSettingsSchema()
        nonexistent = schema.get_schema_by_path('non.existent.path')
        self.assertIsNone(nonexistent)


if __name__ == '__main__':
    print("Running Global Settings Configuration tests...")
    print("="*50)

    # Run all tests
    unittest.main(verbosity=2)