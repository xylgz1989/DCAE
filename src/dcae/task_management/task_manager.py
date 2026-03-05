"""
Enhanced Task Management System for DCAE

This module provides functionality to manage multiple concurrent tasks
through a unified interface, allowing parallel execution and control.
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Awaitable
from dataclasses import dataclass, field
from pathlib import Path
import logging


class TaskStatus(Enum):
    """Enum representing possible task statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskInfo:
    """Information about a specific task."""
    task_id: str
    name: str
    status: TaskStatus
    coroutine_func: Optional[Callable[[str], Awaitable[Any]]] = None  # Store the function
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # Progress percentage (0.0 to 100.0)
    progress_message: str = ""
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskManager:
    """Manages multiple concurrent tasks."""

    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}
        self._task_lock = asyncio.Lock()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger(__name__)

    async def create_task(
        self,
        name: str,
        coroutine_func: Callable[[str], Awaitable[Any]],  # Function that takes task_id as param
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new task with the given name and coroutine function."""
        if task_id is None:
            task_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}

        async with self._task_lock:
            task_info = TaskInfo(
                task_id=task_id,
                name=name,
                status=TaskStatus.PENDING,
                coroutine_func=coroutine_func,
                metadata=metadata
            )
            self._tasks[task_id] = task_info

        return task_id

    async def start_task(self, task_id: str) -> bool:
        """Start execution of a task."""
        async with self._task_lock:
            if task_id not in self._tasks:
                return False

            task_info = self._tasks[task_id]
            if task_info.status != TaskStatus.PENDING:
                return False

            task_info.status = TaskStatus.RUNNING
            task_info.started_at = datetime.now()

        # Create and store the asyncio task
        coro = self._execute_task(task_id)
        asyncio_task = asyncio.create_task(coro)
        self._running_tasks[task_id] = asyncio_task

        return True

    async def _execute_task(self, task_id: str):
        """Execute the actual task coroutine and handle completion."""
        try:
            async with self._task_lock:
                if task_id not in self._tasks:
                    return  # Task was removed

                task_info = self._tasks[task_id]

                # Check if there's a specific coroutine function for this task
                if task_info.coroutine_func:
                    # Execute the stored coroutine function
                    result = await task_info.coroutine_func(task_id)
                    task_info.result = result
                else:
                    # Fallback: simulate work with progress updates
                    await self.update_task_progress(task_id, 10.0, "Initializing...")

                    # Simulate work with progress updates
                    for i in range(1, 11):
                        await asyncio.sleep(0.2)  # Simulate work
                        progress = i * 10.0
                        await self.update_task_progress(task_id, progress, f"Processing step {i}/10")

            async with self._task_lock:
                if task_id in self._tasks:
                    task_info = self._tasks[task_id]
                    task_info.status = TaskStatus.COMPLETED
                    task_info.completed_at = datetime.now()
                    task_info.progress = 100.0
                    if task_info.result is None:
                        task_info.result = f"Completed task: {task_info.name}"

        except asyncio.CancelledError:
            # Handle task cancellation
            async with self._task_lock:
                if task_id in self._tasks:
                    task_info = self._tasks[task_id]
                    task_info.status = TaskStatus.CANCELLED
                    task_info.completed_at = datetime.now()
                    task_info.progress_message = "Task cancelled by user"

                    # Remove from running tasks
                    if task_id in self._running_tasks:
                        del self._running_tasks[task_id]

            raise  # Re-raise to properly cancel
        except Exception as e:
            async with self._task_lock:
                if task_id in self._tasks:
                    task_info = self._tasks[task_id]
                    task_info.status = TaskStatus.FAILED
                    task_info.completed_at = datetime.now()
                    task_info.error = str(e)

    async def start_all_tasks(self) -> List[str]:
        """Start all pending tasks."""
        pending_tasks = []
        async with self._task_lock:
            for task_id, task_info in self._tasks.items():
                if task_info.status == TaskStatus.PENDING:
                    pending_tasks.append(task_id)

        started_tasks = []
        for task_id in pending_tasks:
            success = await self.start_task(task_id)
            if success:
                started_tasks.append(task_id)

        return started_tasks

    async def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """Get information about a specific task."""
        async with self._task_lock:
            return self._tasks.get(task_id)

    async def get_all_tasks(self) -> List[TaskInfo]:
        """Get information about all tasks."""
        async with self._task_lock:
            return list(self._tasks.values())

    async def get_tasks_by_status(self, status: TaskStatus) -> List[TaskInfo]:
        """Get all tasks with a specific status."""
        async with self._task_lock:
            return [task for task in self._tasks.values() if task.status == status]

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        async with self._task_lock:
            if task_id not in self._tasks:
                return False

            task_info = self._tasks[task_id]
            if task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return False  # Cannot cancel completed/failed/cancelled tasks

            # Cancel the asyncio task if it exists
            if task_id in self._running_tasks:
                self._running_tasks[task_id].cancel()

            return True

    async def cancel_all_tasks(self) -> int:
        """Cancel all running tasks."""
        async with self._task_lock:
            running_task_ids = [
                tid for tid, tinfo in self._tasks.items()
                if tinfo.status == TaskStatus.RUNNING
            ]

        cancelled_count = 0
        for task_id in running_task_ids:
            success = await self.cancel_task(task_id)
            if success:
                cancelled_count += 1

        return cancelled_count

    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for a specific task to complete."""
        async with self._task_lock:
            if task_id not in self._running_tasks:
                return True  # Already finished or not running

            asyncio_task = self._running_tasks[task_id]

        try:
            await asyncio.wait_for(asyncio_task, timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> bool:
        """Wait for all running tasks to complete."""
        async with self._task_lock:
            running_asyncio_tasks = list(self._running_tasks.values())

        if not running_asyncio_tasks:
            return True

        try:
            await asyncio.wait_for(
                asyncio.gather(*running_asyncio_tasks, return_exceptions=True),
                timeout=timeout
            )
            return True
        except asyncio.TimeoutError:
            return False

    async def update_task_progress(self, task_id: str, progress: float, message: str = "") -> bool:
        """Update the progress of a running task."""
        async with self._task_lock:
            if task_id not in self._tasks:
                return False

            task_info = self._tasks[task_id]
            if task_info.status != TaskStatus.RUNNING:
                return False  # Only update progress for running tasks

            task_info.progress = max(0.0, min(100.0, progress))  # Clamp between 0-100
            if message:
                task_info.progress_message = message

            return True

    async def get_active_tasks_count(self) -> int:
        """Get the count of currently active (running) tasks."""
        async with self._task_lock:
            return len([t for t in self._tasks.values() if t.status == TaskStatus.RUNNING])

    async def get_tasks_summary(self) -> Dict[str, int]:
        """Get a summary of tasks by status."""
        summary = {status.value: 0 for status in TaskStatus}

        async with self._task_lock:
            for task in self._tasks.values():
                summary[task.status.value] += 1

        return summary

    async def clear_completed_tasks(self) -> int:
        """Remove all completed and failed tasks from the manager."""
        async with self._task_lock:
            completed_task_ids = [
                tid for tid, tinfo in self._tasks.items()
                if tinfo.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            ]

            for task_id in completed_task_ids:
                # Remove from running tasks if present
                if task_id in self._running_tasks:
                    del self._running_tasks[task_id]

                # Remove from tasks
                del self._tasks[task_id]

        return len(completed_task_ids)


# Global task manager instance
task_manager = TaskManager()


async def run_example_tasks():
    """Example usage of the task manager."""
    print("Creating example tasks...")

    # Create some sample tasks
    async def sample_task_func(task_id: str):
        """Example task function that simulates work."""
        for i in range(10):
            await asyncio.sleep(0.2)
            progress = (i + 1) * 10
            await task_manager.update_task_progress(task_id, progress, f"Step {i+1}/10 completed")
        return f"Task completed successfully!"

    task1_id = await task_manager.create_task(
        name="Data Processing Task",
        coroutine_func=sample_task_func
    )

    task2_id = await task_manager.create_task(
        name="File Analysis Task",
        coroutine_func=sample_task_func
    )

    task3_id = await task_manager.create_task(
        name="Report Generation Task",
        coroutine_func=sample_task_func
    )

    print(f"Created tasks: {task1_id[:8]}, {task2_id[:8]}, {task3_id[:8]}")

    # Start all tasks
    started_tasks = await task_manager.start_all_tasks()
    print(f"Started {len(started_tasks)} tasks")

    # Monitor progress
    print("\nMonitoring progress:")
    while await task_manager.get_active_tasks_count() > 0:
        await asyncio.sleep(0.5)
        tasks = await task_manager.get_all_tasks()
        running_tasks = [t for t in tasks if t.status == TaskStatus.RUNNING]

        for task in running_tasks:
            print(f"  {task.name}: {task.progress:.1f}% - {task.progress_message}")

    # Show results
    print("\nTask results:")
    all_tasks = await task_manager.get_all_tasks()
    for task in all_tasks:
        print(f"  {task.name}: {task.status.value}")
        if task.error:
            print(f"    Error: {task.error}")

    summary = await task_manager.get_tasks_summary()
    print(f"\nSummary: {summary}")

    return all_tasks


if __name__ == "__main__":
    asyncio.run(run_example_tasks())