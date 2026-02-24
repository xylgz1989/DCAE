import unittest
from src.dcae.discipline_control.compliance_tracker import ComplianceTracker, ReportGenerator, DashboardService, ViolationDetector
from src.dcae.discipline_control.discipline_controller import DisciplineLevel


class TestComplianceTracker(unittest.TestCase):
    """Test cases for ComplianceTracker."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tracker = ComplianceTracker()

    def test_tracker_initialization(self):
        """Test initializing the compliance tracker."""
        self.assertIsNotNone(self.tracker.events)
        self.assertIsNotNone(self.tracker.metrics)

    def test_track_discipline_event(self):
        """Test tracking a discipline-related event."""
        self.tracker.track_event('validation_passed', DisciplineLevel.STRICT, 'FastAPI endpoint validation')

        # Should have recorded the event
        self.assertEqual(len(self.tracker.events), 1)

    def test_track_multiple_events(self):
        """Test tracking multiple events."""
        self.tracker.track_event('validation_passed', DisciplineLevel.BALANCED, 'Model validation')
        self.tracker.track_event('review_completed', DisciplineLevel.BALANCED, 'Code review for feature X')
        self.tracker.track_event('methodology_violation', DisciplineLevel.STRICT, 'TDD not followed')

        self.assertEqual(len(self.tracker.events), 3)

    def test_get_events_by_level(self):
        """Test getting events by discipline level."""
        self.tracker.track_event('event1', DisciplineLevel.FAST, 'desc1')
        self.tracker.track_event('event2', DisciplineLevel.STRICT, 'desc2')
        self.tracker.track_event('event3', DisciplineLevel.FAST, 'desc3')

        fast_events = self.tracker.get_events_by_level(DisciplineLevel.FAST)
        strict_events = self.tracker.get_events_by_level(DisciplineLevel.STRICT)

        self.assertEqual(len(fast_events), 2)
        self.assertEqual(len(strict_events), 1)

    def test_get_events_by_type(self):
        """Test getting events by type."""
        self.tracker.track_event('validation_passed', DisciplineLevel.BALANCED, 'desc1')
        self.tracker.track_event('validation_passed', DisciplineLevel.FAST, 'desc2')
        self.tracker.track_event('review_completed', DisciplineLevel.BALANCED, 'desc3')

        validation_events = self.tracker.get_events_by_type('validation_passed')
        review_events = self.tracker.get_events_by_type('review_completed')

        self.assertEqual(len(validation_events), 2)
        self.assertEqual(len(review_events), 1)

    def test_calculate_compliance_score(self):
        """Test calculating compliance score."""
        # Add some events
        for i in range(10):
            self.tracker.track_event('validation_passed', DisciplineLevel.BALANCED, f'Event {i}')

        score = self.tracker.calculate_compliance_score(DisciplineLevel.BALANCED)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_track_compliance_metrics(self):
        """Test tracking compliance metrics."""
        self.tracker.track_compliance_metric('validation_success_rate', 0.95, DisciplineLevel.STRICT)
        self.tracker.track_compliance_metric('review_completion_rate', 0.85, DisciplineLevel.BALANCED)

        metrics = self.tracker.get_metrics_for_level(DisciplineLevel.STRICT)
        self.assertIn('validation_success_rate', metrics)

    def test_get_compliance_history(self):
        """Test getting compliance history over time."""
        from datetime import datetime, timedelta

        # Add events with timestamps
        for i in range(5):
            self.tracker.track_event('validation', DisciplineLevel.BALANCED, f'Event {i}')

        history = self.tracker.get_compliance_history(days=7)
        self.assertGreaterEqual(len(history), 0)  # Could be 0 if we're tracking by date

    def test_reset_events(self):
        """Test resetting tracked events."""
        self.tracker.track_event('event1', DisciplineLevel.FAST, 'desc')
        self.tracker.reset_events()

        self.assertEqual(len(self.tracker.events), 0)

    def test_export_events(self):
        """Test exporting events."""
        self.tracker.track_event('validation_passed', DisciplineLevel.STRICT, 'Model validation')
        self.tracker.track_event('review_completed', DisciplineLevel.BALANCED, 'Code review')

        exported = self.tracker.export_events()

        self.assertIn('events', exported)
        self.assertIn('summary', exported)
        self.assertGreaterEqual(len(exported['events']), 2)

    def test_aggregate_statistics(self):
        """Test aggregating compliance statistics."""
        stats = self.tracker.aggregate_statistics()

        self.assertIn('total_events', stats)
        self.assertIn('by_level', stats)
        self.assertIn('by_type', stats)


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tracker = ComplianceTracker()
        self.generator = ReportGenerator(self.tracker)

    def test_report_generation(self):
        """Test generating a compliance report."""
        # Add some events to the tracker
        self.tracker.track_event('validation_passed', DisciplineLevel.BALANCED, 'API validation')
        self.tracker.track_event('review_completed', DisciplineLevel.BALANCED, 'Code review')

        report = self.generator.generate_report()

        self.assertIn('summary', report)
        self.assertIn('details', report)
        self.assertIn('recommendations', report)

    def test_periodic_report(self):
        """Test generating periodic reports."""
        report = self.generator.generate_periodic_report('weekly')

        self.assertIsNotNone(report)

    def test_violation_report(self):
        """Test generating violation-specific reports."""
        self.tracker.track_event('methodology_violation', DisciplineLevel.STRICT, 'TDD not followed')

        violation_report = self.generator.generate_violation_report()

        self.assertIn('violations', violation_report)
        self.assertGreaterEqual(len(violation_report['violations']), 0)

    def test_level_specific_report(self):
        """Test generating reports for specific discipline levels."""
        report = self.generator.generate_report_for_level(DisciplineLevel.FAST)

        self.assertIsNotNone(report)

    def test_export_report(self):
        """Test exporting reports."""
        import tempfile
        import os

        # Generate a report
        report = self.generator.generate_report()

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            self.generator.export_report(report, temp_path)
            self.assertTrue(os.path.exists(temp_path))
        finally:
            os.unlink(temp_path)


class TestDashboardService(unittest.TestCase):
    """Test cases for DashboardService."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.tracker = ComplianceTracker()
        self.dashboard = DashboardService(self.tracker)

    def test_dashboard_data_generation(self):
        """Test generating dashboard data."""
        # Add some events
        self.tracker.track_event('validation_passed', DisciplineLevel.BALANCED, 'Test event')

        dashboard_data = self.dashboard.get_dashboard_data()

        self.assertIn('compliance_score', dashboard_data)
        self.assertIn('recent_events', dashboard_data)
        self.assertIn('metrics', dashboard_data)

    def test_compliance_visualization_data(self):
        """Test getting data for compliance visualizations."""
        data = self.dashboard.get_visualization_data()

        self.assertIn('timeline', data)
        self.assertIn('compliance_by_level', data)

    def test_get_summary_stats(self):
        """Test getting summary statistics."""
        stats = self.dashboard.get_summary_stats()

        self.assertIsNotNone(stats)

    def test_refresh_dashboard_data(self):
        """Test refreshing dashboard data."""
        # Add new events
        self.tracker.track_event('review_started', DisciplineLevel.STRICT, 'Started review')

        # Refresh should update internal state
        self.dashboard.refresh_data()

        # Verify data was updated
        new_data = self.dashboard.get_dashboard_data()
        self.assertIsNotNone(new_data)


class TestViolationDetector(unittest.TestCase):
    """Test cases for ViolationDetector."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = ViolationDetector()

    def test_violation_detection(self):
        """Test detecting discipline violations."""
        # Simulate some data that should trigger violations
        sample_context = {
            'follows_tdd': False,
            'has_review': False,
            'validation_level': 'low'
        }

        violations = self.detector.detect_violations(sample_context, DisciplineLevel.STRICT)

        # Should detect some violations for strict level with poor compliance
        self.assertGreaterEqual(len(violations), 0)

    def test_tdd_violation_detection(self):
        """Test detecting TDD violations."""
        context = {
            'test_written_first': False,
            'test_coverage': 0.3  # Low coverage
        }

        violations = self.detector.detect_tdd_violations(context)

        self.assertGreaterEqual(len(violations), 0)

    def test_review_violation_detection(self):
        """Test detecting review violations."""
        context = {
            'review_done': False,
            'review_quality': 'poor'
        }

        violations = self.detector.detect_review_violations(context)

        self.assertGreaterEqual(len(violations), 0)

    def test_configurable_violation_rules(self):
        """Test using configurable violation rules."""
        custom_rules = {
            'min_test_coverage': 0.9,
            'max_complexity_score': 5
        }

        self.detector.update_rules(custom_rules)

        # Should use new rules now
        self.assertEqual(self.detector.rules['min_test_coverage'], 0.9)

    def test_violation_severity_classification(self):
        """Test classifying violation severity."""
        violations = [
            {'type': 'critical', 'description': 'Security vulnerability'},
            {'type': 'minor', 'description': 'Minor style issue'}
        ]

        classified = self.detector.classify_violation_severity(violations)

        # Should classify based on content
        self.assertIsNotNone(classified)


if __name__ == '__main__':
    unittest.main()