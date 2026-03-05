"""Performance statistics data models for DCAE."""

from datetime import datetime
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class OperationType(str, Enum):
    """Types of operations that can be tracked."""
    PROJECT_CREATION = "project_creation"
    TASK_COMPLETION = "task_completion"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    REQUIREMENT_GEN = "requirement_generation"
    TEST_DOC_GEN = "test_documentation_generation"
    TEST_CASE_GEN = "test_case_generation"


class PerformanceStatistics(BaseModel):
    """Model representing statistical data for DCAE operations."""

    # Basic identifiers
    id: Optional[str] = Field(default=None, description="Unique identifier for the statistics record")
    project_id: Optional[str] = Field(default=None, description="ID of the associated project")

    # Operation details
    operation_type: OperationType = Field(description="Type of operation being tracked")
    operation_name: str = Field(description="Name/description of the operation")

    # Timing information
    start_time: datetime = Field(default_factory=datetime.utcnow, description="When the operation started")
    end_time: Optional[datetime] = Field(default=None, description="When the operation completed")
    duration_ms: Optional[float] = Field(default=None, description="Duration of operation in milliseconds")

    # Success/failure metrics
    success: bool = Field(default=True, description="Whether the operation succeeded")
    error_message: Optional[str] = Field(default=None, description="Error message if operation failed")

    # Resource usage metrics
    api_calls: int = Field(default=0, description="Number of API calls made during operation")
    tokens_used: int = Field(default=0, description="Total tokens used during operation")
    model_used: Optional[str] = Field(default=None, description="Model used for the operation")

    # Custom metadata
    metadata: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict,
                                                            description="Additional custom metadata")

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

    def calculate_duration(self) -> float:
        """Calculate duration if not already calculated."""
        if self.duration_ms is not None:
            return self.duration_ms

        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            duration_ms = delta.total_seconds() * 1000
            self.duration_ms = duration_ms
            return duration_ms

        return 0.0

    def mark_complete(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark the operation as complete."""
        self.end_time = datetime.utcnow()
        self.success = success
        self.error_message = error_message
        self.calculate_duration()


class AggregateStatistics(BaseModel):
    """Model representing aggregated performance statistics."""

    # Time range
    start_period: datetime = Field(description="Start of the aggregation period")
    end_period: datetime = Field(description="End of the aggregation period")

    # Overall metrics
    total_operations: int = Field(default=0, description="Total number of operations")
    successful_operations: int = Field(default=0, description="Number of successful operations")
    failed_operations: int = Field(default=0, description="Number of failed operations")
    success_rate: float = Field(default=0.0, description="Success rate percentage (0-100)")

    # Duration metrics
    avg_duration_ms: float = Field(default=0.0, description="Average operation duration in milliseconds")
    min_duration_ms: float = Field(default=0.0, description="Minimum operation duration in milliseconds")
    max_duration_ms: float = Field(default=0.0, description="Maximum operation duration in milliseconds")
    total_duration_ms: float = Field(default=0.0, description="Total duration of all operations in milliseconds")

    # Resource metrics
    total_api_calls: int = Field(default=0, description="Total API calls across all operations")
    total_tokens_used: int = Field(default=0, description="Total tokens used across all operations")
    avg_tokens_per_operation: float = Field(default=0.0, description="Average tokens per operation")

    # Breakdown by operation type
    operations_by_type: Dict[OperationType, int] = Field(default_factory=dict,
                                                        description="Operations count by type")
    success_rates_by_type: Dict[OperationType, float] = Field(default_factory=dict,
                                                             description="Success rates by operation type")

    # Custom metadata averages
    metadata_stats: Dict[str, float] = Field(default_factory=dict,
                                           description="Aggregated statistics for numeric metadata fields")

    @classmethod
    def from_statistics_list(cls, stats_list: List[PerformanceStatistics]) -> 'AggregateStatistics':
        """Create aggregate statistics from a list of individual statistics."""
        if not stats_list:
            return cls(
                start_period=datetime.utcnow(),
                end_period=datetime.utcnow(),
                success_rate=0.0
            )

        # Determine time range
        start_period = min(stat.start_time for stat in stats_list)
        end_period = max(stat.end_time or stat.start_time for stat in stats_list)

        # Count totals
        total_operations = len(stats_list)
        successful_operations = sum(1 for stat in stats_list if stat.success)
        failed_operations = total_operations - successful_operations
        success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0.0

        # Calculate durations
        durations = [stat.calculate_duration() for stat in stats_list]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        min_duration = min(durations) if durations else 0.0
        max_duration = max(durations) if durations else 0.0
        total_duration = sum(durations)

        # Calculate resource usage
        total_api_calls = sum(stat.api_calls for stat in stats_list)
        total_tokens = sum(stat.tokens_used for stat in stats_list)
        avg_tokens = total_tokens / total_operations if total_operations > 0 else 0.0

        # Group by operation type
        operations_by_type = {}
        success_by_type = {}
        for stat in stats_list:
            op_type = stat.operation_type
            operations_by_type[op_type] = operations_by_type.get(op_type, 0) + 1

            # Calculate success rates by type
            if op_type not in success_by_type:
                success_by_type[op_type] = {'success': 0, 'total': 0}

            if stat.success:
                success_by_type[op_type]['success'] += 1
            success_by_type[op_type]['total'] += 1

        # Calculate success rates by type
        success_rates_by_type = {
            op_type: data['success'] / data['total'] * 100
            for op_type, data in success_by_type.items()
            if data['total'] > 0
        }

        # Calculate metadata stats (for numeric fields only)
        metadata_stats = {}
        for stat in stats_list:
            for key, value in stat.metadata.items():
                if isinstance(value, (int, float)):
                    if key not in metadata_stats:
                        metadata_stats[key] = {'sum': 0, 'count': 0}
                    metadata_stats[key]['sum'] += value
                    metadata_stats[key]['count'] += 1

        # Average metadata values
        for key in metadata_stats:
            metadata_stats[key] = metadata_stats[key]['sum'] / metadata_stats[key]['count']

        return cls(
            start_period=start_period,
            end_period=end_period,
            total_operations=total_operations,
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            success_rate=success_rate,
            avg_duration_ms=avg_duration,
            min_duration_ms=min_duration,
            max_duration_ms=max_duration,
            total_duration_ms=total_duration,
            total_api_calls=total_api_calls,
            total_tokens_used=total_tokens,
            avg_tokens_per_operation=avg_tokens,
            operations_by_type=operations_by_type,
            success_rates_by_type=success_rates_by_type,
            metadata_stats=metadata_stats
        )


class ExportData(BaseModel):
    """Model representing exported statistics data."""

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When data was exported")
    period_start: datetime = Field(description="Start of export period")
    period_end: datetime = Field(description="End of export period")
    statistics: List[PerformanceStatistics] = Field(description="List of performance statistics")
    aggregate: AggregateStatistics = Field(description="Aggregate statistics for the period")

    def to_csv(self) -> str:
        """Convert statistics to CSV format."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        header = [
            'operation_type', 'operation_name', 'start_time', 'end_time',
            'duration_ms', 'success', 'error_message', 'api_calls',
            'tokens_used', 'model_used'
        ]
        writer.writerow(header)

        # Rows
        for stat in self.statistics:
            row = [
                stat.operation_type.value,
                stat.operation_name,
                stat.start_time.isoformat(),
                stat.end_time.isoformat() if stat.end_time else '',
                stat.duration_ms or 0,
                stat.success,
                stat.error_message or '',
                stat.api_calls,
                stat.tokens_used,
                stat.model_used or ''
            ]
            writer.writerow(row)

        return output.getvalue()

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'statistics': [stat.dict() for stat in self.statistics],
            'aggregate': self.aggregate.dict()
        }