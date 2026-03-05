"""Persistent storage for performance statistics."""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiosqlite

from .models import PerformanceStatistics


class StatisticsStorage:
    """Handles persistent storage of performance statistics."""

    def __init__(self, db_path: str = "./dcae_stats.db"):
        """
        Initialize the statistics storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialized = False

    async def initialize(self):
        """Initialize the database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            # Create table for statistics
            await db.execute('''
                CREATE TABLE IF NOT EXISTS performance_stats (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    operation_type TEXT NOT NULL,
                    operation_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_ms REAL,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    api_calls INTEGER DEFAULT 0,
                    tokens_used INTEGER DEFAULT 0,
                    model_used TEXT,
                    metadata_json TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create indexes for faster queries
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_start_time ON performance_stats(start_time)
            ''')

            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_operation_type ON performance_stats(operation_type)
            ''')

            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_project_id ON performance_stats(project_id)
            ''')

            await db.commit()

        self._initialized = True

    async def store_statistic(self, stat: PerformanceStatistics) -> bool:
        """
        Store a single statistic record.

        Args:
            stat: PerformanceStatistics object to store

        Returns:
            True if successful, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO performance_stats (
                        id, project_id, operation_type, operation_name,
                        start_time, end_time, duration_ms, success,
                        error_message, api_calls, tokens_used, model_used, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stat.id, stat.project_id, stat.operation_type.value, stat.operation_name,
                    stat.start_time.isoformat(),
                    stat.end_time.isoformat() if stat.end_time else None,
                    stat.duration_ms, stat.success, stat.error_message,
                    stat.api_calls, stat.tokens_used, stat.model_used,
                    json.dumps(stat.metadata) if stat.metadata else '{}'
                ))

                await db.commit()
                return True

        except Exception as e:
            print(f"Error storing statistic: {e}")
            return False

    async def store_statistics_batch(self, stats: List[PerformanceStatistics]) -> int:
        """
        Store multiple statistics records in a batch.

        Args:
            stats: List of PerformanceStatistics objects to store

        Returns:
            Number of successfully stored records
        """
        if not self._initialized:
            await self.initialize()

        success_count = 0

        try:
            async with aiosqlite.connect(self.db_path) as db:
                for stat in stats:
                    try:
                        await db.execute('''
                            INSERT INTO performance_stats (
                                id, project_id, operation_type, operation_name,
                                start_time, end_time, duration_ms, success,
                                error_message, api_calls, tokens_used, model_used, metadata_json
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            stat.id, stat.project_id, stat.operation_type.value, stat.operation_name,
                            stat.start_time.isoformat(),
                            stat.end_time.isoformat() if stat.end_time else None,
                            stat.duration_ms, stat.success, stat.error_message,
                            stat.api_calls, stat.tokens_used, stat.model_used,
                            json.dumps(stat.metadata) if stat.metadata else '{}'
                        ))
                        success_count += 1
                    except Exception as e:
                        print(f"Error storing statistic {stat.id}: {e}")

                await db.commit()

        except Exception as e:
            print(f"Error in batch storage: {e}")

        return success_count

    async def get_statistics_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        project_id: Optional[str] = None,
        operation_type: Optional[str] = None
    ) -> List[PerformanceStatistics]:
        """
        Retrieve statistics within a date range with optional filters.

        Args:
            start_date: Start of date range
            end_date: End of date range
            project_id: Optional project ID to filter by
            operation_type: Optional operation type to filter by

        Returns:
            List of PerformanceStatistics objects
        """
        if not self._initialized:
            await self.initialize()

        # Build query with filters
        query = '''
            SELECT id, project_id, operation_type, operation_name,
                   start_time, end_time, duration_ms, success,
                   error_message, api_calls, tokens_used, model_used, metadata_json
            FROM performance_stats
            WHERE start_time BETWEEN ? AND ?
        '''
        params = [start_date.isoformat(), end_date.isoformat()]

        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)

        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)

        query += " ORDER BY start_time DESC"

        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()

                    stats = []
                    for row in rows:
                        # Parse datetime strings back to datetime objects
                        start_time = datetime.fromisoformat(row[4])
                        end_time = datetime.fromisoformat(row[5]) if row[5] else None

                        # Parse metadata JSON
                        metadata = json.loads(row[12]) if row[12] else {}

                        stat = PerformanceStatistics(
                            id=row[0],
                            project_id=row[1],
                            operation_type=row[2],
                            operation_name=row[3],
                            start_time=start_time,
                            end_time=end_time,
                            duration_ms=row[6],
                            success=bool(row[7]),
                            error_message=row[8],
                            api_calls=row[9],
                            tokens_used=row[10],
                            model_used=row[11],
                            metadata=metadata
                        )
                        stats.append(stat)

                    return stats

        except Exception as e:
            print(f"Error retrieving statistics: {e}")
            return []

    async def get_statistics_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        project_id: Optional[str] = None
    ) -> int:
        """
        Get the count of stored statistics with optional filters.

        Args:
            start_date: Start of date range (optional)
            end_date: End of date range (optional)
            project_id: Optional project ID to filter by

        Returns:
            Count of matching statistics
        """
        if not self._initialized:
            await self.initialize()

        query = "SELECT COUNT(*) FROM performance_stats"
        params = []

        conditions = []
        if start_date:
            conditions.append("start_time >= ?")
            params.append(start_date.isoformat())

        if end_date:
            conditions.append("start_time <= ?")
            params.append(end_date.isoformat())

        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(query, params) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0

        except Exception as e:
            print(f"Error getting statistics count: {e}")
            return 0

    async def cleanup_old_records(self, days_to_keep: int = 30) -> int:
        """
        Remove statistics older than specified number of days.

        Args:
            days_to_keep: Number of days to keep records (default 30)

        Returns:
            Number of records removed
        """
        if not self._initialized:
            await self.initialize()

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM performance_stats WHERE start_time < ?",
                    (cutoff_date.isoformat(),)
                )
                changes = db.total_changes
                await db.commit()
                return changes

        except Exception as e:
            print(f"Error cleaning up old records: {e}")
            return 0

    async def close(self):
        """Close the database connection."""
        # Database connections are managed per operation in aiosqlite
        # Nothing specific needed here
        pass