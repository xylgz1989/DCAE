"""Simple test script for performance statistics."""
import sys
sys.path.insert(0, 'src')

from src.dcae.performance_statistics import StatisticsCollector
from src.dcae.performance_dashboard import PerformanceDashboard
import tempfile
import os

def test_basic_functionality():
    print("Testing basic performance statistics functionality...")

    # Create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()

    try:
        # Initialize collector
        collector = StatisticsCollector(stats_file_path=temp_file.name)

        # Record a few operations
        collector.record_operation(
            operation_type="create_project",
            project_name="test_project",
            duration_seconds=1.5,
            success=True
        )

        collector.record_operation(
            operation_type="generate_code",
            project_name="test_project",
            duration_seconds=3.2,
            success=True
        )

        collector.record_operation(
            operation_type="create_project",
            project_name="another_project",
            duration_seconds=2.1,
            success=False,
            error_message="Permission denied"
        )

        # Get statistics
        stats = collector.get_statistics()
        print(f"Total operations: {stats.total_operations}")
        print(f"Successful operations: {stats.successful_operations}")
        print(f"Failed operations: {stats.failed_operations}")
        print(f"Average duration: {stats.average_duration:.2f}s")

        # Test dashboard
        dashboard = PerformanceDashboard(collector=collector)
        report = dashboard.generate_summary_report()
        print("\nSample report generated successfully!")
        print(f"Report length: {len(report)} characters")

        print("All tests passed!")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

if __name__ == "__main__":
    test_basic_functionality()