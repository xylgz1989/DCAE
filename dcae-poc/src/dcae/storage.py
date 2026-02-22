"""Storage layer for DCAE - SQLite implementation."""

import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import ConsensusResult, DecisionRecord


class SQLiteStorage:
    """SQLite storage for decisions and consensus results."""

    def __init__(self, db_path: str = "./dcae-poc.db"):
        """Initialize storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None
        self._is_memory = str(db_path) == ":memory:"

    async def initialize(self):
        """Create database tables if they don't exist."""
        # For in-memory databases, keep a single connection
        if self._is_memory:
            self._connection = await aiosqlite.connect(self.db_path)
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                agent TEXT NOT NULL,
                task TEXT NOT NULL,
                skill TEXT,
                consensus_enabled BOOLEAN NOT NULL,
                output TEXT NOT NULL,
                consensus_result TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS consensus_votes (
                id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                model TEXT NOT NULL,
                output TEXT NOT NULL,
                approved BOOLEAN NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT,
                duration_ms INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (decision_id) REFERENCES decisions(id)
            )
        """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                step_order INTEGER NOT NULL,
                agent TEXT NOT NULL,
                task TEXT NOT NULL,
                skill TEXT,
                status TEXT NOT NULL,
                output TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id)
            )
        """
        )

        await db.commit()

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

    async def log_decision(self, decision: DecisionRecord):
        """Log a decision to storage.

        Args:
            decision: DecisionRecord to log
        """
        if self._connection:
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        await db.execute(
            """
            INSERT INTO decisions
            (id, timestamp, agent, task, skill, consensus_enabled, output, consensus_result, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                decision.id,
                decision.timestamp.isoformat(),
                decision.agent,
                decision.task,
                decision.skill,
                decision.consensus_enabled,
                decision.output,
                json.dumps(decision.consensus_result.to_dict()) if decision.consensus_result else None,
                json.dumps(decision.metadata),
            ),
        )

        # Log individual votes if consensus was used
        if decision.consensus_result and decision.consensus_result.votes:
            for vote in decision.consensus_result.votes:
                await db.execute(
                    """
                    INSERT INTO consensus_votes
                    (id, decision_id, model, output, approved, confidence, reasoning, duration_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"{decision.id}-{vote.model}",
                        decision.id,
                        vote.model,
                        vote.output,
                        vote.approved,
                        vote.confidence,
                        vote.reasoning,
                        vote.duration_ms,
                    ),
                )

        await db.commit()

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

    async def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        """Get a decision by ID.

        Args:
            decision_id: Decision ID

        Returns:
            DecisionRecord or None
        """
        if self._connection:
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM decisions WHERE id = ?", (decision_id,)
        )
        row = await cursor.fetchone()

        if row:
            return DecisionRecord(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                agent=row["agent"],
                task=row["task"],
                skill=row["skill"],
                consensus_enabled=row["consensus_enabled"],
                output=row["output"],
                consensus_result=None,  # Would need to deserialize
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            )

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

        return None

    async def get_decisions_by_agent(self, agent: str) -> List[DecisionRecord]:
        """Get all decisions for a specific agent.

        Args:
            agent: Agent name

        Returns:
            List of DecisionRecord
        """
        if self._connection:
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM decisions WHERE agent = ? ORDER BY timestamp DESC",
            (agent,),
        )
        rows = await cursor.fetchall()

        result = [
            DecisionRecord(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                agent=row["agent"],
                task=row["task"],
                skill=row["skill"],
                consensus_enabled=row["consensus_enabled"],
                output=row["output"],
                consensus_result=None,
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            )
            for row in rows
        ]

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

        return result

    async def start_workflow(
        self, workflow_id: str, name: str, description: str = ""
    ):
        """Start a workflow execution.

        Args:
            workflow_id: Workflow ID
            name: Workflow name
            description: Workflow description
        """
        if self._connection:
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        await db.execute(
            """
            INSERT INTO workflows (id, name, description, status, started_at)
            VALUES (?, ?, ?, 'in_progress', ?)
        """,
            (workflow_id, name, description, datetime.now().isoformat()),
        )
        await db.commit()

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

    async def complete_workflow(self, workflow_id: str, status: str = "completed"):
        """Mark a workflow as completed.

        Args:
            workflow_id: Workflow ID
            status: Final status
        """
        if self._connection:
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        await db.execute(
            """
            UPDATE workflows SET status = ?, completed_at = ? WHERE id = ?
        """,
            (status, datetime.now().isoformat(), workflow_id),
        )
        await db.commit()

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

    async def log_workflow_step(
        self,
        workflow_id: str,
        step_id: str,
        step_order: int,
        agent: str,
        task: str,
        skill: Optional[str],
        status: str,
        output: str = "",
    ):
        """Log a workflow step execution.

        Args:
            workflow_id: Workflow ID
            step_id: Step ID
            step_order: Step order
            agent: Agent name
            task: Task description
            skill: Skill used
            status: Step status
            output: Step output
        """
        if self._connection:
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        await db.execute(
            """
            INSERT INTO workflow_steps
            (id, workflow_id, step_order, agent, task, skill, status, output)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                step_id,
                workflow_id,
                step_order,
                agent,
                task,
                skill,
                status,
                output,
            ),
        )
        await db.commit()

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow execution status.

        Args:
            workflow_id: Workflow ID

        Returns:
            Dictionary with workflow status or None
        """
        if self._connection:
            db = self._connection
        else:
            db = await aiosqlite.connect(self.db_path)

        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT * FROM workflows WHERE id = ?", (workflow_id,)
        )
        workflow_row = await cursor.fetchone()

        if not workflow_row:
            if not self._is_memory:
                await db.close()
            return None

        cursor = await db.execute(
            "SELECT * FROM workflow_steps WHERE workflow_id = ? ORDER BY step_order",
            (workflow_id,),
        )
        step_rows = await cursor.fetchall()

        result = {
            "workflow": dict(workflow_row),
            "steps": [dict(row) for row in step_rows],
        }

        # For file-based databases, close the connection
        if not self._is_memory:
            await db.close()

        return result

    async def close(self):
        """Close the database connection (for in-memory databases)."""
        if self._connection:
            await self._connection.close()
            self._connection = None
