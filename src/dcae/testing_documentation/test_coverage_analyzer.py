"""Module for analyzing test coverage of code."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import subprocess
import sys
import os


@dataclass
class CoverageReport:
    """Represents a test coverage report."""
    total_statements: int
    covered_statements: int
    missing_statements: int
    percentage_covered: float
    files_coverage: Dict[str, Dict[str, Any]]
    uncovered_lines: Dict[str, List[int]]


class TestCoverageAnalyzer:
    """Analyzes test coverage of code using various coverage tools."""

    def __init__(self):
        """Initialize the test coverage analyzer."""
        self.coverage_tool = "coverage"  # Default to coverage.py

    def analyze_coverage(self, source_paths: List[str], test_paths: List[str] = None) -> CoverageReport:
        """
        Analyze test coverage for the given source paths.

        Args:
            source_paths: List of source code file or directory paths to analyze
            test_paths: Optional list of test file paths (if not provided, assumes tests are in 'tests/' dir)

        Returns:
            CoverageReport containing coverage information
        """
        # If test paths not provided, try to find them
        if test_paths is None:
            test_paths = self._discover_test_paths()

        # Run coverage analysis
        coverage_result = self._run_coverage_analysis(source_paths, test_paths)

        # Parse the coverage result into a CoverageReport
        report = self._parse_coverage_result(coverage_result, source_paths)

        return report

    def _discover_test_paths(self) -> List[str]:
        """Discover test paths in common locations."""
        test_paths = []
        common_locations = ['tests/', 'test/', 'spec/', 'specs/']

        for location in common_locations:
            if os.path.exists(location):
                test_paths.append(location)

        return test_paths

    def _run_coverage_analysis(self, source_paths: List[str], test_paths: List[str]) -> Dict[str, Any]:
        """Run coverage analysis using coverage.py or similar tool."""
        try:
            # Check if coverage tool is available
            import coverage
        except ImportError:
            # Try to install coverage if not available
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'],
                             check=True, capture_output=True)
                import coverage
            except subprocess.CalledProcessError:
                raise Exception("Coverage analysis requires 'coverage' package. Please install it: pip install coverage")

        # Create a coverage object
        cov = coverage.Coverage(source=source_paths)

        # Start coverage measurement
        cov.start()

        # Run tests
        for test_path in test_paths:
            if os.path.isfile(test_path) and test_path.endswith('.py'):
                # Run a single test file
                exec(open(test_path).read())
            elif os.path.isdir(test_path):
                # Find and run all test files in directory
                import unittest
                loader = unittest.TestLoader()
                suite = loader.discover(test_path)
                runner = unittest.TextTestRunner(verbosity=0)
                runner.run(suite)

        # Stop coverage measurement
        cov.stop()
        cov.save()

        # Get the coverage data
        analysis = cov.analysis()

        # Create a result dictionary
        result = {
            'summary': {
                'total_statements': 0,
                'covered_statements': 0,
                'missing_statements': 0,
                'percentage': 0.0
            },
            'files': {},
            'missing_lines': {}
        }

        # For each source path, get coverage data
        for source_path in source_paths:
            if os.path.isfile(source_path):
                try:
                    analyzed = cov.analysis2(source_path)
                    # (filename, executable_statements, excluded_statements, covered_statements, missing_lines, readable_missing)
                    filename, executable, excluded, covered, missing, readable_missing = analyzed

                    if executable > 0:
                        percent_covered = (covered / executable) * 100
                    else:
                        percent_covered = 100.0  # If no executable statements, consider it fully covered

                    result['files'][filename] = {
                        'executable_statements': executable,
                        'covered_statements': covered,
                        'percent_covered': percent_covered
                    }

                    if missing:
                        result['missing_lines'][filename] = list(missing)

                    result['summary']['total_statements'] += executable
                    result['summary']['covered_statements'] += covered
                    result['summary']['missing_statements'] += len(missing)
                except Exception as e:
                    print(f"Warning: Could not analyze {source_path}: {str(e)}")
            elif os.path.isdir(source_path):
                # Walk through directory
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        if file.endswith('.py'):
                            filepath = os.path.join(root, file)
                            try:
                                analyzed = cov.analysis2(filepath)
                                filename, executable, excluded, covered, missing, readable_missing = analyzed

                                if executable > 0:
                                    percent_covered = (covered / executable) * 100
                                else:
                                    percent_covered = 100.0

                                result['files'][filename] = {
                                    'executable_statements': executable,
                                    'covered_statements': covered,
                                    'percent_covered': percent_covered
                                }

                                if missing:
                                    result['missing_lines'][filename] = list(missing)

                                result['summary']['total_statements'] += executable
                                result['summary']['covered_statements'] += covered
                                result['summary']['missing_statements'] += len(missing)
                            except Exception as e:
                                print(f"Warning: Could not analyze {filepath}: {str(e)}")

        # Calculate overall percentage
        if result['summary']['total_statements'] > 0:
            result['summary']['percentage'] = (
                result['summary']['covered_statements'] /
                result['summary']['total_statements']
            ) * 100
        else:
            result['summary']['percentage'] = 100.0

        return result

    def _parse_coverage_result(self, coverage_result: Dict[str, Any], source_paths: List[str]) -> CoverageReport:
        """Parse the coverage analysis result into a CoverageReport."""
        total_stmts = coverage_result['summary']['total_statements']
        covered_stmts = coverage_result['summary']['covered_statements']
        missing_stmts = coverage_result['summary']['missing_statements']
        percentage = coverage_result['summary']['percentage']

        # Create the CoverageReport
        report = CoverageReport(
            total_statements=total_stmts,
            covered_statements=covered_stmts,
            missing_statements=missing_stmts,
            percentage_covered=percentage,
            files_coverage=coverage_result['files'],
            uncovered_lines=coverage_result['missing_lines']
        )

        return report

    def generate_coverage_report(self, coverage_report: CoverageReport, output_format: str = 'text') -> str:
        """
        Generate a human-readable coverage report in specified format.

        Args:
            coverage_report: The coverage report to format
            output_format: Format for output ('text', 'markdown', 'json')

        Returns:
            Formatted coverage report as string
        """
        if output_format == 'text':
            report_text = f"Total Statements: {coverage_report.total_statements}\n"
            report_text += f"Covered Statements: {coverage_report.covered_statements}\n"
            report_text += f"Missing Statements: {coverage_report.missing_statements}\n"
            report_text += f"Percentage Covered: {coverage_report.percentage_covered:.2f}%\n\n"

            report_text += "Files Coverage:\n"
            for filepath, data in coverage_report.files_coverage.items():
                report_text += f"  {filepath}: {data['percent_covered']:.2f}% ({data['covered_statements']}/{data['executable_statements']})\n"

            if coverage_report.uncovered_lines:
                report_text += "\nUncovered Lines:\n"
                for filepath, lines in coverage_report.uncovered_lines.items():
                    report_text += f"  {filepath}: {lines}\n"

            return report_text

        elif output_format == 'markdown':
            report_md = f"# Test Coverage Report\n\n"
            report_md += f"- Total Statements: {coverage_report.total_statements}\n"
            report_md += f"- Covered Statements: {coverage_report.covered_statements}\n"
            report_md += f"- Missing Statements: {coverage_report.missing_statements}\n"
            report_md += f"- **Percentage Covered: {coverage_report.percentage_covered:.2f}%**\n\n"

            report_md += "## Files Coverage\n"
            for filepath, data in coverage_report.files_coverage.items():
                report_md += f"- `{filepath}`: {data['percent_covered']:.2f}% ({data['covered_statements']}/{data['executable_statements']})\n"

            if coverage_report.uncovered_lines:
                report_md += "\n## Uncovered Lines\n"
                for filepath, lines in coverage_report.uncovered_lines.items():
                    report_md += f"- `{filepath}`: {lines}\n"

            return report_md

        elif output_format == 'json':
            import json
            # Create a serializable dict representation
            report_dict = {
                "total_statements": coverage_report.total_statements,
                "covered_statements": coverage_report.covered_statements,
                "missing_statements": coverage_report.missing_statements,
                "percentage_covered": coverage_report.percentage_covered,
                "files_coverage": coverage_report.files_coverage,
                "uncovered_lines": coverage_report.uncovered_lines
            }
            return json.dumps(report_dict, indent=2)

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def check_coverage_threshold(self, coverage_report: CoverageReport, threshold: float = 80.0) -> bool:
        """
        Check if the coverage meets the specified threshold.

        Args:
            coverage_report: The coverage report to check
            threshold: Minimum required coverage percentage

        Returns:
            True if coverage meets threshold, False otherwise
        """
        return coverage_report.percentage_covered >= threshold