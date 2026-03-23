#!/usr/bin/env python3
"""
DCAE Framework Core - Main framework implementation

DCAE (Design-Code-Analyze-Evolve) is a structured TDD framework
that guides developers through disciplined software development.
"""

import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List


# =============================================================================
# Cross-Platform Support
# =============================================================================

def get_platform() -> str:
    """
    Detect the current operating system.
    
    Returns:
        str: 'windows', 'macos', or 'linux'
    """
    if sys.platform.startswith('win') or sys.platform == 'cygwin':
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'macos'
    else:
        return 'linux'


def get_python_command() -> list:
    """
    Get the appropriate Python command for the current platform.
    
    Returns:
        list: Command list for running Python
    """
    platform = get_platform()
    if platform == 'windows':
        return ['python']
    else:
        return ['python3']


PLATFORM = get_platform()
PYTHON_CMD = get_python_command()


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class DCAEResult:
    """Result of a DCAE phase execution."""
    status: str  # success, partial, failed
    phase: str   # design, code, analyze, evolve
    timestamp: str
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    coverage_lines: float = 0.0
    coverage_functions: float = 0.0
    iterations: int = 0
    artifacts: list = None
    recommendations: list = None
    errors: list = None

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []
        if self.recommendations is None:
            self.recommendations = []
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @property
    def coverage_percent(self) -> float:
        """Get coverage as percentage."""
        return self.coverage_lines

    @property
    def success_rate(self) -> float:
        """Get test success rate."""
        if self.tests_total == 0:
            return 0.0
        return (self.tests_passed / self.tests_total) * 100


# =============================================================================
# DCAE Framework
# =============================================================================

class DCAEFramework:
    """
    DCAE Framework - Main class for TDD workflow.
    
    Usage:
        dcae = DCAEFramework(project_root="/path/to/project")
        result = dcae.run("tests/test_feature.py", "src/feature.py")
    """

    def __init__(self, project_root: str = "."):
        """
        Initialize DCAE Framework.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        self.state = {
            "phase": "init",
            "iterations": 0,
            "test_file": None,
            "source_file": None,
        }

    def _run_command(self, cmd: list, capture: bool = True) -> tuple:
        """
        Run a shell command.
        
        Args:
            cmd: Command list
            capture: Whether to capture output
            
        Returns:
            tuple: (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=capture,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def _run_tests(self, test_file: Optional[str] = None) -> DCAEResult:
        """
        Run pytest on specified test file or all tests.
        
        Args:
            test_file: Optional specific test file
            
        Returns:
            DCAEResult with test results
        """
        cmd = PYTHON_CMD + ["-m", "pytest"]
        
        if test_file:
            cmd.append(str(test_file))
        
        cmd.extend(["-v", "--tb=short"])
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        # Parse test results (simplified)
        tests_total = tests_passed = tests_failed = 0
        
        for line in stdout.split('\n'):
            if 'passed' in line:
                tests_passed += line.count('passed')
            if 'failed' in line:
                tests_failed += line.count('failed')
        
        tests_total = tests_passed + tests_failed
        
        status = "success" if returncode == 0 and tests_failed == 0 else "failed"
        
        return DCAEResult(
            status=status,
            phase="test",
            timestamp=datetime.now().isoformat(),
            tests_total=tests_total,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            errors=[stderr] if stderr else []
        )

    def _run_coverage(self) -> dict:
        """
        Run coverage analysis.
        
        Returns:
            dict: Coverage metrics
        """
        cmd = PYTHON_CMD + ["-m", "pytest", "--cov=dcae", "--cov-report=json", "-q"]
        
        returncode, stdout, stderr = self._run_command(cmd)
        
        # Try to read coverage report
        coverage_file = self.project_root / "coverage.json"
        if coverage_file.exists():
            import json
            try:
                with open(coverage_file) as f:
                    data = json.load(f)
                    return {
                        "lines": data.get("totals", {}).get("percent_covered", 0),
                        "functions": data.get("totals", {}).get("percent_covered", 0)
                    }
            except:
                pass
        
        return {"lines": 0.0, "functions": 0.0}

    def design(self, test_file: str, test_cases: Optional[List[str]] = None) -> DCAEResult:
        """
        Phase 1: Design - Create failing test specification.
        
        Args:
            test_file: Path to test file
            test_cases: Optional list of test case descriptions
            
        Returns:
            DCAEResult with design phase results
        """
        self.state["phase"] = "design"
        self.state["test_file"] = test_file
        
        # Create test file if it doesn't exist
        test_path = self.project_root / test_file
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not test_path.exists():
            # Create basic test template
            test_name = Path(test_file).stem
            content = f'''"""Tests for {test_name}."""
import pytest


def test_{test_name}_happy_path():
    """Test the main use case."""
    # TODO: Implement test
    assert True, "Test not implemented"


def test_{test_name}_edge_cases():
    """Test boundary conditions."""
    # TODO: Implement edge case tests
    assert True, "Test not implemented"
'''
            with open(test_path, 'w') as f:
                f.write(content)
        
        # Run tests to verify they fail (or pass if not implemented)
        result = self._run_tests(test_file)
        result.phase = "design"
        
        if result.tests_total == 0:
            result.recommendations = [
                "Implement test cases in the test file",
                "Start with happy path, then add edge cases",
                "Ensure tests fail before implementing code"
            ]
        else:
            result.recommendations = [
                "Tests created, proceed to Code phase",
                "Ensure tests are specific and test behavior, not implementation"
            ]
        
        self.state["iterations"] += 1
        return result

    def code(self, source_file: str) -> DCAEResult:
        """
        Phase 2: Code - Implement minimal code to pass tests.
        
        Args:
            source_file: Path to source file
            
        Returns:
            DCAEResult with code phase results
        """
        self.state["phase"] = "code"
        self.state["source_file"] = source_file
        
        # Create source file if it doesn't exist
        source_path = self.project_root / source_file
        source_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not source_path.exists():
            # Create basic source template
            module_name = Path(source_file).stem
            content = f'''"""{module_name} module."""


def {module_name}(input_data):
    """
    Process input data.
    
    Args:
        input_data: Input to process
        
    Returns:
        Processed result
    """
    # TODO: Implement function
    return input_data
'''
            with open(source_path, 'w') as f:
                f.write(content)
        
        # Run tests to check if they pass
        test_file = self.state.get("test_file")
        result = self._run_tests(test_file)
        result.phase = "code"
        
        if result.status == "success":
            result.recommendations = [
                "Tests passing, proceed to Analyze phase",
                "Consider adding more edge case tests"
            ]
        else:
            result.recommendations = [
                "Tests failing, implement code to pass tests",
                "Write minimal code to pass - don't over-engineer",
                "Follow YAGNI principle"
            ]
        
        self.state["iterations"] += 1
        return result

    def analyze(self, coverage_threshold: float = 80.0) -> DCAEResult:
        """
        Phase 3: Analyze - Check code quality and coverage.
        
        Args:
            coverage_threshold: Minimum coverage percentage
            
        Returns:
            DCAEResult with analysis results
        """
        self.state["phase"] = "analyze"
        
        # Run tests first
        test_file = self.state.get("test_file")
        result = self._run_tests(test_file)
        result.phase = "analyze"
        
        # Run coverage analysis
        coverage = self._run_coverage()
        result.coverage_lines = coverage.get("lines", 0.0)
        result.coverage_functions = coverage.get("functions", 0.0)
        
        # Check against threshold
        if result.coverage_lines < coverage_threshold:
            result.status = "partial"
            result.recommendations = [
                f"Coverage {result.coverage_lines:.1f}% below threshold {coverage_threshold}%",
                "Add tests for uncovered code paths",
                "Focus on edge cases and error handling"
            ]
        else:
            result.status = "success"
            result.recommendations = [
                f"Coverage {result.coverage_lines:.1f}% meets threshold",
                "Proceed to Evolve phase for refactoring",
                "Consider adding integration tests"
            ]
        
        self.state["iterations"] += 1
        return result

    def evolve(self, optimize: bool = False) -> DCAEResult:
        """
        Phase 4: Evolve - Refactor code without changing behavior.
        
        Args:
            optimize: Whether to include performance optimization
            
        Returns:
            DCAEResult with evolution results
        """
        self.state["phase"] = "evolve"
        
        # Run tests to ensure they pass before refactoring
        test_file = self.state.get("test_file")
        result = self._run_tests(test_file)
        result.phase = "evolve"
        
        # Provide refactoring recommendations
        result.recommendations = [
            "Extract duplicate code into helper functions",
            "Improve variable and function naming",
            "Add docstrings to public functions",
            "Consider breaking down large functions",
            "Review and simplify complex conditionals"
        ]
        
        if optimize:
            result.recommendations.extend([
                "Profile code to identify bottlenecks",
                "Consider algorithmic improvements",
                "Review data structure choices"
            ])
        
        if result.status == "success":
            result.recommendations.append("All tests passing after refactoring")
        
        self.state["iterations"] += 1
        return result

    def run(self, test_file: str, source_file: str, max_iterations: int = 10) -> DCAEResult:
        """
        Run complete DCAE cycle.
        
        Args:
            test_file: Path to test file
            source_file: Path to source file
            max_iterations: Maximum TDD iterations
            
        Returns:
            DCAEResult with complete cycle results
        """
        self.state["test_file"] = test_file
        self.state["source_file"] = source_file
        self.state["iterations"] = 0
        
        final_result = None
        
        for iteration in range(max_iterations):
            self.state["iterations"] = iteration + 1
            
            # Design phase
            design_result = self.design(test_file)
            
            # Code phase
            code_result = self.code(source_file)
            
            # Analyze phase
            analyze_result = self.analyze()
            
            # Check if we're done
            if analyze_result.status == "success" and code_result.status == "success":
                # Evolve phase
                evolve_result = self.evolve()
                final_result = evolve_result
                final_result.phase = "complete"
                break
            
            final_result = analyze_result
        
        if final_result is None:
            final_result = DCAEResult(
                status="partial",
                phase="complete",
                timestamp=datetime.now().isoformat(),
                iterations=self.state["iterations"],
                recommendations=["Maximum iterations reached, review progress"]
            )
        
        final_result.artifacts = [test_file, source_file]
        return final_result

    def init(self, project_name: str) -> DCAEResult:
        """
        Initialize new DCAE project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            DCAEResult with initialization results
        """
        self.state["phase"] = "init"
        
        # Create project structure
        project_dir = self.project_root / project_name
        tests_dir = project_dir / "tests"
        src_dir = project_dir / "src"
        
        tests_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        (tests_dir / "__init__.py").touch()
        (src_dir / "__init__.py").touch()
        
        # Create pytest.ini
        pytest_ini = project_dir / "pytest.ini"
        pytest_ini.write_text("""[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
""")
        
        # Create conftest.py
        conftest = tests_dir / "conftest.py"
        conftest.write_text("""\"\"\"Pytest configuration and fixtures.\"\"\"
import pytest


@pytest.fixture
def sample_data():
    \"\"\"Sample data fixture.\"\"\"
    return {"key": "value"}
""")
        
        artifacts = [
            str(project_dir / "tests"),
            str(project_dir / "src"),
            str(pytest_ini),
            str(conftest)
        ]
        
        return DCAEResult(
            status="success",
            phase="init",
            timestamp=datetime.now().isoformat(),
            artifacts=artifacts,
            recommendations=[
                "Start with 'dcae design' to create your first test",
                "Follow TDD cycle: Red → Green → Refactor",
                "Write one test at a time"
            ]
        )

    def status(self) -> DCAEResult:
        """
        Get current DCAE state.
        
        Returns:
            DCAEResult with current state
        """
        return DCAEResult(
            status="success",
            phase=self.state["phase"],
            timestamp=datetime.now().isoformat(),
            iterations=self.state["iterations"],
            artifacts=[
                self.state.get("test_file", ""),
                self.state.get("source_file", "")
            ]
        )
