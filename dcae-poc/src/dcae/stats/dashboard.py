"""Performance dashboard for aggregating and presenting DCAE statistics."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
from pathlib import Path
import json

from .models import PerformanceStatistics, AggregateStatistics, ExportData, OperationType


class PerformanceDashboard:
    """Class for aggregating and presenting performance statistics."""

    def __init__(self, storage_path: str = "./storage"):
        """
        Initialize the performance dashboard.

        Args:
            storage_path: Base path for retrieving statistics
        """
        self.storage_path = Path(storage_path)

    def get_statistics_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        project_id: Optional[str] = None
    ) -> List[PerformanceStatistics]:
        """
        Retrieve statistics within a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            project_id: Optional project ID to filter by

        Returns:
            List of PerformanceStatistics objects
        """
        # Format dates to match our storage structure (YYYY-MM-DD)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        all_stats = []

        # Iterate through days in the range
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            date_str = current_date.strftime("%Y-%m-%d")

            # Try to get statistics for this date
            date_path = self.storage_path / "stats" / date_str

            if date_path.exists():
                # List all statistic files for this date
                stat_files = list(date_path.glob("*.json"))

                for file_path in stat_files:
                    try:
                        # Load the statistic
                        with open(file_path, 'r', encoding='utf-8') as f:
                            stat_dict = json.load(f)

                        # Create PerformanceStatistics object
                        stat = PerformanceStatistics(**stat_dict)

                        # Filter by project if specified
                        if project_id and stat.project_id != project_id:
                            continue

                        # Check if stat falls within our time range
                        if start_date <= stat.start_time <= end_date:
                            all_stats.append(stat)

                    except Exception as e:
                        print(f"Warning: Could not load statistic from {file_path}: {e}")
                        continue

            # Move to next date
            current_date += timedelta(days=1)

        return all_stats

    def get_aggregate_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        project_id: Optional[str] = None,
        operation_types: Optional[List[OperationType]] = None
    ) -> AggregateStatistics:
        """
        Get aggregate statistics for a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            project_id: Optional project ID to filter by
            operation_types: Optional list of operation types to filter by

        Returns:
            AggregateStatistics object
        """
        all_stats = self.get_statistics_by_date_range(start_date, end_date, project_id)

        # Filter by operation types if specified
        if operation_types:
            all_stats = [stat for stat in all_stats if stat.operation_type in operation_types]

        return AggregateStatistics.from_statistics_list(all_stats)

    def get_project_statistics(
        self,
        project_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> AggregateStatistics:
        """
        Get aggregate statistics for a specific project.

        Args:
            project_id: ID of the project
            start_date: Start of date range
            end_date: End of date range

        Returns:
            AggregateStatistics object for the project
        """
        return self.get_aggregate_statistics(start_date, end_date, project_id)

    def get_operation_trends(
        self,
        operation_type: OperationType,
        start_date: datetime,
        end_date: datetime,
        interval_hours: int = 24
    ) -> List[Tuple[datetime, AggregateStatistics]]:
        """
        Get trends for a specific operation type over time.

        Args:
            operation_type: Type of operation to analyze
            start_date: Start of date range
            end_date: End of date range
            interval_hours: Size of intervals in hours

        Returns:
            List of (datetime, AggregateStatistics) tuples representing trends
        """
        trends = []
        current_time = start_date

        while current_time < end_date:
            interval_end = current_time + timedelta(hours=interval_hours)
            if interval_end > end_date:
                interval_end = end_date

            # Get stats for this interval
            stats = self.get_aggregate_statistics(
                current_time, interval_end, operation_types=[operation_type]
            )

            trends.append((current_time, stats))
            current_time = interval_end

        return trends

    def get_top_projects(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get top projects by operation count.

        Args:
            start_date: Start of date range
            end_date: End of date range
            limit: Maximum number of projects to return

        Returns:
            List of (project_id, operation_count) tuples
        """
        all_stats = self.get_statistics_by_date_range(start_date, end_date)

        # Count operations by project
        project_counts: Dict[str, int] = {}
        for stat in all_stats:
            if stat.project_id:
                project_counts[stat.project_id] = project_counts.get(stat.project_id, 0) + 1

        # Sort by count and return top N
        sorted_projects = sorted(
            project_counts.items(), key=lambda x: x[1], reverse=True
        )[:limit]

        return sorted_projects

    def get_recent_operations(
        self,
        limit: int = 10,
        project_id: Optional[str] = None
    ) -> List[PerformanceStatistics]:
        """
        Get most recent operations.

        Args:
            limit: Maximum number of operations to return
            project_id: Optional project ID to filter by

        Returns:
            List of recent PerformanceStatistics objects
        """
        # We'll implement this by checking the last few days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)  # Look at last week

        all_stats = self.get_statistics_by_date_range(start_date, end_date, project_id)

        # Sort by start time descending and return top N
        sorted_stats = sorted(
            all_stats, key=lambda x: x.start_time, reverse=True
        )[:limit]

        return sorted_stats

    def export_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
        project_id: Optional[str] = None
    ) -> ExportData:
        """
        Export statistics for a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            project_id: Optional project ID to filter by

        Returns:
            ExportData object containing statistics and aggregates
        """
        statistics = self.get_statistics_by_date_range(start_date, end_date, project_id)
        aggregate = self.get_aggregate_statistics(start_date, end_date, project_id)

        return ExportData(
            period_start=start_date,
            period_end=end_date,
            statistics=statistics,
            aggregate=aggregate
        )

    def get_health_status(self) -> Dict[str, any]:
        """
        Get overall health status of the system.

        Returns:
            Dictionary containing health metrics
        """
        # Get stats from the last 24 hours
        now = datetime.utcnow()
        yesterday = now - timedelta(hours=24)

        recent_stats = self.get_statistics_by_date_range(yesterday, now)

        # Calculate health metrics
        total_ops = len(recent_stats)
        successful_ops = sum(1 for stat in recent_stats if stat.success)
        failure_ops = total_ops - successful_ops

        success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0.0

        # Average duration
        durations = [stat.calculate_duration() for stat in recent_stats if stat.calculate_duration() > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Operations by type
        ops_by_type: Dict[OperationType, int] = {}
        for stat in recent_stats:
            ops_by_type[stat.operation_type] = ops_by_type.get(stat.operation_type, 0) + 1

        return {
            "timestamp": now,
            "total_operations_24h": total_ops,
            "successful_operations_24h": successful_ops,
            "failed_operations_24h": failure_ops,
            "success_rate_24h": success_rate,
            "average_duration_ms": avg_duration,
            "operations_by_type": {k.value: v for k, v in ops_by_type.items()},
            "system_status": "healthy" if success_rate >= 90 else "degraded" if success_rate >= 70 else "unhealthy"
        }