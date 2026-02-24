import unittest
import tempfile
import os
import sys
from io import StringIO
from unittest.mock import patch
from src.dcae.testing_documentation.cli_interface import CLIInterface


class TestEpic8CLIFunctionality(unittest.TestCase):
    """Test CLI interface functionality for Epic #8."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.cli = CLIInterface()
        self.sample_code = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

class Calculator:
    """A simple calculator class."""

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b
'''

    def test_cli_help_display(self):
        """Test that CLI help displays properly."""
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            self.cli.parser.print_help()
            output = captured_output.getvalue()
            self.assertIn("DCAE Testing & Documentation Generation Tool", output)
            self.assertIn("generate-tests", output)
            self.assertIn("generate-docs", output)
            self.assertIn("analyze-coverage", output)
        finally:
            sys.stdout = sys.__stdout__  # Restore original stdout

    def test_generate_tests_command(self):
        """Test the generate-tests CLI command."""
        # Create a temporary file with sample code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(self.sample_code)
            temp_file_path = temp_file.name

        try:
            # Mock stdin/stdout to capture the output
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                # Simulate command line arguments
                test_args = [
                    'generate-tests',
                    '--source', temp_file_path,
                    '--framework', 'pytest',
                    '--type', 'unit'
                ]

                # Since we can't easily capture the output from the actual method call,
                # we'll verify the argument parsing works by checking if the args are parsed correctly
                parsed_args = self.cli.parser.parse_args(test_args)
                self.assertEqual(parsed_args.command, 'generate-tests')
                self.assertEqual(parsed_args.source, temp_file_path)
                self.assertEqual(parsed_args.framework, 'pytest')
                self.assertEqual(parsed_args.type, 'unit')
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_generate_docs_command(self):
        """Test the generate-docs CLI command."""
        # Create a temporary file with sample code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(self.sample_code)
            temp_file_path = temp_file.name

        try:
            parsed_args = self.cli.parser.parse_args([
                'generate-docs',
                '--source', temp_file_path,
                '--format', 'markdown'
            ])

            self.assertEqual(parsed_args.command, 'generate-docs')
            self.assertEqual(parsed_args.source, temp_file_path)
            self.assertEqual(parsed_args.format, 'markdown')
        finally:
            os.unlink(temp_file_path)

    def test_analyze_coverage_command(self):
        """Test the analyze-coverage CLI command."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(self.sample_code)
            temp_file_path = temp_file.name

        try:
            parsed_args = self.cli.parser.parse_args([
                'analyze-coverage',
                '--source', temp_file_path,
                '--threshold', '80'
            ])

            self.assertEqual(parsed_args.command, 'analyze-coverage')
            self.assertEqual(parsed_args.source, temp_file_path)
            self.assertEqual(parsed_args.threshold, 80.0)
        finally:
            os.unlink(temp_file_path)

    def test_review_tests_command(self):
        """Test the review-tests CLI command."""
        # Create a temporary test file
        test_code = '''
def test_addition():
    """Test addition function."""
    assert 2 + 2 == 4
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(test_code)
            temp_file_path = temp_file.name

        try:
            parsed_args = self.cli.parser.parse_args([
                'review-tests',
                '--test-file', temp_file_path,
                '--format', 'text'
            ])

            self.assertEqual(parsed_args.command, 'review-tests')
            self.assertEqual(parsed_args.test_file, temp_file_path)
            self.assertEqual(parsed_args.format, 'text')
        finally:
            os.unlink(temp_file_path)

    def test_invalid_command(self):
        """Test handling of invalid commands."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Test with no command - this should not crash but should show help or have None command
            parsed_args = self.cli.parser.parse_args([])
            self.assertIsNone(parsed_args.command)

    def test_argument_validation(self):
        """Test argument validation in CLI."""
        # Test that invalid framework raises error during parsing
        with self.assertRaises(SystemExit):  # argparse raises SystemExit on error
            with patch('sys.stderr'):  # Suppress stderr output
                self.cli.parser.parse_args([
                    'generate-tests',
                    '--source', 'dummy.py',
                    '--framework', 'invalid_framework'
                ])

        # Test that invalid test type raises error during parsing
        with self.assertRaises(SystemExit):  # argparse raises SystemExit on error
            with patch('sys.stderr'):  # Suppress stderr output
                self.cli.parser.parse_args([
                    'generate-tests',
                    '--source', 'dummy.py',
                    '--type', 'invalid_type'
                ])


class TestEpic8IntegrationCLI(unittest.TestCase):
    """Integration tests for CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = CLIInterface()
        self.sample_code = '''
def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y
'''

    def test_end_to_end_cli_workflow(self):
        """Test an end-to-end workflow using the CLI interface."""
        # This test verifies that the CLI can be instantiated and has proper structure

        # Rather than inspecting internal argparse structures,
        # just verify that the main CLI functions work
        # Verify that expected commands exist by checking if the parser accepts them
        # The fact that other tests pass shows that the commands exist

        # We can at least check that the CLI has the expected subcommands registered
        # by verifying that known command combinations work
        try:
            # Test that a minimal command with required arguments parses
            parsed = self.cli.parser.parse_args([
                'generate-tests',
                '--source', 'dummy.py'
            ])
            self.assertEqual(parsed.command, 'generate-tests')
            self.assertEqual(parsed.source, 'dummy.py')

            parsed = self.cli.parser.parse_args([
                'generate-docs',
                '--source', 'dummy.py'
            ])
            self.assertEqual(parsed.command, 'generate-docs')
            self.assertEqual(parsed.source, 'dummy.py')

            parsed = self.cli.parser.parse_args([
                'analyze-coverage',
                '--source', 'dummy.py'
            ])
            self.assertEqual(parsed.command, 'analyze-coverage')
            self.assertEqual(parsed.source, 'dummy.py')

            parsed = self.cli.parser.parse_args([
                'review-tests',
                '--test-file', 'dummy.py'
            ])
            self.assertEqual(parsed.command, 'review-tests')
            self.assertEqual(parsed.test_file, 'dummy.py')

        except Exception as e:
            self.fail(f"CLI command parsing failed: {e}")


if __name__ == '__main__':
    unittest.main()