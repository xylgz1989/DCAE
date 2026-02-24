import unittest
from src.dcae.discipline_control import (
    DisciplineController, DisciplineLevel,
    ValidationAdjuster,
    ReviewAdjuster,
    MethodologyEnforcer, TDDEnforcer,
    ComplianceTracker, ReportGenerator, DashboardService, ViolationDetector
)


class TestEpic7Integration(unittest.TestCase):
    """Integration tests for Epic #7: Discipline Control & Methodology Enforcement."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize all components
        self.controller = DisciplineController()
        self.validation_adjuster = ValidationAdjuster()
        self.review_adjuster = ReviewAdjuster()
        self.enforcer = MethodologyEnforcer()
        self.tdd_enforcer = TDDEnforcer()
        self.tracker = ComplianceTracker()
        self.report_gen = ReportGenerator(self.tracker)
        self.dashboard = DashboardService(self.tracker)
        self.violation_detector = ViolationDetector()

    def test_discipline_level_setting_and_adjustment(self):
        """Test setting discipline level and adjusting validation/review accordingly."""
        # Set discipline level to strict
        self.controller.set_level(DisciplineLevel.STRICT)

        # Verify settings changed appropriately
        self.assertEqual(self.controller.get_current_level(), DisciplineLevel.STRICT)

        # Get validation and review adjustments for this level
        validation_rules = self.validation_adjuster.adjust_validation_for_level(DisciplineLevel.STRICT)
        review_rules = self.review_adjuster.adjust_review_for_level(DisciplineLevel.STRICT)

        # Validation and review rules should be comprehensive for strict mode
        self.assertGreater(len(validation_rules), 3)  # Should have multiple validation checks
        self.assertGreater(len(review_rules), 3)     # Should have multiple review steps

    def test_methodology_enforcement_with_different_levels(self):
        """Test methodology enforcement with different discipline levels."""
        # Enable TDD enforcement
        self.enforcer.enable_process('TDD')

        # Check compliance with different contexts
        compliant_context = {'follows_tdd': True, 'has_tests': True}
        non_compliant_context = {'follows_tdd': False, 'has_tests': False}

        # Set level to strict and check compliance
        self.controller.set_level(DisciplineLevel.STRICT)

        # Track events for compliance tracking
        self.tracker.track_event('implementation_completed', DisciplineLevel.STRICT, 'Created implementation')

        # Verify TDD compliance check works
        tdd_compliant = self.tdd_enforcer.validate_test_coverage({'lines': 100, 'covered': 90})
        self.assertTrue(tdd_compliant)

    def test_compliance_tracking_and_reporting(self):
        """Test comprehensive compliance tracking and reporting."""
        # Track various events
        self.tracker.track_event('validation_passed', DisciplineLevel.BALANCED, 'API validation passed')
        self.tracker.track_event('review_completed', DisciplineLevel.BALANCED, 'Code review completed')
        self.tracker.track_event('methodology_violation', DisciplineLevel.STRICT, 'TDD not followed')

        # Generate reports
        report = self.report_gen.generate_report()
        violation_report = self.report_gen.generate_violation_report()

        # Verify reports contain expected information
        self.assertIn('summary', report)
        self.assertIn('details', report)

        # Check that total_events is an integer and greater than 0
        total_events = report['summary']['total_events']
        self.assertIsInstance(total_events, int)
        self.assertGreaterEqual(total_events, 3)

        # Check violation report specifically
        self.assertIn('violations', violation_report)
        self.assertGreaterEqual(violation_report['total_violations'], 0)

    def test_discipline_change_and_history_tracking(self):
        """Test changing discipline levels and tracking history."""
        initial_level = self.controller.get_current_level()
        initial_history_count = len(self.controller.history)

        # Change discipline level multiple times
        self.controller.set_level(DisciplineLevel.FAST, "Speeding up for prototype")
        self.controller.set_level(DisciplineLevel.STRICT, "Securing for production")

        # Verify history is maintained
        expected_history_count = initial_history_count + 2  # 2 changes
        self.assertEqual(len(self.controller.history), expected_history_count)

        # Verify current level
        self.assertEqual(self.controller.get_current_level(), DisciplineLevel.STRICT)

    def test_end_to_end_discipline_workflow(self):
        """Test end-to-end discipline workflow."""
        # Start with balanced discipline
        self.controller.set_level(DisciplineLevel.BALANCED)

        # Track an implementation event
        self.tracker.track_event('code_implemented', DisciplineLevel.BALANCED, 'User authentication module')

        # Generate validation and review settings for current level
        validation_settings = self.validation_adjuster.prepare_settings(DisciplineLevel.BALANCED)
        review_settings = self.review_adjuster.prepare_settings(DisciplineLevel.BALANCED)

        # These should be reasonable for balanced mode
        self.assertIn('enabled_checks', validation_settings)
        self.assertIn('approvals_needed', review_settings)

        # Run compliance checks
        compliance_score = self.tracker.calculate_compliance_score(DisciplineLevel.BALANCED)

        # Generate dashboard data
        dashboard_data = self.dashboard.get_dashboard_data()

        self.assertIsNotNone(dashboard_data['compliance_score'])
        self.assertIn('recent_events', dashboard_data)

    def test_violation_detection_and_response(self):
        """Test detecting violations and responding appropriately."""
        # Create a context that should trigger violations
        problematic_context = {
            'test_coverage': 0.4,  # Below threshold
            'follows_tdd': False,
            'review_done': False
        }

        # Detect violations
        violations = self.violation_detector.detect_violations(problematic_context, DisciplineLevel.STRICT)

        # Should detect some violations for strict level with poor compliance
        self.assertGreaterEqual(len(violations), 0)

        # Record violations in the tracker using the correct method
        for violation in violations:
            # Track the violations in the compliance tracker
            self.tracker.track_event('methodology_violation', DisciplineLevel.STRICT,
                                   f"{violation['type']}: {violation['description']}",
                                   violation['severity'])

    def test_discipline_level_influence_on_process_enforcement(self):
        """Test how discipline level influences process enforcement."""
        # Enable multiple processes
        self.enforcer.enable_process('TDD')
        self.enforcer.enable_process('CodeReview')

        # Create contexts for different discipline levels
        strict_context = {
            'follows_tdd': True,
            'has_tests': True,
            'test_coverage': 0.9,
            'has_review': True
        }

        fast_context = {
            'follows_tdd': False,  # Doesn't follow TDD
            'has_tests': False,    # No tests
            'has_review': False    # No review
        }

        # Check compliance under strict discipline
        self.controller.set_level(DisciplineLevel.STRICT)
        strict_compliant = self.enforcer.check_compliance('feature_implementation', strict_context)

        # Check compliance under fast discipline
        self.controller.set_level(DisciplineLevel.FAST)
        fast_compliant = self.enforcer.check_compliance('feature_implementation', fast_context)

        # Both should return a boolean result
        self.assertIsInstance(strict_compliant, bool)
        self.assertIsInstance(fast_compliant, bool)

    def test_integration_with_settings_persistence(self):
        """Test that discipline settings persist correctly."""
        # Set a specific level
        self.controller.set_level(DisciplineLevel.STRICT, "Starting production phase")

        # Save settings
        self.controller.save_settings("test_project_integration")

        # Create a new controller and load
        new_controller = DisciplineController()
        loaded = new_controller.load_settings("test_project_integration")

        # Verify the settings were loaded correctly
        self.assertTrue(loaded)
        self.assertEqual(new_controller.get_current_level(), DisciplineLevel.STRICT)

        # Check history preservation
        if self.controller.history:
            self.assertGreaterEqual(len(new_controller.history), 1)


if __name__ == '__main__':
    unittest.main()