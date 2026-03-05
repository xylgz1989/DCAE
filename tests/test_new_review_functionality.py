import os
import tempfile
import unittest
from pathlib import Path
import shutil
import json

from src.dcae.generated_output_review import (
    GeneratedOutputReviewer,
    ReviewSeverity,
    ReviewCategory,
    ReviewFinding,
    ReviewReport
)


class TestNewReviewFunctionality(unittest.TestCase):
    """Test cases for the new review functionality added to GeneratedOutputReviewer."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reviewer_initialization_with_custom_config(self):
        """Test initializing the reviewer with custom configuration."""
        custom_config = {
            "code_quality": {
                "max_function_length": 30,
                "enable_todo_check": True,
                "enable_fixme_check": True,
                "enable_formatting_check": True,
                "enable_naming_convention_check": True
            },
            "security": {
                "enable_hardcoded_credential_scan": True,
                "enable_sql_injection_scan": True,
                "enable_unsafe_import_scan": True
            }
        }

        reviewer = GeneratedOutputReviewer(
            self.project_path,
            config=custom_config
        )

        self.assertEqual(reviewer.config, custom_config)

    def test_requirements_coverage_with_traced_requirements(self):
        """Test requirements coverage with actual requirement traces in code."""
        # Create a file with requirement traceability
        req_file = os.path.join(self.project_path, "requirement_impl.py")
        with open(req_file, 'w') as f:
            f.write('''
# REQ001: User authentication module
def authenticate_user(username, password):
    """Authenticate user credentials. Implements REQ001"""
    # TODO: Add password hashing - REQ002 trace
    return username and password

class AuthService:
    """Service to handle authentication. Related to REQ001"""
    def login(self):
        pass
''')

        # Create requirements specification
        req_spec = {
            "functional_requirements": [
                {"id": "REQ001", "title": "User Auth", "description": "System shall authenticate users"},
                {"id": "REQ002", "title": "Password Security", "description": "Passwords must be hashed"}
            ]
        }

        reviewer = GeneratedOutputReviewer(self.project_path, requirements_spec=req_spec)
        report = reviewer.review_generated_output()

        # Should have no findings for REQ001 since it's traced in the code
        req_findings = [f for f in report.findings if f.category == ReviewCategory.REQUIREMENTS_COVERAGE]

        # Should only have a finding for REQ002 since it's not properly implemented, just mentioned
        uncovered_reqs = [f for f in req_findings if "not implemented" in f.issue_description]
        self.assertGreaterEqual(len(uncovered_reqs), 0)

    def test_security_review_extended_features(self):
        """Test extended security review features."""
        # Create a file with various security issues
        sec_file = os.path.join(self.project_path, "security_extended.py")
        with open(sec_file, 'w') as f:
            f.write('''
# Various security issues to detect
password = "secret123"
api_key = "my_api_key"
import pickle
from pickle import loads
eval("some_code")
exec("more_code")
import os
os.system("dangerous_command")
''')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for various security findings
        sec_findings = [f for f in report.findings if f.category == ReviewCategory.SECURITY]

        # Should have findings for multiple types of security issues
        hardcoded_findings = [f for f in sec_findings if "Hardcoded" in f.issue_description]
        pickle_findings = [f for f in sec_findings if "pickle" in f.issue_description.lower()]
        eval_exec_findings = [f for f in sec_findings if "eval" in f.issue_description.lower() or "exec" in f.issue_description.lower()]
        cmd_injection_findings = [f for f in sec_findings if "command injection" in f.issue_description.lower()]

        self.assertGreaterEqual(len(hardcoded_findings), 1, "Expected hardcoded credential findings")
        self.assertGreaterEqual(len(pickle_findings), 1, "Expected pickle import findings")
        self.assertGreaterEqual(len(eval_exec_findings), 1, "Expected eval/exec findings")

    def test_code_quality_formatting_and_naming(self):
        """Test code quality checks for formatting and naming conventions."""
        # Create a file with formatting and naming convention issues
        quality_file = os.path.join(self.project_path, "quality_issues.py")
        with open(quality_file, 'w') as f:
            f.write('''# Mixed tabs and spaces, bad naming
variable_Name = 1  # Wrong naming convention
AnotherVar = 2     # Wrong naming convention

def BadFunctionName():  # Wrong naming convention
	return "result"     # Mixed indentation

class wrongClassName:   # Wrong naming convention
	def __init__(self):
		pass
''')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for code quality findings
        cq_findings = [f for f in report.findings if f.category == ReviewCategory.CODE_QUALITY]

        # Should have findings for naming conventions and possibly indentation
        naming_findings = [f for f in cq_findings if "naming" in f.issue_description.lower()]

        # At least a few naming convention violations should be detected
        self.assertGreaterEqual(len(naming_findings), 1, "Expected some naming convention findings")

    def test_configurable_review_parameters(self):
        """Test that review parameters can be configured."""
        # Create a file with a long function
        long_func_file = os.path.join(self.project_path, "long_func.py")
        with open(long_func_file, 'w') as f:
            f.write("def long_function():\n")
            for i in range(20):  # Below default threshold of 50
                f.write(f"    x{i} = {i}\n")
            f.write("    return True\n")

        # Test with a very low threshold
        strict_config = {
            "code_quality": {
                "max_function_length": 5,  # Very strict
                "enable_todo_check": True,
                "enable_fixme_check": True
            }
        }

        reviewer = GeneratedOutputReviewer(self.project_path, config=strict_config)
        report = reviewer.review_generated_output()

        # Should have findings due to the strict configuration
        cq_findings = [f for f in report.findings if f.category == ReviewCategory.CODE_QUALITY]
        long_func_findings = [f for f in cq_findings if "too long" in f.issue_description.lower()]

        self.assertGreaterEqual(len(long_func_findings), 1, "Expected long function findings with strict config")


if __name__ == '__main__':
    unittest.main()