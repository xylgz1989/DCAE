import os
import tempfile
import unittest
from pathlib import Path
import shutil

from src.dcae.generated_output_review import (
    GeneratedOutputReviewer,
    ReviewSeverity,
    ReviewCategory,
    ReviewFinding,
    ReviewReport
)


class TestGeneratedOutputReviewer(unittest.TestCase):
    """Test cases for the generated output review module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reviewer_initialization_without_specs(self):
        """Test initializing the reviewer without requirements or architecture specs."""
        reviewer = GeneratedOutputReviewer(self.project_path)

        self.assertEqual(reviewer.project_path, Path(self.project_path))
        self.assertEqual(reviewer.requirements_spec, {})
        self.assertEqual(reviewer.architecture_spec, {})

    def test_reviewer_initialization_with_specs(self):
        """Test initializing the reviewer with requirements and architecture specs."""
        requirements_spec = {
            "functional_requirements": [
                {"id": "REQ001", "title": "Test Req", "description": "A test requirement"}
            ]
        }
        architecture_spec = {
            "components": [
                {"name": "Test Component"}
            ]
        }

        reviewer = GeneratedOutputReviewer(self.project_path, requirements_spec, architecture_spec)

        self.assertEqual(reviewer.requirements_spec, requirements_spec)
        self.assertEqual(reviewer.architecture_spec, architecture_spec)

    def test_review_empty_project(self):
        """Test reviewing an empty project."""
        reviewer = GeneratedOutputReviewer(self.project_path)

        report = reviewer.review_generated_output()

        # Should have a report with no findings
        self.assertIsInstance(report, ReviewReport)
        self.assertEqual(len(report.findings), 0)
        self.assertIn("total_findings", report.summary)

    def test_review_project_with_simple_file(self):
        """Test reviewing a project with a simple file."""
        # Create a simple Python file
        simple_file = os.path.join(self.project_path, "simple.py")
        with open(simple_file, 'w') as f:
            f.write("# A simple file without issues\n")

        reviewer = GeneratedOutputReviewer(self.project_path)

        report = reviewer.review_generated_output()

        # Should have a report
        self.assertIsInstance(report, ReviewReport)
        # May have no findings or just informational ones

    def test_review_project_with_issues(self):
        """Test reviewing a project with known issues."""
        # Create a Python file with security issues
        risky_file = os.path.join(self.project_path, "risky.py")
        with open(risky_file, 'w') as f:
            f.write("""
# File with issues
password = "hardcoded_secret"  # Security issue
def long_function():
    # Function with many lines to potentially trigger code quality issue
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x_val = 27
    y_val = 28
    z_val = 29
    aa = 30
    ab = 31
    ac = 32
    ad = 33
    ae = 34
    af = 35
    ag = 36
    ah = 37
    ai = 38
    aj = 39
    ak = 40
    al = 41
    am = 42
    an = 43
    ao = 44
    ap = 45
    aq = 46
    ar = 47
    as_val = 48
    at = 49
    au = 50
    av = 51
    aw = 52
    ax = 53
    ay = 54
    az = 55
    ba = 56
    bb = 57
    bc = 58
    bd = 59
    be = 60
    bf = 61  # Over 50 lines to trigger function length issue
    return x_val
""")

        reviewer = GeneratedOutputReviewer(self.project_path)

        report = reviewer.review_generated_output()

        # Should have findings (at minimum security findings)
        self.assertIsInstance(report, ReviewReport)

        # Check for security finding
        security_findings = [f for f in report.findings if f.category == ReviewCategory.SECURITY]

        # We should at least have security findings for hardcoded credentials
        self.assertGreaterEqual(len(security_findings), 1,
                                "Expected at least one security finding for hardcoded credentials")

    def test_export_report(self):
        """Test exporting the review report."""
        # Create a file with issues
        risky_file = os.path.join(self.project_path, "risky.py")
        with open(risky_file, 'w') as f:
            f.write('password = "hardcoded"  # Security issue\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Export the report
        output_path = os.path.join(self.project_path, "test_report.json")
        reviewer.export_report(report, output_path)

        # Verify file was created
        self.assertTrue(os.path.exists(output_path))

        # Verify file contains JSON data
        with open(output_path, 'r') as f:
            import json
            data = json.load(f)
            self.assertIn("findings", data)
            self.assertIn("summary", data)

    def test_print_findings_summary(self):
        """Test printing the findings summary."""
        # Create a file with issues
        risky_file = os.path.join(self.project_path, "risky.py")
        with open(risky_file, 'w') as f:
            f.write('password = "hardcoded"  # Security issue\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Just test that the method runs without error
        try:
            reviewer.print_findings_summary(report)
        except Exception as e:
            self.fail(f"print_findings_summary raised {type(e).__name__}: {e}")


class TestReviewComponents(unittest.TestCase):
    """Test cases for individual review components."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_review_finding_creation(self):
        """Test creating a review finding."""
        finding = ReviewFinding(
            id="test_finding_1",
            category=ReviewCategory.SECURITY,
            severity=ReviewSeverity.HIGH,
            file_path="test.py",
            line_number=10,
            issue_description="Test issue",
            recommendation="Fix the issue",
            code_snippet="problematic_code()"
        )

        self.assertEqual(finding.id, "test_finding_1")
        self.assertEqual(finding.category, ReviewCategory.SECURITY)
        self.assertEqual(finding.severity, ReviewSeverity.HIGH)
        self.assertEqual(finding.file_path, "test.py")

    def test_review_report_creation(self):
        """Test creating a review report."""
        finding = ReviewFinding(
            id="test_finding_1",
            category=ReviewCategory.SECURITY,
            severity=ReviewSeverity.HIGH,
            file_path="test.py",
            line_number=10,
            issue_description="Test issue",
            recommendation="Fix the issue",
            code_snippet="problematic_code()"
        )

        report = ReviewReport(
            findings=[finding],
            summary={"total_findings": 1},
            timestamp="2023-01-01T00:00:00",
            review_configuration={}
        )

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].id, "test_finding_1")
        self.assertEqual(report.summary["total_findings"], 1)


if __name__ == '__main__':
    unittest.main()