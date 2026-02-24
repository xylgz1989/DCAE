"""
Review and Quality Assurance - Code Issue Identification Module

This module implements the functionality for systematically identifying code issues
including bugs, vulnerabilities, and deviations from standards.
"""

import ast
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import subprocess
import sys


class IssueSeverity(Enum):
    """Enumeration for issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IssueCategory(Enum):
    """Enumeration for issue categories."""
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ISSUE = "logic_issue"
    SECURITY_VULNERABILITY = "security_vulnerability"
    PERFORMANCE_ISSUE = "performance_issue"
    MAINTAINABILITY_ISSUE = "maintainability_issue"
    STANDARDS_VIOLATION = "standards_violation"
    RESOURCE_LEAK = "resource_leak"
    TYPE_ERROR = "type_error"


@dataclass
class IdentifiedIssue:
    """Represents an identified code issue."""
    id: str
    category: IssueCategory
    severity: IssueSeverity
    file_path: str
    line_number: int
    column_number: int
    issue_description: str
    recommendation: str
    code_snippet: str
    confidence: float  # Between 0 and 1
    related_issues: List[str]


class IssueDetector:
    """Detects code issues in source files."""

    def __init__(self, project_path: str):
        """
        Initialize the issue detector.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.supported_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs'}
        self.issues: List[IdentifiedIssue] = []
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, Any]:
        """Load predefined issue detection patterns."""
        return {
            # Security vulnerability patterns
            "sql_injection": {
                "regex": r"(cursor\.execute|execute\(|conn\.execute|\.query)",
                "keywords": ["f'", 'f"', '+', '.format', '%'],
                "severity": IssueSeverity.CRITICAL,
                "category": IssueCategory.SECURITY_VULNERABILITY,
                "description": "Potential SQL injection vulnerability detected",
                "recommendation": "Use parameterized queries instead of string concatenation"
            },
            "hardcoded_credential": {
                "regex": r'(password|secret|token|key|credential|api_key).*["\'][^"\']+["\']',
                "severity": IssueSeverity.CRITICAL,
                "category": IssueCategory.SECURITY_VULNERABILITY,
                "description": "Hardcoded credential found in code",
                "recommendation": "Move credentials to environment variables or secure configuration"
            },
            "pickle_usage": {
                "regex": r'import pickle|from pickle',
                "severity": IssueSeverity.CRITICAL,
                "category": IssueCategory.SECURITY_VULNERABILITY,
                "description": "Unsafe pickle module usage",
                "recommendation": "Avoid pickle for untrusted data; use safer serialization methods"
            },
            # Performance patterns
            "nested_loops": {
                "severity": IssueSeverity.WARNING,
                "category": IssueCategory.PERFORMANCE_ISSUE,
                "description": "Nested loops detected which may cause performance issues",
                "recommendation": "Consider algorithm optimization or alternative data structures"
            },
            # Maintainability patterns
            "long_function": {
                "threshold": 50,  # lines
                "severity": IssueSeverity.WARNING,
                "category": IssueCategory.MAINTAINABILITY_ISSUE,
                "description": "Function is too long",
                "recommendation": "Consider breaking down the function into smaller, more manageable functions"
            },
            # Common logic issues
            "todo_comment": {
                "regex": r'TODO',
                "severity": IssueSeverity.INFO,
                "category": IssueCategory.LOGIC_ISSUE,
                "description": "TODO comment found in code",
                "recommendation": "Address the TODO before finalizing the code"
            },
            "fixme_comment": {
                "regex": r'FIXME',
                "severity": IssueSeverity.ERROR,
                "category": IssueCategory.LOGIC_ISSUE,
                "description": "FIXME comment found in code",
                "recommendation": "Address the FIXME issue immediately"
            },
            # Resource management
            "unhandled_file_close": {
                "keywords": ["open(", "file"],
                "severity": IssueSeverity.WARNING,
                "category": IssueCategory.RESOURCE_LEAK,
                "description": "Possible file resource leak - file opened without proper closure",
                "recommendation": "Use context managers (with statement) for proper resource management"
            }
        }

    def scan_project(self, target_path: Optional[str] = None) -> List[IdentifiedIssue]:
        """
        Scan a project or specific directory for code issues.

        Args:
            target_path: Specific path to scan (optional, defaults to entire project)

        Returns:
            List of identified issues
        """
        scan_path = Path(target_path) if target_path else self.project_path
        self.issues = []  # Reset issues

        print(f"Scanning for issues in: {scan_path}")

        for file_path in scan_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                print(f"  Scanning: {file_path}")
                self._scan_file(file_path)

        return self.issues

    def _scan_file(self, file_path: Path):
        """Scan a single file for issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Scan for each type of pattern
            self._scan_regex_patterns(file_path, lines)
            self._scan_structural_issues(file_path, content, lines)

            # For Python files, also perform AST analysis
            if file_path.suffix == '.py':
                self._scan_python_ast(file_path, content)

        except Exception as e:
            print(f"    Warning: Could not scan {file_path}: {str(e)}")

    def _scan_regex_patterns(self, file_path: Path, lines: List[str]):
        """Scan file content using regex patterns."""
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()

            for pattern_name, pattern_info in self.patterns.items():
                if 'regex' in pattern_info:
                    if re.search(pattern_info['regex'], line, re.IGNORECASE):
                        # Check if there are additional keywords required
                        keyword_match = True
                        if 'keywords' in pattern_info:
                            keyword_match = any(keyword.lower() in line_lower for keyword in pattern_info['keywords'])

                        if keyword_match:
                            issue_id = f"{pattern_name}_{file_path}:{i}"

                            issue = IdentifiedIssue(
                                id=issue_id,
                                category=pattern_info['category'],
                                severity=pattern_info['severity'],
                                file_path=str(file_path),
                                line_number=i,
                                column_number=line.find(re.search(pattern_info['regex'], line, re.IGNORECASE).group()),
                                issue_description=pattern_info['description'],
                                recommendation=pattern_info['recommendation'],
                                code_snippet=line.strip(),
                                confidence=0.9,  # High confidence for regex matches
                                related_issues=[]
                            )
                            self.issues.append(issue)

    def _scan_structural_issues(self, file_path: Path, content: str, lines: List[str]):
        """Scan for structural issues that require analyzing the entire file."""

        # Check for long functions (more than 50 lines)
        current_func_start = None
        func_line_count = 0

        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*(def |class |function |public |private |protected )', line):
                if current_func_start is not None:
                    # Previous function ended, check its length
                    if func_line_count > self.patterns['long_function']['threshold']:
                        issue_id = f"long_function_{file_path}:{current_func_start}"
                        issue = IdentifiedIssue(
                            id=issue_id,
                            category=self.patterns['long_function']['category'],
                            severity=self.patterns['long_function']['severity'],
                            file_path=str(file_path),
                            line_number=current_func_start,
                            column_number=0,
                            issue_description=f"{self.patterns['long_function']['description']} ({func_line_count} lines, >{self.patterns['long_function']['threshold']})",
                            recommendation=self.patterns['long_function']['recommendation'],
                            code_snippet='\n'.join(lines[current_func_start-1:min(current_func_start+3, len(lines))]),
                            confidence=0.8,
                            related_issues=[]
                        )
                        self.issues.append(issue)

                current_func_start = i
                func_line_count = 0
            else:
                func_line_count += 1

        # Check the last function if it exists
        if current_func_start is not None and func_line_count > self.patterns['long_function']['threshold']:
            issue_id = f"long_function_{file_path}:{current_func_start}"
            issue = IdentifiedIssue(
                id=issue_id,
                category=self.patterns['long_function']['category'],
                severity=self.patterns['long_function']['severity'],
                file_path=str(file_path),
                line_number=current_func_start,
                column_number=0,
                issue_description=f"{self.patterns['long_function']['description']} ({func_line_count} lines, >{self.patterns['long_function']['threshold']})",
                recommendation=self.patterns['long_function']['recommendation'],
                code_snippet='\n'.join(lines[current_func_start-1:min(current_func_start+3, len(lines))]),
                confidence=0.8,
                related_issues=[]
            )
            self.issues.append(issue)

        # Check for files that open resources without closing them properly
        open_count = len(re.findall(r'open\(', content))
        with_count = len(re.findall(r'with ', content))

        if open_count > with_count and open_count > 0:
            # If there are more open() calls than with statements, flag potential resource leaks
            for i, line in enumerate(lines, 1):
                if 'open(' in line and 'with ' not in line:
                    issue_id = f"unhandled_file_close_{file_path}:{i}"

                    issue = IdentifiedIssue(
                        id=issue_id,
                        category=self.patterns['unhandled_file_close']['category'],
                        severity=self.patterns['unhandled_file_close']['severity'],
                        file_path=str(file_path),
                        line_number=i,
                        column_number=line.find('open('),
                        issue_description=self.patterns['unhandled_file_close']['description'],
                        recommendation=self.patterns['unhandled_file_close']['recommendation'],
                        code_snippet=line.strip(),
                        confidence=0.7,
                        related_issues=[]
                    )
                    self.issues.append(issue)

    def _scan_python_ast(self, file_path: Path, content: str):
        """Scan Python files using AST analysis."""
        try:
            tree = ast.parse(content)

            # Walk through the AST to identify issues
            for node in ast.walk(tree):
                # Look for nested loops
                if isinstance(node, (ast.For, ast.While)):
                    # Check child nodes for more loops (nested loops)
                    for child in ast.iter_child_nodes(node):
                        if isinstance(child, (ast.For, ast.While)):
                            issue_id = f"nested_loop_{file_path}:{node.lineno}"
                            code_snippet = content.split('\n')[node.lineno-1] if node.lineno <= len(content.split('\n')) else ""

                            issue = IdentifiedIssue(
                                id=issue_id,
                                category=self.patterns['nested_loops']['category'],
                                severity=self.patterns['nested_loops']['severity'],
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column_number=getattr(node, 'col_offset', 0),
                                issue_description=self.patterns['nested_loops']['description'],
                                recommendation=self.patterns['nested_loops']['recommendation'],
                                code_snippet=code_snippet.strip(),
                                confidence=0.85,
                                related_issues=[]
                            )
                            self.issues.append(issue)

                # Look for eval usage (security risk)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    issue_id = f"eval_usage_{file_path}:{node.lineno}"
                    code_snippet = content.split('\n')[node.lineno-1] if node.lineno <= len(content.split('\n')) else ""

                    issue = IdentifiedIssue(
                        id=issue_id,
                        category=IssueCategory.SECURITY_VULNERABILITY,
                        severity=IssueSeverity.CRITICAL,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        column_number=getattr(node, 'col_offset', 0),
                        issue_description="Use of eval() function presents serious security risk",
                        recommendation="Avoid eval(); use ast.literal_eval() for parsing literals or redesign to eliminate dynamic evaluation",
                        code_snippet=code_snippet.strip(),
                        confidence=1.0,
                        related_issues=[]
                    )
                    self.issues.append(issue)

                # Look for exec usage (security risk)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'exec':
                    issue_id = f"exec_usage_{file_path}:{node.lineno}"
                    code_snippet = content.split('\n')[node.lineno-1] if node.lineno <= len(content.split('\n')) else ""

                    issue = IdentifiedIssue(
                        id=issue_id,
                        category=IssueCategory.SECURITY_VULNERABILITY,
                        severity=IssueSeverity.CRITICAL,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        column_number=getattr(node, 'col_offset', 0),
                        issue_description="Use of exec() function presents serious security risk",
                        recommendation="Avoid exec(); redesign to eliminate dynamic code execution",
                        code_snippet=code_snippet.strip(),
                        confidence=1.0,
                        related_issues=[]
                    )
                    self.issues.append(issue)

        except SyntaxError:
            # This would be caught by syntax checking anyway
            pass

    def get_issues_by_severity(self, severity: IssueSeverity) -> List[IdentifiedIssue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: IssueCategory) -> List[IdentifiedIssue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]

    def get_issues_by_file(self, file_path: str) -> List[IdentifiedIssue]:
        """Get issues for a specific file."""
        return [issue for issue in self.issues if issue.file_path == file_path]

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of identified issues."""
        report = {
            "summary": {
                "total_issues": len(self.issues),
                "by_severity": {},
                "by_category": {},
                "by_file": {}
            },
            "issues": []
        }

        # Calculate summary statistics
        for issue in self.issues:
            # Count by severity
            sev_val = issue.severity.value
            report["summary"]["by_severity"][sev_val] = report["summary"]["by_severity"].get(sev_val, 0) + 1

            # Count by category
            cat_val = issue.category.value
            report["summary"]["by_category"][cat_val] = report["summary"]["by_category"].get(cat_val, 0) + 1

            # Count by file
            file_val = issue.file_path
            report["summary"]["by_file"][file_val] = report["summary"]["by_file"].get(file_val, 0) + 1

        # Add detailed issue information
        for issue in self.issues:
            issue_dict = {
                "id": issue.id,
                "category": issue.category.value,
                "severity": issue.severity.value,
                "file_path": issue.file_path,
                "line_number": issue.line_number,
                "column_number": issue.column_number,
                "issue_description": issue.issue_description,
                "recommendation": issue.recommendation,
                "code_snippet": issue.code_snippet,
                "confidence": issue.confidence
            }
            report["issues"].append(issue_dict)

        return report

    def print_issues_summary(self):
        """Print a summary of identified issues."""
        print("\n" + "="*70)
        print("CODE ISSUES IDENTIFICATION REPORT")
        print("="*70)

        if not self.issues:
            print("No issues found in the scanned codebase.")
            return

        # Generate report
        report = self.generate_report()

        print(f"Total Issues Found: {report['summary']['total_issues']}")

        print("\nIssues by Severity:")
        for severity, count in report['summary']['by_severity'].items():
            print(f"  {severity.upper()}: {count}")

        print("\nIssues by Category:")
        for category, count in report['summary']['by_category'].items():
            print(f"  {category.replace('_', ' ').title()}: {count}")

        print("\nTop 5 Files with Most Issues:")
        sorted_files = sorted(report['summary']['by_file'].items(), key=lambda x: x[1], reverse=True)[:5]
        for file_path, count in sorted_files:
            print(f"  {file_path}: {count} issues")

        print("="*70)

    def export_report(self, output_path: str):
        """Export the issue report to a JSON file."""
        report = self.generate_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"Issue report exported to: {output_path}")


def main():
    """Example usage of the code issue identification system."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Create sample files with various issues
        sample_file1 = project_path / "security_issues.py"
        sample_code1 = '''
import pickle  # Security issue: unsafe pickle usage

def process_user_input(user_input):
    # Security issue: potential SQL injection
    query = f"SELECT * FROM users WHERE id = {user_input}"
    cursor.execute(query)

    # Security issue: hardcoded credential
    password = "super_secret_password"

    # Logic issue: TODO comment
    # TODO: Implement proper validation

    # Resource issue: improper file handling
    f = open("data.txt")
    data = f.read()
    # Forgot to close the file!

    # Performance issue: nested loops
    for i in users:
        for j in users:  # Nested loop
            if i == j:
                result.append(i)

    # Security issue: eval usage
    result = eval(user_input)

    return result
        '''

        with open(sample_file1, 'w', encoding='utf-8') as f:
            f.write(sample_code1)

        # Another file with issues
        sample_file2 = project_path / "long_function.py"
        long_func_code = '''
def very_long_function():  # This function will be too long
    """Long function to trigger maintainability issue."""
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
    bf = 61  # Over 50 lines

    return x_val
        '''

        with open(sample_file2, 'w', encoding='utf-8') as f:
            f.write(long_func_code)

        # Initialize the issue detector
        detector = IssueDetector(str(project_path))

        print("DCAE Review & Quality Assurance - Code Issue Identification")
        print("="*70)

        # Scan the project
        issues = detector.scan_project()

        # Print summary
        detector.print_issues_summary()

        # Show detailed critical issues
        critical_issues = detector.get_issues_by_severity(IssueSeverity.CRITICAL)
        if critical_issues:
            print(f"\nCRITICAL ISSUES FOUND ({len(critical_issues)}):")
            print("-" * 50)
            for issue in critical_issues[:5]:  # Show first 5 critical issues
                print(f"File: {issue.file_path}:{issue.line_number}")
                print(f"Description: {issue.issue_description}")
                print(f"Recommendation: {issue.recommendation}")
                print(f"Code: {issue.code_snippet}")
                print()

        # Export full report
        output_path = project_path / "issue_report.json"
        detector.export_report(str(output_path))

        print(f"\nCode issue identification completed. Report available at: {output_path}")


if __name__ == "__main__":
    main()