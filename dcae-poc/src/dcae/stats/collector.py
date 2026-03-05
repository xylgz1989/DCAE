"""Statistics collector for gathering DCAE operational metrics."""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from .models import PerformanceStatistics, OperationType
from ..config import DCAEConfig  # Using existing config module


class StatisticsCollector:
    """Component to gather metrics during DCAE operations."""

    def __init__(self, storage_path: Optional[str] = None, enabled: bool = True):
        """
        Initialize the statistics collector.

        Args:
            storage_path: Path for storing statistics (optional)
            enabled: Whether statistics collection is enabled
        """
        self.storage_path = storage_path
        self.enabled = enabled
        self._active_operations: Dict[str, PerformanceStatistics] = {}

    def start_operation(
        self,
        operation_type: OperationType,
        operation_name: str,
        project_id: Optional[str] = None,
        model_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start tracking an operation.

        Args:
            operation_type: Type of operation being tracked
            operation_name: Name/description of the operation
            project_id: ID of the associated project
            model_used: Model used for the operation
            metadata: Additional custom metadata

        Returns:
            Operation ID for tracking this operation
        """
        if not self.enabled:
            return ""

        operation_id = f"op_{int(time.time() * 1000000)}"  # Unique ID based on microseconds

        stats = PerformanceStatistics(
            id=operation_id,
            project_id=project_id,
            operation_type=operation_type,
            operation_name=operation_name,
            model_used=model_used,
            metadata=metadata or {}
        )

        self._active_operations[operation_id] = stats
        return operation_id

    def complete_operation(
        self,
        operation_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
        api_calls: Optional[int] = None,
        tokens_used: Optional[int] = None,
        metadata_updates: Optional[Dict[str, Any]] = None
    ) -> Optional[PerformanceStatistics]:
        """
        Complete tracking of an operation.

        Args:
            operation_id: ID of the operation to complete
            success: Whether the operation succeeded
            error_message: Error message if operation failed
            api_calls: Number of API calls made during operation
            tokens_used: Total tokens used during operation
            metadata_updates: Additional metadata to add/update

        Returns:
            The completed PerformanceStatistics object, or None if operation not found
        """
        if not self.enabled:
            return None

        if operation_id not in self._active_operations:
            return None

        stats = self._active_operations[operation_id]

        # Update statistics with completion info
        stats.mark_complete(success=success, error_message=error_message)

        if api_calls is not None:
            stats.api_calls = api_calls

        if tokens_used is not None:
            stats.tokens_used = tokens_used

        if metadata_updates:
            stats.metadata.update(metadata_updates)

        # Remove from active operations
        del self._active_operations[operation_id]

        # Persist to storage if path provided
        if self.storage_path:
            try:
                # Store in a structured way - by date for easy retrieval
                date_str = datetime.utcnow().strftime("%Y-%m-%d")
                full_path = Path(self.storage_path) / "stats" / date_str
                full_path.mkdir(parents=True, exist_ok=True)

                storage_file = full_path / f"{operation_id}.json"
                with open(storage_file, 'w', encoding='utf-8') as f:
                    json.dump(stats.dict(), f, default=str, indent=2)
            except Exception as e:
                # Silently fail to avoid disrupting the main operation
                print(f"Warning: Could not save statistics to storage: {e}")

        return stats

    def track_resource_usage(
        self,
        operation_id: str,
        api_calls: int = 0,
        tokens_used: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track resource usage during an active operation.

        Args:
            operation_id: ID of the operation to update
            api_calls: Additional API calls to record
            tokens_used: Additional tokens to record
            metadata: Additional metadata to add

        Returns:
            True if operation was found and updated, False otherwise
        """
        if not self.enabled:
            return False

        if operation_id not in self._active_operations:
            return False

        stats = self._active_operations[operation_id]

        # Update resource usage
        stats.api_calls += api_calls
        stats.tokens_used += tokens_used

        # Update metadata
        if metadata:
            stats.metadata.update(metadata)

        return True

    def get_active_operations(self) -> List[PerformanceStatistics]:
        """Get all currently active operations."""
        return list(self._active_operations.values())

    def get_operation_count(self) -> int:
        """Get the count of currently active operations."""
        return len(self._active_operations)

    def shutdown(self) -> None:
        """Shutdown the collector and finalize any remaining operations."""
        # Mark all remaining active operations as failed/cancelled
        for operation_id in list(self._active_operations.keys()):
            self.complete_operation(
                operation_id,
                success=False,
                error_message="Operation cancelled during shutdown"
            )