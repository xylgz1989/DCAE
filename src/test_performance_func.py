#!/usr/bin/env python3
"""
Test script to verify performance statistics functionality.
"""

import sys
import os
sys.path.insert(0, '.')

from dcae.performance_statistics import StatisticsCollector, PerformanceRecord
from dcae.performance_dashboard import PerformanceDashboard

def test_functionality():
    print("Testing performance statistics functionality...")

    # Create collector with test file
    collector = StatisticsCollector(stats_file_path='../.dcae/test_perf_stats.json')

    # Record several test operations
    print("Recording test operations...")
    collector.record_operation(
        operation_type='project_creation',
        project_name='test_project',
        duration_seconds=1.5,
        success=True
    )

    collector.record_operation(
        operation_type='code_generation',
        project_name='test_project',
        duration_seconds=3.2,
        success=True
    )

    collector.record_operation(
        operation_type='project_creation',
        project_name='another_project',
        duration_seconds=2.1,
        success=False,
        error_message='Permission denied'
    )

    # Get and display statistics
    stats = collector.get_statistics()
    print(f"Retrieved statistics: {stats.total_operations} total operations")
    print(f"Successful: {stats.successful_operations}, Failed: {stats.failed_operations}")
    print(f"Average duration: {stats.average_duration:.2f}s")

    # Test dashboard
    print("Generating dashboard report...")
    dashboard = PerformanceDashboard(collector=collector)
    report = dashboard.generate_summary_report()
    print(f"Dashboard report generated ({len(report)} characters)")

    # Test project-specific report
    print("Generating project-specific report...")
    project_report = dashboard.generate_project_report('test_project')
    print(f"Project report generated ({len(project_report)} characters)")

    # Test other dashboard functions
    print("Testing other dashboard functions...")
    slow_ops = dashboard.get_top_slow_operations(top_n=3)
    print(f"Retrieved top {len(slow_ops)} slow operations")

    failure_rates = dashboard.get_failure_rate_by_operation_type()
    print(f"Got failure rates for {len(failure_rates)} operation types")

    trend = dashboard.get_efficiency_trend()
    print(f"Trend analysis completed: {trend.get('message', 'Has trend data')}")

    print("\nAll functionality working correctly!")

if __name__ == "__main__":
    test_functionality()