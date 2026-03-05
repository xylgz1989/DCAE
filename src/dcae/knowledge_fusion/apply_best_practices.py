#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Best Practices Application Script

This script applies best practices to the entire DCAE codebase.
It analyzes each Python file and improves it according to best practices.
"""

import os
import sys
from pathlib import Path
import shutil
from typing import List, Tuple

# Add the src directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dcae.knowledge_fusion.best_practices_analyzer import BestPracticesAnalyzer, apply_best_practices_improvements


def find_python_files(root_dir: str) -> List[Path]:
    """
    Find all Python files in the given directory and subdirectories.

    Args:
        root_dir: Root directory to search for Python files

    Returns:
        List of Python file paths
    """
    python_files = []
    root_path = Path(root_dir)

    for py_file in root_path.rglob("*.py"):
        # Skip test files and virtual environments
        if "test" not in py_file.parts and ".venv" not in py_file.parts and "__pycache__" not in py_file.parts:
            python_files.append(py_file)

    return python_files


def backup_file(file_path: Path) -> Path:
    """
    Create a backup of the given file.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to the backup file
    """
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copy2(file_path, backup_path)
    return backup_path


def apply_best_practices_to_codebase(codebase_root: str, dry_run: bool = False) -> List[Tuple[str, str]]:
    """
    Apply best practices to all Python files in the codebase.

    Args:
        codebase_root: Root directory of the codebase
        dry_run: If True, don't actually modify files, just report what would be done

    Returns:
        List of tuples containing (file_path, status_message)
    """
    analyzer = BestPracticesAnalyzer()
    results = []

    python_files = find_python_files(codebase_root)

    print(f"Found {len(python_files)} Python files to analyze")

    for file_path in python_files:
        try:
            print(f"Analyzing: {file_path}")

            # Perform analysis
            analysis = analyzer.analyze_file(str(file_path))

            # Check if improvements are needed
            violations_found = any(not result.is_followed for result in analysis["best_practice_results"])

            if violations_found or analysis["content_analysis"]["potential_security_issues"]:
                status = f"IMPROVEMENTS_NEEDED: {len([r for r in analysis['best_practice_results'] if not r.is_followed])} violations found"

                if not dry_run:
                    # Create backup
                    backup_path = backup_file(file_path)

                    # Apply improvements
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()

                    improved_content = apply_best_practices_improvements(original_content)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(improved_content)

                    status = f"IMPROVED: Backup saved as {backup_path}"

                results.append((str(file_path), status))
            else:
                results.append((str(file_path), "NO_ISSUES_FOUND"))

        except Exception as e:
            results.append((str(file_path), f"ERROR: {str(e)}"))

    return results


def create_best_practices_report(results: List[Tuple[str, str]], output_file: str):
    """
    Create a comprehensive best practices report.

    Args:
        results: List of (file_path, status_message) tuples
        output_file: Path to save the report
    """
    improved_files = [r for r in results if "IMPROVED" in r[1]]
    needs_improvement = [r for r in results if "IMPROVEMENTS_NEEDED" in r[1]]
    errors = [r for r in results if "ERROR" in r[1]]

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Best Practices Report\n\n")

        f.write(f"## Summary\n\n")
        f.write(f"- Total files analyzed: {len(results)}\n")
        f.write(f"- Files improved: {len(improved_files)}\n")
        f.write(f"- Files needing improvement: {len(needs_improvement)}\n")
        f.write(f"- Errors encountered: {len(errors)}\n\n")

        if improved_files:
            f.write("## Improved Files\n\n")
            for file_path, status in improved_files:
                f.write(f"- `{file_path}`: {status}\n")
            f.write("\n")

        if needs_improvement:
            f.write("## Files Needing Improvement\n\n")
            for file_path, status in needs_improvement:
                f.write(f"- `{file_path}`: {status}\n")
            f.write("\n")

        if errors:
            f.write("## Errors Encountered\n\n")
            for file_path, status in errors:
                f.write(f"- `{file_path}`: {status}\n")
            f.write("\n")

        f.write("## Recommendations\n\n")
        f.write("1. Review all improved files to ensure the changes are appropriate\n")
        f.write("2. Address any remaining best practice violations\n")
        f.write("3. Consider expanding the best practices analyzer with additional checks\n")
        f.write("4. Integrate best practices checking into the CI/CD pipeline\n")


def main():
    """Main function to run the best practices application script."""
    if len(sys.argv) < 2:
        print("Usage: python apply_best_practices.py <codebase_root> [--dry-run]")
        print("Example: python apply_best_practices.py .")
        print("Example (dry run): python apply_best_practices.py . --dry-run")
        sys.exit(1)

    codebase_root = sys.argv[1]
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("Running in dry-run mode (no files will be modified)")

    print(f"Applying best practices to codebase: {codebase_root}")

    results = apply_best_practices_to_codebase(codebase_root, dry_run)

    # Create a report
    report_file = "best_practices_report.md" if not dry_run else "best_practices_report_dry_run.md"
    create_best_practices_report(results, report_file)

    print(f"\nAnalysis complete! Report saved to: {report_file}")

    # Print summary
    improved = len([r for r in results if "IMPROVED" in r[1]])
    needs_improvement = len([r for r in results if "IMPROVEMENTS_NEEDED" in r[1]])
    errors = len([r for r in results if "ERROR" in r[1]])

    print(f"\nSummary:")
    print(f"- {improved} files improved")
    print(f"- {needs_improvement} files need improvement")
    print(f"- {errors} errors encountered")


if __name__ == "__main__":
    main()