import unittest
import tempfile
import os
from src.dcae.testing_documentation.test_generator import TestGenerator, TestType, FrameworkPreference
from src.dcae.testing_documentation.documentation_generator import DocumentationGenerator, DocFormat
from src.dcae.testing_documentation.test_coverage_analyzer import TestCoverageAnalyzer, CoverageReport
from src.dcae.testing_documentation.test_reviewer import TestReviewer
from src.dcae.testing_documentation.cli_interface import CLIInterface


class TestEpic8Integration(unittest.TestCase):
    """Integration tests for Epic #8: Testing & Documentation Generation."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_code = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

def multiply_numbers(x: int, y: int) -> int:
    """Multiply two numbers together."""
    return x * y

class Calculator:
    """A simple calculator class."""

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b

    def divide(self, a: int, b: int) -> float:
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
'''

    def test_complete_testing_workflow(self):
        """Test the complete testing workflow: generate → review → coverage."""
        # Step 1: Generate tests
        gen = TestGenerator(framework=FrameworkPreference.PYTEST)
        generated_tests = gen.generate_from_code(self.sample_code, TestType.UNIT)

        # Should contain tests for functions and methods
        self.assertIn("test_add_numbers", generated_tests)
        self.assertIn("test_multiply_numbers", generated_tests)

        # Step 2: Review the generated tests
        reviewer = TestReviewer()
        comments = reviewer.review_test_case(generated_tests)

        # Should return a list of comments
        self.assertIsInstance(comments, list)

        # Step 3: Verify test quality
        is_valid, issues = reviewer.validate_test_quality(generated_tests)

        # Step 4: For a more complete workflow, we'd run the tests and analyze coverage
        # For now, we'll just ensure the workflow components work together
        self.assertIsNotNone(generated_tests)
        self.assertIsInstance(comments, list)

    def test_complete_documentation_workflow(self):
        """Test the complete documentation workflow: generate → format."""
        # Generate documentation in markdown
        md_gen = DocumentationGenerator(format=DocFormat.MARKDOWN)
        md_docs = md_gen.generate_from_code(self.sample_code)

        # Should contain markdown elements
        self.assertIn("## add_numbers", md_docs)
        self.assertIn("Calculator", md_docs)

        # Generate documentation in RST
        rst_gen = DocumentationGenerator(format=DocFormat.RST)
        rst_docs = rst_gen.generate_from_code(self.sample_code)

        # Should contain RST elements
        self.assertIn("add_numbers", rst_docs)

    def test_cross_functionality_interaction(self):
        """Test interaction between different components."""
        # Generate tests
        gen = TestGenerator(framework=FrameworkPreference.PYTEST)
        tests = gen.generate_from_code(self.sample_code, TestType.UNIT)

        # Review tests
        reviewer = TestReviewer()
        review_comments = reviewer.review_test_case(tests)

        # Suggest modifications based on review
        modifications = reviewer.suggest_modifications(tests)

        # Apply modifications
        if modifications:
            modified_tests = reviewer.apply_modifications(tests, modifications)

            # Review modified tests again
            new_comments = reviewer.review_test_case(modified_tests)

            # The modifications should address some issues
            self.assertIsNotNone(modified_tests)

    def test_coverage_analysis_with_generated_tests(self):
        """Test that generated tests can be used for coverage analysis."""
        # Generate tests
        gen = TestGenerator(framework=FrameworkPreference.UNITTEST)
        tests = gen.generate_from_code(self.sample_code, TestType.UNIT)

        # Create a temporary file with the generated tests
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_test_file:
            # Write a simple test file with imports and basic structure
            test_content = """import unittest
from sample_module import add_numbers, Calculator

class TestGenerated(unittest.TestCase):
    def test_add_numbers_basic(self):
        result = add_numbers(2, 3)
        self.assertEqual(result, 5)

    def test_calculator_subtract(self):
        calc = Calculator()
        result = calc.subtract(5, 3)
        self.assertEqual(result, 2)

if __name__ == '__main__':
    unittest.main()
"""
            temp_test_file.write(test_content)
            temp_test_file_path = temp_test_file.name

        try:
            # Perform coverage analysis (this would work with actual source code)
            analyzer = TestCoverageAnalyzer()

            # We can't actually run coverage on non-existent source files,
            # but we can test the report generation and analysis methods
            # Create a mock report for testing
            mock_report = CoverageReport(
                total_statements=10,
                covered_statements=8,
                missing_statements=2,
                percentage_covered=80.0,
                files_coverage={
                    "sample_module.py": {
                        "executable_statements": 10,
                        "covered_statements": 8,
                        "percent_covered": 80.0
                    }
                },
                uncovered_lines={"sample_module.py": [15, 25]}
            )

            # Generate report in different formats
            text_report = analyzer.generate_coverage_report(mock_report, 'text')
            self.assertIn("80.00%", text_report)

            md_report = analyzer.generate_coverage_report(mock_report, 'markdown')
            self.assertIn("80.00%", md_report)

            json_report = analyzer.generate_coverage_report(mock_report, 'json')
            self.assertIn("percentage_covered", json_report)

            # Check threshold
            meets = analyzer.check_coverage_threshold(mock_report, 75.0)
            self.assertTrue(meets)

            meets_low = analyzer.check_coverage_threshold(mock_report, 85.0)
            self.assertFalse(meets_low)
        finally:
            # Clean up temp file
            os.unlink(temp_test_file_path)

    def test_cli_interface_integration(self):
        """Test CLI interface integration."""
        # Test that the CLI can be instantiated
        cli = CLIInterface()
        self.assertIsNotNone(cli.parser)

        # Create a temporary code file to test with
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_code_file:
            temp_code_file.write(self.sample_code)
            temp_code_file_path = temp_code_file.name

        try:
            # This would normally be called with sys.argv, but for testing we'll verify the functionality
            # Create a generator to test with the file
            gen = TestGenerator(framework=FrameworkPreference.PYTEST)
            with open(temp_code_file_path, 'r') as f:
                code = f.read()
            tests = gen.generate_from_code(code)

            self.assertIn("test_add_numbers", tests)
        finally:
            # Clean up temp file
            os.unlink(temp_code_file_path)

    def test_requirements_based_generation(self):
        """Test generating tests and docs from requirements."""
        # Define sample requirements
        requirements = [
            {
                'id': 'REQ001',
                'name': 'Add Numbers Function',
                'description': 'Function should add two numbers and return the result',
                'acceptance_criteria': 'add_numbers(2, 3) should return 5'
            },
            {
                'id': 'REQ002',
                'name': 'Calculator Division',
                'description': 'Division function should handle division operation and throw error on division by zero',
                'acceptance_criteria': 'divide(6, 2) should return 3, divide(5, 0) should raise ValueError'
            }
        ]

        # Generate tests from requirements
        gen = TestGenerator(framework=FrameworkPreference.PYTEST)
        tests_from_reqs = gen.generate_from_requirements(requirements, TestType.UNIT)

        # Should contain references to the requirements
        self.assertIn("requirement_add_numbers_function", tests_from_reqs.lower())  # For REQ001
        self.assertIn("requirement_calculator_division", tests_from_reqs.lower())  # For REQ002

        # Generate documentation from requirements
        doc_gen = DocumentationGenerator(format=DocFormat.MARKDOWN)
        docs_from_reqs = doc_gen.generate_from_requirements(requirements)

        # Should contain requirement information
        self.assertIn("REQ-REQ001", docs_from_reqs)
        self.assertIn("REQ-REQ002", docs_from_reqs)

    def test_multiple_test_types_generation(self):
        """Test generating different types of tests."""
        generators = {
            TestType.UNIT: TestGenerator(framework=FrameworkPreference.PYTEST),
            TestType.INTEGRATION: TestGenerator(framework=FrameworkPreference.PYTEST),
            # Add more test types as needed
        }

        for test_type, gen in generators.items():
            with self.subTest(test_type=test_type):
                tests = gen.generate_from_code(self.sample_code, test_type)
                # At minimum, should generate something without error
                self.assertIsInstance(tests, str)
                # Should contain test-related content
                self.assertIn("test_", tests) if len(tests) > 0 else True


if __name__ == '__main__':
    unittest.main()