"""
Unit tests for the Requirements Conflict Detector module.
Tests cover all the functionality defined in story 2-4.
"""

import pytest
from src.requirements_conflict_detector import (
    RequirementsConflictDetector,
    ConflictType,
    IssueSeverity,
    DetectedIssue,
    ConflictDetectionResult
)


class TestRequirementsConflictDetector:
    """Test class for RequirementsConflictDetector functionality."""

    def test_detect_contradictions_positive(self):
        """Test that contradictions in requirements are properly detected."""
        detector = RequirementsConflictDetector()

        # Sample requirements with contradiction
        requirements_text = """
        REQ-001: The system shall allow users to modify their profile information at any time.
        REQ-002: The system shall prevent users from modifying their profile information after initial setup.
        """

        result = detector.detect_conflicts(requirements_text)

        # Find contradiction issues
        contradiction_issues = [issue for issue in result.issues
                               if issue.conflict_type == ConflictType.CONTRADICTION]

        assert len(contradiction_issues) > 0
        assert contradiction_issues[0].severity == IssueSeverity.HIGH
        assert "contradicts" in contradiction_issues[0].description.lower()

    def test_detect_contradictions_negative(self):
        """Test that non-contradictory requirements don't trigger contradiction detection."""
        detector = RequirementsConflictDetector()

        # Sample requirements without contradiction
        requirements_text = """
        REQ-001: The system shall allow users to modify their profile information at any time.
        REQ-002: The system shall provide a dashboard for users to view their profile.
        """

        result = detector.detect_conflicts(requirements_text)

        # Find contradiction issues
        contradiction_issues = [issue for issue in result.issues
                               if issue.conflict_type == ConflictType.CONTRADICTION]

        assert len(contradiction_issues) == 0

    def test_detect_inconsistencies_positive(self):
        """Test that inconsistencies in requirements are properly detected."""
        detector = RequirementsConflictDetector()

        # Sample requirements with inconsistency
        requirements_text = """
        REQ-001: The user authentication module shall use MySQL database for storing credentials.
        REQ-002: The user authentication module shall use PostgreSQL database for storing credentials.
        """

        result = detector.detect_conflicts(requirements_text)

        # Find inconsistency issues
        inconsistency_issues = [issue for issue in result.issues
                               if issue.conflict_type == ConflictType.INCONSISTENCY]

        assert len(inconsistency_issues) > 0
        assert inconsistency_issues[0].severity == IssueSeverity.MEDIUM

    def test_detect_ambiguities_positive(self):
        """Test that ambiguous requirements are properly detected."""
        detector = RequirementsConflictDetector()

        # Sample requirements with ambiguous terms
        requirements_text = """
        REQ-001: The system should respond quickly to user requests.
        REQ-002: Users may access the system sometimes.
        """

        result = detector.detect_conflicts(requirements_text)

        # Find ambiguity issues
        ambiguity_issues = [issue for issue in result.issues
                           if issue.conflict_type == ConflictType.AMBIGUITY]

        assert len(ambiguity_issues) > 0
        assert all(issue.severity in [IssueSeverity.MEDIUM, IssueSeverity.LOW]
                  for issue in ambiguity_issues)

    def test_detect_ambiguities_negative(self):
        """Test that unambiguous requirements don't trigger ambiguity detection."""
        detector = RequirementsConflictDetector()

        # Sample requirements without ambiguous terms
        requirements_text = """
        REQ-001: The system shall respond to user requests within 2 seconds.
        REQ-002: Users may access the system between 8AM and 8PM.
        """

        result = detector.detect_conflicts(requirements_text)

        # Find ambiguity issues
        ambiguity_issues = [issue for issue in result.issues
                           if issue.conflict_type == ConflictType.AMBIGUITY]

        assert len(ambiguity_issues) == 0

    def test_detect_feasibility_issues_positive(self):
        """Test that unfeasible requirements are properly detected."""
        detector = RequirementsConflictDetector()

        # Sample requirements with feasibility concerns
        requirements_text = """
        REQ-001: The system shall respond to all requests immediately.
        REQ-002: The system shall provide 100% uptime.
        """

        result = detector.detect_conflicts(requirements_text)

        # Find feasibility issues
        feasibility_issues = [issue for issue in result.issues
                             if issue.conflict_type == ConflictType.FEASIBILITY]

        assert len(feasibility_issues) > 0
        assert all(issue.severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL]
                  for issue in feasibility_issues)

    def test_detect_duplicate_requirements(self):
        """Test that duplicate requirements are detected."""
        detector = RequirementsConflictDetector()

        # Sample requirements with duplicates
        requirements_text = """
        REQ-001: The system shall authenticate users with username and password.
        REQ-002: The system shall authenticate users with username and password.
        """

        result = detector.detect_conflicts(requirements_text)

        # Find duplicate issues
        duplicate_issues = [issue for issue in result.issues
                           if issue.conflict_type == ConflictType.DUPLICATE_REQUIREMENT]

        assert len(duplicate_issues) > 0
        assert duplicate_issues[0].severity == IssueSeverity.LOW

    def test_issue_classification_by_severity(self):
        """Test that issues are properly classified by severity."""
        detector = RequirementsConflictDetector()

        # Sample requirements with different issue types and expected severities
        requirements_text = """
        REQ-001: The system shall respond to all requests immediately.  # Feasibility - High
        REQ-002: The system should be user friendly.                   # Ambiguity - Medium
        REQ-003: The system shall provide 100% uptime.                # Feasibility - High
        """

        result = detector.detect_conflicts(requirements_text)

        # Verify that each issue has the expected severity level
        severity_counts = {}
        for issue in result.issues:
            severity = issue.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Should have at least HIGH and MEDIUM severity issues
        assert severity_counts.get('high', 0) > 0
        assert severity_counts.get('medium', 0) > 0

    def test_empty_requirements(self):
        """Test that empty requirements text produces no issues."""
        detector = RequirementsConflictDetector()

        requirements_text = ""

        result = detector.detect_conflicts(requirements_text)

        assert len(result.issues) == 0
        assert all(count == 0 for count in result.summary.values())

    def test_parsing_requirements_basic(self):
        """Test that requirements are properly parsed from text."""
        detector = RequirementsConflictDetector()

        requirements_text = """
        REQ-001: The system shall authenticate users.
        REQ-002: The system shall store user profiles.
        """

        # We can't directly test the parsing method since it's private,
        # but we can infer it worked by ensuring the conflict detection ran
        result = detector.detect_conflicts(requirements_text)

        # At minimum, the parsing should not crash and return a valid result
        assert isinstance(result, ConflictDetectionResult)
        assert hasattr(result, 'issues')
        assert hasattr(result, 'summary')

    def test_generate_summary(self):
        """Test that the summary generation works correctly."""
        detector = RequirementsConflictDetector()

        # Create requirements that will generate various types of issues
        requirements_text = """
        REQ-001: The system shall respond immediately to all requests.  # Feasibility issue
        REQ-002: The system should be user friendly.                   # Ambiguity issue
        """

        result = detector.detect_conflicts(requirements_text)

        # Verify summary has correct structure
        assert isinstance(result.summary, dict)
        assert all(key in ['critical', 'high', 'medium', 'low'] for key in result.summary.keys())

        # At least some issues should be counted
        total_in_summary = sum(result.summary.values())
        total_actual_issues = len(result.issues)
        assert total_in_summary == total_actual_issues

    def test_confidence_scoring(self):
        """Test that detected issues have appropriate confidence scores."""
        detector = RequirementsConflictDetector()

        # Create requirements that should generate clear issues
        requirements_text = """
        REQ-001: The system shall respond immediately to all requests.  # Clear feasibility issue
        """

        result = detector.detect_conflicts(requirements_text)

        if result.issues:
            # All issues should have a confidence score between 0 and 1
            for issue in result.issues:
                assert 0.0 <= issue.confidence_score <= 1.0

    def test_parse_requirements_various_formats(self):
        """Test that the parser handles various requirement formats."""
        detector = RequirementsConflictDetector()

        # Different requirement formats
        requirements_text = """
        # Standard format
        REQ-001: The system shall authenticate users.

        # Alternative format
        Requirement 1.2: The system shall store user data.

        # Numbered list format
        1.3 The system shall validate input.

        # Imperative statement (without explicit ID)
        The system shall encrypt data transmission.
        """

        result = detector.detect_conflicts(requirements_text)

        # The parsing should handle all these formats
        assert isinstance(result, ConflictDetectionResult)

    def test_no_false_positives_simple(self):
        """Test that basic, well-formed requirements don't trigger false positives."""
        detector = RequirementsConflictDetector()

        # Well-formed, non-conflicting requirements
        requirements_text = """
        REQ-001: The system shall authenticate users with username and password.
        REQ-002: The system shall log user authentication attempts.
        REQ-003: The system shall store user profile information.
        """

        result = detector.detect_conflicts(requirements_text)

        # Should not detect any issues with these clear, non-conflicting requirements
        assert len(result.issues) == 0

    def test_issue_attributes_complete(self):
        """Test that all required attributes are present in detected issues."""
        detector = RequirementsConflictDetector()

        requirements_text = """
        REQ-001: The system shall respond immediately.  # Feasibility issue
        """

        result = detector.detect_conflicts(requirements_text)

        if result.issues:
            issue = result.issues[0]

            # Check all required attributes exist
            assert hasattr(issue, 'id')
            assert hasattr(issue, 'title')
            assert hasattr(issue, 'description')
            assert hasattr(issue, 'conflict_type')
            assert hasattr(issue, 'severity')
            assert hasattr(issue, 'affected_requirements')
            assert hasattr(issue, 'confidence_score')
            assert hasattr(issue, 'suggested_resolution')

            # Check that important attributes are not empty
            assert issue.id is not None
            assert issue.title is not None
            assert issue.description is not None
            assert issue.conflict_type is not None
            assert issue.severity is not None
            assert issue.affected_requirements is not None
            assert issue.confidence_score is not None
            assert issue.suggested_resolution is not None


class TestReportGeneration:
    """Test the report generation functionality."""

    def test_generate_conflict_report(self):
        """Test that conflict reports can be generated."""
        from src.requirements_conflict_detector import generate_conflict_report

        detector = RequirementsConflictDetector()

        # Create sample requirements with some conflicts
        requirements_text = """
        REQ-001: The system shall respond immediately to all requests.
        """

        result = detector.detect_conflicts(requirements_text)
        report = generate_conflict_report(result)

        # The report should be a non-empty string
        assert isinstance(report, str)
        assert len(report) > 0
        assert "# Requirements Conflict Detection Report" in report

    def test_report_includes_summary(self):
        """Test that reports include summary information."""
        from src.requirements_conflict_detector import generate_conflict_report

        detector = RequirementsConflictDetector()

        # Create requirements with conflicts
        requirements_text = """
        REQ-001: The system shall respond immediately to all requests.  # Feasibility
        """

        result = detector.detect_conflicts(requirements_text)
        report = generate_conflict_report(result)

        # Report should include summary section
        assert "## Summary" in report
        assert "Total Issues Found:" in report

    def test_report_includes_detailed_issues(self):
        """Test that reports include detailed issue information."""
        from src.requirements_conflict_detector import generate_conflict_report

        detector = RequirementsConflictDetector()

        # Create requirements with conflicts
        requirements_text = """
        REQ-001: The system shall respond immediately to all requests.  # Feasibility
        """

        result = detector.detect_conflicts(requirements_text)
        report = generate_conflict_report(result)

        # Report should include detailed issues
        assert "## Detailed Issues" in report
        if result.issues:
            assert "### Issue 1:" in report
            assert "- **Type:**" in report
            assert "- **Severity:**" in report


if __name__ == "__main__":
    pytest.main([__file__])