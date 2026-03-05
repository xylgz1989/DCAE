"""
Main Review Mechanism Entry Point

This module provides the main command-line interface for the DCAE review mechanism.
"""
import argparse
import sys
from pathlib import Path
from typing import Dict, Any
import json

# Import the unified review interface
from dcae.unified_review import UnifiedReviewInterface


def run_review_command(args: argparse.Namespace) -> int:
    """Run the review command with the provided arguments."""
    try:
        # Initialize the unified review interface
        reviewer = UnifiedReviewInterface(args.project_path or str(Path.cwd()))

        # Determine target path
        target_path = args.target_path
        if target_path and not Path(target_path).exists():
            print(f"Error: Target path {target_path} does not exist.")
            return 1

        # Determine requirements and architecture specs
        requirements_spec = None
        architecture_spec = None

        if args.requirements_file and Path(args.requirements_file).exists():
            with open(args.requirements_file, 'r', encoding='utf-8') as f:
                requirements_spec = json.load(f)

        if args.architecture_file and Path(args.architecture_file).exists():
            with open(args.architecture_file, 'r', encoding='utf-8') as f:
                architecture_spec = json.load(f)

        # Run the review
        print(f"Starting review of: {target_path or 'entire project'}")

        results = reviewer.run_comprehensive_review(
            target_path=target_path,
            requirements_spec=requirements_spec,
            architecture_spec=architecture_spec
        )

        # Display results summary
        print("\n" + "="*60)
        print("REVIEW RESULTS SUMMARY")
        print("="*60)

        summary = results.get("summary", {})
        print(f"Total Findings: {summary.get('total_findings', 0)}")
        print(f"Overall Score: {summary.get('overall_score', 0)}/100")

        print("\nFindings by Severity:")
        for severity, count in summary.get("findings_by_severity", {}).items():
            print(f"  {severity.title()}: {count}")

        print("\nFindings by Category:")
        for category, count in summary.get("findings_by_category", {}).items():
            print(f"  {category.replace('_', ' ').title()}: {count}")

        # Generate report if requested
        if args.generate_report:
            report_format = args.report_format or "text"
            report_path = reviewer.generate_unified_report(results, output_format=report_format)
            print(f"\nReport generated: {report_path}")

        # Exit with error code if findings exceed threshold
        if args.fail_on_issues:
            severity_threshold = args.severity_threshold or "medium"
            severity_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}

            threshold_level = severity_map.get(severity_threshold.lower(), 2)
            max_severity_level = 0

            # Determine the highest severity level found
            for severity, count in summary.get("findings_by_severity", {}).items():
                if count > 0 and severity in severity_map:
                    level = severity_map[severity]
                    if level > max_severity_level:
                        max_severity_level = level

            if max_severity_level >= threshold_level:
                print(f"\nExiting with error code due to issues at or above {severity_threshold} severity")
                return 1

        return 0

    except KeyboardInterrupt:
        print("\nReview interrupted by user.")
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"Error running review: {e}")
        return 1


def run_configure_command(args: argparse.Namespace) -> int:
    """Run the configure command with the provided arguments."""
    try:
        reviewer = UnifiedReviewInterface(args.project_path or str(Path.cwd()))

        # Load configuration from file if provided
        if args.config_file:
            success = reviewer.import_configuration(args.config_file)
            if success:
                print(f"Configuration imported from: {args.config_file}")
            else:
                print(f"Failed to import configuration from: {args.config_file}")
                return 1
        else:
            # Allow enabling/disabling specific review types
            config_updates = {}
            if args.review_types:
                for review_type in args.review_types.split(','):
                    review_type = review_type.strip()
                    config_updates[review_type] = True

            # Apply the configuration changes
            if config_updates:
                current_config = reviewer.default_config.get("review_types", {})
                current_config.update(config_updates)
                reviewer.default_config["review_types"] = current_config
                print(f"Enabled review types: {list(config_updates.keys())}")

        return 0

    except Exception as e:
        print(f"Error running configure: {e}")
        return 1


def run_export_command(args: argparse.Namespace) -> int:
    """Run the export command with the provided arguments."""
    try:
        reviewer = UnifiedReviewInterface(args.project_path or str(Path.cwd()))

        success = reviewer.export_configuration(args.output_file)
        if success:
            print(f"Configuration exported to: {args.output_file}")
            return 0
        else:
            print(f"Failed to export configuration to: {args.output_file}")
            return 1

    except Exception as e:
        print(f"Error running export: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the review mechanism."""
    parser = argparse.ArgumentParser(
        prog="dcae-review",
        description="DCAE Review & Quality Assurance Mechanism",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s review src/
  %(prog)s review --generate-report --report-format html
  %(prog)s review --fail-on-issues --severity-threshold high
  %(prog)s configure --review-types security_scanning,code_quality
  %(prog)s export --output-file my-review-config.json
        """
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # Review command
    review_parser = subparsers.add_parser("review", help="Run code review on specified path")
    review_parser.add_argument(
        "target_path",
        nargs="?",
        help="Path to review (defaults to entire project if not specified)"
    )
    review_parser.add_argument(
        "--project-path",
        help="Project root path (defaults to current directory)"
    )
    review_parser.add_argument(
        "--requirements-file",
        help="JSON file containing requirements specification for traceability"
    )
    review_parser.add_argument(
        "--architecture-file",
        help="JSON file containing architecture specification for alignment"
    )
    review_parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate a review report"
    )
    review_parser.add_argument(
        "--report-format",
        choices=["text", "html", "json"],
        help="Format for the generated report (text, html, or json)"
    )
    review_parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="Exit with error code if issues are found above the severity threshold"
    )
    review_parser.add_argument(
        "--severity-threshold",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Severity level at which to fail (default: medium)"
    )
    review_parser.set_defaults(func=run_review_command)

    # Configure command
    configure_parser = subparsers.add_parser("configure", help="Configure review settings")
    configure_parser.add_argument(
        "--project-path",
        help="Project root path (defaults to current directory)"
    )
    configure_parser.add_argument(
        "--review-types",
        help="Comma-separated list of review types to enable (e.g., security_scanning,code_quality)"
    )
    configure_parser.add_argument(
        "--config-file",
        help="Import configuration from JSON file"
    )
    configure_parser.set_defaults(func=run_configure_command)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export review configuration")
    export_parser.add_argument(
        "--project-path",
        help="Project root path (defaults to current directory)"
    )
    export_parser.add_argument(
        "--output-file",
        required=True,
        help="Output file for exported configuration"
    )
    export_parser.set_defaults(func=run_export_command)

    return parser


def main():
    """Main entry point for the DCAE review mechanism CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Execute the appropriate function based on the command
    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()