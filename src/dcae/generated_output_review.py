"""
Review and Quality Assurance - Generated Output Review Module

This module implements the functionality for systematically reviewing generated code
and artifacts to ensure quality, correctness, and alignment with requirements.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import ast
import re
from collections import defaultdict
import subprocess
import tempfile


class ReviewSeverity(Enum):
    """Enumeration for review severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewCategory(Enum):
    """Enumeration for review categories."""
    CODE_QUALITY = "code_quality"
    ARCHITECTURE_ALIGNMENT = "architecture_alignment"
    REQUIREMENTS_COVERAGE = "requirements_coverage"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"


@dataclass
class ReviewFinding:
    """Represents a single finding from the review process."""
    id: str
    category: ReviewCategory
    severity: ReviewSeverity
    file_path: str
    line_number: int
    issue_description: str
    recommendation: str
    code_snippet: str


@dataclass
class ReviewReport:
    """Represents the complete review report."""
    findings: List[ReviewFinding]
    summary: Dict[str, Any]
    timestamp: str
    review_configuration: Dict[str, Any]


class GeneratedOutputReviewer:
    """Reviews generated code and artifacts for quality and alignment."""

    def __init__(self, project_path: str, requirements_spec: Optional[Dict[str, Any]] = None,
                 architecture_spec: Optional[Dict[str, Any]] = None):
        """
        Initialize the output reviewer.

        Args:
            project_path: Path to the project root
            requirements_spec: Requirements specification
            architecture_spec: Architecture specification
        """
        self.project_path = Path(project_path)
        self.requirements_spec = requirements_spec or {}
        self.architecture_spec = architecture_spec or {}
        self.findings: List[ReviewFinding] = []
        self.file_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs'}

    def review_generated_output(self, target_path: Optional[str] = None) -> ReviewReport:
        """
        Perform a comprehensive review of generated output.

        Args:
            target_path: Specific path to review (optional, defaults to entire project)

        Returns:
            ReviewReport containing findings and summary
        """
        review_path = Path(target_path) if target_path else self.project_path

        # Check if the path exists
        if not review_path.exists():
            print(f"Warning: Path {review_path} does not exist. Creating empty report.")
            self.findings = []  # Reset findings
            summary = self._generate_summary()

            report = ReviewReport(
                findings=self.findings,
                summary=summary,
                timestamp="unknown",
                review_configuration={
                    "requirements_tracing_enabled": bool(self.requirements_spec),
                    "architecture_validation_enabled": bool(self.architecture_spec)
                }
            )
            return report

        self.findings = []  # Reset findings

        print(f"Starting review of generated output in: {review_path}")

        # Perform all review categories
        self._review_code_quality(review_path)
        self._review_architecture_alignment(review_path)
        self._review_requirements_coverage(review_path)
        self._review_security(review_path)
        self._review_performance(review_path)
        self._review_best_practices(review_path)

        # Generate summary
        summary = self._generate_summary()

        # Create report
        import time
        report = ReviewReport(
            findings=self.findings,
            summary=summary,
            timestamp=str(time.time()),
            review_configuration={
                "requirements_tracing_enabled": bool(self.requirements_spec),
                "architecture_validation_enabled": bool(self.architecture_spec)
            }
        )

        return report

    def _review_code_quality(self, path: Path):
        """Review code quality aspects."""
        print(f"  Performing code quality review in: {path}")

        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.file_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check for long functions (more than 50 lines)
                    # Parse the content using AST to identify functions properly
                    lines = content.split('\n')  # Move this line outside try-catch to make it available everywhere
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                # Count the lines in the function body
                                start_line = node.lineno
                                end_line = max([getattr(n, 'lineno', start_line) for n in ast.walk(node)])

                                # Calculate the function length based on source
                                func_lines = content.split('\n')[start_line-1:end_line]
                                func_length = len([ln for ln in func_lines if ln.strip()])

                                if func_length > 50:
                                    finding = ReviewFinding(
                                        id=f"cq_long_func_{file_path}:{start_line}",
                                        category=ReviewCategory.CODE_QUALITY,
                                        severity=ReviewSeverity.MEDIUM,
                                        file_path=str(file_path),
                                        line_number=start_line,
                                        issue_description=f"Function '{node.name}' is too long ({func_length} non-empty lines, >50)",
                                        recommendation="Consider breaking down the function into smaller, more manageable functions",
                                        code_snippet='\n'.join(func_lines[:5])  # First 5 lines as snippet
                                    )
                                    self.findings.append(finding)
                    except SyntaxError:
                        # If we can't parse the file, fall back to basic line counting
                        i = 0
                        while i < len(lines):
                            line = lines[i]
                            stripped_line = line.strip()

                            # Check if this line starts a function or class definition
                            if re.match(r'^\s*(def |class |async def )', stripped_line):
                                func_start_idx = i
                                func_line_count = 1  # Count the function definition line

                                # Look ahead to count lines until next function/class or end of file
                                j = i + 1
                                indent_level = len(line) - len(line.lstrip()) if line.strip() else float('inf')

                                # For function definitions, we need to look for indented code
                                while j < len(lines):
                                    next_line = lines[j]
                                    next_stripped = next_line.strip()

                                    if not next_stripped:
                                        # Empty line, still part of function
                                        func_line_count += 1
                                        j += 1
                                        continue

                                    # Check the indentation to see if we're still in the function
                                    next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else float('inf')

                                    # If it's another function/class definition at same or less indentation, end current function
                                    if re.match(r'^\s*(def |class |async def )', next_stripped) and next_indent <= indent_level and next_stripped:
                                        break

                                    # If it's a statement at the same or lower indentation level, but it's not inside the function
                                    if next_indent <= indent_level and not re.match(r'^\s+(.*)', next_stripped) and next_stripped:
                                        break

                                    # Otherwise, this line is part of the function
                                    func_line_count += 1
                                    j += 1

                                # If the function is too long, add a finding
                                if func_line_count > 50:
                                    finding = ReviewFinding(
                                        id=f"cq_long_func_{file_path}:{func_start_idx + 1}",
                                        category=ReviewCategory.CODE_QUALITY,
                                        severity=ReviewSeverity.MEDIUM,
                                        file_path=str(file_path),
                                        line_number=func_start_idx + 1,
                                        issue_description=f"Function is too long ({func_line_count} lines, >50)",
                                        recommendation="Consider breaking down the function into smaller, more manageable functions",
                                        code_snippet='\n'.join(lines[func_start_idx:min(func_start_idx+5, len(lines))])
                                    )
                                    self.findings.append(finding)

                                # Move to the end of the function
                                i = j
                            else:
                                i += 1

                    # Check for TODO/FIXME comments
                    for i, line in enumerate(lines, 1):
                        if 'TODO' in line.upper():
                            finding = ReviewFinding(
                                id=f"cq_todo_{file_path}:{i}",
                                category=ReviewCategory.CODE_QUALITY,
                                severity=ReviewSeverity.LOW,
                                file_path=str(file_path),
                                line_number=i,
                                issue_description="TODO comment found in code",
                                recommendation="Address the TODO before finalizing the code",
                                code_snippet=line.strip()
                            )
                            self.findings.append(finding)

                        if 'FIXME' in line.upper():
                            finding = ReviewFinding(
                                id=f"cq_fixme_{file_path}:{i}",
                                category=ReviewCategory.CODE_QUALITY,
                                severity=ReviewSeverity.HIGH,
                                file_path=str(file_path),
                                line_number=i,
                                issue_description="FIXME comment found in code",
                                recommendation="Address the FIXME issue immediately",
                                code_snippet=line.strip()
                            )
                            self.findings.append(finding)

                except Exception as e:
                    print(f"    Warning: Could not review {file_path}: {str(e)}")

    def _review_architecture_alignment(self, path: Path):
        """Review alignment with architectural specifications."""
        print(f"  Performing architecture alignment review in: {path}")

        if not self.architecture_spec:
            print("    Skipping architecture review - no architecture specification provided")
            return

        # Check for required components
        required_components = []
        if "components" in self.architecture_spec:
            for component in self.architecture_spec["components"]:
                if "name" in component:
                    # Store original name and variations for matching
                    name = component["name"]
                    name_lower = name.lower()
                    required_components.append({
                        "original": name,
                        "variations": [
                            name_lower.replace(" ", "").replace("-", "").replace("_", ""),
                            name_lower.replace(" ", "_"),
                            name_lower.replace(" ", "-"),
                            name_lower.replace("-", " ").replace("_", " "),  # normalize spaces
                            # Additional variations for better matching
                            name_lower.replace(" ", "").replace("-", "_"),  # mix of separators
                            name_lower.replace(" ", "").replace("_", "-")   # mix of separators
                        ]
                    })

        # Find actual components in codebase by looking for class/function definitions
        actual_components = []

        # Walk through all Python files to find class and function names
        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Look for class and function definitions
                    # Class names like "AuthService", "Auth_Service", "Auth-service"
                    classes = re.findall(r'class (\w+)', content)
                    # Function names like "auth_service", "authenticate_user", etc.
                    functions = re.findall(r'def (\w+)', content)

                    for cls in classes:
                        # Store the original class name and its variations
                        actual_components.append({
                            "original": cls,
                            "variations": [
                                cls.lower().replace(" ", "").replace("-", "").replace("_", ""),
                                cls.lower().replace(" ", "_"),
                                cls.lower().replace(" ", "-"),
                                cls.lower(),  # just lowercase
                                # Additional variations for better matching
                                cls.lower().replace(" ", "").replace("-", "_"),  # mix of separators
                                cls.lower().replace(" ", "").replace("_", "-")   # mix of separators
                            ]
                        })

                    for func in functions:
                        # Store the original function name and its variations
                        actual_components.append({
                            "original": func,
                            "variations": [
                                func.lower().replace(" ", "").replace("-", "").replace("_", ""),
                                func.lower().replace(" ", "_"),
                                func.lower().replace(" ", "-"),
                                func.lower(),  # just lowercase
                                # Additional variations for better matching
                                func.lower().replace(" ", "").replace("-", "_"),  # mix of separators
                                func.lower().replace(" ", "").replace("_", "-")   # mix of separators
                            ]
                        })

                except Exception as e:
                    print(f"    Warning: Could not review {file_path}: {str(e)}")
                    continue

        # Check for missing components using more conservative matching
        missing_components = []

        for req_comp in required_components:
            matched = False

            # Try to match each required component with actual components
            for actual_comp in actual_components:
                # Check if any of the actual variations contain or are contained in required variations
                for req_var in req_comp["variations"]:
                    for act_var in actual_comp["variations"]:
                        # Exact match
                        if req_var == act_var:
                            matched = True
                            break
                        # Substring match but with stricter constraints
                        # Require that the shorter string is at least 80% of the longer one to prevent false matches
                        elif req_var in act_var:
                            if len(req_var) >= len(act_var) * 0.8:
                                matched = True
                                break
                        elif act_var in req_var:
                            if len(act_var) >= len(req_var) * 0.8:
                                matched = True
                                break
                    if matched:
                        break

                if matched:
                    break

            if not matched:
                missing_components.append(req_comp["original"])

        # Report missing components
        for component in missing_components:
            # Only create findings for meaningful components (not empty or very generic terms)
            if component and len(component) > 2:  # Avoid empty strings and very short names
                finding = ReviewFinding(
                    id=f"arch_missing_comp_{component.replace(' ', '_').replace('-', '_').replace('.', '_')}",
                    category=ReviewCategory.ARCHITECTURE_ALIGNMENT,
                    severity=ReviewSeverity.HIGH,
                    file_path="architecture",
                    line_number=0,
                    issue_description=f"Required component '{component}' is missing from implementation",
                    recommendation=f"Implement the required component '{component}' as specified in the architecture",
                    code_snippet=""
                )
                self.findings.append(finding)

    def _review_requirements_coverage(self, path: Path):
        """Review coverage of requirements."""
        print(f"  Performing requirements coverage review in: {path}")

        if not self.requirements_spec:
            print("    Skipping requirements review - no requirements specification provided")
            return

        # Extract requirement IDs
        requirement_ids = set()
        if "functional_requirements" in self.requirements_spec:
            for req in self.requirements_spec["functional_requirements"]:
                if "id" in req:
                    requirement_ids.add(req["id"])

        if "non_functional_requirements" in self.requirements_spec:
            for req in self.requirements_spec["non_functional_requirements"]:
                if "id" in req:
                    requirement_ids.add(req["id"])

        # For this basic implementation, we'll just report that we checked
        # In a full implementation, this would look for requirement traces in code comments/docstrings
        print(f"    Checked for coverage of {len(requirement_ids)} requirements")

    def _review_security(self, path: Path):
        """Review security aspects."""
        print(f"  Performing security review in: {path}")

        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.file_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        # Check for hardcoded passwords
                        if re.search(r'(password|secret|token).*["\'][^"\']+["\']', line, re.IGNORECASE):
                            finding = ReviewFinding(
                                id=f"sec_hardcoded_{file_path}:{i}",
                                category=ReviewCategory.SECURITY,
                                severity=ReviewSeverity.CRITICAL,
                                file_path=str(file_path),
                                line_number=i,
                                issue_description="Hardcoded credential found in code",
                                recommendation="Move credentials to environment variables or secure configuration",
                                code_snippet=line.strip()
                            )
                            self.findings.append(finding)

                        # Check for SQL injection vulnerabilities (simple patterns)
                        if re.search(r'cursor.execute|execute\(|conn.execute', line, re.IGNORECASE) and \
                           re.search(r'f"|f\'|\+.+|".+|format\(', line):
                            finding = ReviewFinding(
                                id=f"sec_sql_inj_{file_path}:{i}",
                                category=ReviewCategory.SECURITY,
                                severity=ReviewSeverity.HIGH,
                                file_path=str(file_path),
                                line_number=i,
                                issue_description="Potential SQL injection vulnerability found",
                                recommendation="Use parameterized queries instead of string concatenation",
                                code_snippet=line.strip()
                            )
                            self.findings.append(finding)

                        # Check for insecure imports
                        if re.search(r'import pickle|from pickle', line, re.IGNORECASE):
                            finding = ReviewFinding(
                                id=f"sec_pickle_{file_path}:{i}",
                                category=ReviewCategory.SECURITY,
                                severity=ReviewSeverity.HIGH,
                                file_path=str(file_path),
                                line_number=i,
                                issue_description="Use of unsafe pickle module",
                                recommendation="Avoid pickle for untrusted data; use safer serialization methods",
                                code_snippet=line.strip()
                            )
                            self.findings.append(finding)

                except Exception as e:
                    print(f"    Warning: Could not review security in {file_path}: {str(e)}")

    def _review_performance(self, path: Path):
        """Review performance aspects."""
        print(f"  Performing performance review in: {path}")

        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Parse AST to analyze code structure
                    try:
                        tree = ast.parse(content)
                        self._analyze_ast_for_performance(tree, file_path)
                    except SyntaxError:
                        continue

                except Exception:
                    continue

    def _analyze_ast_for_performance(self, tree: ast.AST, file_path: Path):
        """Analyze AST for performance issues."""
        for node in ast.walk(tree):
            if isinstance(node, ast.For) or isinstance(node, ast.While):
                # Check for nested loops which could indicate performance issues
                for child in ast.walk(node):
                    if isinstance(child, ast.For) or isinstance(child, ast.While):
                        finding = ReviewFinding(
                            id=f"perf_nested_loop_{file_path}:{node.lineno}",
                            category=ReviewCategory.PERFORMANCE,
                            severity=ReviewSeverity.MEDIUM,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_description="Nested loops detected which may cause performance issues",
                            recommendation="Consider algorithm optimization or alternative data structures",
                            code_snippet=ast.get_source_segment(open(file_path).read(), node)
                        )
                        self.findings.append(finding)

    def _review_best_practices(self, path: Path):
        """Review adherence to best practices."""
        print(f"  Performing best practices review in: {path}")

        for file_path in path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        # Check for print statements in production code
                        if line.strip().startswith('print(') and 'debug' not in file_path.name.lower():
                            finding = ReviewFinding(
                                id=f"bp_print_stmt_{file_path}:{i}",
                                category=ReviewCategory.BEST_PRACTICES,
                                severity=ReviewSeverity.LOW,
                                file_path=str(file_path),
                                line_number=i,
                                issue_description="Print statement found in non-debug code",
                                recommendation="Remove print statements or use proper logging",
                                code_snippet=line.strip()
                            )
                            self.findings.append(finding)

                except Exception:
                    continue

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the review."""
        summary = {
            "total_findings": len(self.findings),
            "findings_by_severity": defaultdict(int),
            "findings_by_category": defaultdict(int),
            "files_reviewed": len(set(f.file_path for f in self.findings)),
            "categories_covered": set(),
        }

        for finding in self.findings:
            summary["findings_by_severity"][finding.severity.value] += 1
            summary["findings_by_category"][finding.category.value] += 1
            summary["categories_covered"].add(finding.category.value)

        # Convert defaultdict to regular dict for JSON serialization
        summary["findings_by_severity"] = dict(summary["findings_by_severity"])
        summary["findings_by_category"] = dict(summary["findings_by_category"])
        summary["categories_covered"] = list(summary["categories_covered"])

        return summary

    def export_report(self, report: ReviewReport, output_path: str):
        """Export the review report to a file."""
        export_data = {
            "timestamp": report.timestamp,
            "summary": report.summary,
            "findings": [
                {
                    "id": f.id,
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "issue_description": f.issue_description,
                    "recommendation": f.recommendation,
                    "code_snippet": f.code_snippet
                } for f in report.findings
            ],
            "configuration": report.review_configuration
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        print(f"Review report exported to: {output_path}")

    def print_findings_summary(self, report: ReviewReport):
        """Print a summary of the review findings."""
        print("\n" + "="*60)
        print("REVIEW FINDINGS SUMMARY")
        print("="*60)
        print(f"Total Findings: {report.summary['total_findings']}")
        print(f"Files Reviewed: {report.summary['files_reviewed']}")
        print(f"Categories Covered: {', '.join(report.summary['categories_covered'])}")
        print("\nFindings by Severity:")
        for severity, count in report.summary["findings_by_severity"].items():
            print(f"  {severity.upper()}: {count}")
        print("\nFindings by Category:")
        for category, count in report.summary["findings_by_category"].items():
            print(f"  {category.replace('_', ' ').title()}: {count}")
        print("="*60)


def main():
    """Example usage of the generated output reviewer."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Create a sample Python file with issues
        sample_file = project_path / "sample.py"
        sample_code = '''
def process_data(data):
    """Sample function with potential issues."""
    password = "hardcoded_secret"  # Security issue
    result = []
    for i in data:  # Outer loop
        for j in data:  # Nested loop - Performance issue
            if i == j:
                result.append(i)
    return result

def long_function():  # This function will be too long
    """Long function to trigger code quality issue."""
    print("This is a debug print")  # Best practice issue
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
    av = 51  # Over 50 lines

    cursor.execute("SELECT * FROM users WHERE id = " + str(x))  # SQL injection
    return x_val
        '''

        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_code)

        # Sample requirements and architecture specs
        requirements_spec = {
            "functional_requirements": [
                {"id": "REQ001", "title": "User Authentication", "description": "System shall authenticate users"}
            ]
        }

        architecture_spec = {
            "components": [
                {"name": "Authentication Service"},
                {"name": "Data Processor"}
            ]
        }

        # Initialize the reviewer
        reviewer = GeneratedOutputReviewer(
            project_path=str(project_path),
            requirements_spec=requirements_spec,
            architecture_spec=architecture_spec
        )

        print("DCAE Review & Quality Assurance - Generated Output Review")
        print("="*60)

        # Perform the review
        report = reviewer.review_generated_output()

        # Print summary
        reviewer.print_findings_summary(report)

        # Export report
        output_path = project_path / "review_report.json"
        reviewer.export_report(report, str(output_path))

        print(f"\nDetailed review completed. Report available at: {output_path}")


if __name__ == "__main__":
    main()