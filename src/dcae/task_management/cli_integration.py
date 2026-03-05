"""
Task Management Integration for DCAE CLI

This module adds task management functionality to the DCAE CLI.
"""

import asyncio
import argparse
from datetime import datetime
from typing import Optional
from pathlib import Path

from .task_manager import task_manager, TaskStatus


def add_task_management_to_parser(parser):
    """Add task management subcommands to the main parser."""
    task_parser = parser.add_parser("tasks", aliases=['task'], help="Manage tasks")
    list_subparsers = task_parser.add_subparsers(dest="task_action", help="Task actions")

    # List all tasks
    list_subparsers.add_parser("list", aliases=['ls'], help="List all tasks")

    # Get specific task
    get_parser = list_subparsers.add_parser("get", help="Get specific task details")
    get_parser.add_argument("task_id", help="Task ID to retrieve")

    # Summary of tasks
    list_subparsers.add_parser("summary", help="Get task summary")

    # Task creation and management
    create_parser = list_subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("name", help="Name of the task")
    create_parser.add_argument("--description", "-d", help="Task description")

    # Start tasks
    start_parser = list_subparsers.add_parser("start", help="Start a task")
    start_parser.add_argument("task_id", help="Task ID to start")

    start_parser_all = list_subparsers.add_parser("start-all", help="Start all pending tasks")

    # Cancel tasks
    cancel_parser = list_subparsers.add_parser("cancel", help="Cancel a task")
    cancel_parser.add_argument("task_id", help="Task ID to cancel")

    cancel_parser_all = list_subparsers.add_parser("cancel-all", help="Cancel all running tasks")

    # Wait for tasks
    wait_parser = list_subparsers.add_parser("wait", help="Wait for a task to complete")
    wait_parser.add_argument("task_id", help="Task ID to wait for")
    wait_parser.add_argument("--timeout", type=int, default=None, help="Timeout in seconds")

    # Clear completed tasks
    list_subparsers.add_parser("clear", help="Clear completed tasks")


def format_task_info(task_info) -> str:
    """Format task information for display."""
    status_icons = {
        TaskStatus.PENDING: "[PND]",
        TaskStatus.RUNNING: "[RUN]",
        TaskStatus.COMPLETED: "[CMP]",
        TaskStatus.FAILED: "[FLD]",
        TaskStatus.CANCELLED: "[CNL]"
    }

    status_icon = status_icons.get(task_info.status, "?")
    status_text = task_info.status.value.upper()

    result = f"{status_icon} {task_info.name} [{task_info.task_id[:8]}]\n"
    result += f"   Status: {status_text}\n"
    result += f"   Created: {task_info.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

    if task_info.started_at:
        result += f"   Started: {task_info.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

    if task_info.completed_at:
        result += f"   Completed: {task_info.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"

    if task_info.status == TaskStatus.RUNNING:
        result += f"   Progress: {task_info.progress:.1f}% - {task_info.progress_message}\n"
    elif task_info.status == TaskStatus.FAILED and task_info.error:
        result += f"   Error: {task_info.error}\n"

    return result


async def handle_task_command(args):
    """Handle task management commands."""
    if args.task_action == "list" or args.task_action == "ls":
        await _handle_list_tasks()

    elif args.task_action == "get":
        await _handle_get_task(args.task_id)

    elif args.task_action == "summary":
        await _handle_task_summary()

    elif args.task_action == "create":
        await _handle_create_task(args.name, getattr(args, 'description', None))

    elif args.task_action == "start":
        await _handle_start_task(args.task_id)

    elif args.task_action == "start-all":
        await _handle_start_all_tasks()

    elif args.task_action == "cancel":
        await _handle_cancel_task(args.task_id)

    elif args.task_action == "cancel-all":
        await _handle_cancel_all_tasks()

    elif args.task_action == "wait":
        await _handle_wait_for_task(args.task_id, args.timeout)

    elif args.task_action == "clear":
        await _handle_clear_completed_tasks()

    else:
        print("Invalid task action. Use --help for available options.")


async def _handle_list_tasks():
    """Handle listing all tasks."""
    tasks = await task_manager.get_all_tasks()

    if not tasks:
        print("No tasks found.")
        return

    print(f"\n📋 Found {len(tasks)} task(s):\n")
    for i, task in enumerate(tasks):
        print(format_task_info(task))
        if i < len(tasks) - 1:  # Add separator between tasks
            print()


async def _handle_get_task(task_id: str):
    """Handle getting a specific task."""
    task_info = await task_manager.get_task_info(task_id)

    if not task_info:
        print(f"[X] Task not found: {task_id[:8]}")
        return

    print("\n📋 Task Details:")
    print(format_task_info(task_info))


async def _handle_task_summary():
    """Handle showing task summary."""
    summary = await task_manager.get_tasks_summary()

    print("\n📊 Task Summary:")
    total = sum(summary.values())
    print(f"   Total: {total}")

    for status, count in summary.items():
        status_name = status.replace('_', ' ').title()
        print(f"   {status_name}: {count}")


async def _handle_create_task(name: str, description: Optional[str] = None):
    """Handle creating a new task."""
    # Define a dummy task function for demonstration
    async def demo_task_func(task_id: str):
        import random
        steps = [
            "Initializing...",
            "Loading data...",
            "Processing data...",
            "Validating results...",
            "Saving outputs...",
            "Cleaning up..."
        ]

        for i, step in enumerate(steps):
            await asyncio.sleep(0.5)  # Simulate work
            progress = ((i + 1) / len(steps)) * 100
            await task_manager.update_task_progress(task_id, progress, step)

        return f"Demo task '{name}' completed successfully!"

    # Create metadata for the task
    metadata = {"created_at": datetime.now().isoformat()}
    if description:
        metadata["description"] = description

    # Create the task
    task_id = await task_manager.create_task(
        name=name,
        coroutine_func=demo_task_func,
        metadata=metadata
    )

    print(f"Created task: {task_id[:8]} - {name}")
    if description:
        print(f"   Description: {description}")


async def _handle_start_task(task_id: str):
    """Handle starting a specific task."""
    success = await task_manager.start_task(task_id)

    if success:
        print(f"[OK] Started task: {task_id[:8]}")
    else:
        task_info = await task_manager.get_task_info(task_id)
        if not task_info:
            print(f"[X] Task not found: {task_id[:8]}")
        elif task_info.status != TaskStatus.PENDING:
            print(f"❌ Task {task_id[:8]} is not in pending state (currently: {task_info.status.value})")


async def _handle_start_all_tasks():
    """Handle starting all pending tasks."""
    started_tasks = await task_manager.start_all_tasks()
    print(f"[OK] Started {len(started_tasks)} pending task(s)")


async def _handle_cancel_task(task_id: str):
    """Handle cancelling a specific task."""
    success = await task_manager.cancel_task(task_id)

    if success:
        print(f"[OK] Cancelled task: {task_id[:8]}")
    else:
        task_info = await task_manager.get_task_info(task_id)
        if not task_info:
            print(f"[X] Task not found: {task_id[:8]}")
        else:
            print(f"❌ Cannot cancel task {task_id[:8]} (status: {task_info.status.value})")


async def _handle_cancel_all_tasks():
    """Handle cancelling all running tasks."""
    cancelled_count = await task_manager.cancel_all_tasks()
    print(f"[OK] Cancelled {cancelled_count} running task(s)")


async def _handle_wait_for_task(task_id: str, timeout: Optional[int] = None):
    """Handle waiting for a specific task to complete."""
    print(f"⏳ Waiting for task {task_id[:8]} to complete...")

    success = await task_manager.wait_for_task(task_id, timeout)

    if success:
        task_info = await task_manager.get_task_info(task_id)
        print(f"[OK] Task completed with status: {task_info.status.value}")

        if task_info.status == TaskStatus.FAILED and task_info.error:
            print(f"   Error: {task_info.error}")
    else:
        print(f"[WAIT] Timeout waiting for task: {task_id[:8]}")


async def _handle_clear_completed_tasks():
    """Handle clearing completed tasks."""
    cleared_count = await task_manager.clear_completed_tasks()
    print(f"[DEL] Cleared {cleared_count} completed/failed/cancelled task(s)")


# Example integration function for use in the main CLI
async def run_task_demo():
    """Run a demonstration of task management capabilities."""
    print("DCAE Task Management Demo")
    print("=" * 40)

    # Create some sample tasks
    print("\n[LIST] Creating sample tasks...")
    task1_id = await task_manager.create_task(
        name="Data Processing Task",
        coroutine_func=lambda task_id: _demo_task_work(task_id, "processing data", 3)
    )

    task2_id = await task_manager.create_task(
        name="Report Generation Task",
        coroutine_func=lambda task_id: _demo_task_work(task_id, "generating report", 2)
    )

    print(f"   Created: {task1_id[:8]} - Data Processing Task")
    print(f"   Created: {task2_id[:8]} - Report Generation Task")

    # Start tasks
    print("\n[START] Starting tasks...")
    await task_manager.start_all_tasks()

    # Monitor progress
    print("\n[MON] Monitoring progress...")
    while await task_manager.get_active_tasks_count() > 0:
        await asyncio.sleep(0.5)
        tasks = await task_manager.get_all_tasks()
        running_tasks = [t for t in tasks if t.status == TaskStatus.RUNNING]

        for task in running_tasks:
            print(f"   {task.name}: {task.progress:.1f}% - {task.progress_message}")

    # Show results
    print("\n[RES] Task Results:")
    all_tasks = await task_manager.get_all_tasks()
    for task in all_tasks:
        print(f"   {task.name}: {task.status.value}")

    summary = await task_manager.get_tasks_summary()
    print(f"\n[SUM] Summary: {summary}")


async def _demo_task_work(task_id: str, work_type: str, duration: int):
    """Helper function for demo task work."""
    steps = [f"Initializing {work_type}...", f"Performing {work_type}...", f"Finalizing {work_type}..."]

    for i, step in enumerate(steps):
        await asyncio.sleep(duration / len(steps))  # Simulate work
        progress = ((i + 1) / len(steps)) * 100
        await task_manager.update_task_progress(task_id, progress, step)

    return f"Demo task completed: {work_type}"