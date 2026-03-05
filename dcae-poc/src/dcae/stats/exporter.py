"""Export functionality for performance statistics."""

import csv
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import io

from .models import PerformanceStatistics, AggregateStatistics, ExportData


class StatisticsExporter:
    """Handles exporting performance statistics in various formats."""

    @staticmethod
    def export_to_csv(stats_list: List[PerformanceStatistics], include_headers: bool = True) -> str:
        """
        Export statistics to CSV format.

        Args:
            stats_list: List of PerformanceStatistics to export
            include_headers: Whether to include column headers

        Returns:
            CSV formatted string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        if include_headers:
            # Write header
            header = [
                'ID', 'Project ID', 'Operation Type', 'Operation Name',
                'Start Time', 'End Time', 'Duration (ms)', 'Success',
                'Error Message', 'API Calls', 'Tokens Used', 'Model Used'
            ]
            writer.writerow(header)

        # Write data rows
        for stat in stats_list:
            row = [
                stat.id or '',
                stat.project_id or '',
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

    @staticmethod
    def export_to_json(stats_list: List[PerformanceStatistics]) -> str:
        """
        Export statistics to JSON format.

        Args:
            stats_list: List of PerformanceStatistics to export

        Returns:
            JSON formatted string
        """
        stats_dicts = [stat.dict() for stat in stats_list]
        return json.dumps(stats_dicts, indent=2, default=str)

    @staticmethod
    def export_aggregate_to_json(aggregate: AggregateStatistics) -> str:
        """
        Export aggregate statistics to JSON format.

        Args:
            aggregate: AggregateStatistics to export

        Returns:
            JSON formatted string
        """
        return json.dumps(aggregate.dict(), indent=2, default=str)

    @staticmethod
    def export_detailed_report(
        stats_list: List[PerformanceStatistics],
        aggregate: AggregateStatistics
    ) -> Dict[str, Any]:
        """
        Export a detailed report with both raw data and aggregate statistics.

        Args:
            stats_list: List of PerformanceStatistics
            aggregate: AggregateStatistics

        Returns:
            Dictionary containing detailed report
        """
        return {
            "report_metadata": {
                "export_timestamp": datetime.utcnow().isoformat(),
                "record_count": len(stats_list),
                "period_start": aggregate.start_period.isoformat(),
                "period_end": aggregate.end_period.isoformat()
            },
            "raw_statistics": [stat.dict() for stat in stats_list],
            "aggregate_statistics": aggregate.dict(),
            "summary_metrics": {
                "total_operations": aggregate.total_operations,
                "success_rate": aggregate.success_rate,
                "avg_duration_ms": aggregate.avg_duration_ms,
                "total_tokens_used": aggregate.total_tokens_used,
                "total_api_calls": aggregate.total_api_calls
            }
        }

    @staticmethod
    def export_to_zip(
        stats_list: List[PerformanceStatistics],
        aggregate: AggregateStatistics,
        filename_prefix: str = "dcae_stats_export"
    ) -> bytes:
        """
        Export statistics to a ZIP archive containing multiple formats.

        Args:
            stats_list: List of PerformanceStatistics to export
            aggregate: AggregateStatistics to include
            filename_prefix: Prefix for the output files in the ZIP

        Returns:
            Bytes of the ZIP archive
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add CSV version
            csv_content = StatisticsExporter.export_to_csv(stats_list)
            zip_file.writestr(f"{filename_prefix}.csv", csv_content)

            # Add JSON version of raw data
            json_content = StatisticsExporter.export_to_json(stats_list)
            zip_file.writestr(f"{filename_prefix}_raw.json", json_content)

            # Add JSON version of aggregate data
            agg_json_content = StatisticsExporter.export_aggregate_to_json(aggregate)
            zip_file.writestr(f"{filename_prefix}_aggregate.json", agg_json_content)

            # Add detailed report
            detailed_report = StatisticsExporter.export_detailed_report(stats_list, aggregate)
            zip_file.writestr(
                f"{filename_prefix}_detailed_report.json",
                json.dumps(detailed_report, indent=2, default=str)
            )

        return zip_buffer.getvalue()

    @staticmethod
    def export_metadata_fields(stats_list: List[PerformanceStatistics]) -> List[str]:
        """
        Get list of all metadata fields across the statistics.

        Args:
            stats_list: List of PerformanceStatistics

        Returns:
            List of unique metadata field names
        """
        all_keys = set()
        for stat in stats_list:
            all_keys.update(stat.metadata.keys())
        return sorted(list(all_keys))

    @staticmethod
    def export_metadata_to_csv(stats_list: List[PerformanceStatistics]) -> str:
        """
        Export metadata fields to CSV format with one column per field.

        Args:
            stats_list: List of PerformanceStatistics

        Returns:
            CSV formatted string with metadata
        """
        if not stats_list:
            return ""

        # Get all unique metadata keys
        all_keys = StatisticsExporter.export_metadata_fields(stats_list)

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        header = ['ID', 'Operation Type', 'Operation Name', 'Start Time'] + all_keys
        writer.writerow(header)

        # Write data rows
        for stat in stats_list:
            row = [
                stat.id or '',
                stat.operation_type.value,
                stat.operation_name,
                stat.start_time.isoformat()
            ]

            # Add metadata values in the same order as headers
            for key in all_keys:
                row.append(stat.metadata.get(key, ''))

            writer.writerow(row)

        return output.getvalue()