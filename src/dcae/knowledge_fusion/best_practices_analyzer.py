#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Best Practices Analyzer and Improver

This module analyzes Python code against best practices and suggests improvements.
It uses the BestPracticesReflector to evaluate code quality, security, and other
important aspects.
"""

import ast
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
import sys
import os

# Add the src directory to the path to import the best practices reflector
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dcae.knowledge_fusion.best_practices_reflector import BestPracticesReflector, BestPracticeCategory
from dcae.knowledge_fusion.domain_knowledge_manager import DomainKnowledgeManager, DomainType


class BestPracticesAnalyzer:
    """Analyzes code against best practices and suggests improvements."""

    def __init__(self):
        """Initialize the analyzer with a domain knowledge manager and best practices reflector."""
        self.domain_manager = DomainKnowledgeManager()
        self.reflector = BestPracticesReflector(self.domain_manager)

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file against best practices.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            Dictionary containing analysis results
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Reflect best practices in the content
        results = self.reflector.reflect_best_practices_in_content(
            content,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.SECURITY, BestPracticeCategory.CODE_QUALITY,
             BestPracticeCategory.TESTING, BestPracticeCategory.PERFORMANCE]
        )

        # Parse the AST to get more detailed analysis
        try:
            tree = ast.parse(content)
            ast_analysis = self._analyze_ast(tree)
        except SyntaxError:
            ast_analysis = {"error": "Syntax error in file"}

        return {
            "file_path": file_path,
            "best_practice_results": results,
            "ast_analysis": ast_analysis,
            "content_analysis": self._analyze_content(content)
        }

    def _analyze_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze the AST for structural best practices."""
        visitor = BestPracticesVisitor()
        visitor.visit(tree)
        return visitor.get_results()

    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze the content for various best practices."""
        analysis = {
            "line_count": len(content.splitlines()),
            "function_count": len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE)),
            "comment_ratio": self._calculate_comment_ratio(content),
            "docstring_count": len(re.findall(r'""".*?"""|\'\'\'.*?\'\'\'', content, re.DOTALL)),
            "potential_security_issues": self._find_security_issues(content),
            "performance_patterns": self._find_performance_patterns(content)
        }
        return analysis

    def _calculate_comment_ratio(self, content: str) -> float:
        """Calculate the ratio of comment lines to total lines."""
        lines = content.splitlines()
        if not lines:
            return 0.0

        comment_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                comment_lines += 1
            elif stripped.startswith(('"""', "'''")):
                # Count docstring lines
                continue

        return comment_lines / len(lines)

    def _find_security_issues(self, content: str) -> List[str]:
        """Find potential security issues in the content."""
        issues = []

        # Check for dangerous functions
        dangerous_calls = [
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\bos\.system\s*\(',
            r'\bsubprocess\.call\s*\([^)]*shell=True',
            r'\bsubprocess\.Popen\s*\([^)]*shell=True'
        ]

        for pattern in dangerous_calls:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Potential security issue: {pattern}")

        return issues

    def _find_performance_patterns(self, content: str) -> List[str]:
        """Find potential performance issues in the content."""
        patterns = []

        # Check for nested loops without obvious optimizations
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if 'for ' in line and any('for ' in l for l in lines[i+1:i+10]):  # Check next 10 lines
                if 'range(' in line and any('range(' in l for l in lines[i+1:i+10]):
                    patterns.append(f"Potential performance issue: nested loops detected around line {i+1}")

        return patterns


class BestPracticesVisitor(ast.NodeVisitor):
    """AST visitor to analyze code structure for best practices."""

    def __init__(self):
        self.results = {
            "functions": [],
            "long_functions": [],
            "complexity_warnings": [],
            "missing_docstrings": [],
            "large_classes": []
        }
        self.function_details = []

    def visit_FunctionDef(self, node):
        """Visit function definitions to analyze for best practices."""
        # Calculate function statistics
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', node.lineno)
        line_count = end_line - start_line + 1

        func_info = {
            "name": node.name,
            "line_count": line_count,
            "param_count": len(node.args.args),
            "start_line": start_line,
            "has_docstring": len(node.body) > 0 and
                             isinstance(node.body[0], ast.Expr) and
                             isinstance(node.body[0].value, ast.Constant) and
                             isinstance(node.body[0].value.value, str)
        }

        self.function_details.append(func_info)

        # Check for long functions (best practice: keep functions short)
        if line_count > 50:  # Using 50 lines as a threshold
            self.results["long_functions"].append(func_info)

        # Check for functions without docstrings
        if not func_info["has_docstring"]:
            self.results["missing_docstrings"].append(func_info)

        # Continue visiting child nodes
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        # Count methods in class
        method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))

        if method_count > 20:  # Arbitrary threshold for large classes
            class_info = {
                "name": node.name,
                "method_count": method_count,
                "line_start": node.lineno
            }
            self.results["large_classes"].append(class_info)

        self.generic_visit(node)

    def get_results(self):
        """Get the collected analysis results."""
        self.results["functions"] = self.function_details
        return self.results


def improve_code_file(file_path: str, output_path: str = None) -> bool:
    """
    Improve a Python code file by applying best practices.

    Args:
        file_path: Path to the Python file to improve
        output_path: Path to save the improved code (same as input if not specified)

    Returns:
        True if improvement was successful, False otherwise
    """
    if output_path is None:
        output_path = file_path

    # Read the original content
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Apply best practices improvements
    improved_content = apply_best_practices_improvements(original_content)

    # Write the improved content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(improved_content)

    return True


def apply_best_practices_improvements(content: str) -> str:
    """
    Apply basic best practices improvements to code content.

    Args:
        content: Original Python code content

    Returns:
        Improved Python code content
    """
    # Add security note if input functions are detected without validation
    if re.search(r'input\(|sys\.argv|argparse', content, re.IGNORECASE):
        if 'validate' not in content.lower() and '# Security:' not in content:
            content += "\n\n# Security: Remember to validate and sanitize all inputs\n"

    # Add testing reminder if functions exist without test mentions
    if 'def ' in content and 'test' not in content.lower():
        content += "\n# TODO: Add unit tests for this code\n"

    # Add performance note if nested loops detected
    if content.count('for ') > 1:  # Simple detection of potential nested loops
        loop_matches = re.findall(r'^(\s*)for\s+.*:$', content, re.MULTILINE)
        if len(loop_matches) > 1:
            content += "\n# Performance: Consider optimizing nested loops if performance is critical\n"

    return content


def main():
    """Main function to run the best practices analyzer."""
    if len(sys.argv) < 2:
        print("Usage: python best_practices_analyzer.py <file_path> [output_path]")
        print("Example: python best_practices_analyzer.py dcae.py")
        sys.exit(1)

    file_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)

    analyzer = BestPracticesAnalyzer()

    print(f"Analyzing {file_path} against best practices...")
    results = analyzer.analyze_file(file_path)

    print("\n=== Best Practice Results ===")
    for result in results["best_practice_results"]:
        status = "[OK] FOLLOWED" if result.is_followed else "[X] VIOLATED"
        print(f"{status} {result.practice_title}")
        if not result.is_followed:
            print(f"  Violations: {result.violations}")
            print(f"  Suggestions: {result.suggestions}")

    print("\n=== Content Analysis ===")
    content_analysis = results["content_analysis"]
    print(f"Lines: {content_analysis['line_count']}")
    print(f"Functions: {content_analysis['function_count']}")
    print(f"Comment Ratio: {content_analysis['comment_ratio']:.2%}")
    print(f"Docstrings: {content_analysis['docstring_count']}")

    if content_analysis['potential_security_issues']:
        print(f"Security Issues: {content_analysis['potential_security_issues']}")

    if content_analysis['performance_patterns']:
        print(f"Performance Patterns: {content_analysis['performance_patterns']}")

    print("\n=== AST Analysis ===")
    ast_analysis = results["ast_analysis"]
    print(f"Functions: {len(ast_analysis['functions'])}")
    print(f"Long Functions (>50 lines): {len(ast_analysis['long_functions'])}")
    print(f"Missing Docstrings: {len(ast_analysis['missing_docstrings'])}")
    print(f"Large Classes (>20 methods): {len(ast_analysis['large_classes'])}")

    # Apply improvements if output path specified
    if output_path:
        print(f"\nApplying improvements to {file_path} -> {output_path}")
        success = improve_code_file(file_path, output_path)
        if success:
            print("Improvements applied successfully!")
        else:
            print("Failed to apply improvements.")


if __name__ == "__main__":
    main()