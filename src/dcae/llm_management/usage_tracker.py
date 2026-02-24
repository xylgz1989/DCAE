"""Module for tracking LLM usage statistics."""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class UsageRecord:
    """Data class representing a single usage record."""
    provider_name: str
    task_type: str
    tokens_used: int
    cost_incurred: float
    project_name: str
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamp to now if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class UsageStatistics:
    """Data class representing aggregated usage statistics."""
    total_requests: int
    total_tokens: int
    total_cost: float
    provider_stats: Dict[str, Dict[str, int]]  # provider -> {requests, tokens, cost}
    task_type_stats: Dict[str, Dict[str, int]]  # task_type -> {requests, tokens, cost}
    project_stats: Dict[str, Dict[str, int]]  # project -> {requests, tokens, cost}


class UsageTracker:
    """Tracks usage metrics for LLM calls."""

    def __init__(self, stats_file_path: str = ".dcae/usage_stats.json"):
        """
        Initialize the UsageTracker.

        Args:
            stats_file_path: Path to the statistics file
        """
        self.stats_file_path = Path(stats_file_path)
        self.records: List[UsageRecord] = []
        self.limits: Dict[Tuple[str, str], float] = {}  # (provider, metric) -> limit

        # Create directory if it doesn't exist
        self.stats_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing records
        self.load_records()

    def record_usage(self, provider_name: str, task_type: str, tokens_used: int,
                     cost_incurred: float, project_name: str, timestamp: Optional[datetime] = None) -> bool:
        """
        Record usage of an LLM call.

        Args:
            provider_name: Name of the provider used
            task_type: Type of task (e.g., 'coding', 'writing')
            tokens_used: Number of tokens used
            cost_incurred: Cost incurred for the call
            project_name: Name of the project
            timestamp: Timestamp of the usage (defaults to now)

        Returns:
            True if the record was added successfully
        """
        record = UsageRecord(
            provider_name=provider_name,
            task_type=task_type,
            tokens_used=tokens_used,
            cost_incurred=cost_incurred,
            project_name=project_name,
            timestamp=timestamp
        )

        self.records.append(record)
        self.save_records()
        return True

    def get_statistics(self) -> UsageStatistics:
        """
        Get current usage statistics.

        Returns:
            UsageStatistics object with aggregated data
        """
        total_requests = len(self.records)
        total_tokens = sum(record.tokens_used for record in self.records)
        total_cost = sum(record.cost_incurred for record in self.records)

        # Aggregate by provider
        provider_stats: Dict[str, Dict[str, int]] = {}
        for record in self.records:
            if record.provider_name not in provider_stats:
                provider_stats[record.provider_name] = {"requests": 0, "tokens": 0, "cost": 0.0}

            provider_stats[record.provider_name]["requests"] += 1
            provider_stats[record.provider_name]["tokens"] += record.tokens_used
            provider_stats[record.provider_name]["cost"] += record.cost_incurred

        # Aggregate by task type
        task_type_stats: Dict[str, Dict[str, int]] = {}
        for record in self.records:
            if record.task_type not in task_type_stats:
                task_type_stats[record.task_type] = {"requests": 0, "tokens": 0, "cost": 0.0}

            task_type_stats[record.task_type]["requests"] += 1
            task_type_stats[record.task_type]["tokens"] += record.tokens_used
            task_type_stats[record.task_type]["cost"] += record.cost_incurred

        # Aggregate by project
        project_stats: Dict[str, Dict[str, int]] = {}
        for record in self.records:
            if record.project_name not in project_stats:
                project_stats[record.project_name] = {"requests": 0, "tokens": 0, "cost": 0.0}

            project_stats[record.project_name]["requests"] += 1
            project_stats[record.project_name]["tokens"] += record.tokens_used
            project_stats[record.project_name]["cost"] += record.cost_incurred

        return UsageStatistics(
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_cost=total_cost,
            provider_stats=provider_stats,
            task_type_stats=task_type_stats,
            project_stats=project_stats
        )

    def get_historical_statistics(self, days: int = 30) -> List[UsageRecord]:
        """
        Get historical usage statistics for the specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of UsageRecord objects from the specified period
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        return [record for record in self.records if record.timestamp and record.timestamp >= cutoff_date]

    def set_usage_limit(self, provider_name: str, metric: str, limit: float):
        """
        Set a usage limit for a specific provider and metric.

        Args:
            provider_name: Name of the provider
            metric: Metric to limit ('requests', 'tokens', 'cost')
            limit: Maximum allowed value for the metric
        """
        self.limits[(provider_name, metric)] = limit

    def check_limits(self) -> List[Dict[str, any]]:
        """
        Check if any usage limits have been exceeded.

        Returns:
            List of dictionaries containing information about exceeded limits
        """
        current_stats = self.get_statistics()
        alerts = []

        for (provider, metric), limit in self.limits.items():
            current_value = 0

            if metric == 'requests' and provider in current_stats.provider_stats:
                current_value = current_stats.provider_stats[provider]['requests']
            elif metric == 'tokens' and provider in current_stats.provider_stats:
                current_value = current_stats.provider_stats[provider]['tokens']
            elif metric == 'cost' and provider in current_stats.provider_stats:
                current_value = current_stats.provider_stats[provider]['cost']

            if current_value > limit:
                alerts.append({
                    'provider': provider,
                    'metric': metric,
                    'current_value': current_value,
                    'limit': limit,
                    'alert_type': 'EXCEEDED'
                })
            elif current_value >= limit * 0.9:  # Alert when approaching 90% of limit
                alerts.append({
                    'provider': provider,
                    'metric': metric,
                    'current_value': current_value,
                    'limit': limit,
                    'alert_type': 'APPROACHING_LIMIT'
                })

        return alerts

    def get_breakdown_by_task_type(self) -> Dict[str, Dict[str, any]]:
        """
        Get usage breakdown by task type.

        Returns:
            Dictionary mapping task types to their statistics
        """
        stats = self.get_statistics()
        return stats.task_type_stats

    def get_breakdown_by_project(self) -> Dict[str, Dict[str, any]]:
        """
        Get usage breakdown by project.

        Returns:
            Dictionary mapping project names to their statistics
        """
        stats = self.get_statistics()
        return stats.project_stats

    def export_statistics(self, export_path: str):
        """
        Export statistics to a file for further analysis.

        Args:
            export_path: Path to export the statistics to
        """
        export_data = {
            'records': [
                {
                    'provider_name': record.provider_name,
                    'task_type': record.task_type,
                    'tokens_used': record.tokens_used,
                    'cost_incurred': record.cost_incurred,
                    'project_name': record.project_name,
                    'timestamp': record.timestamp.isoformat() if record.timestamp else None
                }
                for record in self.records
            ],
            'summary': {
                'total_requests': len(self.records),
                'total_tokens': sum(r.tokens_used for r in self.records),
                'total_cost': sum(r.cost_incurred for r in self.records)
            },
            'breakdown_by_provider': self.get_statistics().provider_stats
        }

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

    def save_records(self):
        """Save usage records to the file."""
        data = [
            {
                'provider_name': record.provider_name,
                'task_type': record.task_type,
                'tokens_used': record.tokens_used,
                'cost_incurred': record.cost_incurred,
                'project_name': record.project_name,
                'timestamp': record.timestamp.isoformat() if record.timestamp else None
            }
            for record in self.records
        ]

        with open(self.stats_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_records(self):
        """Load usage records from the file."""
        if not self.stats_file_path.exists():
            # Create empty file if it doesn't exist
            self.save_records()
            return

        try:
            with open(self.stats_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.records = []
            for item in data:
                timestamp = datetime.fromisoformat(item['timestamp']) if item['timestamp'] else None
                record = UsageRecord(
                    provider_name=item['provider_name'],
                    task_type=item['task_type'],
                    tokens_used=item['tokens_used'],
                    cost_incurred=item['cost_incurred'],
                    project_name=item['project_name'],
                    timestamp=timestamp
                )
                self.records.append(record)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading usage records: {e}")
            # Create a default empty file if there's an error
            self.save_records()

    def reset_statistics(self):
        """Reset all usage statistics."""
        self.records = []
        self.save_records()