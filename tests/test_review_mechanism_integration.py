"""
Comprehensive Tests for the Review Mechanism

This module contains integration tests for the entire review mechanism,
including all components working together.
"""
import sys
import os
# Add the src directory to the Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path
import json
from datetime import datetime

from dcae.review_orchestrator import ReviewMechanismOrchestrator, ReviewContextManager, ReviewScheduler, ReviewCoordinator
from dcae.unified_review import UnifiedReviewInterface
from dcae.correlation_engine import ReviewCorrelationEngine, Finding
from dcae.workflow_integration import DevelopmentWorkflowIntegrator, CIPipelineIntegrator, TeamCollaborationIntegrator
from dcae.reporting_analytics import UnifiedReportingSystem, HistoricalReviewTracker, ReviewSnapshot


class TestReviewMechanismIntegration(unittest.TestCase):
    """Integration tests for the entire review mechanism."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        # Create a sample project structure
        self.sample_file = self.project_path / "sample.py"
        sample_code = '''
def problematic_function():
    """A function with multiple issues."""
    password = "hardcoded_password"  # Security issue
    result = []
    for i in range(10):
        for j in range(10):  # Performance issue: nested loops
            result.append(i * j)
    return result
'''
        with open(self.sample_file, 'w') as f:
            f.write(sample_code)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_full_review_process_integration(self):
        """Test the full review process from start to finish."""
        # Initialize the unified review interface
        reviewer = UnifiedReviewInterface(str(self.project_path))

        # Run comprehensive review
        results = reviewer.run_comprehensive_review(
            target_path=str(self.sample_file)
        )

        # Verify results structure
        self.assertIsNotNone(results)
        self.assertIn('summary', results)
        self.assertIn('findings', results)
        self.assertGreaterEqual(len(results['findings']), 1)  # Should have at least one finding

        # Verify summary contains expected keys
        summary = results['summary']
        self.assertIn('total_findings', summary)
        self.assertIn('findings_by_severity', summary)
        self.assertIn('findings_by_category', summary)
        self.assertGreaterEqual(summary['total_findings'], 1)

    def test_review_orchestration_components_integration(self):
        """Test integration between orchestration components."""
        # Initialize orchestrator
        orchestrator = ReviewMechanismOrchestrator()

        # Create a simple configuration
        config = {
            "reviews": [
                {
                    "type": "generated_output_review",
                    "params": {
                        "project_path": str(self.project_path),
                        "target_path": str(self.sample_file)
                    },
                    "priority": 2
                }
            ]
        }

        # Run comprehensive review
        results = orchestrator.run_comprehensive_review(config)

        # Verify results
        self.assertIsNotNone(results)
        self.assertIn('summary', results)
        self.assertIn('findings', results)

    def test_correlation_engine_integration(self):
        """Test correlation engine with findings from different sources."""
        # Create sample findings
        finding1 = Finding(
            id="finding_1",
            module="generated_output_review",
            category="security",
            severity="high",
            file_path=str(self.sample_file),
            line_number=3,
            issue_description="Hardcoded credential",
            recommendation="Use environment variables",
            code_snippet='password = "hardcoded_password"'
        )

        finding2 = Finding(
            id="finding_2",
            module="rules_engine",
            category="security",
            severity="high",
            file_path=str(self.sample_file),
            line_number=3,
            issue_description="Hardcoded password assignment",
            recommendation="Secure configuration",
            code_snippet='password = "hardcoded_password"'
        )

        finding3 = Finding(
            id="finding_3",
            module="generated_output_review",
            category="performance",
            severity="medium",
            file_path=str(self.sample_file),
            line_number=5,
            issue_description="Nested loops detected",
            recommendation="Optimize algorithm",
            code_snippet="for i in range(10):\n    for j in range(10):"
        )

        # Initialize correlation engine
        engine = ReviewCorrelationEngine()

        # Add findings
        engine.add_findings([finding1, finding2, finding3])

        # Find correlations
        correlations = engine.find_correlations()

        # Verify correlations were found
        self.assertGreaterEqual(len(correlations), 1)

        # Check for specific correlations
        same_file_correlations = [c for c in correlations if c.correlation_type.value == "same_file"]
        same_issue_correlations = [c for c in correlations if c.correlation_type.value == "same_issue_type"]

        # Should have at least one same_file correlation (findings 1 and 2 are in same file)
        self.assertGreaterEqual(len(same_file_correlations), 1)

    def test_reporting_system_integration(self):
        """Test the reporting system with sample results."""
        # Initialize historical tracker
        tracker = HistoricalReviewTracker(str(self.project_path / "test_history.db"))

        # Create sample snapshot
        snapshot = ReviewSnapshot(
            timestamp=datetime.now(),
            project_path=str(self.project_path),
            target_path=str(self.sample_file),
            total_findings=5,
            findings_by_severity={"critical": 0, "high": 2, "medium": 2, "low": 1},
            findings_by_category={"security": 2, "performance": 2, "code_quality": 1},
            overall_score=80.0,
            review_duration=10.5,
            metadata={"test_run": True}
        )

        # Save snapshot
        success = tracker.save_review_snapshot(snapshot)
        self.assertTrue(success)

        # Retrieve and verify
        historical_data = tracker.get_historical_data(str(self.project_path))
        self.assertEqual(len(historical_data), 1)
        self.assertEqual(historical_data[0].total_findings, 5)

        # Initialize reporting system
        reporting_system = UnifiedReportingSystem(tracker)

        # Create sample results for report generation
        sample_results = {
            "summary": {
                "total_findings": 5,
                "overall_score": 80.0,
                "findings_by_severity": {"critical": 0, "high": 2, "medium": 2, "low": 1},
                "findings_by_category": {"security": 2, "performance": 2, "code_quality": 1}
            },
            "review_timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "target_path": str(self.sample_file),
            "duration": 10.5
        }

        # Generate reports
        outputs = reporting_system.generate_current_report(
            sample_results,
            report_formats=["json", "txt"],
            output_dir=str(self.project_path)
        )

        # Verify outputs
        self.assertIn("json", outputs)
        self.assertIn("txt", outputs)

        # Check that files were created
        for fmt, path in outputs.items():
            self.assertTrue(Path(path).exists())


class TestWorkflowIntegration(unittest.TestCase):
    """Test workflow integration components."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_development_workflow_integrator(self):
        """Test development workflow integration."""
        # Initialize integrator
        integrator = DevelopmentWorkflowIntegrator(str(self.project_path))

        # Test that it can find git root (even though none exists in temp dir)
        # This should handle the case gracefully
        is_git_repo = integrator.is_git_repository()
        # This might be False depending on temp directory structure

        # Test editor integration setup
        success = integrator.integrate_with_editor("vscode")
        self.assertTrue(success)

        # Verify VSCode files were created
        vscode_dir = self.project_path / ".vscode"
        self.assertTrue(vscode_dir.exists())
        self.assertTrue((vscode_dir / "settings.json").exists())
        self.assertTrue((vscode_dir / "tasks.json").exists())

    def test_ci_pipeline_integrator(self):
        """Test CI pipeline integration."""
        # Initialize integrator
        integrator = CIPipelineIntegrator(str(self.project_path))

        # Test GitHub Actions setup
        success = integrator.setup_github_actions()
        self.assertTrue(success)

        # Verify GitHub Actions file was created
        github_dir = self.project_path / ".github" / "workflows"
        workflow_files = list(github_dir.glob("*.yml"))
        self.assertGreaterEqual(len(workflow_files), 1)

        # Test GitLab CI setup
        success = integrator.setup_gitlab_ci()
        self.assertTrue(success)

        # Verify GitLab CI file was created
        gitlab_ci_file = self.project_path / ".gitlab-ci.yml"
        self.assertTrue(gitlab_ci_file.exists())

    def test_team_collaboration_integrator(self):
        """Test team collaboration integration."""
        # Initialize integrator
        integrator = TeamCollaborationIntegrator(str(self.project_path))

        # Test notification system setup
        config = integrator.setup_notification_system(
            channels=["console"],
            recipients=["test@example.com"]
        )

        # Verify configuration
        self.assertIn("channels", config)
        self.assertIn("recipients", config)
        self.assertEqual(config["channels"], ["console"])

        # Create sample results for collaboration report
        sample_results = {
            "summary": {
                "total_findings": 3,
                "overall_score": 85.0,
                "findings_by_severity": {"high": 1, "medium": 1, "low": 1},
                "findings_by_category": {"security": 1, "performance": 1, "code_quality": 1}
            },
            "review_timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "target_path": "src/",
            "duration": 15.0
        }

        # Generate collaboration report
        report_path = integrator.generate_collaboration_report(
            sample_results,
            output_format="markdown"
        )

        # Verify report was created
        self.assertTrue(Path(report_path).exists())


class TestPerformanceAndOptimization(unittest.TestCase):
    """Tests for performance and optimization aspects."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        # Create several sample files to test with
        for i in range(5):
            sample_file = self.project_path / f"sample_{i}.py"
            sample_code = f'''
def function_{i}():
    """Sample function {i}."""
    password = "hardcoded_password_{i}"  # Security issue
    result = []
    for j in range(10):
        for k in range(10):  # Performance issue
            result.append(j * k)
    return result
'''
            with open(sample_file, 'w') as f:
                f.write(sample_code)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_review_performance_under_load(self):
        """Test performance when reviewing multiple files."""
        import time

        # Initialize unified review interface
        reviewer = UnifiedReviewInterface(str(self.project_path))

        # Measure time to run comprehensive review
        start_time = time.time()
        results = reviewer.run_comprehensive_review(
            target_path=str(self.project_path)
        )
        end_time = time.time()

        duration = end_time - start_time

        # Verify results were generated
        self.assertIsNotNone(results)
        self.assertIn('summary', results)
        self.assertGreaterEqual(results['summary']['total_findings'], 1)

        # Verify performance is reasonable (less than 30 seconds for this test)
        self.assertLess(duration, 30.0, f"Review took too long: {duration:.2f}s")

    def test_correlation_engine_performance(self):
        """Test correlation engine performance with multiple findings."""
        import time

        # Create multiple findings to test correlation performance
        findings = []
        for i in range(20):
            finding = Finding(
                id=f"finding_{i}",
                module="test_module",
                category="security" if i % 2 == 0 else "performance",
                severity="high" if i < 5 else "medium",
                file_path=f"file_{i % 5}.py",
                line_number=i + 1,
                issue_description=f"Issue number {i}",
                recommendation="Fix the issue",
                code_snippet=f"code_snippet_{i}"
            )
            findings.append(finding)

        # Initialize correlation engine
        engine = ReviewCorrelationEngine()

        # Add findings
        engine.add_findings(findings)

        # Measure correlation time
        start_time = time.time()
        correlations = engine.find_correlations()
        end_time = time.time()

        correlation_time = end_time - start_time

        # Verify correlations were found
        self.assertGreaterEqual(len(correlations), 0)  # May not have correlations in test data

        # Verify performance is reasonable
        self.assertLess(correlation_time, 10.0, f"Correlation took too long: {correlation_time:.2f}s")


class TestConfigurationAndUserExperience(unittest.TestCase):
    """Tests for configuration and user experience aspects."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

        # Create a sample project file
        self.sample_file = self.project_path / "sample.py"
        sample_code = '''
def sample_function():
    """A sample function."""
    return "hello world"
'''
        with open(self.sample_file, 'w') as f:
            f.write(sample_code)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_configuration_loading_and_saving(self):
        """Test configuration loading and saving functionality."""
        # Initialize unified review interface
        reviewer = UnifiedReviewInterface(str(self.project_path))

        # Export configuration
        export_path = str(self.project_path / "test_config.json")
        success = reviewer.export_configuration(export_path)
        self.assertTrue(success)

        # Verify export file exists and has content
        self.assertTrue(Path(export_path).exists())

        # Check that it's valid JSON
        with open(export_path, 'r') as f:
            config_data = json.load(f)

        self.assertIn("version", config_data)
        self.assertIn("default_config", config_data)

        # Import configuration to new instance
        reviewer2 = UnifiedReviewInterface(str(self.project_path))
        import_success = reviewer2.import_configuration(export_path)
        self.assertTrue(import_success)

    def test_different_review_types(self):
        """Test different types of reviews."""
        # Initialize unified review interface
        reviewer = UnifiedReviewInterface(str(self.project_path))

        # Test specific reviews
        specific_results = reviewer.run_specific_reviews(
            review_types=["generated_output"],
            target_path=str(self.sample_file)
        )

        self.assertIn("generated_output", specific_results)
        self.assertIn("report", specific_results["generated_output"])

        # Test comprehensive review
        comprehensive_results = reviewer.run_comprehensive_review(
            target_path=str(self.sample_file)
        )

        self.assertIsNotNone(comprehensive_results)
        self.assertIn("summary", comprehensive_results)

    def test_report_generation_various_formats(self):
        """Test report generation in various formats."""
        # Initialize historical tracker
        tracker = HistoricalReviewTracker(str(self.project_path / "test_history.db"))

        # Initialize reporting system
        reporting_system = UnifiedReportingSystem(tracker)

        # Create sample results
        sample_results = {
            "summary": {
                "total_findings": 2,
                "overall_score": 90.0,
                "findings_by_severity": {"low": 2},
                "findings_by_category": {"code_quality": 2}
            },
            "review_timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "target_path": str(self.sample_file),
            "duration": 5.0
        }

        # Generate reports in all supported formats
        formats = ["html", "json", "csv", "txt"]
        outputs = reporting_system.generate_current_report(
            sample_results,
            report_formats=formats,
            output_dir=str(self.project_path)
        )

        # Verify all formats were generated
        for fmt in formats:
            self.assertIn(fmt, outputs, f"Format {fmt} was not generated")
            output_path = outputs[fmt]
            self.assertTrue(Path(output_path).exists(), f"Output file for {fmt} does not exist: {output_path}")


def run_integration_tests():
    """Run all integration tests."""
    # Create a test suite
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTest(unittest.makeSuite(TestReviewMechanismIntegration))
    suite.addTest(unittest.makeSuite(TestWorkflowIntegration))
    suite.addTest(unittest.makeSuite(TestPerformanceAndOptimization))
    suite.addTest(unittest.makeSuite(TestConfigurationAndUserExperience))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """Main function to run tests."""
    print("DCAE Review Mechanism - Integration Tests")
    print("="*50)

    success = run_integration_tests()

    if success:
        print("\n✅ All integration tests passed!")
        return 0
    else:
        print("\n❌ Some integration tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())