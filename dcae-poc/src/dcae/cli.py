"""CLI interface for DCAE."""

import asyncio
from pathlib import Path

import typer

from .core import DCAEOrchestrator
from .storage import SQLiteStorage

# Check if terminal supports emoji
import sys
try:
    sys.stdout.write("\U0001f464")
    sys.stdout.flush()
    SUPPORTS_EMOJI = True
except:
    SUPPORTS_EMOJI = False

def safe_emoji(text: str) -> str:
    """Return text only if terminal supports emoji."""
    return text if SUPPORTS_EMOJI else ""

app = typer.Typer(
    name="dcae",
    help="DCAE - Disciplined Consensus-Driven Agentic Engineering POC",
    add_completion=False,
)

config_path_option = typer.Option(
    "./config.yaml", "--config", "-c", help="Path to configuration file"
)


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Project name"),
    output_dir: str = typer.Option(".", "--output", "-o", help="Output directory"),
):
    """Initialize a new DCAE project."""
    from .templates import create_project_template

    create_project_template(project_name, Path(output_dir))
    typer.echo(f"{safe_emoji('✅ ')}DCAE project '{project_name}' initialized in {output_dir}")


@app.command()
async def run(
    workflow: str = typer.Argument(..., help="Workflow file or name"),
    config: str = config_path_option,
    dry_run: bool = typer.Option(False, "--dry-run", help="Print what would be executed"),
):
    """Run a DCAE workflow."""
    orchestrator = DCAEOrchestrator(Path(config))
    await orchestrator.initialize()

    # Check if workflow is a path or a name
    workflow_path = Path(workflow)
    if not workflow_path.exists():
        # Try to find in workflows directory
        workflow_path = Path("./workflows") / f"{workflow}.yaml"

    if not workflow_path.exists():
        typer.echo(f"{safe_emoji('❌ ')}Workflow file not found: {workflow}")
        raise typer.Exit(1)

    result = await orchestrator.execute_workflow(workflow_path, dry_run)

    typer.echo(f"\nWorkflow ID: {result['workflow_id']}")
    typer.echo(f"Steps completed: {len(result['results'])}")


@app.command()
async def status(
    workflow_id: str = typer.Argument(..., help="Workflow ID"),
    config: str = config_path_option,
):
    """Show workflow status."""
    orchestrator = DCAEOrchestrator(Path(config))
    await orchestrator.initialize()

    status = await orchestrator.get_workflow_status(workflow_id)

    if not status:
        typer.echo(f"{safe_emoji('❌ ')}Workflow not found: {workflow_id}")
        raise typer.Exit(1)

    typer.echo(f"Workflow: {status['workflow']['name']}")
    typer.echo(f"Status: {status['workflow']['status']}")
    typer.echo(f"\nSteps:")
    for step in status["steps"]:
        typer.echo(f"  {step['step_order']}. [{step['status']}] {step['agent']}")


@app.command()
async def decisions(
    agent: str = typer.Option(None, "--agent", "-a", help="Filter by agent"),
    config: str = config_path_option,
):
    """Query stored decisions."""
    orchestrator = DCAEOrchestrator(Path(config))
    await orchestrator.initialize()

    decisions = await orchestrator.query_decisions(agent)

    if not decisions:
        typer.echo("No decisions found")
        return

    typer.echo(f"\n{'='*60}")
    typer.echo(f"Decisions ({len(decisions)})")
    typer.echo(f"{'='*60}\n")

    for decision in decisions:
        consensus_icon = f"{safe_emoji('📊 ')}" if decision.consensus_enabled else f"{safe_emoji('🤖 ')}"
        typer.echo(f"{consensus_icon}[{decision.timestamp}] {decision.agent}")
        typer.echo(f"   Task: {decision.task[:60]}{'...' if len(decision.task) > 60 else ''}")
        if decision.skill:
            typer.echo(f"   Skill: {decision.skill}")
        typer.echo(f"   ID: {decision.id}")
        typer.echo()


@app.command()
def agents(config: str = config_path_option):
    """List available agents."""
    from .config import DCAEConfig

    cfg = DCAEConfig.load(Path(config))

    typer.echo(f"\n{'='*60}")
    typer.echo(f"Available Agents")
    typer.echo(f"{'='*60}\n")

    for name, agent_config in cfg.agents.items():
        consensus_status = f"{safe_emoji('📊 ')}ON" if agent_config.consensus.enabled else f"{safe_emoji('📌 ')}OFF"
        typer.echo(f"{safe_emoji('👤 ')}{name}: {agent_config.name}")
        typer.echo(f"   Role: {agent_config.role}")
        typer.echo(f"   Model: {agent_config.model}")
        typer.echo(f"   Consensus: {consensus_status}")
        if agent_config.skills:
            typer.echo(f"   Skills: {', '.join(agent_config.skills)}")
        typer.echo()


@app.command()
def skills():
    """List available skills."""
    from pathlib import Path

    skills_dir = Path(__file__).parent.parent.parent / "skills"

    if not skills_dir.exists():
        typer.echo("No skills directory found")
        return

    typer.echo(f"\n{'='*60}")
    typer.echo(f"Available Skills")
    typer.echo(f"{'='*60}\n")

    for skill_file in sorted(skills_dir.glob("*.yaml")):
        import yaml

        with open(skill_file, "r", encoding="utf-8") as f:
            skill_config = yaml.safe_load(f)

        typer.echo(f"{safe_emoji('⚡ ')}{skill_file.stem}")
        if skill_config.get("description"):
            typer.echo(f"   {skill_config['description']}")
        mandatory_for = skill_config.get("mandatory_for", [])
        if mandatory_for:
            typer.echo(f"   Mandatory for: {', '.join(mandatory_for)}")
        typer.echo()


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
