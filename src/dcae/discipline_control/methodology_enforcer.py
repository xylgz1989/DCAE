"""Module for enforcing development methodologies."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ViolationRecord:
    """Record of a methodology violation."""
    methodology: str
    description: str
    timestamp: str
    severity: str = "medium"


class MethodologyEnforcer:
    """Enforces specific development methodologies like TDD."""

    def __init__(self):
        """Initialize the methodology enforcer."""
        self.active_enforcements: Dict[str, Any] = {}
        self.violations: List[ViolationRecord] = []

    def enable_process(self, process_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Enable enforcement of a specific process.

        Args:
            process_name: Name of the process to enforce
            config: Configuration options for the process
        """
        self.active_enforcements[process_name] = config or {}

    def disable_process(self, process_name: str):
        """
        Disable enforcement of a specific process.

        Args:
            process_name: Name of the process to disable
        """
        if process_name in self.active_enforcements:
            del self.active_enforcements[process_name]

    def check_compliance(self, operation: str, context: Dict[str, Any]) -> bool:
        """
        Check if an operation complies with active methodologies.

        Args:
            operation: The operation being performed
            context: Context information about the operation

        Returns:
            True if the operation is compliant, False otherwise
        """
        # By default, assume compliant unless we find violations
        is_compliant = True

        for methodology in self.active_enforcements.keys():
            if methodology == 'TDD':
                # For TDD, check if tests exist for implementations
                if not context.get('follows_tdd', True):
                    is_compliant = False
                    self.record_violation('TDD', f'Operation {operation} does not follow TDD practices')
            elif methodology == 'CodeReview':
                # For code review, check if review was performed
                if not context.get('has_review', True):
                    is_compliant = False
                    self.record_violation('CodeReview', f'Operation {operation} bypassed code review')
            # Add more methodology checks as needed

        return is_compliant

    def is_operation_allowed(self, operation: str, context: Dict[str, Any]) -> bool:
        """
        Check if an operation is allowed based on methodology compliance.

        Args:
            operation: The operation being performed
            context: Context information about the operation

        Returns:
            True if the operation is allowed, False otherwise
        """
        return self.check_compliance(operation, context)

    def record_violation(self, methodology: str, description: str, severity: str = "medium"):
        """
        Record a methodology violation.

        Args:
            methodology: The methodology that was violated
            description: Description of the violation
            severity: Severity of the violation
        """
        timestamp = datetime.now().isoformat()
        violation = ViolationRecord(
            methodology=methodology,
            description=description,
            timestamp=timestamp,
            severity=severity
        )
        self.violations.append(violation)

    def generate_violation_report(self) -> Dict[str, Any]:
        """
        Generate a report of all violations.

        Returns:
            Dictionary containing violation information
        """
        return {
            'violation_count': len(self.violations),
            'violations': [
                {
                    'methodology': v.methodology,
                    'description': v.description,
                    'timestamp': v.timestamp,
                    'severity': v.severity
                }
                for v in self.violations
            ],
            'by_methodology': self._get_violations_by_methodology()
        }

    def _get_violations_by_methodology(self) -> Dict[str, int]:
        """Group violations by methodology."""
        counts = {}
        for violation in self.violations:
            counts[violation.methodology] = counts.get(violation.methodology, 0) + 1
        return counts

    def reset_violations(self):
        """Reset the violations list."""
        self.violations.clear()

    def configure_methodologies(self, config: Dict[str, Dict[str, Any]]):
        """
        Configure multiple methodologies at once.

        Args:
            config: Configuration dictionary with methodology settings
        """
        for methodology, settings in config.items():
            self.enable_process(methodology, settings)


class TDDEnforcer(MethodologyEnforcer):
    """Specific enforcer for Test-Driven Development methodology."""

    def __init__(self):
        """Initialize the TDD enforcer."""
        super().__init__()
        self.tdd_rules = {
            'require_test_first': True,
            'min_test_coverage': 0.8,
            'test_naming_patterns': [r'.*test.*', r'.*_test', r'^test_.*', r'.*[Tt]est.*', r'.*spec.*', r'^spec_.*']
        }

    def validate_tdd_sequence(self, file_creation_order: List[str]) -> bool:
        """
        Validate that files were created in TDD sequence (test before implementation).

        Args:
            file_creation_order: Order in which files were created

        Returns:
            True if the sequence follows TDD principles
        """
        # Find the first occurrence of any test file
        first_test_index = -1
        first_impl_index = -1

        for i, filename in enumerate(file_creation_order):
            if self.validate_test_filename(filename):
                if first_test_index == -1:
                    first_test_index = i
            else:
                if first_impl_index == -1 and first_test_index == -1:  # Only track first implementation if it comes before any test
                    first_impl_index = i

        # TDD is followed if we find a test file and it comes before any implementation file
        # Or if there are only test files
        if first_test_index != -1 and (first_impl_index == -1 or first_test_index < first_impl_index):
            return True
        elif first_test_index == -1 and first_impl_index == -1:  # No files qualify as test or impl
            return True  # Cannot violate TDD if no relevant files
        else:
            return False  # Implementation came before test

    def validate_test_filename(self, filename: str) -> bool:
        """
        Check if a filename suggests it's a test file.

        Args:
            filename: Name of the file to check

        Returns:
            True if the filename suggests it's a test file
        """
        import re

        for pattern in self.tdd_rules['test_naming_patterns']:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        return False

    def validate_test_coverage(self, coverage_info: Dict[str, float]) -> bool:
        """
        Validate that test coverage meets requirements.

        Args:
            coverage_info: Dictionary containing coverage information

        Returns:
            True if coverage meets requirements
        """
        required_coverage = self.tdd_rules['min_test_coverage']
        actual_coverage = coverage_info.get('covered', 0) / max(coverage_info.get('lines', 1), 1)
        return actual_coverage >= required_coverage

    def get_enforcement_rules(self, discipline_level: 'DisciplineLevel') -> Dict[str, Any]:
        """
        Get TDD enforcement rules based on discipline level.

        Args:
            discipline_level: The discipline level to get rules for

        Returns:
            Dictionary of TDD enforcement rules for the discipline level
        """
        if discipline_level.value == 'fast':
            return {
                'required_tests': 1,  # Minimal requirement
                'coverage_threshold': 0.5,
                'review_required': False
            }
        elif discipline_level.value == 'balanced':
            return {
                'required_tests': 2,  # Moderate requirement
                'coverage_threshold': 0.75,
                'review_required': True
            }
        elif discipline_level.value == 'strict':
            return {
                'required_tests': 5,  # High requirement
                'coverage_threshold': 0.9,
                'review_required': True,
                'complexity_analysis': True
            }
        else:
            # Default to balanced
            return self.get_enforcement_rules(type(discipline_level).BALANCED)


class ProcessValidator:
    """Validates that processes are followed correctly."""

    def __init__(self):
        """Initialize the process validator."""
        self.process_rules = {
            'TDD': {
                'sequence': ['write_test', 'implement', 'refactor'],
                'requirements': {
                    'test_coverage': 0.8,
                    'review_before_merge': True
                }
            },
            'CodeReview': {
                'sequence': ['write_code', 'submit_for_review', 'address_feedback', 'approve', 'merge'],
                'requirements': {
                    'min_reviewers': 1,
                    'review_time_limit': 24  # hours
                }
            }
        }

    def validate_process(self, process_name: str, steps_taken: List[str]) -> bool:
        """
        Validate that a process was followed correctly.

        Args:
            process_name: Name of the process to validate
            steps_taken: Steps that were actually taken

        Returns:
            True if the process was followed correctly
        """
        if process_name not in self.process_rules:
            return True  # Unknown process - assume compliant

        required_sequence = self.process_rules[process_name]['sequence']

        # Check if all required steps are present
        for step in required_sequence:
            if step not in steps_taken:
                return False

        # Check if sequence is followed correctly (simplified)
        # Find indices of required steps in the taken steps
        step_indices = []
        for step in required_sequence:
            try:
                idx = steps_taken.index(step)
                step_indices.append(idx)
            except ValueError:
                return False  # Required step not found

        # Check that indices are in ascending order (meaning steps were done in order)
        return step_indices == sorted(step_indices)