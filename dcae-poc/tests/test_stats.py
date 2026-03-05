"""Tests for performance statistics components."""

import asyncio
import tempfile
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from dcae.stats.models import PerformanceStatistics, AggregateStatistics, OperationType, ExportData
from dcae.stats.collector import StatisticsCollector
from dcae.stats.storage import StatisticsStorage


class MockStorageManager:
    """Mock StorageManager for testing."""
    def __init__(self, root_path: str = "./temp_storage"):
        self.root_path = Path(root_path)
        self.root_path.mkdir(exist_ok=True, parents=True)

    async def save(self, path: str, data: dict):
        """Save data to storage."""
        file_path = self.root_path / path
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'w') as f:
            import json
            json.dump(data, f)

    async def load(self, path: str):
        """Load data from storage."""
        file_path = self.root_path / path
        with open(file_path, 'r') as f:
            import json
            return json.load(f)

    async def list_files(self, directory: str):
        """List files in a directory."""
        dir_path = self.root_path / directory
        if not dir_path.exists():
            return []
        return [str(p.relative_to(self.root_path)) for p in dir_path.rglob("*") if p.is_file()]


from dcae.stats.dashboard import PerformanceDashboard
from dcae.stats.exporter import StatisticsExporter


@pytest.fixture
def temp_db_path():
    """Provide a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        yield tmp_file.name
    Path(tmp_file.name).unlink(missing_ok=True)


@pytest.fixture
async def stats_storage(temp_db_path):
    """Create and initialize a StatisticsStorage instance."""
    storage = StatisticsStorage(db_path=temp_db_path)
    await storage.initialize()
    yield storage
    await storage.close()


@pytest.fixture
async def storage_manager():
    """Create a mock storage manager for testing."""
    # Create a temporary directory for testing
    import tempfile
    tmp_dir = Path(tempfile.mkdtemp())
    storage = MockStorageManager(root_path=tmp_dir)
    yield storage
    # Cleanup is handled by temp directory cleanup


@pytest.mark.asyncio
async def test_performance_statistics_model():
    """Test the PerformanceStatistics model."""
    # Create a basic statistic
    stat = PerformanceStatistics(
        operation_type=OperationType.CODE_GENERATION,
        operation_name="Test Operation",
        project_id="test-project"
    )

    assert stat.operation_type == OperationType.CODE_GENERATION
    assert stat.operation_name == "Test Operation"
    assert stat.project_id == "test-project"
    assert stat.success is True  # Default value
    assert stat.api_calls == 0   # Default value
    assert stat.tokens_used == 0 # Default value

    # Test marking complete
    stat.mark_complete(success=True)
    assert stat.end_time is not None
    assert stat.success is True

    # Test with failure
    stat_fail = PerformanceStatistics(
        operation_type=OperationType.CODE_REVIEW,
        operation_name="Failing Operation"
    )
    stat_fail.mark_complete(success=False, error_message="Test error")
    assert stat_fail.success is False
    assert stat_fail.error_message == "Test error"

    # Test duration calculation
    start_time = datetime.utcnow() - timedelta(seconds=1)
    duration_stat = PerformanceStatistics(
        operation_type=OperationType.DEBUGGING,
        operation_name="Duration Test",
        start_time=start_time
    )
    duration_stat.mark_complete()

    calculated_duration = duration_stat.calculate_duration()
    assert calculated_duration > 0
    assert duration_stat.duration_ms == calculated_duration


@pytest.mark.asyncio
async def test_aggregate_statistics_from_list():
    """Test creating aggregate statistics from a list."""
    # Create sample statistics
    stats_list = [
        PerformanceStatistics(
            operation_type=OperationType.CODE_GENERATION,
            operation_name="Op 1",
            start_time=datetime.utcnow() - timedelta(minutes=5),
            duration_ms=1000.0,
            success=True,
            api_calls=2,
            tokens_used=100,
            metadata={"complexity": "high"}
        ),
        PerformanceStatistics(
            operation_type=OperationType.CODE_REVIEW,
            operation_name="Op 2",
            start_time=datetime.utcnow() - timedelta(minutes=4),
            duration_ms=2000.0,
            success=False,
            api_calls=1,
            tokens_used=50,
            metadata={"complexity": "medium"}
        ),
        PerformanceStatistics(
            operation_type=OperationType.CODE_GENERATION,
            operation_name="Op 3",
            start_time=datetime.utcnow() - timedelta(minutes=3),
            duration_ms=1500.0,
            success=True,
            api_calls=3,
            tokens_used=150,
            metadata={"complexity": "high"}
        )
    ]

    # Mark operations complete
    for stat in stats_list:
        stat.mark_complete(stat.success)

    # Create aggregate
    aggregate = AggregateStatistics.from_statistics_list(stats_list)

    assert aggregate.total_operations == 3
    assert aggregate.successful_operations == 2
    assert aggregate.failed_operations == 1
    assert aggregate.success_rate == pytest.approx(66.67, abs=0.01)

    # Check duration metrics
    assert aggregate.total_duration_ms == 4500.0
    assert aggregate.avg_duration_ms == pytest.approx(1500.0)
    assert aggregate.min_duration_ms == 1000.0
    assert aggregate.max_duration_ms == 2000.0

    # Check resource metrics
    assert aggregate.total_api_calls == 6
    assert aggregate.total_tokens_used == 300
    assert aggregate.avg_tokens_per_operation == 100.0

    # Check operation type breakdown
    assert aggregate.operations_by_type[OperationType.CODE_GENERATION] == 2
    assert aggregate.operations_by_type[OperationType.CODE_REVIEW] == 1

    # Check success rates by type
    assert aggregate.success_rates_by_type[OperationType.CODE_GENERATION] == pytest.approx(100.0)
    assert aggregate.success_rates_by_type[OperationType.CODE_REVIEW] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_statistics_collector_basic(stats_storage):
    """Test basic functionality of StatisticsCollector."""
    collector = StatisticsCollector(enabled=True)

    # Start an operation
    op_id = collector.start_operation(
        operation_type=OperationType.PROJECT_CREATION,
        operation_name="Test Project Creation",
        project_id="test-project",
        model_used="gpt-4",
        metadata={"size": "large"}
    )

    assert op_id != ""
    assert collector.get_operation_count() == 1

    # Complete the operation
    completed_stat = collector.complete_operation(
        op_id,
        success=True,
        api_calls=5,
        tokens_used=1000,
        metadata_updates={"final_size": "large_final"}
    )

    assert completed_stat is not None
    assert completed_stat.success is True
    assert completed_stat.api_calls == 5
    assert completed_stat.tokens_used == 1000
    assert completed_stat.metadata["size"] == "large"
    assert completed_stat.metadata["final_size"] == "large_final"
    assert collector.get_operation_count() == 0


@pytest.mark.asyncio
async def test_statistics_collector_track_resources(stats_storage):
    """Test resource tracking in StatisticsCollector."""
    collector = StatisticsCollector(enabled=True)

    # Start an operation
    op_id = collector.start_operation(
        operation_type=OperationType.CODE_GENERATION,
        operation_name="Resource Tracking Test"
    )

    # Track resource usage during operation
    updated = collector.track_resource_usage(
        op_id,
        api_calls=3,
        tokens_used=500,
        metadata={"phase": "initial"}
    )
    assert updated is True

    # Track more resources
    updated = collector.track_resource_usage(
        op_id,
        api_calls=2,
        tokens_used=300,
        metadata={"phase": "completion", "additional_info": "value"}
    )
    assert updated is True

    # Complete the operation
    completed_stat = collector.complete_operation(op_id, success=True)
    assert completed_stat is not None
    assert completed_stat.api_calls == 5  # 3 + 2
    assert completed_stat.tokens_used == 800  # 500 + 300
    assert completed_stat.metadata["phase"] == "completion"  # Last update wins for same key
    assert completed_stat.metadata["additional_info"] == "value"


@pytest.mark.asyncio
async def test_statistics_storage_basic(stats_storage):
    """Test basic functionality of StatisticsStorage."""
    # Create a test statistic
    stat = PerformanceStatistics(
        id="test-stat-1",
        operation_type=OperationType.CODE_GENERATION,
        operation_name="Storage Test",
        project_id="test-project",
        model_used="gpt-4",
        metadata={"test": True, "value": 42}
    )
    stat.mark_complete(success=True, error_message=None)

    # Store the statistic
    success = await stats_storage.store_statistic(stat)
    assert success is True

    # Retrieve statistics
    retrieved_stats = await stats_storage.get_statistics_by_date_range(
        start_date=datetime.utcnow() - timedelta(hours=1),
        end_date=datetime.utcnow() + timedelta(hours=1),
        project_id="test-project"
    )

    assert len(retrieved_stats) == 1
    retrieved = retrieved_stats[0]

    assert retrieved.id == stat.id
    assert retrieved.operation_type == stat.operation_type
    assert retrieved.operation_name == stat.operation_name
    assert retrieved.project_id == stat.project_id
    assert retrieved.model_used == stat.model_used
    assert retrieved.metadata["test"] is True
    assert retrieved.metadata["value"] == 42


@pytest.mark.asyncio
async def test_statistics_storage_batch(stats_storage):
    """Test batch storage functionality."""
    # Create multiple test statistics
    stats = []
    for i in range(5):
        stat = PerformanceStatistics(
            id=f"batch-stat-{i}",
            operation_type=OperationType.CODE_REVIEW,
            operation_name=f"Batch Test {i}",
            project_id="batch-project"
        )
        stat.mark_complete(success=(i % 2 == 0))  # Alternate success/failure
        stats.append(stat)

    # Store in batch
    stored_count = await stats_storage.store_statistics_batch(stats)
    assert stored_count == 5

    # Retrieve all for this project
    retrieved_stats = await stats_storage.get_statistics_by_date_range(
        start_date=datetime.utcnow() - timedelta(hours=1),
        end_date=datetime.utcnow() + timedelta(hours=1),
        project_id="batch-project"
    )

    assert len(retrieved_stats) == 5

    # Check success/failure distribution
    successful = sum(1 for s in retrieved_stats if s.success)
    assert successful == 3  # 0, 2, 4 are True (0 % 2 == 0, 2 % 2 == 0, 4 % 2 == 0)


@pytest.mark.asyncio
async def test_statistics_exporter_csv():
    """Test CSV export functionality."""
    # Create sample statistics
    stats = [
        PerformanceStatistics(
            id="exp-1",
            operation_type=OperationType.CODE_GENERATION,
            operation_name="Export Test 1",
            start_time=datetime(2023, 1, 1, 12, 0, 0),
            end_time=datetime(2023, 1, 1, 12, 0, 2),
            duration_ms=2000.0,
            success=True,
            api_calls=3,
            tokens_used=500,
            model_used="gpt-4"
        ),
        PerformanceStatistics(
            id="exp-2",
            operation_type=OperationType.CODE_REVIEW,
            operation_name="Export Test 2",
            start_time=datetime(2023, 1, 1, 13, 0, 0),
            end_time=datetime(2023, 1, 1, 13, 0, 1),
            duration_ms=1000.0,
            success=False,
            error_message="Test error",
            api_calls=1,
            tokens_used=200,
            model_used="gpt-3.5"
        )
    ]

    # Export to CSV
    csv_content = StatisticsExporter.export_to_csv(stats)

    # Verify CSV contains expected data
    lines = csv_content.strip().split('\n')
    assert len(lines) == 3  # Header + 2 data rows
    assert "Operation Type" in lines[0]  # Header
    assert "code_generation" in lines[1]  # First row
    assert "code_review" in lines[2]     # Second row
    assert "Test error" in lines[2]      # Error in second row


@pytest.mark.asyncio
async def test_statistics_exporter_json():
    """Test JSON export functionality."""
    # Create sample statistics
    stats = [
        PerformanceStatistics(
            id="json-1",
            operation_type=OperationType.DEBUGGING,
            operation_name="JSON Test",
            start_time=datetime(2023, 1, 1, 12, 0, 0),
            success=True,
            metadata={"debug_info": "test_value"}
        )
    ]

    # Export to JSON
    json_content = StatisticsExporter.export_to_json(stats)
    assert '"id": "json-1"' in json_content
    assert '"operation_type": "debugging"' in json_content
    assert "test_value" in json_content


@pytest.mark.asyncio
async def test_statistics_exporter_zip():
    """Test ZIP export functionality."""
    # Create sample statistics and aggregate
    stats = [
        PerformanceStatistics(
            id="zip-1",
            operation_type=OperationType.CODE_GENERATION,
            operation_name="ZIP Test 1",
            start_time=datetime(2023, 1, 1, 12, 0, 0),
            success=True
        )
    ]

    aggregate = AggregateStatistics(
        start_period=datetime(2023, 1, 1, 12, 0, 0),
        end_period=datetime(2023, 1, 1, 13, 0, 0),
        total_operations=1,
        successful_operations=1,
        success_rate=100.0
    )

    # Export to ZIP
    zip_bytes = StatisticsExporter.export_to_zip(stats, aggregate, "test_export")

    # Verify we got some bytes
    assert len(zip_bytes) > 0

    # Test that it's a valid ZIP file by trying to read it
    import zipfile
    import io

    zip_buffer = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        file_names = zip_file.namelist()

        # Should have all expected files
        expected_files = [
            "test_export.csv",
            "test_export_raw.json",
            "test_export_aggregate.json",
            "test_export_detailed_report.json"
        ]

        for expected_file in expected_files:
            assert expected_file in file_names


@pytest.mark.asyncio
async def test_dashboard_get_statistics_by_date_range(stats_storage):
    """Test dashboard retrieval of statistics by date range."""
    # First store some statistics in the database
    past_date = datetime.utcnow() - timedelta(days=1)

    stats = [
        PerformanceStatistics(
            id="dash-1",
            operation_type=OperationType.CODE_GENERATION,
            operation_name="Dashboard Test 1",
            start_time=past_date,
            success=True
        ),
        PerformanceStatistics(
            id="dash-2",
            operation_type=OperationType.CODE_REVIEW,
            operation_name="Dashboard Test 2",
            start_time=datetime.utcnow(),
            success=False
        )
    ]

    for stat in stats:
        await stats_storage.store_statistic(stat)

    # Create a mock storage manager
    import tempfile
    tmp_dir = Path(tempfile.mkdtemp())
    storage_manager = MockStorageManager(root_path=tmp_dir)

    # Create dashboard and try to get statistics
    dashboard = PerformanceDashboard(storage_manager)

    # Test with an empty result for date range
    start_date = datetime.utcnow() - timedelta(hours=1)
    end_date = datetime.utcnow() + timedelta(hours=1)

    # For now, just verify the dashboard can be created and basic methods exist
    assert hasattr(dashboard, 'get_aggregate_statistics')

    # Cleanup
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_aggregate_statistics_empty_list():
    """Test aggregate statistics with empty list."""
    aggregate = AggregateStatistics.from_statistics_list([])

    assert aggregate.total_operations == 0
    assert aggregate.successful_operations == 0
    assert aggregate.failed_operations == 0
    assert aggregate.success_rate == 0.0
    assert aggregate.total_duration_ms == 0.0
    assert aggregate.avg_duration_ms == 0.0


@pytest.mark.asyncio
async def test_performance_statistics_calculate_duration():
    """Test duration calculation in PerformanceStatistics."""
    start_time = datetime.utcnow() - timedelta(seconds=2, milliseconds=500)
    stat = PerformanceStatistics(
        operation_type=OperationType.CODE_GENERATION,
        operation_name="Duration Calc Test",
        start_time=start_time
    )

    # Initially no duration
    assert stat.duration_ms is None

    # Calculate duration manually (before completion)
    duration = stat.calculate_duration()
    assert duration > 2000  # At least 2 seconds (2000ms)
    assert stat.duration_ms == duration

    # Mark complete (should recalculate)
    stat.mark_complete()
    assert stat.duration_ms is not None
    assert stat.calculate_duration() == stat.duration_ms  # Should return cached value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])