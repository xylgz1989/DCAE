"""Module for reviewing and modifying generated test cases."""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class ReviewComment:
    """A comment on a test case review."""
    line_number: int
    comment: str
    severity: str  # 'info', 'warning', 'error'
    suggestion: Optional[str] = None


@dataclass
class TestCaseModification:
    """Represents a modification to a test case."""
    original_content: str
    modified_content: str
    reason: str


class TestReviewer:
    """Reviews and allows modification of generated test cases."""

    def __init__(self):
        """Initialize the test reviewer."""
        self.review_rules = self._load_default_rules()

    def _load_default_rules(self) -> Dict[str, Any]:
        """Load default review rules for test cases."""
        return {
            # Naming conventions
            'test_naming': {
                'pattern': r'def test_[a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*\):',
                'message': 'Test function names should follow the convention: test_*',
                'severity': 'error'
            },
            # Assertion checks
            'has_assertions': {
                'pattern': r'(assert|self\.assert)',
                'message': 'Test should contain assertion statements',
                'severity': 'error'
            },
            # Test documentation
            'has_docstring': {
                'pattern': r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
                'message': 'Test should have a descriptive docstring',
                'severity': 'warning'
            }
        }

    def review_test_case(self, test_code: str) -> List[ReviewComment]:
        """
        Review a test case and return comments.

        Args:
            test_code: Test code to review

        Returns:
            List of review comments
        """
        comments = []

        # Split code into lines for line-number tracking
        lines = test_code.split('\n')

        # Check for test naming convention
        has_proper_naming = False
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') and re.search(r'test_[a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*\):', line):
                has_proper_naming = True
                break

        if not has_proper_naming:
            comments.append(ReviewComment(
                line_number=1,
                comment=self.review_rules['test_naming']['message'],
                severity=self.review_rules['test_naming']['severity']
            ))

        # Check for assertions
        has_assertions = False
        for i, line in enumerate(lines):
            if re.search(r'(assert|self\.assert)', line):
                has_assertions = True
                break

        if not has_assertions:
            comments.append(ReviewComment(
                line_number=1,
                comment=self.review_rules['has_assertions']['message'],
                severity=self.review_rules['has_assertions']['severity']
            ))

        # Check for docstrings
        has_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                has_docstring = True
                break

        if not has_docstring:
            comments.append(ReviewComment(
                line_number=1,
                comment=self.review_rules['has_docstring']['message'],
                severity=self.review_rules['has_docstring']['severity']
            ))

        return comments

    def review_test_suite(self, test_suite_code: str) -> Dict[str, List[ReviewComment]]:
        """
        Review an entire test suite and return comments grouped by test function.

        Args:
            test_suite_code: Complete test suite code to review

        Returns:
            Dictionary mapping test function names to lists of review comments
        """
        reviews = {}

        # Split the test suite into individual test functions
        lines = test_suite_code.split('\n')

        current_function = None
        current_function_code = []
        in_function = False

        for i, line in enumerate(lines):
            # Check if this is a function definition
            func_match = re.match(r'^def\s+(test_\w+)\s*\(.*\):', line)
            if func_match:
                # If we were already in a function, save it
                if in_function and current_function:
                    reviews[current_function] = self.review_test_case("\n".join(current_function_code))

                # Start new function
                current_function = func_match.group(1)
                current_function_code = [line]
                in_function = True
            elif in_function:
                current_function_code.append(line)

                # Check if this is the end of the function (when we encounter a line that's not indented)
                if not line.strip() and not self._in_indent(current_function_code, i):
                    continue
                elif line.startswith('def ') and not line.startswith('    def '):
                    # Found the start of the next function
                    reviews[current_function] = self.review_test_case("\n".join(current_function_code))
                    current_function = None
                    in_function = False

        # Handle the last function if it exists
        if in_function and current_function:
            reviews[current_function] = self.review_test_case("\n".join(current_function_code))

        return reviews

    def _in_indent(self, code_lines, current_line_idx):
        """Check if the current line is properly indented as part of the function."""
        if current_line_idx == 0:
            return True

        # Look at the indentation of the function definition
        func_def_line = 0
        for i, line in enumerate(code_lines):
            if line.strip().startswith('def '):
                func_def_line = i
                break

        # Get the indentation of the function body (first line after definition)
        func_body_indent = 0
        for i in range(func_def_line + 1, len(code_lines)):
            if code_lines[i].strip():
                # Found first non-empty line in function body
                func_body_indent = len(code_lines[i]) - len(code_lines[i].lstrip())
                break

        # Check if current line has the same or greater indentation
        current_line = code_lines[current_line_idx]
        current_indent = len(current_line) - len(current_line.lstrip()) if current_line.strip() else 0

        return current_indent >= func_body_indent

    def suggest_modifications(self, test_code: str) -> List[TestCaseModification]:
        """
        Suggest modifications to improve the test case.

        Args:
            test_code: Test code to suggest modifications for

        Returns:
            List of suggested modifications
        """
        modifications = []

        lines = test_code.split('\n')

        # Check for missing assertions
        has_assertions = any(re.search(r'(assert|self\.assert)', line) for line in lines)
        if not has_assertions:
            # Suggest adding an assertion
            non_empty_lines = [i for i, line in enumerate(lines) if line.strip()]
            if non_empty_lines:
                insert_at = non_empty_lines[-1] + 1
                # Determine indentation
                last_line = lines[non_empty_lines[-1]]
                indent = len(last_line) - len(last_line.lstrip())

                original_part = ""
                modified_part = " " * indent + "# TODO: Add appropriate assertion\n" + " " * indent + "assert True  # Replace with actual assertion\n"

                modification = TestCaseModification(
                    original_content=original_part,
                    modified_content=modified_part,
                    reason="Adding a basic assertion to satisfy test requirements"
                )
                modifications.append(modification)

        # Check for missing docstring
        has_docstring = any('"""' in line or "'''" in line for line in lines)
        if not has_docstring:
            # Find where to add docstring (after function definition)
            for i, line in enumerate(lines):
                if line.strip().startswith('def '):
                    # Determine indentation for docstring
                    indent = len(line) - len(line.lstrip())
                    docstring_content = ' ' * (indent + 4) + '"""\n' + \
                                      ' ' * (indent + 4) + 'TODO: Add test description\n' + \
                                      ' ' * (indent + 4) + '"""\n'

                    original_part = ''
                    modified_part = docstring_content

                    modification = TestCaseModification(
                        original_content=original_part,
                        modified_content=modified_part,
                        reason="Adding docstring for test description"
                    )
                    modifications.append(modification)
                    break

        return modifications

    def apply_modifications(self, test_code: str, modifications: List[TestCaseModification]) -> str:
        """
        Apply suggested modifications to test code.

        Args:
            test_code: Original test code
            modifications: List of modifications to apply

        Returns:
            Modified test code
        """
        result = test_code

        # Apply modifications in reverse order to maintain line positions
        for mod in reversed(modifications):
            if mod.original_content in result:
                result = result.replace(mod.original_content, mod.modified_content, 1)
            else:
                # If original content not found, append the modification
                result += mod.modified_content

        return result

    def update_review_rules(self, new_rules: Dict[str, Any]):
        """
        Update the review rules.

        Args:
            new_rules: New review rules to apply
        """
        self.review_rules.update(new_rules)

    def validate_test_quality(self, test_code: str) -> Tuple[bool, List[str]]:
        """
        Validate the quality of a test based on multiple criteria.

        Args:
            test_code: Test code to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Run review to get issues
        comments = self.review_test_case(test_code)

        for comment in comments:
            issues.append(f"[{comment.severity.upper()}] Line {comment.line_number}: {comment.comment}")

        # Additional quality checks
        lines = test_code.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

        # Check if test has substantial content
        if len(code_lines) < 3:  # Minimal test might just be def and pass
            issues.append("[WARNING] Test appears to have minimal content")

        is_valid = len([c for c in comments if c.severity == 'error']) == 0

        return is_valid, issues