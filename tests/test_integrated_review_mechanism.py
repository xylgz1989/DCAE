import os
import tempfile
import unittest
from pathlib import Path
import shutil

from src.dcae.integrated_review_mechanism import (
    ReviewOrchestrator,
    ReviewPhase,
    ReviewStatus,
    ReviewResult,
    ReviewConfiguration
)


class TestReviewOrchestrator(unittest.TestCase):
    """Test cases for the integrated review mechanism."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_orchestrator_initialization_without_specs(self):
        """Test initializing the orchestrator without specifications."""
        orchestrator = ReviewOrchestrator(self.project_path)

        self.assertEqual(orchestrator.project_path, Path(self.project_path))
        self.assertEqual(orchestrator.requirements_spec, {})
        self.assertEqual(orchestrator.architecture_spec, {})
        self.assertEqual(orchestrator.status, ReviewStatus.PENDING)

    def test_orchestrator_initialization_with_specs(self):
        """Test initializing the orchestrator with specifications."""
        requirements_spec = {
            "functional_requirements": [
                {"id": "REQ001", "title": "Test Requirement", "description": "A test requirement"}
            ]
        }
        architecture_spec = {
            "components": [
                {"name": "Test Component"}
            ]
        }

        orchestrator = ReviewOrchestrator(self.project_path, requirements_spec, architecture_spec)

        self.assertEqual(orchestrator.requirements_spec, requirements_spec)
        self.assertEqual(orchestrator.architecture_spec, architecture_spec)

    def test_configure_method(self):
        """Test configuring the review process."""
        orchestrator = ReviewOrchestrator(self.project_path)

        # Create a new configuration
        config = ReviewConfiguration()
        config.enable_security_review = False
        config.verbose_logging = False

        # Apply the configuration
        orchestrator.configure(config)

        # Check that the configuration was applied
        self.assertFalse(orchestrator.config.enable_security_review)
        self.assertFalse(orchestrator.config.verbose_logging)

    def test_run_complete_review_empty_project(self):
        """Test running a complete review on an empty project."""
        orchestrator = ReviewOrchestrator(self.project_path)

        # Run the complete review
        results = orchestrator.run_complete_review()

        # Should have completed at least initialization and completion phases
        self.assertGreaterEqual(len(results), 2)

        # Check that first phase is initialization
        if results:
            self.assertEqual(results[0].phase, ReviewPhase.INITIALIZATION)

        # Check that last phase is completion
        if len(results) >= 2:
            self.assertEqual(results[-1].phase, ReviewPhase.COMPLETION)

    def test_run_complete_review_with_issues(self):
        """Test running a complete review with files that have issues."""
        # Create a file with issues
        test_file = os.path.join(self.project_path, "risky.py")
        with open(test_file, 'w') as f:
            f.write("""
import pickle  # Security issue

def long_function():
    # Long function to trigger quality issue
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
    password = "hardcoded_secret"  # Security issue
    return x_val
""")

        orchestrator = ReviewOrchestrator(self.project_path)

        # Run the complete review
        results = orchestrator.run_complete_review()

        # Should have completed with multiple phases
        self.assertGreaterEqual(len(results), 2)

        # Check that some phases completed successfully
        completed_phases = [r for r in results if r.status == ReviewStatus.COMPLETED]
        self.assertGreaterEqual(len(completed_phases), 2)

    def test_get_overall_summary(self):
        """Test getting the overall summary."""
        orchestrator = ReviewOrchestrator(self.project_path)

        # Get summary before running any review
        summary = orchestrator.get_overall_summary()

        # Should have initial state information
        self.assertIn("status", summary)
        self.assertEqual(summary["status"], "no_results")

        # Run a minimal review to generate results
        results = orchestrator.run_complete_review()

        # Get summary after running review
        summary_after = orchestrator.get_overall_summary()

        # Should have more detailed information
        self.assertIn("overall_status", summary_after)
        self.assertIn("total_phases", summary_after)
        self.assertIn("completed_phases", summary_after)

    def test_export_results(self):
        """Test exporting the review results."""
        orchestrator = ReviewOrchestrator(self.project_path)

        # Run a review
        results = orchestrator.run_complete_review()

        # Export the results
        output_path = os.path.join(self.project_path, "review_export.json")
        orchestrator.export_results(output_path)

        # Verify file was created
        self.assertTrue(os.path.exists(output_path))

        # Verify file contains JSON data
        with open(output_path, 'r') as f:
            import json
            data = json.load(f)
            self.assertIn("summary", data)
            self.assertIn("results_by_phase", data)
            self.assertIn("project_path", data)

    def test_execute_individual_phases(self):
        """Test executing individual review phases."""
        orchestrator = ReviewOrchestrator(self.project_path)

        # Test initialization phase
        init_result = orchestrator._execute_initialization_phase()
        self.assertEqual(init_result.phase, ReviewPhase.INITIALIZATION)
        self.assertEqual(init_result.status, ReviewStatus.COMPLETED)

        # Test report generation phase
        report_result = orchestrator._execute_report_generation_phase()
        self.assertEqual(report_result.phase, ReviewPhase.REPORT_GENERATION)
        self.assertEqual(report_result.status, ReviewStatus.COMPLETED)


class TestReviewConfiguration(unittest.TestCase):
    """Test cases for review configuration components."""

    def test_review_configuration_defaults(self):
        """Test default review configuration."""
        config = ReviewConfiguration()

        # Check default values
        self.assertTrue(config.enable_static_analysis)
        self.assertTrue(config.enable_security_review)
        self.assertTrue(config.enable_performance_evaluation)
        self.assertTrue(config.enable_architecture_check)
        self.assertTrue(config.enable_requirements_verification)
        self.assertTrue(config.enable_issue_identification)
        self.assertEqual(config.max_execution_time, 3600)
        self.assertEqual(config.output_format, "json")
        self.assertTrue(config.verbose_logging)

    def test_review_configuration_custom(self):
        """Test custom review configuration."""
        config = ReviewConfiguration(
            enable_static_analysis=False,
            enable_security_review=False,
            max_execution_time=1800,
            output_format="xml",
            verbose_logging=False
        )

        self.assertFalse(config.enable_static_analysis)
        self.assertFalse(config.enable_security_review)
        self.assertEqual(config.max_execution_time, 1800)
        self.assertEqual(config.output_format, "xml")
        self.assertFalse(config.verbose_logging)


class TestReviewComponents(unittest.TestCase):
    """Test cases for individual review components."""

    def test_review_result_creation(self):
        """Test creating a review result."""
        result = ReviewResult(
            phase=ReviewPhase.INITIALIZATION,
            status=ReviewStatus.COMPLETED,
            findings=[{"type": "test", "message": "test message"}],
            metrics={"test_metric": 100},
            timestamp="2023-01-01T00:00:00",
            duration=1.0,
            details={"detail_key": "detail_value"}
        )

        self.assertEqual(result.phase, ReviewPhase.INITIALIZATION)
        self.assertEqual(result.status, ReviewStatus.COMPLETED)
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.metrics["test_metric"], 100)
        self.assertEqual(result.timestamp, "2023-01-01T00:00:00")
        self.assertEqual(result.duration, 1.0)
        self.assertEqual(result.details["detail_key"], "detail_value")

    def test_review_phase_enum(self):
        """Test the ReviewPhase enum values."""
        phases = [phase.value for phase in ReviewPhase]

        expected_phases = [
            "initialization",
            "static_analysis",
            "security_review",
            "performance_evaluation",
            "architecture_check",
            "requirements_verification",
            "issue_identification",
            "report_generation",
            "completion"
        ]

        for expected in expected_phases:
            self.assertIn(expected, phases)

    def test_review_status_enum(self):
        """Test the ReviewStatus enum values."""
        statuses = [status.value for status in ReviewStatus]

        expected_statuses = [
            "pending",
            "in_progress",
            "completed",
            "failed",
            "cancelled"
        ]

        for expected in expected_statuses:
            self.assertIn(expected, statuses)


if __name__ == '__main__':
    unittest.main()