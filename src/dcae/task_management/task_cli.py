"""
CLI interface for the Task Manager in DCAE
"""
import asyncio
import argparse
from typing import List
from dcae.task_management.task_manager import task_manager, TaskStatus, TaskInfo


def format_task_info(task_info: TaskInfo) -> str:
    """Format task information for display."""
    status_icon = {
        TaskStatus.PENDING: "⏳",
        TaskStatus.RUNNING: "🏃",
        TaskStatus.COMPLETED: "✅",
        TaskStatus.FAILED: "❌",
        TaskStatus.CANCELLED: "🚫"
    }.get(task_info.status, "?")

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


async def list_tasks(args):
    """List all tasks or filter by status."""
    if args.status:
        try:
            status = TaskStatus(args.status.lower())
            tasks = await task_manager.get_tasks_by_status(status)
        except ValueError:
            print(f"Invalid status: {args.status}")
            return
    else:
        tasks = await task_manager.get_all_tasks()

    if not tasks:
        print("No tasks found.")
        return

    print(f"\nFound {len(tasks)} task(s):\n")
    for task in tasks:
        print(format_task_info(task))


async def create_task(args):
    """Create a new task."""
    # For demonstration purposes, we'll create a simple task that just waits
    async def dummy_task(task_id: str):
        import random
        steps = ["Initializing", "Processing", "Cleaning up", "Finalizing"]
        for i, step in enumerate(steps):
            await asyncio.sleep(0.5)  # Simulate work
            progress = (i + 1) * 25
            await task_manager.update_task_progress(task_id, progress, f"{step}...")
        return "Task completed successfully!"

    task_id = await task_manager.create_task(
        name=args.name,
        coroutine_func=dummy_task,
        metadata={"type": "demo", "created_by": "cli"}
    )

    print(f"Created task: {task_id[:8]} - {args.name}")


async def start_task(args):
    """Start a specific task."""
    success = await task_manager.start_task(args.task_id)
    if success:
        print(f"Started task: {args.task_id[:8]}")
    else:
        print(f"Failed to start task: {args.task_id[:8]}")


async def start_all_tasks(args):
    """Start all pending tasks."""
    started_tasks = await task_manager.start_all_tasks()
    print(f"Started {len(started_tasks)} tasks")


async def cancel_task(args):
    """Cancel a specific task."""
    success = await task_manager.cancel_task(args.task_id)
    if success:
        print(f"Cancelled task: {args.task_id[:8]}")
    else:
        print(f"Failed to cancel task: {args.task_id[:8]}")


async def cancel_all_tasks(args):
    """Cancel all running tasks."""
    cancelled_count = await task_manager.cancel_all_tasks()
    print(f"Cancelled {cancelled_count} running tasks")


async def get_task(args):
    """Get information about a specific task."""
    task_info = await task_manager.get_task_info(args.task_id)
    if task_info:
        print("\nTask Details:")
        print(format_task_info(task_info))
    else:
        print(f"Task not found: {args.task_id[:8]}")


async def wait_for_task(args):
    """Wait for a specific task to complete."""
    print(f"Waiting for task {args.task_id[:8]} to complete...")
    success = await task_manager.wait_for_task(args.task_id, args.timeout)
    if success:
        task_info = await task_manager.get_task_info(args.task_id)
        print(f"Task completed with status: {task_info.status.value}")
    else:
        print(f"Timeout waiting for task: {args.task_id[:8]}")


async def wait_for_all_tasks(args):
    """Wait for all tasks to complete."""
    print("Waiting for all tasks to complete...")
    success = await task_manager.wait_for_all_tasks(args.timeout)
    if success:
        print("All tasks completed.")
    else:
        print("Timeout waiting for tasks to complete.")


async def summary(args):
    """Show a summary of all tasks."""
    summary = await task_manager.get_tasks_summary()
    print("\nTask Summary:")
    for status, count in summary.items():
        print(f"  {status.capitalize()}: {count}")


async def clear_completed(args):
    """Clear completed tasks."""
    cleared_count = await task_manager.clear_completed_tasks()
    print(f"Cleared {cleared_count} completed/failed/cancelled tasks")


def main():
    parser = argparse.ArgumentParser(description="DCAE Task Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List tasks
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--status", help="Filter by status (pending, running, completed, failed, cancelled)")

    # Create task
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("name", help="Task name")

    # Start task
    start_parser = subparsers.add_parser("start", help="Start a specific task")
    start_parser.add_argument("task_id", help="ID of the task to start")

    # Start all tasks
    start_all_parser = subparsers.add_parser("start-all", help="Start all pending tasks")

    # Cancel task
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a specific task")
    cancel_parser.add_argument("task_id", help="ID of the task to cancel")

    # Cancel all tasks
    cancel_all_parser = subparsers.add_parser("cancel-all", help="Cancel all running tasks")

    # Get task info
    get_parser = subparsers.add_parser("get", help="Get information about a specific task")
    get_parser.add_argument("task_id", help="ID of the task to get info for")

    # Wait for task
    wait_parser = subparsers.add_parser("wait", help="Wait for a specific task to complete")
    wait_parser.add_argument("task_id", help="ID of the task to wait for")
    wait_parser.add_argument("--timeout", type=float, default=None, help="Timeout in seconds")

    # Wait for all tasks
    wait_all_parser = subparsers.add_parser("wait-all", help="Wait for all tasks to complete")
    wait_all_parser.add_argument("--timeout", type=float, default=None, help="Timeout in seconds")

    # Summary
    subparsers.add_parser("summary", help="Show task summary")

    # Clear completed
    subparsers.add_parser("clear-completed", help="Clear completed tasks")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Map commands to functions
    command_map = {
        "list": list_tasks,
        "create": create_task,
        "start": start_task,
        "start-all": start_all_tasks,
        "cancel": cancel_task,
        "cancel-all": cancel_all_tasks,
        "get": get_task,
        "wait": wait_for_task,
        "wait-all": wait_for_all_tasks,
        "summary": summary,
        "clear-completed": clear_completed,
    }

    # Run the selected command
    if args.command in command_map:
        asyncio.run(command_map[args.command](args))
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()