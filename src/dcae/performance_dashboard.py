"""Module for displaying performance statistics dashboard."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .performance_statistics import StatisticsCollector, PerformanceStatistics, PerformanceRecord


class PerformanceDashboard:
    """Provides methods to format and display performance statistics."""

    def __init__(self, collector: StatisticsCollector = None):
        """
        Initialize the PerformanceDashboard.

        Args:
            collector: StatisticsCollector instance to use (default: global instance)
        """
        self.collector = collector or StatisticsCollector()

    def generate_summary_report(self, days: int = 30) -> str:
        """
        Generate a summary report of performance statistics.

        Args:
            days: Number of days to include in the report (default: 30)

        Returns:
            Formatted summary report as a string
        """
        stats = self.collector.get_statistics(days=days)

        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DCAE Performance Statistics Report")
        report_lines.append("=" * 60)

        if stats.total_operations == 0:
            report_lines.append("No operations recorded.")
            report_lines.append("=" * 60)
            return "\n".join(report_lines)

        # Date range
        if stats.start_date and stats.end_date:
            report_lines.append(f"Date Range: {stats.start_date.strftime('%Y-%m-%d')} to {stats.end_date.strftime('%Y-%m-%d')}")
            report_lines.append("")

        # Overall metrics
        report_lines.append("Overall Metrics:")
        report_lines.append(f"  Total Operations: {stats.total_operations}")
        report_lines.append(f"  Successful Operations: {stats.successful_operations}")
        report_lines.append(f"  Failed Operations: {stats.failed_operations}")
        report_lines.append(f"  Success Rate: {(stats.successful_operations / stats.total_operations * 100):.2f}%")
        report_lines.append(f"  Average Duration: {stats.average_duration:.2f}s")
        report_lines.append(f"  Total Duration: {stats.total_duration:.2f}s")
        report_lines.append("")

        # Operation type breakdown
        report_lines.append("Operations by Type:")
        for op_type, op_stats in stats.operation_types.items():
            avg_dur = op_stats['avg_duration']
            report_lines.append(f"  {op_type}: {op_stats['count']} ops ({op_stats['successful']} success, "
                              f"{op_stats['failed']} failed) - avg {avg_dur:.2f}s")
        report_lines.append("")

        # Project breakdown
        report_lines.append("Operations by Project:")
        for proj_name, proj_stats in stats.projects.items():
            avg_dur = proj_stats['avg_duration']
            report_lines.append(f"  {proj_name}: {proj_stats['count']} ops ({proj_stats['successful']} success, "
                              f"{proj_stats['failed']} failed) - avg {avg_dur:.2f}s")
        report_lines.append("")

        # Recent operations
        report_lines.append("Recent Operations:")
        for record in stats.recent_operations[-10:]:  # Show last 10 operations
            status = "SUCCESS" if record.success else "FAILED"
            report_lines.append(f"  {record.operation_type} in {record.project_name}: {record.duration_seconds:.2f}s [{status}]")

        report_lines.append("=" * 60)
        return "\n".join(report_lines)

    def generate_project_report(self, project_name: str) -> str:
        """
        Generate a detailed report for a specific project.

        Args:
            project_name: Name of the project to report on

        Returns:
            Formatted project report as a string
        """
        stats = self.collector.get_project_statistics(project_name)

        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"DCAE Performance Report for Project: {project_name}")
        report_lines.append("=" * 60)

        if stats.total_operations == 0:
            report_lines.append(f"No operations recorded for project '{project_name}'.")
            report_lines.append("=" * 60)
            return "\n".join(report_lines)

        # Date range
        if stats.start_date and stats.end_date:
            report_lines.append(f"Date Range: {stats.start_date.strftime('%Y-%m-%d')} to {stats.end_date.strftime('%Y-%m-%d')}")
            report_lines.append("")

        # Overall metrics for this project
        report_lines.append("Project Metrics:")
        report_lines.append(f"  Total Operations: {stats.total_operations}")
        report_lines.append(f"  Successful Operations: {stats.successful_operations}")
        report_lines.append(f"  Failed Operations: {stats.failed_operations}")
        report_lines.append(f"  Success Rate: {(stats.successful_operations / stats.total_operations * 100):.2f}%")
        report_lines.append(f"  Average Duration: {stats.average_duration:.2f}s")
        report_lines.append(f"  Total Duration: {stats.total_duration:.2f}s")
        report_lines.append("")

        # Operation type breakdown for this project
        report_lines.append("Operations by Type:")
        for op_type, op_stats in stats.operation_types.items():
            avg_dur = op_stats['avg_duration']
            report_lines.append(f"  {op_type}: {op_stats['count']} ops ({op_stats['successful']} success, "
                              f"{op_stats['failed']} failed) - avg {avg_dur:.2f}s")
        report_lines.append("")

        # Recent operations for this project
        report_lines.append("Recent Operations:")
        for record in stats.recent_operations[-10:]:  # Show last 10 operations
            status = "SUCCESS" if record.success else "FAILED"
            timestamp = record.start_time.strftime("%Y-%m-%d %H:%M:%S")
            report_lines.append(f"  [{timestamp}] {record.operation_type}: {record.duration_seconds:.2f}s [{status}]")

        report_lines.append("=" * 60)
        return "\n".join(report_lines)

    def get_top_slow_operations(self, top_n: int = 5, days: int = 30) -> List[PerformanceRecord]:
        """
        Get the slowest operations over the specified time period.

        Args:
            top_n: Number of slowest operations to return
            days: Number of days to look back

        Returns:
            List of the slowest PerformanceRecord objects
        """
        records = self.collector.get_statistics(days=days).recent_operations
        # Sort by duration descending and take top N
        sorted_records = sorted(records, key=lambda x: x.duration_seconds, reverse=True)
        return sorted_records[:top_n]

    def get_failure_rate_by_operation_type(self, days: int = 30) -> Dict[str, float]:
        """
        Get the failure rate for each operation type.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary mapping operation type to failure rate percentage
        """
        stats = self.collector.get_statistics(days=days)
        failure_rates = {}

        for op_type, op_stats in stats.operation_types.items():
            total_ops = op_stats['count']
            failed_ops = op_stats['failed']
            failure_rate = (failed_ops / total_ops * 100) if total_ops > 0 else 0
            failure_rates[op_type] = failure_rate

        return failure_rates

    def get_efficiency_trend(self, days: int = 30) -> Dict[str, float]:
        """
        Get efficiency trend by comparing early and recent operations.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with efficiency comparison data
        """
        all_records = self.collector.get_statistics(days=days).recent_operations

        if len(all_records) < 2:
            return {"message": "Insufficient data for trend analysis"}

        # Split records into first half and second half
        midpoint = len(all_records) // 2
        first_half = all_records[:midpoint]
        second_half = all_records[midpoint:]

        if not first_half or not second_half:
            return {"message": "Insufficient data for trend analysis"}

        # Calculate average durations
        first_avg = sum(r.duration_seconds for r in first_half) / len(first_half)
        second_avg = sum(r.duration_seconds for r in second_half) / len(second_half)

        improvement = ((first_avg - second_avg) / first_avg * 100) if first_avg > 0 else 0

        return {
            "first_period_avg_duration": first_avg,
            "second_period_avg_duration": second_avg,
            "improvement_percentage": improvement,
            "trend": "improving" if improvement > 0 else "degrading"
        }


def display_dashboard(days: int = 30):
    """
    Display the performance dashboard to the console.

    Args:
        days: Number of days to include in the report
    """
    dashboard = PerformanceDashboard()
    report = dashboard.generate_summary_report(days)
    print(report)


def display_project_dashboard(project_name: str):
    """
    Display the performance dashboard for a specific project.

    Args:
        project_name: Name of the project to display
    """
    dashboard = PerformanceDashboard()
    report = dashboard.generate_project_report(project_name)
    print(report)