import unittest
import tempfile
import os
from src.dcae.testing_documentation.test_generator import TestGenerator, FrameworkPreference, TestType
from src.dcae.testing_documentation.documentation_generator import DocumentationGenerator, DocFormat
from src.dcae.testing_documentation.test_reviewer import TestReviewer
from src.dcae.testing_documentation.cli_interface import CLIInterface


class TestEpic8RealWorldScenario(unittest.TestCase):
    """Test Epic #8 functionality in a realistic end-to-end scenario."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Realistic code sample simulating a real module
        self.realistic_code = '''
"""Utility functions for mathematical operations."""

def calculate_compound_interest(principal: float, rate: float, time: float, compounds_per_year: int) -> float:
    """
    Calculate compound interest using the formula A = P(1 + r/n)^(nt).

    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as decimal)
        time: Time period in years
        compounds_per_year: Number of times interest is compounded per year

    Returns:
        Final amount after compound interest
    """
    if principal <= 0 or rate < 0 or time < 0 or compounds_per_year <= 0:
        raise ValueError("All parameters must be positive (rate can be zero)")

    return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)


def is_prime(n: int) -> bool:
    """
    Determine if a number is prime.

    Args:
        n: Integer to check for primality

    Returns:
        True if the number is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Check odd divisors up to sqrt(n)
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False

    return True


class DataProcessor:
    """Class to process numerical data with various operations."""

    def __init__(self, data: list):
        """Initialize with a list of numbers."""
        if not isinstance(data, list):
            raise TypeError("Data must be a list")
        self.data = data

    def get_average(self) -> float:
        """Calculate the average of the stored data."""
        if not self.data:
            raise ValueError("Cannot calculate average of empty dataset")
        return sum(self.data) / len(self.data)

    def get_median(self) -> float:
        """Calculate the median of the stored data."""
        if not self.data:
            raise ValueError("Cannot calculate median of empty dataset")

        sorted_data = sorted(self.data)
        n = len(sorted_data)
        mid = n // 2

        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            return sorted_data[mid]

    def add_data_point(self, value: float):
        """Add a new data point to the dataset."""
        if not isinstance(value, (int, float)):
            raise TypeError("Data point must be a number")
        self.data.append(float(value))
'''


    def test_complete_development_workflow(self):
        """Test the complete workflow: code → tests → docs → review."""
        # 1. Generate tests from the code
        test_gen = TestGenerator(framework=FrameworkPreference.PYTEST)
        generated_tests = test_gen.generate_from_code(self.realistic_code, TestType.UNIT)

        # 2. Generate documentation from the code
        doc_gen = DocumentationGenerator(format=DocFormat.MARKDOWN)
        docs = doc_gen.generate_from_code(self.realistic_code)

        # 3. Review the generated tests
        reviewer = TestReviewer()
        review_comments = reviewer.review_test_case(generated_tests)

        # 4. Validate test quality
        is_valid, issues = reviewer.validate_test_quality(generated_tests)

        # 5. Suggest and apply modifications if needed
        modifications = reviewer.suggest_modifications(generated_tests)
        if modifications:
            improved_tests = reviewer.apply_modifications(generated_tests, modifications)
        else:
            improved_tests = generated_tests

        # Assertions to verify the workflow completed properly
        self.assertIsInstance(generated_tests, str)
        self.assertIsInstance(docs, str)
        self.assertIsInstance(review_comments, list)
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(issues, list)
        self.assertIsInstance(improved_tests, str)

        # Verify generated content contains expected elements
        self.assertIn("calculate_compound_interest", generated_tests)
        self.assertIn("is_prime", generated_tests)
        # Instead of looking for "DataProcessor", look for its methods
        self.assertIn("get_average", generated_tests)  # A method in DataProcessor class
        self.assertIn("get_median", generated_tests)   # A method in DataProcessor class
        self.assertIn("add_data_point", generated_tests)  # A method in DataProcessor class

        self.assertIn("calculate compound interest", docs.lower())
        self.assertIn("is prime", docs.lower())
        self.assertIn("dataprocessor", docs.lower())

        # The improved tests should be similar but potentially enhanced
        self.assertEqual(len(improved_tests), len(generated_tests))  # Same length in this case since no modifications were made in templates

    def test_requirements_driven_workflow(self):
        """Test generating both tests and docs from requirements."""
        requirements = [
            {
                'id': 'FIN-CALC-001',
                'name': 'Compound Interest Calculation',
                'description': 'System shall calculate compound interest based on principal, rate, time, and compounding frequency',
                'acceptance_criteria': 'Given principal=1000, rate=0.05, time=2, compounds=4, when calculating, then result should be approximately 1104.49'
            },
            {
                'id': 'MATH-UTIL-002',
                'name': 'Prime Number Detection',
                'description': 'System shall determine if a number is prime',
                'acceptance_criteria': 'Given number=17, when checking for primality, then should return true; given number=15, then should return false'
            }
        ]

        # Generate tests from requirements
        test_gen = TestGenerator(framework=FrameworkPreference.PYTEST)
        req_tests = test_gen.generate_from_requirements(requirements, TestType.UNIT)

        # Generate docs from requirements
        doc_gen = DocumentationGenerator(format=DocFormat.MARKDOWN)
        req_docs = doc_gen.generate_from_requirements(requirements)

        # Verify the outputs
        self.assertIsInstance(req_tests, str)
        self.assertIsInstance(req_docs, str)

        # Check that requirement information is reflected in outputs
        self.assertIn("compound_interest", req_tests.lower())
        self.assertIn("prime", req_tests.lower())

        self.assertIn("FIN-CALC-001", req_docs)
        self.assertIn("MATH-UTIL-002", req_docs)

    def test_cli_simulation(self):
        """Simulate CLI operations to validate the command-line interface."""
        # Create temporary files for the simulation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as code_file:
            code_file.write(self.realistic_code)
            code_file_path = code_file.name

        try:
            # Test CLI argument parsing (without executing)
            cli = CLIInterface()

            # Parse test generation command
            test_cmd = cli.parser.parse_args([
                'generate-tests',
                '--source', code_file_path,
                '--framework', 'pytest',
                '--type', 'unit',
                '--output', 'temp_tests.py'
            ])

            self.assertEqual(test_cmd.command, 'generate-tests')
            self.assertEqual(test_cmd.source, code_file_path)
            self.assertEqual(test_cmd.framework, 'pytest')

            # Parse documentation generation command
            doc_cmd = cli.parser.parse_args([
                'generate-docs',
                '--source', code_file_path,
                '--format', 'markdown',
                '--output', 'temp_docs.md'
            ])

            self.assertEqual(doc_cmd.command, 'generate-docs')
            self.assertEqual(doc_cmd.source, code_file_path)
            self.assertEqual(doc_cmd.format, 'markdown')

        finally:
            # Cleanup
            os.unlink(code_file_path)

    def test_cross_module_integration(self):
        """Test integration between all Epic #8 modules."""
        # Generate from code
        test_gen = TestGenerator(framework=FrameworkPreference.PYTEST)
        doc_gen = DocumentationGenerator(format=DocFormat.MARKDOWN)

        tests = test_gen.generate_from_code(self.realistic_code, TestType.UNIT)
        docs = doc_gen.generate_from_code(self.realistic_code)

        # Review the generated tests
        reviewer = TestReviewer()
        is_valid, issues = reviewer.validate_test_quality(tests)

        # Verify all components worked together
        self.assertTrue(len(tests) > 0, "Tests should be generated")
        self.assertTrue(len(docs) > 0, "Docs should be generated")
        self.assertIsInstance(is_valid, bool, "Validation should return boolean")

        # Check that generated content contains expected elements from the original code
        elements_to_check = [
            "calculate_compound_interest",
            "is_prime",
            # For class methods, the tests are named after the methods, not the class name itself
            "get_average",  # A method in DataProcessor class
            "get_median",   # Another method in DataProcessor class
            "add_data_point", # Another method in DataProcessor class
            "test_",       # Tests should have test_ prefix
        ]

        for element in elements_to_check:
            self.assertIn(element, tests, f"Element '{element}' should be in generated tests")

        # Check documentation for appropriate elements (excluding test_-specific ones)
        doc_elements_to_check = [
            "calculate_compound_interest",
            "is_prime",
            "get_average",
            "get_median",
            "add_data_point",
        ]

        for element in doc_elements_to_check:
            self.assertIn(element, docs, f"Element '{element}' should be in generated docs")


if __name__ == '__main__':
    unittest.main()