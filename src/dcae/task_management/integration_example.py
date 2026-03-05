"""
Integration examples for the task management system with DCAE functions
"""
import asyncio
from pathlib import Path
from dcae.task_management.task_manager import task_manager, TaskStatus


async def generate_documentation_task(task_id: str, source_file: str, output_file: str):
    """Simulate a documentation generation task."""
    await task_manager.update_task_progress(task_id, 0, "Starting documentation generation...")

    # Simulate reading source file
    await task_manager.update_task_progress(task_id, 10, "Reading source code...")
    await asyncio.sleep(0.2)

    # Simulate analyzing code structure
    await task_manager.update_task_progress(task_id, 30, "Analyzing code structure...")
    await asyncio.sleep(0.3)

    # Simulate generating documentation content
    await task_manager.update_task_progress(task_id, 60, "Generating documentation content...")
    await asyncio.sleep(0.4)

    # Simulate saving output
    await task_manager.update_task_progress(task_id, 90, "Saving documentation...")
    await asyncio.sleep(0.1)

    await task_manager.update_task_progress(task_id, 100, "Documentation generation completed!")

    # Create a mock documentation file
    Path(output_file).write_text(f"# Documentation for {source_file}\n\nGenerated at {task_id}")

    return f"Documentation for {source_file} saved to {output_file}"


async def run_tests_task(task_id: str, test_suite: str):
    """Simulate a test execution task."""
    await task_manager.update_task_progress(task_id, 0, "Starting test execution...")

    # Simulate discovering tests
    await task_manager.update_task_progress(task_id, 10, "Discovering tests...")
    await asyncio.sleep(0.2)

    # Simulate running tests
    await task_manager.update_task_progress(task_id, 20, "Running tests...")
    for i in range(1, 11):  # Simulate 10 tests
        await asyncio.sleep(0.1)
        progress = 20 + (i * 7)  # From 20% to 90%
        await task_manager.update_task_progress(task_id, progress, f"Running test {i}/10...")

    # Simulate generating test report
    await task_manager.update_task_progress(task_id, 95, "Generating test report...")
    await asyncio.sleep(0.1)

    await task_manager.update_task_progress(task_id, 100, "Tests completed!")

    return f"Test suite {test_suite} completed successfully"


async def train_model_task(task_id: str, dataset_path: str):
    """Simulate a model training task."""
    await task_manager.update_task_progress(task_id, 0, "Starting model training...")

    await task_manager.update_task_progress(task_id, 5, "Loading dataset...")
    await asyncio.sleep(0.2)

    await task_manager.update_task_progress(task_id, 10, "Preparing data...")
    await asyncio.sleep(0.2)

    # Simulate training epochs
    for epoch in range(1, 6):  # 5 epochs
        await asyncio.sleep(0.3)
        progress = 10 + (epoch * 15)  # From 25% to 85%
        await task_manager.update_task_progress(task_id, progress, f"Training epoch {epoch}/5...")

    await task_manager.update_task_progress(task_id, 95, "Saving model...")
    await asyncio.sleep(0.1)

    await task_manager.update_task_progress(task_id, 100, "Model training completed!")

    return f"Model trained on {dataset_path} completed"


async def run_dcae_integration_example():
    """Demonstrate the task management system with DCAE-like tasks."""
    print("DCAE Task Management Integration Example")
    print("=" * 50)

    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create various DCAE-related tasks
    print("\nCreating DCAE tasks...")

    # Create a documentation generation task
    doc_task_id = await task_manager.create_task(
        name="Documentation Generation",
        coroutine_func=lambda tid: generate_documentation_task(tid, "src/main.py", "docs/main.md"),
        metadata={
            "type": "documentation",
            "source_file": "src/main.py",
            "output_file": "docs/main.md"
        }
    )

    # Create a test execution task
    test_task_id = await task_manager.create_task(
        name="Unit Test Execution",
        coroutine_func=lambda tid: run_tests_task(tid, "core_module_tests"),
        metadata={
            "type": "testing",
            "test_suite": "core_module_tests"
        }
    )

    # Create a model training task
    train_task_id = await task_manager.create_task(
        name="Model Training",
        coroutine_func=lambda tid: train_model_task(tid, "datasets/train.csv"),
        metadata={
            "type": "training",
            "dataset": "datasets/train.csv"
        }
    )

    print(f"   Created: {doc_task_id[:8]} - Documentation Generation")
    print(f"   Created: {test_task_id[:8]} - Unit Test Execution")
    print(f"   Created: {train_task_id[:8]} - Model Training")

    # Start all tasks
    print(f"\nStarting tasks...")
    started_tasks = await task_manager.start_all_tasks()
    print(f"   Started {len(started_tasks)} tasks")

    # Monitor progress of all tasks
    print(f"\nMonitoring progress:")
    initial_count = await task_manager.get_active_tasks_count()

    while await task_manager.get_active_tasks_count() > 0:
        await asyncio.sleep(0.3)  # Poll every 300ms

        # Get current task states
        all_tasks = await task_manager.get_all_tasks()
        active_tasks = [t for t in all_tasks if t.status == TaskStatus.RUNNING]

        # Print progress for active tasks
        if active_tasks:
            print(f"   Active tasks: {len(active_tasks)}")
            for task in active_tasks:
                print(f"     -> {task.name[:20]:<20} {task.progress:5.1f}% - {task.progress_message}")

    print(f"\nAll tasks completed!")

    # Display final results
    print(f"\nFinal Results:")
    all_tasks = await task_manager.get_all_tasks()
    for task in all_tasks:
        status_symbol = {
            TaskStatus.COMPLETED: "[OK]",
            TaskStatus.FAILED: "[ER]",
            TaskStatus.CANCELLED: "[CN]"
        }.get(task.status, "[??]")

        print(f"   {status_symbol} {task.name:<30} {task.status.value}")
        if task.result:
            print(f"       Result: {task.result}")
        if task.error:
            print(f"       Error: {task.error}")

    # Show summary
    summary = await task_manager.get_tasks_summary()
    print(f"\nSummary:")
    for status, count in summary.items():
        if count > 0:
            print(f"   {status.title()}: {count}")

    total_time = sum([(t.completed_at - t.started_at).total_seconds() for t in all_tasks if t.completed_at and t.started_at], 0)
    print(f"   Total execution time: {total_time:.1f}s")

    return all_tasks


if __name__ == "__main__":
    asyncio.run(run_dcae_integration_example())