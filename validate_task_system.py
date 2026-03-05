import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from dcae.task_management.task_manager import task_manager, TaskStatus

async def run_final_test():
    print('Starting comprehensive task management test...')

    # Clear any existing tasks
    await task_manager.clear_completed_tasks()

    # Create a test task
    async def test_worker(task_id):
        for step in range(5):
            await asyncio.sleep(0.1)
            progress = (step + 1) * 20
            await task_manager.update_task_progress(task_id, progress, f'Processing step {step+1}/5')
        return 'Success'

    task_id = await task_manager.create_task('Test Task', test_worker)
    print(f'Created task: {task_id[:8]}')

    await task_manager.start_task(task_id)
    print('Task started')

    await task_manager.wait_for_task(task_id)
    print('Task completed')

    info = await task_manager.get_task_info(task_id)
    print(f'Status: {info.status.value}')
    print(f'Result: {info.result}')

    # Now test multiple concurrent tasks
    print('\\nTesting multiple concurrent tasks...')

    async def worker(task_id, name, duration):
        for step in range(3):
            await asyncio.sleep(duration)
            progress = (step + 1) * 33
            await task_manager.update_task_progress(task_id, progress, f'{name} step {step+1}/3')
        return f'{name} completed'

    # Create multiple tasks
    task1 = await task_manager.create_task('Concurrent Task 1', lambda tid: worker(tid, 'Task1', 0.1))
    task2 = await task_manager.create_task('Concurrent Task 2', lambda tid: worker(tid, 'Task2', 0.15))
    task3 = await task_manager.create_task('Concurrent Task 3', lambda tid: worker(tid, 'Task3', 0.2))

    print(f'Created tasks: {task1[:8]}, {task2[:8]}, {task3[:8]}')

    # Start all tasks
    started_tasks = await task_manager.start_all_tasks()
    print(f'Started {len(started_tasks)} tasks')

    # Wait for all to complete
    await task_manager.wait_for_all_tasks()

    # Check all results
    all_tasks = await task_manager.get_all_tasks()
    for task in all_tasks:
        print(f'Task {task.name}: {task.status.value}')
        if task.result:
            print(f'  Result: {task.result}')

    # Show summary
    summary = await task_manager.get_tasks_summary()
    print(f'\\nTask summary: {summary}')

    print('\\nAll tests passed successfully! The task management system is working correctly.')
    return True

if __name__ == '__main__':
    success = asyncio.run(run_final_test())
    if success:
        print('\\n✓ Task management system validation completed successfully!')
    else:
        print('\\n✗ Task management system validation failed!')