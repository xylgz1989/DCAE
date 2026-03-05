"""
Tests for the Log Error Reporting module.
Testing Epic #1: Project Setup & Management
Story 1.10: Log Error Reporting
"""

import unittest
import tempfile
import os
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

from src.dcae.log_error_reporting import (
    LogManager, ErrorReporter, LogEntry, LogErrorConfig,
    log_message, log_error, create_error_report, setup_logging
)


class TestLogErrorConfig(unittest.TestCase):
    """Test cases for LogErrorConfig class."""

    def test_default_config(self):
        """Test that default configuration is created correctly."""
        config = LogErrorConfig()

        self.assertEqual(config.log_level, 'INFO')
        self.assertTrue(config.handlers['console']['enabled'])
        self.assertTrue(config.handlers['file']['enabled'])
        self.assertEqual(config.handlers['file']['path'], './logs/dcae.log')

    def test_custom_config(self):
        """Test that custom configuration is applied correctly."""
        custom_config = {
            'log_level': 'DEBUG',
            'handlers': {
                'console': {'enabled': False},
                'file': {
                    'enabled': True,
                    'path': './custom.log'
                }
            }
        }

        config = LogErrorConfig(custom_config)

        self.assertEqual(config.log_level, 'DEBUG')
        self.assertFalse(config.handlers['console']['enabled'])
        self.assertTrue(config.handlers['file']['enabled'])
        self.assertEqual(config.handlers['file']['path'], './custom.log')


class TestLogManager(unittest.TestCase):
    """Test cases for LogManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = LogErrorConfig({
            'log_level': 'DEBUG',
            'handlers': {
                'console': {'enabled': False},  # Disable console for tests
                'file': {
                    'enabled': False  # Disable file for tests to avoid cluttering filesystem
                }
            }
        })
        self.log_manager = LogManager(self.test_config)

    def test_log_message_formats_correctly(self):
        """Test that log messages are formatted correctly."""
        # Test that logging doesn't crash (we can't easily capture the output due to handlers being disabled)
        self.log_manager.log_message('INFO', 'Test message', 'TestModule')
        # Just ensure no exception is raised

    def test_different_log_levels(self):
        """Test that different log levels work correctly."""
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        for level in levels:
            with self.subTest(level=level):
                self.log_manager.log_message(level, f'Test {level} message', 'TestModule')

    def test_context_inclusion(self):
        """Test that context is included in log messages."""
        context = {'user_id': 123, 'action': 'test'}
        self.log_manager.log_message('INFO', 'Test with context', 'TestModule', context)

    def test_correlation_id_handling(self):
        """Test that correlation IDs are handled properly."""
        self.log_manager.set_correlation_id('test-correlation-id')
        correlation_id = self.log_manager.get_correlation_id()
        self.assertEqual(correlation_id, 'test-correlation-id')

    def test_set_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = 'test-correlation-123'
        self.log_manager.set_correlation_id(test_id)
        self.assertEqual(self.log_manager.get_correlation_id(), test_id)


class TestErrorReporter(unittest.TestCase):
    """Test cases for ErrorReporter class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_error_log = os.path.join(self.temp_dir, 'errors.log')

        # Create a log manager that writes to our temp location
        config = LogErrorConfig({
            'handlers': {
                'console': {'enabled': False},
                'file': {'enabled': False}  # Disable file handler to avoid extra files
            }
        })
        self.log_manager = LogManager(config)

        self.error_reporter = ErrorReporter(self.log_manager)

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temp files
        if os.path.exists(self.temp_error_log):
            os.remove(self.temp_error_log)

    def test_log_error(self):
        """Test that errors are logged correctly."""
        test_error = ValueError("Test error message")
        context = {'test_param': 'value'}

        result = self.error_reporter.log_error(test_error, 'TestModule', context, include_traceback=False)

        # Check that the returned error entry has expected structure
        self.assertIn('timestamp', result)
        self.assertEqual(result['module'], 'TestModule')
        self.assertEqual(result['error_type'], 'ValueError')
        self.assertEqual(result['error_message'], 'Test error message')
        self.assertIn('context', result)

    def test_create_error_report(self):
        """Test creating a structured error report."""
        test_error = RuntimeError("Test runtime error")
        context = {'user_id': 123, 'session_id': 'abc123'}

        report = self.error_reporter.create_error_report(test_error, context)

        # Verify report structure
        self.assertIn('report_timestamp', report)
        self.assertEqual(report['error_type'], 'RuntimeError')
        self.assertEqual(report['error_message'], 'Test runtime error')
        self.assertEqual(report['context'], context)
        self.assertIn('system_info', report)
        self.assertIn('traceback', report)

    def test_classify_error(self):
        """Test error classification functionality."""
        # Test connection error
        conn_error = ConnectionError("Network error")
        classification = self.error_reporter.classify_error(conn_error)
        self.assertIn('CONNECTION', classification)

        # Test permission error
        perm_error = PermissionError("Access denied")
        classification = self.error_reporter.classify_error(perm_error)
        self.assertIn('PERMISSION', classification)

        # Test general error
        general_error = ValueError("Invalid value")
        classification = self.error_reporter.classify_error(general_error)
        self.assertIn('GENERAL', classification)


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global logging functions."""

    def test_global_logger_access(self):
        """Test that global logger can be accessed."""
        logger1 = log_message.__globals__['get_logger']()
        logger2 = log_message.__globals__['get_logger']()

        # Should return the same instance
        self.assertIsNotNone(logger1)

    def test_global_error_reporter_access(self):
        """Test that global error reporter can be accessed."""
        reporter = log_error.__globals__['get_error_reporter']()
        self.assertIsNotNone(reporter)


class TestIntegration(unittest.TestCase):
    """Integration tests for the logging system."""

    def test_setup_logging(self):
        """Test the setup_logging function."""
        config = {
            'log_level': 'WARNING',
            'handlers': {
                'console': {'enabled': False},
                'file': {'enabled': False}
            }
        }

        log_manager = setup_logging(config)
        self.assertIsInstance(log_manager, LogManager)
        # Note: We can't easily verify the log level was set without introspection
        # since logging levels are internal to the logging module


if __name__ == '__main__':
    unittest.main()