"""Module for tracking compliance with discipline settings."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json


@dataclass
class ComplianceEvent:
    """An event related to discipline compliance."""
    event_type: str
    discipline_level: str
    description: str
    timestamp: str
    severity: str = "medium"


class ComplianceTracker:
    """Tracks discipline-related events and compliance metrics."""

    def __init__(self):
        """Initialize the compliance tracker."""
        self.events: List[ComplianceEvent] = []
        self.metrics: Dict[str, float] = {}
        self.compliance_scores: Dict[str, float] = {}

    def track_event(self, event_type: str, discipline_level: 'DisciplineLevel', description: str, severity: str = "medium"):
        """
        Track a discipline-related event.

        Args:
            event_type: Type of event (e.g., 'validation_passed', 'review_completed')
            discipline_level: The discipline level during the event
            description: Description of the event
            severity: Severity of the event
        """
        timestamp = datetime.now().isoformat()
        event = ComplianceEvent(
            event_type=event_type,
            discipline_level=discipline_level.value,
            description=description,
            timestamp=timestamp,
            severity=severity
        )
        self.events.append(event)

    def get_events_by_level(self, discipline_level: 'DisciplineLevel') -> List[ComplianceEvent]:
        """
        Get events for a specific discipline level.

        Args:
            discipline_level: The discipline level to filter by

        Returns:
            List of events for the discipline level
        """
        return [event for event in self.events if event.discipline_level == discipline_level.value]

    def get_events_by_type(self, event_type: str) -> List[ComplianceEvent]:
        """
        Get events of a specific type.

        Args:
            event_type: The event type to filter by

        Returns:
            List of events of the specified type
        """
        return [event for event in self.events if event.event_type == event_type]

    def calculate_compliance_score(self, discipline_level: 'DisciplineLevel') -> float:
        """
        Calculate compliance score for a discipline level.

        Args:
            discipline_level: The discipline level to calculate score for

        Returns:
            Compliance score between 0 and 1
        """
        level_events = self.get_events_by_level(discipline_level)

        if not level_events:
            return 1.0  # Perfect compliance if no events to judge

        total_events = len(level_events)
        positive_events = len([e for e in level_events if e.event_type not in ['methodology_violation', 'validation_failed']])

        return positive_events / total_events if total_events > 0 else 1.0

    def track_compliance_metric(self, metric_name: str, value: float, discipline_level: 'DisciplineLevel'):
        """
        Track a specific compliance metric.

        Args:
            metric_name: Name of the metric
            value: Value of the metric
            discipline_level: The discipline level for this metric
        """
        key = f"{metric_name}_{discipline_level.value}"
        self.metrics[key] = value

    def get_metrics_for_level(self, discipline_level: 'DisciplineLevel') -> Dict[str, float]:
        """
        Get all metrics for a specific discipline level.

        Args:
            discipline_level: The discipline level to get metrics for

        Returns:
            Dictionary of metrics for the level
        """
        level_metrics = {}
        for key, value in self.metrics.items():
            if key.endswith(f"_{discipline_level.value}"):
                metric_name = key.replace(f"_{discipline_level.value}", "")
                level_metrics[metric_name] = value
        return level_metrics

    def get_compliance_history(self, days: int = 30) -> List[ComplianceEvent]:
        """
        Get compliance history for the specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of events from the specified time period
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()

        return [event for event in self.events if event.timestamp >= cutoff_iso]

    def reset_events(self):
        """Reset all tracked events."""
        self.events.clear()

    def export_events(self) -> Dict[str, Any]:
        """
        Export events in a structured format.

        Returns:
            Dictionary containing exported events and summary
        """
        return {
            'events': [
                {
                    'type': event.event_type,
                    'level': event.discipline_level,
                    'description': event.description,
                    'timestamp': event.timestamp,
                    'severity': event.severity
                }
                for event in self.events
            ],
            'summary': {
                'total_events': len(self.events),
                'by_level': {
                    level_value: len([e for e in self.events if e.discipline_level == level_value])
                    for level_value in ['fast', 'balanced', 'strict']
                },
                'by_type': {
                    etype: len(self.get_events_by_type(etype))
                    for etype in set(e.event_type for e in self.events)
                }
            }
        }

    def aggregate_statistics(self) -> Dict[str, Any]:
        """
        Aggregate compliance statistics.

        Returns:
            Dictionary containing aggregated statistics
        """
        from collections import Counter

        total_events = len(self.events)
        events_by_level = Counter(e.discipline_level for e in self.events)
        events_by_type = Counter(e.event_type for e in self.events)

        # Create mock discipline levels for calculation
        class MockDisciplineLevel:
            def __init__(self, value):
                self.value = value

        compliance_scores = {}
        for level_value in ['fast', 'balanced', 'strict']:
            mock_level = MockDisciplineLevel(level_value)
            compliance_scores[level_value] = self.calculate_compliance_score(mock_level)  # type: ignore

        return {
            'total_events': total_events,
            'by_level': dict(events_by_level),
            'by_type': dict(events_by_type),
            'compliance_scores': compliance_scores,
            'time_range': {
                'start': min((e.timestamp for e in self.events), default=None),
                'end': max((e.timestamp for e in self.events), default=None)
            } if self.events else {}
        }


class ReportGenerator:
    """Generates compliance reports based on tracked events."""

    def __init__(self, compliance_tracker: ComplianceTracker):
        """
        Initialize the report generator.

        Args:
            compliance_tracker: The tracker to generate reports from
        """
        self.tracker = compliance_tracker

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report.

        Returns:
            Dictionary containing the report
        """
        stats = self.tracker.aggregate_statistics()

        return {
            'summary': {
                'total_events': stats['total_events'],
                'compliance_score': stats['compliance_scores'],
                'report_generated_at': datetime.now().isoformat()
            },
            'details': {
                'events_by_level': stats['by_level'],
                'events_by_type': stats['by_type']
            },
            'recommendations': self._generate_recommendations(),
            'period': 'current'
        }

    def generate_periodic_report(self, period: str = 'weekly') -> Dict[str, Any]:
        """
        Generate a periodic compliance report.

        Args:
            period: Time period for the report ('daily', 'weekly', 'monthly')

        Returns:
            Dictionary containing the periodic report
        """
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30}
        days = days_map.get(period, 7)

        events = self.tracker.get_compliance_history(days)

        return {
            'summary': {
                'period': period,
                'events_count': len(events),
                'date_range': {
                    'start': events[0].timestamp if events else None,
                    'end': events[-1].timestamp if events else None
                } if events else {}
            },
            'details': [
                {
                    'type': event.event_type,
                    'level': event.discipline_level,
                    'description': event.description,
                    'timestamp': event.timestamp
                }
                for event in events
            ],
            'period': period
        }

    def generate_violation_report(self) -> Dict[str, Any]:
        """
        Generate a report focusing on violations.

        Returns:
            Dictionary containing violation report
        """
        violations = [e for e in self.tracker.events if 'violation' in e.event_type.lower()]

        # Count violations by level
        by_level = {}
        for level_value in ['fast', 'balanced', 'strict']:
            by_level[level_value] = len([v for v in violations if v.discipline_level == level_value])

        return {
            'violations': [
                {
                    'type': v.event_type,
                    'level': v.discipline_level,
                    'description': v.description,
                    'timestamp': v.timestamp,
                    'severity': v.severity
                }
                for v in violations
            ],
            'total_violations': len(violations),
            'by_level': by_level,
            'summary': 'Violation-focused report'
        }

    def generate_report_for_level(self, discipline_level: 'DisciplineLevel') -> Dict[str, Any]:
        """
        Generate a report for a specific discipline level.

        Args:
            discipline_level: The discipline level to generate report for

        Returns:
            Dictionary containing the level-specific report
        """
        level_events = self.tracker.get_events_by_level(discipline_level)
        compliance_score = self.tracker.calculate_compliance_score(discipline_level)

        return {
            'level': discipline_level.value,
            'compliance_score': compliance_score,
            'events': [
                {
                    'type': e.event_type,
                    'description': e.description,
                    'timestamp': e.timestamp,
                    'severity': e.severity
                }
                for e in level_events
            ],
            'event_count': len(level_events)
        }

    def export_report(self, report: Dict[str, Any], filepath: str):
        """
        Export a report to a file.

        Args:
            report: The report to export
            filepath: Path to export the report to
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on compliance data."""
        # Simple recommendation logic based on violations
        violations = [e for e in self.tracker.events if 'violation' in e.event_type.lower()]

        recommendations = []
        if violations:
            recommendations.append(f"Address {len(violations)} violations detected")

        # Add more recommendations based on metrics
        if not recommendations:
            recommendations.append("No immediate issues detected. Maintain current practices.")

        return recommendations


class DashboardService:
    """Provides dashboard data for compliance visualization."""

    def __init__(self, compliance_tracker: ComplianceTracker):
        """
        Initialize the dashboard service.

        Args:
            compliance_tracker: The tracker to get data from
        """
        self.tracker = compliance_tracker

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for the compliance dashboard.

        Returns:
            Dictionary containing dashboard data
        """
        stats = self.tracker.aggregate_statistics()
        recent_events = self.tracker.get_compliance_history(days=7)[-10:]  # Last 10 events

        return {
            'compliance_score': stats['compliance_scores'],
            'recent_events': [
                {
                    'type': e.event_type,
                    'description': e.description,
                    'timestamp': e.timestamp
                }
                for e in recent_events
            ],
            'metrics': self.tracker.metrics,
            'summary': {
                'total_events': stats['total_events'],
                'active_violations': len([e for e in self.tracker.events if 'violation' in e.event_type.lower()])
            }
        }

    def get_visualization_data(self) -> Dict[str, Any]:
        """
        Get data formatted for visualization.

        Returns:
            Dictionary containing visualization-ready data
        """
        # Group events by date for timeline
        from collections import defaultdict

        timeline_data = defaultdict(int)
        for event in self.tracker.events:
            date = event.timestamp.split('T')[0]  # Get date part
            timeline_data[date] += 1

        # Create mock discipline levels for calculation
        class MockDisciplineLevel:
            def __init__(self, value):
                self.value = value

        compliance_by_level = {}
        for level_value in ['fast', 'balanced', 'strict']:
            mock_level = MockDisciplineLevel(level_value)
            compliance_by_level[level_value] = self.tracker.calculate_compliance_score(mock_level)  # type: ignore

        return {
            'timeline': dict(timeline_data),
            'compliance_by_level': compliance_by_level,
            'event_types': list(set(e.event_type for e in self.tracker.events))
        }

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for quick display.

        Returns:
            Dictionary containing summary statistics
        """
        stats = self.tracker.aggregate_statistics()

        return {
            'total_events': stats['total_events'],
            'compliance_score': sum(stats['compliance_scores'].values()) / len(stats['compliance_scores']) if stats['compliance_scores'] else 0,
            'active_violations': len([e for e in self.tracker.events if 'violation' in e.event_type.lower()]),
            'last_updated': datetime.now().isoformat()
        }

    def refresh_data(self):
        """Refresh dashboard data if needed."""
        # In a real implementation, this might refresh cached data
        # For now, just a placeholder
        pass


class ViolationDetector:
    """Detects violations of discipline settings."""

    def __init__(self):
        """Initialize the violation detector."""
        self.rules = {
            'min_test_coverage': 0.8,
            'max_complexity_score': 8,
            'required_reviews': 1,
            'response_time_threshold': 24  # hours
        }

    def detect_violations(self, context: Dict[str, Any], discipline_level: 'DisciplineLevel') -> List[Dict[str, str]]:
        """
        Detect violations based on context and discipline level.

        Args:
            context: Context information to check for violations
            discipline_level: The discipline level to check against

        Returns:
            List of detected violations
        """
        violations = []

        # Check test coverage
        if context.get('test_coverage', 1.0) < self.rules['min_test_coverage']:
            violations.append({
                'type': 'test_coverage',
                'description': f"Test coverage {context.get('test_coverage', 0):.2f} is below required threshold",
                'severity': 'high'
            })

        # Check if methodology was followed (e.g. TDD)
        if discipline_level.value == 'strict' and not context.get('follows_tdd', True):
            violations.append({
                'type': 'methodology',
                'description': 'Strict discipline level requires TDD methodology compliance',
                'severity': 'high'
            })

        return violations

    def detect_tdd_violations(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Specifically detect TDD violations.

        Args:
            context: Context information about TDD compliance

        Returns:
            List of TDD violations
        """
        violations = []

        if not context.get('test_written_first', False):
            violations.append({
                'type': 'tdd_sequence',
                'description': 'Implementation written before test',
                'severity': 'high'
            })

        if context.get('test_coverage', 1.0) < self.rules['min_test_coverage']:
            violations.append({
                'type': 'tdd_coverage',
                'description': f'Test coverage {context.get("test_coverage", 0):.2f} below threshold',
                'severity': 'medium'
            })

        return violations

    def detect_review_violations(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Specifically detect review violations.

        Args:
            context: Context information about review compliance

        Returns:
            List of review violations
        """
        violations = []

        if not context.get('review_done', False):
            violations.append({
                'type': 'missing_review',
                'description': 'Required code review was not performed',
                'severity': 'high'
            })

        if context.get('review_quality', 'good') == 'poor':
            violations.append({
                'type': 'quality_issue',
                'description': 'Review quality was rated as poor',
                'severity': 'medium'
            })

        return violations

    def update_rules(self, new_rules: Dict[str, Any]):
        """
        Update violation detection rules.

        Args:
            new_rules: New rules to apply
        """
        self.rules.update(new_rules)

    def classify_violation_severity(self, violations: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Classify severity of violations.

        Args:
            violations: List of violations to classify

        Returns:
            List of violations with updated severity classification
        """
        # This is a simplified classifier - in practice, you'd have more sophisticated rules
        for violation in violations:
            if 'security' in violation['description'].lower():
                violation['severity'] = 'critical'
            elif 'test' in violation['description'].lower() or 'coverage' in violation['description'].lower():
                violation['severity'] = 'high'
            elif 'performance' in violation['description'].lower():
                violation['severity'] = 'medium'
            elif 'style' in violation['description'].lower():
                violation['severity'] = 'low'

        return violations