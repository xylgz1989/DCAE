import asyncio
import sys
import os
# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import AsyncMock, MagicMock
from dcae.task_management.task_manager import task_manager, TaskStatus


@pytest.mark.asyncio
async def test_create_task():
    """Test creating a new task."""
    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create a simple task
    async def dummy_task(task_id):
        await asyncio.sleep(0.1)
        return "completed"

    task_id = await task_manager.create_task(
        name="Test Task",
        coroutine_func=dummy_task
    )

    # Verify task was created
    assert task_id is not None
    task_info = await task_manager.get_task_info(task_id)
    assert task_info is not None
    assert task_info.name == "Test Task"
    assert task_info.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_start_task():
    """Test starting a task."""
    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create a task
    async def dummy_task(task_id):
        await asyncio.sleep(0.1)
        return "completed"

    task_id = await task_manager.create_task(
        name="Start Test Task",
        coroutine_func=dummy_task
    )

    # Start the task
    success = await task_manager.start_task(task_id)
    assert success is True

    # Check that task status changed to running
    task_info = await task_manager.get_task_info(task_id)
    assert task_info.status == TaskStatus.RUNNING


@pytest.mark.asyncio
async def test_task_completion():
    """Test that a task completes successfully."""
    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create a task that completes quickly
    async def quick_task(task_id):
        await asyncio.sleep(0.1)
        return "quick task done"

    task_id = await task_manager.create_task(
        name="Quick Task",
        coroutine_func=quick_task
    )

    # Start the task
    await task_manager.start_task(task_id)

    # Wait for completion
    await task_manager.wait_for_task(task_id)

    # Verify task completed
    task_info = await task_manager.get_task_info(task_id)
    assert task_info.status == TaskStatus.COMPLETED
    assert task_info.result is not None


@pytest.mark.asyncio
async def test_task_progress():
    """Test task progress updates."""
    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create a task that updates progress
    async def progress_task(task_id):
        for i in range(10):
            await asyncio.sleep(0.05)  # Small delay to allow for progress updates
            progress = (i + 1) * 10
            await task_manager.update_task_progress(task_id, progress, f"Step {i+1}/10")
        return "progress task done"

    task_id = await task_manager.create_task(
        name="Progress Task",
        coroutine_func=progress_task
    )

    # Start the task
    await task_manager.start_task(task_id)

    # Allow some time for progress updates
    await asyncio.sleep(0.2)

    # Check initial progress
    task_info = await task_manager.get_task_info(task_id)
    assert task_info.progress > 0
    assert task_info.progress_message != ""

    # Wait for completion
    await task_manager.wait_for_task(task_id)

    # Verify final progress
    task_info = await task_manager.get_task_info(task_id)
    assert task_info.status == TaskStatus.COMPLETED
    assert task_info.progress == 100.0


@pytest.mark.asyncio
async def test_cancel_task():
    """Test cancelling a running task."""
    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create a long-running task
    async def long_task(task_id):
        for i in range(10):
            await asyncio.sleep(0.1)
            await task_manager.update_task_progress(task_id, (i + 1) * 10, f"Step {i+1}/10")
        return "long task done"

    task_id = await task_manager.create_task(
        name="Long Task",
        coroutine_func=long_task
    )

    # Start the task
    await task_manager.start_task(task_id)

    # Give the task some time to start
    await asyncio.sleep(0.2)

    # Cancel the task
    success = await task_manager.cancel_task(task_id)
    assert success is True

    # Check that task status is cancelled
    task_info = await task_manager.get_task_info(task_id)
    assert task_info.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_multiple_tasks():
    """Test running multiple tasks concurrently."""
    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create multiple tasks
    task_ids = []
    for i in range(3):
        async def make_task(n):
            async def task_func(task_id):
                await asyncio.sleep(0.1)
                return f"task {n} done"
            return task_func

        task_id = await task_manager.create_task(
            name=f"Task {i}",
            coroutine_func=make_task(i)
        )
        task_ids.append(task_id)

    # Start all tasks
    started_tasks = await task_manager.start_all_tasks()
    assert len(started_tasks) == 3

    # Wait for all to complete
    await task_manager.wait_for_all_tasks()

    # Verify all tasks completed
    all_tasks = await task_manager.get_all_tasks()
    assert len(all_tasks) == 3
    for task in all_tasks:
        assert task.status == TaskStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])