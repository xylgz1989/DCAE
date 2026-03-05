"""
Example usage of the DCAE Performance Statistics module.

This script demonstrates how to use the performance statistics tracking
and dashboard functionality in DCAE.
"""

import sys
import os
import time
import random
from datetime import datetime, timedelta

# Add the src directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from dcae.performance_statistics import StatisticsCollector, get_performance_collector
from dcae.performance_dashboard import PerformanceDashboard, display_dashboard, display_project_dashboard


def simulate_operations(collector: StatisticsCollector, num_operations: int = 10):
    """
    Simulate some DCAE operations to populate statistics.

    Args:
        collector: StatisticsCollector instance to record operations
        num_operations: Number of operations to simulate
    """
    operation_types = ["project_creation", "code_generation", "requirement_analysis", "architecture_design", "testing"]
    project_names = ["Project Alpha", "Project Beta", "Project Gamma", "Project Delta", "Project Epsilon"]

    print(f"Simulating {num_operations} operations...")

    for i in range(num_operations):
        op_type = random.choice(operation_types)
        project = random.choice(project_names)
        duration = round(random.uniform(0.5, 5.0), 2)  # Random duration between 0.5 and 5.0 seconds
        success = random.choice([True, True, True, True, False])  # 80% success rate

        error_msg = None
        if not success:
            error_msg = f"Simulated error in {op_type}"

        # Add some metadata
        metadata = {
            "cpu_load": round(random.uniform(10, 90), 2),
            "memory_used_mb": random.randint(100, 1000),
            "api_calls": random.randint(1, 5)
        }

        collector.record_operation(
            operation_type=op_type,
            project_name=project,
            duration_seconds=duration,
            success=success,
            error_message=error_msg,
            metadata=metadata
        )

        print(f"  Recorded: {op_type} in {project} - {duration}s {'✓' if success else '✗'}")

        # Small delay to simulate real-time operations
        time.sleep(0.01)

    print(f"\nSuccessfully recorded {num_operations} operations.\n")


def main():
    """Main function demonstrating the performance statistics functionality."""
    print("DCAE Performance Statistics Demo")
    print("=" * 40)

    # Get the default collector instance
    collector = get_performance_collector()

    # Simulate some operations
    simulate_operations(collector, 20)

    # Create a dashboard instance
    dashboard = PerformanceDashboard(collector=collector)

    # Generate and display the summary report
    print("\n" + "=" * 60)
    print("SUMMARY PERFORMANCE REPORT")
    print("=" * 60)
    summary_report = dashboard.generate_summary_report()
    print(summary_report)

    # Show specific project report
    print("\n" + "=" * 60)
    print("SPECIFIC PROJECT REPORT")
    print("=" * 60)
    project_report = dashboard.generate_project_report("Project Alpha")
    print(project_report)

    # Show top slow operations
    print("\n" + "=" * 60)
    print("TOP 5 SLOWEST OPERATIONS")
    print("=" * 60)
    slow_ops = dashboard.get_top_slow_operations(top_n=5)
    for i, op in enumerate(slow_ops, 1):
        status = "SUCCESS" if op.success else "FAILED"
        print(f"{i}. {op.operation_type} in {op.project_name}: {op.duration_seconds:.2f}s [{status}]")

    # Show failure rates by operation type
    print("\n" + "=" * 60)
    print("FAILURE RATES BY OPERATION TYPE")
    print("=" * 60)
    failure_rates = dashboard.get_failure_rate_by_operation_type()
    for op_type, rate in sorted(failure_rates.items(), key=lambda x: x[1], reverse=True):
        print(f"{op_type}: {rate:.2f}% failure rate")

    # Show efficiency trend
    print("\n" + "=" * 60)
    print("EFFICIENCY TREND ANALYSIS")
    print("=" * 60)
    trend = dashboard.get_efficiency_trend()
    if "message" not in trend:
        print(f"First period average: {trend['first_period_avg_duration']:.2f}s")
        print(f"Second period average: {trend['second_period_avg_duration']:.2f}s")
        print(f"Improvement: {trend['improvement_percentage']:.2f}% ({trend['trend']})")
    else:
        print(trend["message"])

    # Demonstrate the convenience functions
    print("\n" + "=" * 60)
    print("USING CONVENIENCE FUNCTIONS")
    print("=" * 60)
    print("Displaying dashboard for last 7 days...")
    display_dashboard(days=7)

    print("\n" + "=" * 60)
    print("PERFORMANCE STATISTICS COMPLETE")
    print("=" * 60)
    print("\nThe performance statistics have been collected and analyzed.")
    print("Data is persisted in the .dcae/performance_stats.json file.")


if __name__ == "__main__":
    main()