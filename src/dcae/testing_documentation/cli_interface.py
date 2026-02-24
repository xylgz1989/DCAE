"""Module for CLI interface functionality for testing and documentation generation."""
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from src.dcae.testing_documentation.test_generator import TestGenerator, TestType, FrameworkPreference
from src.dcae.testing_documentation.documentation_generator import DocumentationGenerator, DocFormat
from src.dcae.testing_documentation.test_coverage_analyzer import TestCoverageAnalyzer
from src.dcae.testing_documentation.test_reviewer import TestReviewer


class CLIInterface:
    """Command-line interface for testing and documentation generation."""

    def __init__(self):
        """Initialize the CLI interface."""
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser for the CLI."""
        parser = argparse.ArgumentParser(
            description="DCAE Testing & Documentation Generation Tool",
            prog="dcae-test-doc"
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Test generation command
        test_gen_parser = subparsers.add_parser('generate-tests', help='Generate test cases from code or requirements')
        test_gen_parser.add_argument('--source', '-s', type=str, required=True,
                                     help='Source code file or directory to generate tests for')
        test_gen_parser.add_argument('--framework', '-f', type=str, choices=['pytest', 'unittest', 'nose'],
                                     default='pytest', help='Test framework to use')
        test_gen_parser.add_argument('--type', '-t', type=str, choices=['unit', 'integration', 'end-to-end'],
                                     default='unit', help='Type of tests to generate')
        test_gen_parser.add_argument('--output', '-o', type=str, help='Output file for generated tests')

        # Documentation generation command
        doc_gen_parser = subparsers.add_parser('generate-docs', help='Generate documentation from code or requirements')
        doc_gen_parser.add_argument('--source', '-s', type=str, required=True,
                                    help='Source code file or directory to generate docs for')
        doc_gen_parser.add_argument('--format', '-fmt', type=str, choices=['markdown', 'rst', 'docstring'],
                                    default='markdown', help='Documentation format to use')
        doc_gen_parser.add_argument('--output', '-o', type=str, help='Output file for generated documentation')

        # Test coverage command
        coverage_parser = subparsers.add_parser('analyze-coverage', help='Analyze test coverage of code')
        coverage_parser.add_argument('--source', '-s', type=str, required=True,
                                    help='Source code file or directory to analyze coverage for')
        coverage_parser.add_argument('--tests', '-t', type=str, help='Test files or directory to run for coverage analysis')
        coverage_parser.add_argument('--threshold', '-th', type=float, default=80.0,
                                     help='Minimum required coverage percentage')

        # Test review command
        review_parser = subparsers.add_parser('review-tests', help='Review generated test cases')
        review_parser.add_argument('--test-file', '-tf', type=str, required=True,
                                   help='Test file to review')
        review_parser.add_argument('--format', '-fmt', choices=['text', 'json'], default='text',
                                   help='Output format for review results')

        return parser

    def run(self, args: List[str] = None):
        """
        Run the CLI with the given arguments.

        Args:
            args: Command line arguments (defaults to sys.argv)
        """
        if args is None:
            args = sys.argv[1:]

        parsed_args = self.parser.parse_args(args)

        if not parsed_args.command:
            self.parser.print_help()
            return

        try:
            if parsed_args.command == 'generate-tests':
                self._handle_generate_tests(parsed_args)
            elif parsed_args.command == 'generate-docs':
                self._handle_generate_docs(parsed_args)
            elif parsed_args.command == 'analyze-coverage':
                self._handle_analyze_coverage(parsed_args)
            elif parsed_args.command == 'review-tests':
                self._handle_review_tests(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}")
                self.parser.print_help()
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

    def _handle_generate_tests(self, args):
        """Handle the generate-tests command."""
        # Load source code
        if os.path.isfile(args.source):
            with open(args.source, 'r', encoding='utf-8') as f:
                source_code = f.read()
        elif os.path.isdir(args.source):
            # If it's a directory, we'll need to process all Python files
            print("Directory support for test generation coming soon.")
            return
        else:
            raise FileNotFoundError(f"Source file/directory not found: {args.source}")

        # Create test generator
        framework_pref = FrameworkPreference(args.framework)
        test_gen = TestGenerator(framework=framework_pref)

        # Determine test type
        test_type = TestType(args.type)

        # Generate tests
        generated_tests = test_gen.generate_from_code(source_code, test_type=test_type)

        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(generated_tests)
            print(f"Tests generated and saved to {args.output}")
        else:
            print("Generated Tests:")
            print(generated_tests)

    def _handle_generate_docs(self, args):
        """Handle the generate-docs command."""
        # Load source code
        if os.path.isfile(args.source):
            with open(args.source, 'r', encoding='utf-8') as f:
                source_code = f.read()
        elif os.path.isdir(args.source):
            # If it's a directory, we'll need to process all Python files
            print("Directory support for documentation generation coming soon.")
            return
        else:
            raise FileNotFoundError(f"Source file/directory not found: {args.source}")

        # Create documentation generator
        doc_format = DocFormat(args.format)
        doc_gen = DocumentationGenerator(format=doc_format)

        # Generate documentation
        generated_docs = doc_gen.generate_from_code(source_code)

        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(generated_docs)
            print(f"Documentation generated and saved to {args.output}")
        else:
            print("Generated Documentation:")
            print(generated_docs)

    def _handle_analyze_coverage(self, args):
        """Handle the analyze-coverage command."""
        # Create coverage analyzer
        coverage_analyzer = TestCoverageAnalyzer()

        # Prepare source paths
        source_paths = [args.source]

        # Prepare test paths
        if args.tests:
            test_paths = [args.tests]
        else:
            # Auto-discover test paths
            test_paths = []
            possible_paths = ['tests/', 'test/']
            for path in possible_paths:
                if os.path.exists(path):
                    test_paths.append(path)

        # Analyze coverage
        coverage_report = coverage_analyzer.analyze_coverage(source_paths, test_paths)

        # Generate formatted report
        formatted_report = coverage_analyzer.generate_coverage_report(coverage_report, output_format='text')

        # Print report
        print(formatted_report)

        # Check threshold
        meets_threshold = coverage_analyzer.check_coverage_threshold(coverage_report, args.threshold)
        print(f"\nCoverage threshold ({args.threshold}%): {'MET' if meets_threshold else 'NOT MET'}")

        if not meets_threshold:
            sys.exit(1)  # Exit with error code if threshold not met

    def _handle_review_tests(self, args):
        """Handle the review-tests command."""
        # Check if test file exists
        if not os.path.exists(args.test_file):
            raise FileNotFoundError(f"Test file not found: {args.test_file}")

        # Read test file
        with open(args.test_file, 'r', encoding='utf-8') as f:
            test_code = f.read()

        # Create test reviewer
        reviewer = TestReviewer()

        # Review the test
        comments = reviewer.review_test_case(test_code)

        # Format output based on specified format
        if args.format == 'json':
            import json
            output_data = {
                "file": args.test_file,
                "comments": [
                    {
                        "line_number": c.line_number,
                        "comment": c.comment,
                        "severity": c.severity,
                        "suggestion": c.suggestion
                    } for c in comments
                ]
            }
            print(json.dumps(output_data, indent=2))
        else:  # text format
            print(f"Reviewing: {args.test_file}\n")
            if comments:
                for comment in comments:
                    print(f"L{comment.line_number} [{comment.severity.upper()}]: {comment.comment}")
                    if comment.suggestion:
                        print(f"    Suggestion: {comment.suggestion}")
            else:
                print("No issues found.")

    def print_help(self):
        """Print help information."""
        self.parser.print_help()


# Entry point function for CLI
def main():
    """Main entry point for the CLI."""
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()