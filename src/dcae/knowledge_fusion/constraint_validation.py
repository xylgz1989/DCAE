"""
Constraint Validation System

This module provides tools to validate code and configurations against project-specific constraints
during the development process.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import ast
import re
from enum import Enum
from .constraint_storage import ProjectConstraintStorage, Constraint
from .project_constraints_manager import ProjectConstraintsManager


class ValidationResult(Enum):
    """Enumeration for validation results"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class ValidationIssue:
    """Represents an issue found during validation"""

    def __init__(self, constraint_id: str, constraint_name: str, severity: str,
                 message: str, file_path: Optional[str] = None, line_number: Optional[int] = None):
        self.constraint_id = constraint_id
        self.constraint_name = constraint_name
        self.severity = severity
        self.message = message
        self.file_path = file_path
        self.line_number = line_number

    def __str__(self):
        location = f"{self.file_path}:{self.line_number}" if self.file_path and self.line_number else "unknown location"
        return f"[{self.severity.upper()}] {location} - {self.constraint_name}: {self.message}"


class ConstraintValidator:
    """
    Validates code and configurations against project-specific constraints
    """

    def __init__(self, storage: ProjectConstraintStorage):
        self.storage = storage

    def validate_file(self, file_path: Path, constraints: Optional[List[Constraint]] = None) -> List[ValidationIssue]:
        """
        Validate a single file against constraints

        Args:
            file_path: Path to the file to validate
            constraints: Optional list of constraints to check against (checks all if None)

        Returns:
            List of validation issues found
        """
        issues = []

        # Get constraints to check
        if constraints is None:
            constraints = self.storage.list_constraints(active_only=True)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the file if it's a Python file
            tree = None
            if file_path.suffix == '.py':
                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    # If we can't parse the file, just do text-based validation
                    pass

            # Validate against each constraint
            for constraint in constraints:
                constraint_issues = self._validate_against_constraint(
                    file_path, content, tree, constraint
                )
                issues.extend(constraint_issues)

        except Exception as e:
            issues.append(ValidationIssue(
                constraint_id="internal-error",
                constraint_name="Internal Validation Error",
                severity="critical",
                message=f"Could not read file {file_path}: {str(e)}"
            ))

        return issues

    def validate_code_content(self, content: str, file_path: Path,
                              constraints: Optional[List[Constraint]] = None) -> List[ValidationIssue]:
        """
        Validate code content against constraints

        Args:
            content: Content to validate
            file_path: Path of the file (for context)
            constraints: Optional list of constraints to check against (checks all if None)

        Returns:
            List of validation issues found
        """
        issues = []

        # Get constraints to check
        if constraints is None:
            constraints = self.storage.list_constraints(active_only=True)

        tree = None
        if file_path.suffix == '.py':
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # If we can't parse the file, just do text-based validation
                pass

        # Validate against each constraint
        for constraint in constraints:
            constraint_issues = self._validate_against_constraint(
                file_path, content, tree, constraint
            )
            issues.extend(constraint_issues)

        return issues

    def _validate_against_constraint(self, file_path: Path, content: str, tree: Optional[ast.AST],
                                   constraint: Constraint) -> List[ValidationIssue]:
        """
        Validate content against a specific constraint

        Args:
            file_path: Path of the file being validated
            content: Content of the file
            tree: AST of the content (if available)
            constraint: Constraint to validate against

        Returns:
            List of validation issues found for this constraint
        """
        issues = []

        # Different validation strategies based on constraint category
        if constraint.category.lower() == "technical":
            issues.extend(self._validate_technical_constraint(file_path, content, tree, constraint))
        elif constraint.category.lower() == "security":
            issues.extend(self._validate_security_constraint(file_path, content, tree, constraint))
        elif constraint.category.lower() == "performance":
            issues.extend(self._validate_performance_constraint(file_path, content, tree, constraint))
        elif constraint.category.lower() == "coding_standard":
            issues.extend(self._validate_coding_standard_constraint(file_path, content, tree, constraint))
        else:
            # General validation for other constraint types
            issues.extend(self._validate_general_constraint(file_path, content, tree, constraint))

        return issues

    def _validate_technical_constraint(self, file_path: Path, content: str, tree: Optional[ast.AST],
                                    constraint: Constraint) -> List[ValidationIssue]:
        """
        Validate against technical constraints
        """
        issues = []

        # Example: Check for specific technology requirements
        if "python 3.11+" in constraint.description.lower():
            # Check if the code uses features that require Python 3.11+
            if tree:
                # Look for match statements (Python 3.10+)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Match):
                        # This is valid for Python 3.10+, which is compatible with 3.11+
                        pass

        # Check for async/await usage if required
        if "asyncio" in constraint.description.lower() or "async" in constraint.description.lower():
            if tree:
                has_async_usage = False
                for node in ast.walk(tree):
                    if isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.AsyncWith, ast.AsyncFor)):
                        has_async_usage = True
                        break

                if not has_async_usage:
                    issues.append(ValidationIssue(
                        constraint_id=constraint.id,
                        constraint_name=constraint.name,
                        severity=constraint.severity,
                        message=f"File does not use async/await as required by constraint: {constraint.description}",
                        file_path=str(file_path)
                    ))

        return issues

    def _validate_security_constraint(self, file_path: Path, content: str, tree: Optional[ast.AST],
                                   constraint: Constraint) -> List[ValidationIssue]:
        """
        Validate against security constraints
        """
        issues = []

        # Check for hardcoded API keys or sensitive information
        if "no hardcoded keys" in constraint.description.lower() or "security" in constraint.category.lower():
            # Look for potential API keys or passwords in string literals
            api_key_patterns = [
                r'["\'](?:api[_-]?key|password|secret|token)["\']\s*[:=]\s*["\']([^"\']+)',
                r'(?:API_KEY|PASSWORD|SECRET|TOKEN)\s*=\s*["\']([^"\']+)["\']',
            ]

            for pattern in api_key_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip if it looks like a placeholder or example
                    value = match.group(1) if len(match.groups()) > 0 else ""
                    if not any(placeholder in value.lower() for placeholder in
                              ['your_', 'placeholder', 'example', 'dummy', 'test']):
                        issues.append(ValidationIssue(
                            constraint_id=constraint.id,
                            constraint_name=constraint.name,
                            severity="critical",
                            message=f"Potential hardcoded secret detected: {match.group(0)[:50]}...",
                            file_path=str(file_path),
                            line_number=content.count('\n', 0, match.start()) + 1
                        ))

        return issues

    def _validate_performance_constraint(self, file_path: Path, content: str, tree: Optional[ast.AST],
                                      constraint: Constraint) -> List[ValidationIssue]:
        """
        Validate against performance constraints
        """
        issues = []

        # Check for performance anti-patterns based on constraint description
        if "token counting" in constraint.description.lower():
            # Check if the file implements token counting
            if "token" not in content.lower():
                issues.append(ValidationIssue(
                    constraint_id=constraint.id,
                    constraint_name=constraint.name,
                    severity=constraint.severity,
                    message=f"File does not appear to implement token counting as required: {constraint.description}",
                    file_path=str(file_path)
                ))

        return issues

    def _validate_coding_standard_constraint(self, file_path: Path, content: str, tree: Optional[ast.AST],
                                          constraint: Constraint) -> List[ValidationIssue]:
        """
        Validate against coding standard constraints
        """
        issues = []

        # Check for proper type hints
        if "type hints" in constraint.description.lower() or "typing" in constraint.description.lower():
            if tree:
                missing_type_hints = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if return type is annotated
                        if node.returns is None:
                            missing_type_hints.append(f"Function '{node.name}' missing return type annotation")

                        # Check if parameters have annotations (excluding 'self' and 'cls')
                        for arg in node.args.args:
                            if arg.arg not in ['self', 'cls'] and arg.annotation is None:
                                missing_type_hints.append(f"Parameter '{arg.arg}' in function '{node.name}' missing type annotation")

                for missing_hint in missing_type_hints:
                    issues.append(ValidationIssue(
                        constraint_id=constraint.id,
                        constraint_name=constraint.name,
                        severity="medium",
                        message=missing_hint,
                        file_path=str(file_path),
                        line_number=getattr(node, 'lineno', None)
                    ))

        return issues

    def _validate_general_constraint(self, file_path: Path, content: str, tree: Optional[ast.AST],
                                  constraint: Constraint) -> List[ValidationIssue]:
        """
        General validation for other constraint types
        """
        issues = []

        # This could implement various other validation strategies based on constraint descriptions
        return issues

    def validate_project(self, project_root: Path, constraints: Optional[List[Constraint]] = None) -> Dict[str, List[ValidationIssue]]:
        """
        Validate an entire project against constraints

        Args:
            project_root: Root directory of the project to validate
            constraints: Optional list of constraints to check against (checks all if None)

        Returns:
            Dictionary mapping file paths to lists of validation issues
        """
        results = {}

        # Get Python files to validate
        for py_file in project_root.rglob("*.py"):
            # Skip virtual environments and other irrelevant directories
            if any(part.startswith('.') or part in ['__pycache__', 'venv', 'env', '.venv']
                   for part in py_file.parts):
                continue

            issues = self.validate_file(py_file, constraints)
            if issues:
                results[str(py_file)] = issues

        return results

    def generate_validation_report(self, validation_results: Dict[str, List[ValidationIssue]]) -> str:
        """
        Generate a human-readable validation report

        Args:
            validation_results: Results from validate_project

        Returns:
            Formatted validation report
        """
        report_lines = ["Constraint Validation Report", "=" * 30, ""]

        total_issues = 0
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for file_path, issues in validation_results.items():
            if issues:
                report_lines.append(f"File: {file_path}")
                report_lines.append("-" * len(f"File: {file_path}"))

                for issue in issues:
                    report_lines.append(str(issue))
                    total_issues += 1
                    severity_counts[issue.severity.lower()] = severity_counts.get(issue.severity.lower(), 0) + 1

                report_lines.append("")  # Empty line after each file

        report_lines.append("Summary:")
        report_lines.append(f"  Total issues: {total_issues}")
        for severity, count in severity_counts.items():
            report_lines.append(f"  {severity.title()}: {count}")

        return "\n".join(report_lines)


class DevelopmentValidator:
    """
    Integrates constraint validation into the development workflow
    """

    def __init__(self, storage: ProjectConstraintStorage):
        self.validator = ConstraintValidator(storage)
        self.storage = storage

    def pre_commit_validation(self, file_paths: List[Path]) -> Tuple[bool, List[ValidationIssue]]:
        """
        Perform validation before committing changes

        Args:
            file_paths: List of files to validate before commit

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        all_issues = []

        for file_path in file_paths:
            if file_path.suffix == '.py':  # Only validate Python files for now
                issues = self.validator.validate_file(file_path)
                all_issues.extend(issues)

        # Determine validity based on critical and high severity issues
        critical_issues = [issue for issue in all_issues if issue.severity.lower() in ['critical', 'high']]

        return len(critical_issues) == 0, all_issues

    def validate_pull_request(self, file_paths: List[Path]) -> Dict[str, List[ValidationIssue]]:
        """
        Validate files in a pull request

        Args:
            file_paths: List of files in the pull request

        Returns:
            Dictionary mapping file paths to validation issues
        """
        results = {}

        for file_path in file_paths:
            if file_path.suffix == '.py':  # Only validate Python files for now
                issues = self.validator.validate_file(file_path)
                if issues:
                    results[str(file_path)] = issues

        return results

    def check_new_constraint_impact(self, new_constraint: Constraint) -> Dict[str, List[ValidationIssue]]:
        """
        Check how a new constraint would impact the existing codebase

        Args:
            new_constraint: The new constraint to evaluate

        Returns:
            Dictionary mapping file paths to validation issues that would occur
        """
        project_root = Path(__file__).parent.parent.parent  # Go up to project root
        all_constraints = self.storage.list_constraints(active_only=True)

        # Temporarily add the new constraint to the list
        temp_constraints = all_constraints + [new_constraint]

        # Validate the entire project with the new constraint
        return self.validator.validate_project(project_root, temp_constraints)


def create_validator() -> DevelopmentValidator:
    """
    Factory function to create a validator with default storage

    Returns:
        DevelopmentValidator instance
    """
    storage = ProjectConstraintStorage()
    return DevelopmentValidator(storage)


if __name__ == "__main__":
    # Example usage
    validator = create_validator()

    # Validate a single file
    test_file = Path(__file__)
    issues = validator.validator.validate_file(test_file)

    print(f"Found {len(issues)} issues in {test_file}")
    for issue in issues[:5]:  # Show first 5 issues
        print(f"  {issue}")

    # Get all active constraints
    constraints = validator.storage.list_constraints(active_only=True)
    print(f"\nUsing {len(constraints)} active constraints for validation")

    # Show constraint statistics
    stats = validator.storage.get_constraint_statistics()
    print(f"Constraint statistics: {stats}")