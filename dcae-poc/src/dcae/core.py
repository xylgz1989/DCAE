"""Core DCAE orchestrator."""

import asyncio
import uuid
from pathlib import Path
from typing import Optional

import yaml

from .agent import AgentFactory
from .config import DCAEConfig
from .models import Workflow, WorkflowStep
from .skill import SkillManager
from .storage import SQLiteStorage


class DCAEOrchestrator:
    """Main orchestrator for DCAE workflows."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the orchestrator.

        Args:
            config_path: Path to config file
        """
        self.config = DCAEConfig.load(config_path)
        self.storage = SQLiteStorage(self.config.storage.path)

        # Initialize skill manager
        skills_dir = Path(__file__).parent.parent.parent / "skills"
        self.skill_manager = SkillManager(skills_dir)

        # Initialize agent factory
        self.agent_factory = AgentFactory(self.config, self.skill_manager)

        # Current workflow context
        self._current_workflow_id: Optional[str] = None

    async def initialize(self):
        """Initialize the orchestrator."""
        await self.storage.initialize()

    async def execute_workflow(
        self, workflow_file: Path, dry_run: bool = False
    ) -> dict:
        """Execute a complete workflow.

        Args:
            workflow_file: Path to workflow definition file
            dry_run: If True, only print what would be executed

        Returns:
            Execution summary
        """
        # Load workflow
        with open(workflow_file, "r", encoding="utf-8") as f:
            workflow_data = yaml.safe_load(f)

        workflow = Workflow(
            name=workflow_data.get("name", "Unnamed"),
            description=workflow_data.get("description", ""),
            steps=[
                WorkflowStep(**step) for step in workflow_data.get("steps", [])
            ],
        )

        # Start workflow
        self._current_workflow_id = str(uuid.uuid4())
        await self.storage.start_workflow(
            self._current_workflow_id, workflow.name, workflow.description
        )

        print(f"\n{'='*60}")
        print(f"🚀 Starting Workflow: {workflow.name}")
        print(f"{'='*60}")
        print(f"Description: {workflow.description}")
        print(f"Steps: {len(workflow.steps)}")
        print(f"{'='*60}\n")

        results = []

        for i, step in enumerate(workflow.steps, 1):
            print(f"\n{'─'*60}")
            print(f"Step {i}/{len(workflow.steps)}: {step.agent}")
            print(f"Task: {step.task[:80]}{'...' if len(step.task) > 80 else ''}")
            if step.skill:
                print(f"Skill: {step.skill}")
            print(f"{'─'*60}")

            if dry_run:
                print(f"[DRY RUN] Would execute: {step.task}")
                results.append({"step": i, "status": "skipped"})
                continue

            # Execute step
            result = await self._execute_step(step, i)
            results.append(result)

        # Complete workflow
        await self.storage.complete_workflow(
            self._current_workflow_id,
            status="completed" if all(r["success"] for r in results) else "partial",
        )

        print(f"\n{'='*60}")
        print(f"✅ Workflow Complete: {workflow.name}")
        print(f"{'='*60}\n")

        return {
            "workflow_id": self._current_workflow_id,
            "workflow_name": workflow.name,
            "results": results,
        }

    async def _execute_step(
        self, step: WorkflowStep, step_order: int
    ) -> dict:
        """Execute a single workflow step.

        Args:
            step: Workflow step
            step_order: Step order number

        Returns:
            Step result
        """
        step_id = str(uuid.uuid4())

        # Get agent
        agent = self.agent_factory.get_agent(step.agent)
        if not agent:
            print(f"❌ Agent '{step.agent}' not found")
            await self.storage.log_workflow_step(
                self._current_workflow_id,
                step_id,
                step_order,
                step.agent,
                step.task,
                step.skill,
                "failed",
                "Agent not found",
            )
            return {"step": step_order, "success": False, "error": "Agent not found"}

        # Check mandatory skills
        mandatory_skills = agent.get_mandatory_skills()
        if step.skill and step.skill not in [s.name for s in mandatory_skills]:
            print(f"⚠️  Skill '{step.skill}' is not mandatory but being used")

        # Print consensus info
        if agent.config.consensus.enabled:
            models = agent.config.consensus.models
            strategy = agent.config.consensus.voting_strategy
            print(f"📊 Consensus Enabled: {len(models)} models, {strategy}")
            print(f"   Models: {', '.join(models)}")

        # Execute
        try:
            record = await agent.execute(
                task=step.task,
                context=step.context or "",
                skill=step.skill,
            )

            # Store decision
            await self.storage.log_decision(record)

            # Store workflow step
            await self.storage.log_workflow_step(
                self._current_workflow_id,
                step_id,
                step_order,
                step.agent,
                step.task,
                step.skill,
                "completed",
                record.output[:500],  # Truncate for storage
            )

            # Display result
            print(f"\n✅ Step Complete")
            print(f"Output preview:")
            print(f"   {record.output[:200]}{'...' if len(record.output) > 200 else ''}")

            if record.consensus_result:
                print(f"\n📊 Consensus Result:")
                print(f"   Status: {record.consensus_result.status.value}")
                print(f"   Confidence: {record.consensus_result.confidence:.2f}")
                print(f"   Duration: {record.consensus_result.duration_ms}ms")
                for vote in record.consensus_result.votes:
                    status_icon = "✅" if vote.approved else "❌"
                    print(f"   {status_icon} {vote.model}: {vote.reasoning}")

            return {
                "step": step_order,
                "success": True,
                "decision_id": record.id,
                "output": record.output,
                "consensus": record.consensus_result is not None,
            }

        except Exception as e:
            print(f"❌ Step Failed: {e}")
            await self.storage.log_workflow_step(
                self._current_workflow_id,
                step_id,
                step_order,
                step.agent,
                step.task,
                step.skill,
                "failed",
                str(e),
            )
            return {"step": step_order, "success": False, "error": str(e)}

    async def query_decisions(self, agent: Optional[str] = None) -> list:
        """Query stored decisions.

        Args:
            agent: Filter by agent name

        Returns:
            List of decisions
        """
        if agent:
            return await self.storage.get_decisions_by_agent(agent)

        # TODO: Implement get_all_decisions
        return []

    async def get_workflow_status(self, workflow_id: str) -> Optional[dict]:
        """Get workflow execution status.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow status
        """
        return await self.storage.get_workflow_status(workflow_id)
