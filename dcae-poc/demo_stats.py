"""Demo script for the Performance Statistics Dashboard functionality."""

import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to the path so we can import our modules
import sys
sys.path.insert(0, './src')

from dcae.stats.models import PerformanceStatistics, OperationType
from dcae.stats.collector import StatisticsCollector
from dcae.stats.dashboard import PerformanceDashboard
from dcae.stats.storage import StatisticsStorage
from dcae.stats.ui import ConsoleDashboardUI
from dcae.stats.exporter import StatisticsExporter


def demo_performance_statistics():
    """Demonstrate the performance statistics functionality."""

    print("DCAE Performance Statistics Demo")
    print("=" * 50)

    # Create temporary storage path
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        print(f"Using temporary storage: {storage_path}")

        # Initialize components
        print("\nInitializing statistics components...")

        # Initialize storage for persistent stats
        stats_storage = StatisticsStorage(db_path=str(storage_path / "dcae_stats.db"))
        # For demo, we'll initialize separately
        import asyncio
        asyncio.run(stats_storage.initialize())

        # Initialize collector with storage path
        collector = StatisticsCollector(storage_path=str(storage_path))

        # Initialize dashboard with storage path
        dashboard = PerformanceDashboard(storage_path=str(storage_path))

        # Initialize UI
        ui = ConsoleDashboardUI(dashboard)

        print("Components initialized successfully")

        # Demonstrate starting and completing operations
        print("\nSimulating DCAE operations...")

        # Simulate some operations
        operations = [
            (OperationType.CODE_GENERATION, "User Authentication Module", "project-1"),
            (OperationType.CODE_REVIEW, "Review API Endpoints", "project-1"),
            (OperationType.DEBUGGING, "Fix Login Issue", "project-2"),
            (OperationType.REQUIREMENT_GEN, "Design Document", "project-2"),
            (OperationType.CODE_GENERATION, "Database Schema", "project-1"),
        ]

        for i, (op_type, op_name, project_id) in enumerate(operations):
            print(f"   - Starting {op_type.value}: {op_name}")

            # Start operation
            op_id = collector.start_operation(
                operation_type=op_type,
                operation_name=op_name,
                project_id=project_id,
                model_used="gpt-4" if i % 2 == 0 else "claude-3",
                metadata={"complexity": "high" if i < 3 else "medium"}
            )

            # Simulate some work happening
            import time
            time.sleep(0.1)  # Simulate processing time

            # Complete operation
            success = i != 2  # Make the debugging operation fail for demo purposes
            error_msg = "Complex issue detected" if i == 2 else None

            collector.complete_operation(
                op_id,
                success=success,
                error_message=error_msg,
                api_calls=i + 1,
                tokens_used=500 * (i + 1),
                metadata_updates={"execution_time": f"{i * 100}ms"}
            )

            print(f"     -> Completed {'successfully' if success else 'with failure'}")

        print("\nOperations completed, showing dashboard...")

        # Show console dashboard
        ui.display_dashboard(days=1)

        # Show specific stats
        print(f"\nProject Statistics (project-1):")
        project_stats = dashboard.get_project_statistics("project-1",
                                                       datetime.utcnow() - timedelta(days=1),
                                                       datetime.utcnow())
        print(f"   Success Rate: {project_stats.success_rate:.1f}%")
        print(f"   Total Operations: {project_stats.total_operations}")
        print(f"   Avg Duration: {project_stats.avg_duration_ms:.2f} ms")

        # Show recent activity
        print(f"\nRecent Operations:")
        recent_ops = dashboard.get_recent_operations(limit=3)
        for i, op in enumerate(recent_ops, 1):
            status = "SUCCESS" if op.success else "FAILED"
            print(f"   {i}. {status} {op.operation_type.value}: {op.operation_name}")

        # Demonstrate export functionality
        print(f"\nExporting statistics...")

        # Get stats for export
        stats_for_export = dashboard.get_statistics_by_date_range(
            datetime.utcnow() - timedelta(days=1),
            datetime.utcnow()
        )

        if stats_for_export:
            aggregate = dashboard.get_aggregate_statistics(
                datetime.utcnow() - timedelta(days=1),
                datetime.utcnow()
            )

            # Export to different formats
            csv_export = StatisticsExporter.export_to_csv(stats_for_export)
            print(f"   CSV export: {len(csv_export)} characters")

            json_export = StatisticsExporter.export_to_json(stats_for_export)
            print(f"   JSON export: {len(json_export)} characters")

            # Export to ZIP (simulated)
            zip_data = StatisticsExporter.export_to_zip(stats_for_export, aggregate, "demo_export")
            print(f"   ZIP export: {len(zip_data)} bytes")

            print(f"\nSample CSV output:")
            lines = csv_export.split('\n')
            for line in lines[:3]:  # Show header and first row
                print(f"   {line}")

        print(f"\nPerformance statistics demo completed!")


if __name__ == "__main__":
    demo_performance_statistics()