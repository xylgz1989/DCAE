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


class TestGeneratedOutputReviewerComprehensive(unittest.TestCase):
    """Comprehensive test cases for the generated output review module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reviewer_initialization_all_params(self):
        """Test initializing the reviewer with all parameters."""
        requirements_spec = {
            "functional_requirements": [
                {"id": "REQ001", "title": "User Auth", "description": "System shall authenticate users"}
            ],
            "non_functional_requirements": [
                {"id": "NFR001", "title": "Performance", "description": "System shall respond in < 1 sec"}
            ]
        }
        architecture_spec = {
            "components": [
                {"name": "Authentication Service"},
                {"name": "Data Processor"}
            ]
        }

        reviewer = GeneratedOutputReviewer(self.project_path, requirements_spec, architecture_spec)

        self.assertEqual(reviewer.project_path, Path(self.project_path))
        self.assertEqual(reviewer.requirements_spec, requirements_spec)
        self.assertEqual(reviewer.architecture_spec, architecture_spec)
        self.assertEqual(reviewer.file_extensions, {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs'})

    def test_review_empty_directory(self):
        """Test reviewing an empty directory."""
        reviewer = GeneratedOutputReviewer(self.project_path)

        report = reviewer.review_generated_output()

        self.assertIsInstance(report, ReviewReport)
        self.assertEqual(len(report.findings), 0)
        self.assertEqual(report.summary["total_findings"], 0)
        self.assertEqual(report.summary["files_reviewed"], 0)
        self.assertEqual(len(report.summary["categories_covered"]), 0)

    def test_review_code_quality_long_functions(self):
        """Test code quality review for long functions."""
        # Create a file with a long function (over 50 lines)
        long_func_file = os.path.join(self.project_path, "long_function.py")
        with open(long_func_file, 'w') as f:
            f.write("def long_function():\n")
            for i in range(55):  # More than 50 lines
                f.write(f"    x{i} = {i}\n")
            f.write("    return True\n")

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for code quality findings
        cq_findings = [f for f in report.findings if f.category == ReviewCategory.CODE_QUALITY]

        # Should find at least one finding for the long function
        self.assertGreaterEqual(len(cq_findings), 1,
                               "Expected at least one code quality finding for long function")

        # Find the specific long function finding
        long_func_findings = [f for f in cq_findings
                              if "long" in f.issue_description.lower()]
        self.assertGreaterEqual(len(long_func_findings), 1,
                               "Expected at least one finding for long function")

    def test_review_code_quality_todos_and_fixmes(self):
        """Test code quality review for TODO and FIXME comments."""
        todo_file = os.path.join(self.project_path, "todo_file.py")
        with open(todo_file, 'w') as f:
            f.write("# TODO: Fix this later\n")
            f.write("# FIXME: This is broken\n")
            f.write("def func():\n")
            f.write("    # TODO: Implement properly\n")
            f.write("    pass\n")

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for TODO and FIXME findings
        cq_findings = [f for f in report.findings if f.category == ReviewCategory.CODE_QUALITY]

        # Should have findings for both TODO and FIXME
        todo_findings = [f for f in cq_findings if "todo" in f.issue_description.lower()]
        fixme_findings = [f for f in cq_findings if "fixme" in f.issue_description.lower()]

        self.assertGreaterEqual(len(todo_findings), 2, "Expected at least 2 TODO findings")
        self.assertGreaterEqual(len(fixme_findings), 1, "Expected at least 1 FIXME finding")

        # Verify severities
        for finding in fixme_findings:
            self.assertEqual(finding.severity, ReviewSeverity.HIGH,
                           "FIXME should have HIGH severity")

    def test_review_security_hardcoded_credentials(self):
        """Test security review for hardcoded credentials."""
        sec_file = os.path.join(self.project_path, "security_risk.py")
        with open(sec_file, 'w') as f:
            f.write('password = "hardcoded_password"\n')
            f.write('secret_token = "secret_value"\n')
            f.write('api_key = "api_key_here"\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for security findings
        sec_findings = [f for f in report.findings if f.category == ReviewCategory.SECURITY]

        self.assertGreaterEqual(len(sec_findings), 1,
                               "Expected at least one security finding for hardcoded credentials")

        # All security findings should be critical for hardcoded creds
        for finding in sec_findings:
            if "hardcoded" in finding.issue_description.lower():
                self.assertEqual(finding.severity, ReviewSeverity.CRITICAL,
                               "Hardcoded credentials should have CRITICAL severity")

    def test_review_security_sql_injection(self):
        """Test security review for SQL injection vulnerabilities."""
        sql_file = os.path.join(self.project_path, "sql_injection.py")
        with open(sql_file, 'w') as f:
            f.write('def get_user(user_id):\n')
            f.write('    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")\n')
            f.write('    conn.execute("DELETE FROM users WHERE id = " + str(user_id))\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for SQL injection findings
        sec_findings = [f for f in report.findings if f.category == ReviewCategory.SECURITY]

        # Should have findings for potential SQL injection
        sql_inj_findings = [f for f in sec_findings
                            if "sql injection" in f.issue_description.lower()]

        self.assertGreaterEqual(len(sql_inj_findings), 1,
                               "Expected at least one SQL injection finding")

    def test_review_security_unsafe_imports(self):
        """Test security review for unsafe imports like pickle."""
        pickle_file = os.path.join(self.project_path, "unsafe_imports.py")
        with open(pickle_file, 'w') as f:
            f.write('import pickle\n')
            f.write('from pickle import loads\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for unsafe import findings
        sec_findings = [f for f in report.findings if f.category == ReviewCategory.SECURITY]

        # Should have findings for pickle imports
        pickle_findings = [f for f in sec_findings
                          if "pickle" in f.issue_description.lower()]

        self.assertGreaterEqual(len(pickle_findings), 1,
                               "Expected at least one finding for unsafe pickle import")

    def test_review_performance_nested_loops(self):
        """Test performance review for nested loops."""
        perf_file = os.path.join(self.project_path, "nested_loops.py")
        with open(perf_file, 'w') as f:
            f.write('def nested_example():\n')
            f.write('    for i in range(10):\n')
            f.write('        for j in range(10):\n')
            f.write('            for k in range(10):\n')
            f.write('                print(i, j, k)\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for performance findings
        perf_findings = [f for f in report.findings if f.category == ReviewCategory.PERFORMANCE]

        # Should have findings for nested loops
        nested_loop_findings = [f for f in perf_findings
                               if "nested loop" in f.issue_description.lower()]

        self.assertGreaterEqual(len(nested_loop_findings), 1,
                               "Expected at least one finding for nested loops")

    def test_review_architecture_alignment(self):
        """Test architecture alignment review."""
        # Create files that should match the expected architecture
        auth_service_file = os.path.join(self.project_path, "auth_service.py")
        with open(auth_service_file, 'w') as f:
            f.write('class AuthService:\n')
            f.write('    def authenticate(self):\n')
            f.write('        pass\n')

        # Create an architecture spec with required components
        arch_spec = {
            "components": [
                {"name": "Authentication Service"},
                {"name": "Data Processor"},
                {"name": "Notification Handler"}
            ]
        }

        reviewer = GeneratedOutputReviewer(self.project_path, architecture_spec=arch_spec)
        report = reviewer.review_generated_output()

        # Should have findings about missing components
        arch_findings = [f for f in report.findings
                        if f.category == ReviewCategory.ARCHITECTURE_ALIGNMENT]

        # Should have a finding about missing components
        missing_comp_findings = [f for f in arch_findings
                                if "missing" in f.issue_description.lower()]

        self.assertGreaterEqual(len(missing_comp_findings), 1,
                               "Expected at least one finding for missing architecture components")

    def test_review_requirements_coverage(self):
        """Test requirements coverage review."""
        req_spec = {
            "functional_requirements": [
                {"id": "REQ001", "title": "User Auth", "description": "System shall authenticate users"}
            ],
            "non_functional_requirements": [
                {"id": "NFR001", "title": "Performance", "description": "System shall respond in < 1 sec"}
            ]
        }

        reviewer = GeneratedOutputReviewer(self.project_path, requirements_spec=req_spec)
        report = reviewer.review_generated_output()

        # The method should run without errors
        # In a full implementation, this would check for requirement traces in code
        self.assertIsInstance(report, ReviewReport)

    def test_review_best_practices_print_statements(self):
        """Test best practices review for print statements."""
        bp_file = os.path.join(self.project_path, "print_statements.py")
        with open(bp_file, 'w') as f:
            f.write('def process_data():\n')
            f.write('    print("Debug: Processing data")\n')
            f.write('    print(f"Processing {len(data)} items")\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Check for best practices findings
        bp_findings = [f for f in report.findings if f.category == ReviewCategory.BEST_PRACTICES]

        # Should have findings for print statements
        print_findings = [f for f in bp_findings
                         if "print statement" in f.issue_description.lower()]

        self.assertGreaterEqual(len(print_findings), 1,
                               "Expected at least one finding for print statements")

    def test_export_report_functionality(self):
        """Test export report functionality with various data types."""
        # Create a file with issues
        issue_file = os.path.join(self.project_path, "issues.py")
        with open(issue_file, 'w') as f:
            f.write('password = "secret123"\n')  # Security issue
            f.write('def long_func():\n')  # Long function
            for i in range(55):
                f.write(f'    x{i} = {i}\n')
            f.write('    print("Debug")\n')  # Best practice issue

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Export the report
        output_path = os.path.join(self.project_path, "comprehensive_report.json")
        reviewer.export_report(report, output_path)

        # Verify file was created
        self.assertTrue(os.path.exists(output_path))

        # Verify file contains valid JSON and expected structure
        with open(output_path, 'r') as f:
            data = json.load(f)

        self.assertIn("findings", data)
        self.assertIn("summary", data)
        self.assertIn("configuration", data)
        self.assertIsInstance(data["findings"], list)
        self.assertIsInstance(data["summary"], dict)

        # Verify findings have expected structure
        for finding in data["findings"]:
            self.assertIn("id", finding)
            self.assertIn("category", finding)
            self.assertIn("severity", finding)
            self.assertIn("file_path", finding)
            self.assertIn("line_number", finding)
            self.assertIn("issue_description", finding)
            self.assertIn("recommendation", finding)
            self.assertIn("code_snippet", finding)

    def test_print_findings_summary_functionality(self):
        """Test that print findings summary works without errors."""
        # Create a file with issues
        issue_file = os.path.join(self.project_path, "issues.py")
        with open(issue_file, 'w') as f:
            f.write('password = "secret"\n')
            f.write('def long_func():\n')
            for i in range(55):
                f.write(f'    x{i} = {i}\n')
            f.write('    return True\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # This should run without raising exceptions
        try:
            reviewer.print_findings_summary(report)
        except Exception as e:
            self.fail(f"print_findings_summary raised {type(e).__name__}: {e}")

    def test_review_specific_target_path(self):
        """Test reviewing a specific target path instead of the entire project."""
        # Create subdirectory with files
        subdir = os.path.join(self.project_path, "subdir")
        os.makedirs(subdir)

        target_file = os.path.join(subdir, "target_file.py")
        with open(target_file, 'w') as f:
            f.write('password = "secret"\n')  # Security issue

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output(target_path=subdir)

        # Should find security issues in the targeted subdirectory
        sec_findings = [f for f in report.findings if f.category == ReviewCategory.SECURITY]
        self.assertGreaterEqual(len(sec_findings), 1,
                               "Expected security findings in targeted subdirectory")

    def test_review_multiple_file_types(self):
        """Test reviewing different file types."""
        # Create files with different extensions
        js_file = os.path.join(self.project_path, "script.js")
        with open(js_file, 'w') as f:
            f.write('// TODO: Fix this later\n')
            f.write('var password = "hardcoded";\n')  # Security issue

        java_file = os.path.join(self.project_path, "App.java")
        with open(java_file, 'w') as f:
            f.write('public class App {\n')
            f.write('    public static void main(String[] args) {\n')
            f.write('        String secret = "hardcoded_secret";\n')  # Security issue
            f.write('    }\n')
            f.write('}\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Should find issues in multiple file types
        all_findings = report.findings
        self.assertGreaterEqual(len(all_findings), 1,
                               "Expected findings in multiple file types")


class TestReviewEnumsAndDataClasses(unittest.TestCase):
    """Test review enums and data classes."""

    def test_review_severity_enum_values(self):
        """Test that ReviewSeverity enum has expected values."""
        self.assertEqual(ReviewSeverity.INFO.value, "info")
        self.assertEqual(ReviewSeverity.LOW.value, "low")
        self.assertEqual(ReviewSeverity.MEDIUM.value, "medium")
        self.assertEqual(ReviewSeverity.HIGH.value, "high")
        self.assertEqual(ReviewSeverity.CRITICAL.value, "critical")

    def test_review_category_enum_values(self):
        """Test that ReviewCategory enum has expected values."""
        self.assertEqual(ReviewCategory.CODE_QUALITY.value, "code_quality")
        self.assertEqual(ReviewCategory.ARCHITECTURE_ALIGNMENT.value, "architecture_alignment")
        self.assertEqual(ReviewCategory.REQUIREMENTS_COVERAGE.value, "requirements_coverage")
        self.assertEqual(ReviewCategory.SECURITY.value, "security")
        self.assertEqual(ReviewCategory.PERFORMANCE.value, "performance")
        self.assertEqual(ReviewCategory.BEST_PRACTICES.value, "best_practices")

    def test_review_finding_creation(self):
        """Test creating a ReviewFinding instance."""
        finding = ReviewFinding(
            id="test_finding_1",
            category=ReviewCategory.SECURITY,
            severity=ReviewSeverity.HIGH,
            file_path="test.py",
            line_number=10,
            issue_description="Test security issue",
            recommendation="Fix the issue",
            code_snippet="vulnerable_code()"
        )

        self.assertEqual(finding.id, "test_finding_1")
        self.assertEqual(finding.category, ReviewCategory.SECURITY)
        self.assertEqual(finding.severity, ReviewSeverity.HIGH)
        self.assertEqual(finding.file_path, "test.py")
        self.assertEqual(finding.line_number, 10)
        self.assertEqual(finding.issue_description, "Test security issue")
        self.assertEqual(finding.recommendation, "Fix the issue")
        self.assertEqual(finding.code_snippet, "vulnerable_code()")

    def test_review_report_creation(self):
        """Test creating a ReviewReport instance."""
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
            summary={"total_findings": 1, "critical_findings": 1},
            timestamp="2023-01-01T00:00:00",
            review_configuration={"security_enabled": True}
        )

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].id, "test_finding_1")
        self.assertEqual(report.summary["total_findings"], 1)
        self.assertEqual(report.timestamp, "2023-01-01T00:00:00")
        self.assertEqual(report.review_configuration["security_enabled"], True)


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_review_nonexistent_path(self):
        """Test handling of nonexistent paths."""
        reviewer = GeneratedOutputReviewer(self.project_path)

        # This should not raise an exception even if path doesn't exist
        nonexistent_path = os.path.join(self.project_path, "nonexistent_dir")
        report = reviewer.review_generated_output(target_path=nonexistent_path)

        self.assertIsInstance(report, ReviewReport)
        self.assertEqual(report.summary["total_findings"], 0)

    def test_review_unreadable_file(self):
        """Test handling of unreadable files."""
        # Create a file with unusual encoding or permissions
        test_file = os.path.join(self.temp_dir, "unreadable.py")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('# Test file\n')

        # Make the file temporarily unreadable to test error handling
        os.chmod(test_file, 0o000)  # Remove read permissions

        reviewer = GeneratedOutputReviewer(self.temp_dir)
        report = reviewer.review_generated_output()

        # Should not crash, even with unreadable files
        self.assertIsInstance(report, ReviewReport)

        # Restore permissions for cleanup
        os.chmod(test_file, 0o644)

    def test_review_empty_files(self):
        """Test handling of empty files."""
        empty_file = os.path.join(self.project_path, "empty.py")
        with open(empty_file, 'w') as f:
            pass  # Create empty file

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Should handle empty files gracefully
        self.assertIsInstance(report, ReviewReport)

    def test_review_large_files(self):
        """Test handling of very large files."""
        large_file = os.path.join(self.project_path, "large.py")
        with open(large_file, 'w') as f:
            f.write('"""Large file for testing"""\n')
            # Add many lines to make it large
            for i in range(1000):
                f.write(f'# Line {i}\n')
                f.write(f'def func_{i}():\n')
                f.write(f'    return {i}\n\n')

        reviewer = GeneratedOutputReviewer(self.project_path)
        report = reviewer.review_generated_output()

        # Should handle large files without crashing
        self.assertIsInstance(report, ReviewReport)


def run_tests():
    """Run all tests and return results."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    import sys
    # Run the tests
    result = run_tests()

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)