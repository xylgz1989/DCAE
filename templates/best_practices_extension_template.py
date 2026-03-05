"""
Template for Adding New Best Practices to DCAE Framework

This template demonstrates how to extend the GeneratedOutputReviewer class
with new best practice checks. Copy and modify this template to add your own
best practice checks to the DCAE framework.
"""

from enum import Enum
from pathlib import Path
from typing import List
from dataclasses import dataclass
import ast
import re


class ExtendedReviewCategory(Enum):
    """Extended review categories - you can add new ones here if needed."""

    # Include all original categories
    CODE_QUALITY = "code_quality"
    ARCHITECTURE_ALIGNMENT = "architecture_alignment"
    REQUIREMENTS_COVERAGE = "requirements_coverage"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"

    # Add your new categories here
    CUSTOM_CATEGORY = "custom_category"


@dataclass
class CustomReviewFinding:
    """Template for custom findings - you can reuse the main ReviewFinding class."""
    id: str
    category: ExtendedReviewCategory  # or ReviewCategory for consistency
    severity: str  # Use "info", "low", "medium", "high", "critical"
    file_path: str
    line_number: int
    issue_description: str
    recommendation: str
    code_snippet: str


class BestPracticesExtensionMixin:
    """
    Mixin class to extend GeneratedOutputReviewer with new best practices.

    When implementing new checks:
    1. Add your check method following the pattern below
    2. Call it from your extended review method
    3. Add configuration options if needed
    4. Register the method in the main review process
    """

    def _review_custom_practices(self, path: Path):
        """
        Review code for custom best practices.

        Args:
            path: Path to review for custom best practices
        """
        print(f"  Performing custom best practices review in: {path}")

        # Check if the custom practice review is enabled in config
        if not self.config.get("custom_practices", {}).get("enable_custom_checks", True):
            print("    Skipping custom practices review - disabled in configuration")
            return

        # Iterate over relevant files
        for file_path in path.rglob("*.py"):  # Change extension as needed
            if file_path.is_file():
                self._check_single_file_for_custom_practices(file_path)

    def _check_single_file_for_custom_practices(self, file_path: Path):
        """
        Check a single file for custom best practices.

        Args:
            file_path: Path to the file to check
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Use AST parsing for structural analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast_for_custom_practices(tree, file_path, content)
            except SyntaxError:
                # If AST parsing fails, fall back to regex/string analysis
                self._analyze_content_for_custom_practices(content, file_path)

        except Exception as e:
            print(f"    Warning: Could not review {file_path}: {str(e)}")

    def _analyze_ast_for_custom_practices(self, tree: ast.AST, file_path: Path, content: str):
        """
        Analyze AST for custom best practices.

        Args:
            tree: Parsed AST of the file content
            file_path: Path to the file being analyzed
            content: Original file content
        """
        lines = content.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Example: Check for specific function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id

                    # Example check: Flag deprecated functions
                    if func_name in ['deprecated_function', 'old_api_call']:
                        line_no = node.lineno
                        finding = CustomReviewFinding(
                            id=f"custom_deprecated_{file_path}:{line_no}",
                            category=ExtendedReviewCategory.CUSTOM_CATEGORY,
                            severity="medium",
                            file_path=str(file_path),
                            line_number=line_no,
                            issue_description=f"Use of deprecated function '{func_name}' detected",
                            recommendation=f"Replace '{func_name}' with the newer alternative",
                            code_snippet=lines[line_no - 1].strip() if line_no <= len(lines) else ""
                        )
                        # Add to main findings list (assuming self.findings exists)
                        # Note: In real implementation, use the main ReviewFinding class
                        # and the actual findings list from GeneratedOutputReviewer
                        # self.findings.append(finding)

            elif isinstance(node, ast.ImportFrom):
                # Example: Check for imports from specific modules
                if node.module and 'unsafe_library' in node.module:
                    line_no = node.lineno
                    finding = CustomReviewFinding(
                        id=f"custom_unsafe_import_{file_path}:{line_no}",
                        category=ExtendedReviewCategory.CUSTOM_CATEGORY,
                        severity="high",
                        file_path=str(file_path),
                        line_number=line_no,
                        issue_description=f"Import from potentially unsafe library '{node.module}'",
                        recommendation="Evaluate security implications of using this library",
                        code_snippet=lines[line_no - 1].strip() if line_no <= len(lines) else ""
                    )

    def _analyze_content_for_custom_practices(self, content: str, file_path: Path):
        """
        Analyze file content using regex/string operations for custom best practices.

        Args:
            content: File content as a string
            file_path: Path to the file being analyzed
        """
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Example: Check for specific patterns in the code
            if re.search(r'magic_number\s*=\s*\d+', line):
                finding = CustomReviewFinding(
                    id=f"custom_magic_num_{file_path}:{i}",
                    category=ExtendedReviewCategory.CUSTOM_CATEGORY,
                    severity="medium",
                    file_path=str(file_path),
                    line_number=i,
                    issue_description="Magic number detected in code",
                    recommendation="Define the number as a named constant",
                    code_snippet=line.strip()
                )
                # self.findings.append(finding)  # Uncomment in real implementation


# Example of how to extend the GeneratedOutputReviewer class
class ExtendedGeneratedOutputReviewer:  # This would inherit from the actual reviewer
    """
    Example of how to integrate the mixin into the actual reviewer class.

    In the actual implementation, you would:
    1. Have this class inherit from GeneratedOutputReviewer
    2. Add custom configuration in _get_default_config
    3. Call _review_custom_practices from review_generated_output
    """

    def __init__(self, project_path: str, requirements_spec=None, architecture_spec=None, config=None):
        """
        Initialize with custom configuration options.
        """
        # Call parent constructor
        # super().__init__(project_path, requirements_spec, architecture_spec, config)

        # Initialize or extend config with custom options
        self.custom_config = {
            "custom_practices": {
                "enable_custom_checks": True,
                "custom_threshold": 10,  # Example custom setting
            }
        }

        if config:
            # Merge custom config with provided config
            self._merge_configs(self.custom_config, config)

    def _merge_configs(self, default_config: dict, provided_config: dict):
        """Recursively merge configuration dictionaries."""
        for key, value in provided_config.items():
            if key in default_config and isinstance(default_config[key], dict) and isinstance(value, dict):
                self._merge_configs(default_config[key], value)
            else:
                default_config[key] = value

    def _get_default_config(self):
        """Get extended configuration including custom checks."""
        # Start with base config (from GeneratedOutputReviewer)
        base_config = {}  # This would come from super()._get_default_config()

        # Extend with custom configuration
        base_config.update(self.custom_config)
        return base_config

    def review_generated_output(self, target_path=None):
        """Extended review method that includes custom practices."""
        # Call the parent review method
        # report = super().review_generated_output(target_path)

        # Perform custom review
        # self._review_custom_practices(Path(target_path) if target_path else Path(self.project_path))

        # Return the combined report
        # return report
        pass


# Configuration Template
CUSTOM_CONFIG_TEMPLATE = {
    "custom_practices": {
        "enable_custom_checks": True,
        "custom_threshold": 10,
        # Add more custom configuration options as needed
    }
}


if __name__ == "__main__":
    # Example usage
    print("Best Practices Extension Template")
    print("=================================")
    print()
    print("This template demonstrates how to extend the DCAE framework with custom best practices.")
    print("Follow these steps to add your own best practice checks:")
    print()
    print("1. Define your check logic in a method following the pattern in _review_custom_practices()")
    print("2. Add configuration options to CUSTOM_CONFIG_TEMPLATE")
    print("3. Update the ExtendedGeneratedOutputReviewer class to integrate your checks")
    print("4. Add your category to ExtendedReviewCategory if needed")
    print("5. Test your implementation thoroughly")