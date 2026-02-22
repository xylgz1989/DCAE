"""Test SQLite storage."""

import pytest
from dcae.storage import SQLiteStorage
from dcae.models import DecisionRecord, ConsensusResult, ConsensusStatus


@pytest.mark.asyncio
async def test_storage_initialize():
    """Test storage initialization."""
    storage = SQLiteStorage(":memory:")
    await storage.initialize()

    # Tables should be created without error
    assert True


@pytest.mark.asyncio
async def test_log_and_get_decision():
    """Test logging and retrieving a decision."""
    storage = SQLiteStorage(":memory:")
    await storage.initialize()

    from datetime import datetime

    decision = DecisionRecord(
        id="test-id",
        timestamp=datetime.now(),
        agent="pm",
        task="Test task",
        skill=None,
        consensus_enabled=False,
        consensus_result=None,
        output="Test output",
    )

    await storage.log_decision(decision)

    retrieved = await storage.get_decision("test-id")
    assert retrieved is not None
    assert retrieved.agent == "pm"
    assert retrieved.task == "Test task"
