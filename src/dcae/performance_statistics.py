"""Module for tracking and managing performance statistics for DCAE operations."""
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading


@dataclass
class PerformanceRecord:
    """Data class representing a single performance measurement."""
    operation_type: str
    project_name: str
    duration_seconds: float
    start_time: datetime
    end_time: datetime
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Ensure timestamps are properly set."""
        if isinstance(self.start_time, str):
            self.start_time = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        if isinstance(self.end_time, str):
            self.end_time = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))


@dataclass
class PerformanceStatistics:
    """Data class representing aggregated performance statistics."""
    total_operations: int
    successful_operations: int
    failed_operations: int
    average_duration: float
    total_duration: float
    operation_types: Dict[str, Dict[str, Any]]  # operation_type -> {stats}
    projects: Dict[str, Dict[str, Any]]  # project_name -> {stats}
    recent_operations: List[PerformanceRecord]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class StatisticsCollector:
    """Collects performance metrics for DCAE operations."""

    def __init__(self, stats_file_path: str = ".dcae/performance_stats.json"):
        """
        Initialize the StatisticsCollector.

        Args:
            stats_file_path: Path to the statistics file
        """
        self.stats_file_path = Path(stats_file_path)
        self.records: List[PerformanceRecord] = []
        self.lock = threading.Lock()  # Thread safety for concurrent operations

        # Create directory if it doesn't exist
        self.stats_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing records
        self.load_records()

    def record_operation(self, operation_type: str, project_name: str,
                        duration_seconds: float, success: bool,
                        error_message: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> bool:
        """
        Record a performance measurement for an operation.

        Args:
            operation_type: Type of operation (e.g., 'project_creation', 'code_generation')
            project_name: Name of the project involved
            duration_seconds: Time taken for the operation in seconds
            success: Whether the operation was successful
            error_message: Error message if operation failed
            metadata: Additional metadata about the operation
            start_time: Start time of the operation (defaults to now - duration)
            end_time: End time of the operation (defaults to now)

        Returns:
            True if the record was added successfully
        """
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(seconds=duration_seconds)

        record = PerformanceRecord(
            operation_type=operation_type,
            project_name=project_name,
            duration_seconds=duration_seconds,
            start_time=start_time,
            end_time=end_time,
            success=success,
            error_message=error_message,
            metadata=metadata
        )

        with self.lock:
            self.records.append(record)
            self.save_records()

        return True

    def start_timer(self) -> float:
        """
        Start a timer for measuring operation duration.

        Returns:
            Start time as a float timestamp
        """
        return time.time()

    def end_timer(self, start_time: float) -> float:
        """
        End a timer and calculate duration.

        Args:
            start_time: Start time as returned by start_timer

        Returns:
            Duration in seconds
        """
        return time.time() - start_time

    @staticmethod
    def time_operation(operation_func, *args, **kwargs) -> Tuple[Any, float]:
        """
        Execute a function and measure its execution time.

        Args:
            operation_func: Function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            A tuple containing (result, duration_in_seconds)
        """
        start_time = time.time()
        try:
            result = operation_func(*args, **kwargs)
            success = True
        except Exception as e:
            result = e
            success = False

        duration = time.time() - start_time

        if not success:
            raise result

        return result, duration

    def get_statistics(self, days: int = None) -> PerformanceStatistics:
        """
        Get current performance statistics.

        Args:
            days: Number of days to look back (None for all records)

        Returns:
            PerformanceStatistics object with aggregated data
        """
        records = self.records
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            records = [r for r in records if r.start_time >= cutoff_date]

        if not records:
            return PerformanceStatistics(
                total_operations=0,
                successful_operations=0,
                failed_operations=0,
                average_duration=0.0,
                total_duration=0.0,
                operation_types={},
                projects={},
                recent_operations=[]
            )

        total_operations = len(records)
        successful_operations = len([r for r in records if r.success])
        failed_operations = total_operations - successful_operations
        total_duration = sum(r.duration_seconds for r in records)
        average_duration = total_duration / total_operations if total_operations > 0 else 0.0

        # Aggregate by operation type
        operation_types: Dict[str, Dict[str, Any]] = {}
        for record in records:
            op_type = record.operation_type
            if op_type not in operation_types:
                operation_types[op_type] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_duration": 0.0,
                    "total_duration": 0.0
                }

            operation_types[op_type]["count"] += 1
            if record.success:
                operation_types[op_type]["successful"] += 1
            else:
                operation_types[op_type]["failed"] += 1
            operation_types[op_type]["total_duration"] += record.duration_seconds

        # Calculate averages for each operation type
        for op_type, stats in operation_types.items():
            if stats["count"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["count"]

        # Aggregate by project
        projects: Dict[str, Dict[str, Any]] = {}
        for record in records:
            proj_name = record.project_name
            if proj_name not in projects:
                projects[proj_name] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_duration": 0.0,
                    "total_duration": 0.0
                }

            projects[proj_name]["count"] += 1
            if record.success:
                projects[proj_name]["successful"] += 1
            else:
                projects[proj_name]["failed"] += 1
            projects[proj_name]["total_duration"] += record.duration_seconds

        # Calculate averages for each project
        for proj_name, stats in projects.items():
            if stats["count"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["count"]

        # Get recent operations (last 20)
        recent_operations = records[-20:]  # Last 20 operations

        start_date = min((r.start_time for r in records), default=None)
        end_date = max((r.end_time for r in records), default=None)

        return PerformanceStatistics(
            total_operations=total_operations,
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            average_duration=average_duration,
            total_duration=total_duration,
            operation_types=operation_types,
            projects=projects,
            recent_operations=recent_operations,
            start_date=start_date,
            end_date=end_date
        )

    def get_operation_breakdown(self, operation_type: str) -> List[PerformanceRecord]:
        """
        Get all performance records for a specific operation type.

        Args:
            operation_type: Type of operation to filter by

        Returns:
            List of PerformanceRecord objects for the specified operation type
        """
        return [r for r in self.records if r.operation_type == operation_type]

    def get_project_statistics(self, project_name: str) -> PerformanceStatistics:
        """
        Get performance statistics for a specific project.

        Args:
            project_name: Name of the project

        Returns:
            PerformanceStatistics for the project
        """
        project_records = [r for r in self.records if r.project_name == project_name]

        if not project_records:
            return PerformanceStatistics(
                total_operations=0,
                successful_operations=0,
                failed_operations=0,
                average_duration=0.0,
                total_duration=0.0,
                operation_types={},
                projects={},
                recent_operations=[],
                start_date=None,
                end_date=None
            )

        total_operations = len(project_records)
        successful_operations = len([r for r in project_records if r.success])
        failed_operations = total_operations - successful_operations
        total_duration = sum(r.duration_seconds for r in project_records)
        average_duration = total_duration / total_operations if total_operations > 0 else 0.0

        # Aggregate by operation type within the project
        operation_types: Dict[str, Dict[str, Any]] = {}
        for record in project_records:
            op_type = record.operation_type
            if op_type not in operation_types:
                operation_types[op_type] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_duration": 0.0,
                    "total_duration": 0.0
                }

            operation_types[op_type]["count"] += 1
            if record.success:
                operation_types[op_type]["successful"] += 1
            else:
                operation_types[op_type]["failed"] += 1
            operation_types[op_type]["total_duration"] += record.duration_seconds

        # Calculate averages
        for op_type, stats in operation_types.items():
            if stats["count"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["count"]

        recent_operations = project_records[-20:]  # Last 20 operations for this project

        start_date = min((r.start_time for r in project_records), default=None)
        end_date = max((r.end_time for r in project_records), default=None)

        # Create a single entry in projects dict for this project
        projects = {
            project_name: {
                "count": total_operations,
                "successful": successful_operations,
                "failed": failed_operations,
                "avg_duration": average_duration,
                "total_duration": total_duration
            }
        }

        return PerformanceStatistics(
            total_operations=total_operations,
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            average_duration=average_duration,
            total_duration=total_duration,
            operation_types=operation_types,
            projects=projects,
            recent_operations=recent_operations,
            start_date=start_date,
            end_date=end_date
        )

    def export_statistics(self, export_path: str, days: int = None):
        """
        Export performance statistics to a file for further analysis.

        Args:
            export_path: Path to export the statistics to
            days: Number of days to include in export (None for all records)
        """
        records = self.records
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            records = [r for r in records if r.start_time >= cutoff_date]

        export_data = {
            'records': [
                {
                    'operation_type': record.operation_type,
                    'project_name': record.project_name,
                    'duration_seconds': record.duration_seconds,
                    'start_time': record.start_time.isoformat(),
                    'end_time': record.end_time.isoformat(),
                    'success': record.success,
                    'error_message': record.error_message,
                    'metadata': record.metadata
                }
                for record in records
            ],
            'summary': {
                'total_operations': len(records),
                'successful_operations': len([r for r in records if r.success]),
                'failed_operations': len([r for r in records if not r.success]),
                'total_duration': sum(r.duration_seconds for r in records),
                'average_duration': sum(r.duration_seconds for r in records) / len(records) if records else 0.0
            }
        }

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

    def save_records(self):
        """Save performance records to the file."""
        with self.lock:
            data = [
                {
                    'operation_type': record.operation_type,
                    'project_name': record.project_name,
                    'duration_seconds': record.duration_seconds,
                    'start_time': record.start_time.isoformat(),
                    'end_time': record.end_time.isoformat(),
                    'success': record.success,
                    'error_message': record.error_message,
                    'metadata': record.metadata
                }
                for record in self.records
            ]

            with open(self.stats_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

    def load_records(self):
        """Load performance records from the file."""
        if not self.stats_file_path.exists():
            # Create empty file if it doesn't exist
            self.save_records()
            return

        try:
            with open(self.stats_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with self.lock:
                self.records = []
                for item in data:
                    start_time = datetime.fromisoformat(item['start_time'])
                    end_time = datetime.fromisoformat(item['end_time'])

                    record = PerformanceRecord(
                        operation_type=item['operation_type'],
                        project_name=item['project_name'],
                        duration_seconds=item['duration_seconds'],
                        start_time=start_time,
                        end_time=end_time,
                        success=item['success'],
                        error_message=item.get('error_message'),
                        metadata=item.get('metadata')
                    )
                    self.records.append(record)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading performance records: {e}")
            # Create a default empty file if there's an error
            with self.lock:
                self.records = []
                self.save_records()

    def reset_statistics(self):
        """Reset all performance statistics."""
        with self.lock:
            self.records = []
            self.save_records()


# Global instance for easy access
_default_collector = None


def get_performance_collector() -> StatisticsCollector:
    """Get the global statistics collector instance."""
    global _default_collector
    if _default_collector is None:
        _default_collector = StatisticsCollector()
    return _default_collector