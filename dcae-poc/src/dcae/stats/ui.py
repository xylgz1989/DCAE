"""Simple console-based dashboard UI for performance statistics."""

from datetime import datetime, timedelta
from typing import Dict, List

from .dashboard import PerformanceDashboard
from .models import AggregateStatistics


class ConsoleDashboardUI:
    """Console-based UI for displaying performance statistics."""

    def __init__(self, dashboard: PerformanceDashboard):
        """
        Initialize the console dashboard UI.

        Args:
            dashboard: PerformanceDashboard instance to get statistics from
        """
        self.dashboard = dashboard

    def display_summary_stats(self, days: int = 7):
        """
        Display a summary of statistics for the last N days.

        Args:
            days: Number of days to look back (default 7)
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        print(f"\nDCAE Performance Summary (Last {days} days)")
        print("=" * 50)

        # Get aggregate statistics
        aggregate = self.dashboard.get_aggregate_statistics(start_date, end_date)

        print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"Total Operations: {aggregate.total_operations}")
        print(f"Successful: {aggregate.successful_operations} ({aggregate.success_rate:.1f}%)")
        print(f"Failed: {aggregate.failed_operations}")
        print(f"Average Duration: {aggregate.avg_duration_ms:.2f} ms")
        print(f"Total Tokens Used: {aggregate.total_tokens_used:,}")
        print(f"Total API Calls: {aggregate.total_api_calls:,}")

        print("\nOperations by Type:")
        for op_type, count in aggregate.operations_by_type.items():
            success_rate = aggregate.success_rates_by_type.get(op_type, 0.0)
            print(f"  - {op_type.value.replace('_', ' ').title()}: {count} ({success_rate:.1f}% success)")

        print("\nResource Usage per Operation:")
        print(f"  - Average Tokens: {aggregate.avg_tokens_per_operation:.1f}")
        print(f"  - Min Duration: {aggregate.min_duration_ms:.2f} ms")
        print(f"  - Max Duration: {aggregate.max_duration_ms:.2f} ms")
        print(f"  - Total Duration: {aggregate.total_duration_ms:.2f} ms")

    def display_project_breakdown(self, days: int = 7):
        """
        Display statistics broken down by project.

        Args:
            days: Number of days to look back (default 7)
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        print(f"\nProject Breakdown (Last {days} days)")
        print("=" * 50)

        # Get top projects
        top_projects = self.dashboard.get_top_projects(start_date, end_date)

        if not top_projects:
            print("No projects found in this period.")
            return

        for project_id, op_count in top_projects:
            print(f"- Project: {project_id}")
            print(f"  Operations: {op_count}")

            # Get detailed stats for this project
            project_stats = self.dashboard.get_project_statistics(project_id, start_date, end_date)
            print(f"  Success Rate: {project_stats.success_rate:.1f}%")
            print(f"  Avg Duration: {project_stats.avg_duration_ms:.2f} ms")
            print()

    def display_recent_activity(self, limit: int = 10):
        """
        Display recent operations.

        Args:
            limit: Maximum number of operations to show (default 10)
        """
        print(f"\nRecent Activity (Last {limit} operations)")
        print("=" * 50)

        recent_ops = self.dashboard.get_recent_operations(limit)

        if not recent_ops:
            print("No recent operations found.")
            return

        for i, stat in enumerate(recent_ops, 1):
            status_icon = "[SUCCESS]" if stat.success else "[FAILED]"
            duration = stat.calculate_duration()

            print(f"{i}. {status_icon} {stat.operation_type.value.replace('_', ' ').title()}")
            print(f"   Name: {stat.operation_name}")
            if stat.project_id:
                print(f"   Project: {stat.project_id}")
            print(f"   Started: {stat.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Duration: {duration:.2f} ms")
            print(f"   Tokens: {stat.tokens_used:,}")
            if not stat.success and stat.error_message:
                print(f"   Error: {stat.error_message[:50]}...")
            print()

    def display_system_health(self):
        """Display overall system health."""
        print("\nSystem Health")
        print("=" * 50)

        health = self.dashboard.get_health_status()

        status_map = {
            "healthy": "HEALTHY",
            "degraded": "DEGRADED",
            "unhealthy": "UNHEALTHY"
        }

        status = health.get("system_status", "unknown")
        status_text = status_map.get(status, "UNKNOWN")

        print(f"Status: {status_text}")
        print(f"Last 24 Hours:")
        print(f"  - Total Operations: {health.get('total_operations_24h', 0)}")
        print(f"  - Successful: {health.get('successful_operations_24h', 0)}")
        print(f"  - Failed: {health.get('failed_operations_24h', 0)}")
        print(f"  - Success Rate: {health.get('success_rate_24h', 0):.1f}%")
        print(f"  - Avg Duration: {health.get('average_duration_ms', 0):.2f} ms")

        print("\nOperations by Type (24h):")
        ops_by_type = health.get("operations_by_type", {})
        for op_type, count in ops_by_type.items():
            print(f"  - {op_type.replace('_', ' ').title()}: {count}")

    def display_trend_analysis(self, days: int = 7):
        """
        Display trend analysis for operations.

        Args:
            days: Number of days to analyze (default 7)
        """
        print(f"\nTrend Analysis (Last {days} days)")
        print("=" * 50)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get all operations for the period
        all_stats = self.dashboard.get_statistics_by_date_range(start_date, end_date)

        if not all_stats:
            print("No data available for trend analysis.")
            return

        # Group by day
        daily_stats = {}
        for stat in all_stats:
            day = stat.start_time.date()
            if day not in daily_stats:
                daily_stats[day] = {"total": 0, "success": 0, "fail": 0, "tokens": 0}

            daily_stats[day]["total"] += 1
            if stat.success:
                daily_stats[day]["success"] += 1
            else:
                daily_stats[day]["fail"] += 1
            daily_stats[day]["tokens"] += stat.tokens_used

        # Display trend data
        sorted_days = sorted(daily_stats.keys(), reverse=True)
        for day in sorted_days:
            stats = daily_stats[day]
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0

            print(f"{day}: {stats['total']} ops, {success_rate:.1f}% success, {stats['tokens']:,} tokens")

    def display_dashboard(self, days: int = 7):
        """
        Display the complete dashboard.

        Args:
            days: Number of days to analyze (default 7)
        """
        self.display_summary_stats(days)
        self.display_recent_activity()
        self.display_project_breakdown(days)
        self.display_system_health()
        self.display_trend_analysis(days)

        print("\n" + "=" * 50)
        print("Dashboard refresh complete!")
        print("=" * 50)