"""Run a coding workflow with China LLMs."""

import asyncio
import sys
from pathlib import Path
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dcae.core import DCAEOrchestrator
from dcae.config import DCAEConfig


async def run_workflow():
    """Run the coding workflow."""
    config_path = Path("./config-qwen.yaml")
    workflow_path = Path("./workflows/qwen-test.yaml")

    print("="*60)
    print("DCAE Coding Workflow Runner - Qwen Only")
    print("="*60)
    print(f"Config: {config_path}")
    print(f"Workflow: {workflow_path}")
    print()

    # Initialize orchestrator
    orchestrator = DCAEOrchestrator(config_path)
    await orchestrator.initialize()

    # Load config to show agents
    cfg = DCAEConfig.load(config_path)
    print("Available Agents:")
    for name, agent_config in cfg.agents.items():
        consensus_status = "ON" if agent_config.consensus.enabled else "OFF"
        print(f"  - {name}: {agent_config.name} ({agent_config.model}) [Consensus: {consensus_status}]")
    print()

    # Execute workflow
    print("Executing workflow...")
    print("="*60)
    print()

    try:
        result = await orchestrator.execute_workflow(workflow_path, dry_run=False)

        print()
        print("="*60)
        print("Workflow Complete")
        print("="*60)
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Workflow Name: {result['workflow_name']}")
        print(f"Steps completed: {len(result['results'])}")

        for i, step_result in enumerate(result['results'], 1):
            print(f"\n{'─'*60}")
            print(f"Step {i}")
            print(f"{'─'*60}")
            success = step_result.get('success', False)
            status_icon = "[OK]" if success else "[FAIL]"
            print(f"Status: {status_icon}")

            if 'output' in step_result:
                output = step_result['output']
                print(f"\nOutput:")
                print(output)

            if 'consensus' in step_result and step_result['consensus']:
                print(f"\nConsensus: Enabled")

        return 0

    except Exception as e:
        print(f"\nError executing workflow: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_workflow())
    sys.exit(exit_code)