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
from .knowledge import DomainKnowledgeBase, KnowledgeFusionEngine
from .knowledge.cross_domain import CrossDomainRecommendationEngine


class DCAEOrchestrator:
    """Main orchestrator for DCAE workflows."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the orchestrator.

        Args:
            config_path: Path to config file
        """
        self.config = DCAEConfig.load(config_path)
        self.storage = SQLiteStorage(self.config.storage.path)

        # Initialize knowledge base and fusion engine
        knowledge_db_path = self.config.storage.path.replace('.db', '-knowledge.db')
        self.knowledge_base = DomainKnowledgeBase(knowledge_db_path)
        self.knowledge_fusion = KnowledgeFusionEngine(self.knowledge_base)

        # Initialize cross-domain recommendation engine
        self.cross_domain_recommender = CrossDomainRecommendationEngine(self.knowledge_base)

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

        # Generate and display cross-domain recommendations at the beginning of the workflow
        self._display_initial_cross_domain_recommendations(workflow)

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

        # Generate final cross-domain recommendations summary
        self._display_final_cross_domain_insights(workflow)

        return {
            "workflow_id": self._current_workflow_id,
            "workflow_name": workflow.name,
            "results": results,
        }

    def _display_initial_cross_domain_recommendations(self, workflow: Workflow):
        """Display initial cross-domain recommendations at the start of workflow execution.

        Args:
            workflow: The workflow being executed
        """
        print(f"\n🔍 CROSS-DOMAIN RECOMMENDATIONS:")
        print(f"-" * 40)

        # Generate recommendations based on the overall workflow context
        workflow_context = f"{workflow.name} {workflow.description}".strip()
        recommendations = self.cross_domain_recommender.generate_recommendations(
            context=workflow_context,
            min_relationship_strength=0.3,
            max_recommendations=3
        )

        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec.title}")
                print(f"   Confidence: {rec.confidence:.2f}")
                print(f"   Domains: {', '.join([d.value for d in rec.source_domains])}")

                # Show a brief explanation
                explanation_lines = rec.explanation.split('\n')
                for line in explanation_lines[:3]:  # Show first few lines of explanation
                    if line.strip():
                        print(f"   {line.strip()}")

                if len(explanation_lines) > 3:
                    print(f"   ... (See full explanation in knowledge system)")
        else:
            print("   No significant cross-domain recommendations found.")

        print()

    def _display_final_cross_domain_insights(self, workflow: Workflow):
        """Display final cross-domain insights after workflow completion.

        Args:
            workflow: The completed workflow
        """
        print(f"\n📊 FINAL CROSS-DOMAIN INSIGHTS:")
        print(f"-" * 40)

        # Generate post-execution insights
        recommendations = self.cross_domain_recommender.generate_recommendations(
            context=f"{workflow.name} completed",
            min_relationship_strength=0.2,
            max_recommendations=5
        )

        if recommendations:
            print(f"   Generated {len(recommendations)} cross-domain insights from workflow execution")

            # Group by confidence level
            high_conf = [r for r in recommendations if r.confidence >= 0.7]
            med_conf = [r for r in recommendations if 0.4 <= r.confidence < 0.7]
            low_conf = [r for r in recommendations if r.confidence < 0.4]

            if high_conf:
                print(f"\n   ⭐ HIGH CONFIDENCE ({len(high_conf)}):")
                for i, rec in enumerate(high_conf, 1):
                    print(f"      • {rec.title} ({rec.confidence:.2f})")

            if med_conf:
                print(f"\n   📊 MEDIUM CONFIDENCE ({len(med_conf)}):")
                for i, rec in enumerate(med_conf, 1):
                    print(f"      • {rec.title} ({rec.confidence:.2f})")

            if low_conf:
                print(f"\n   🔍 LOW CONFIDENCE ({len(low_conf)}):")
                for i, rec in enumerate(low_conf, 1):
                    print(f"      • {rec.title} ({rec.confidence:.2f})")
        else:
            print("   No cross-domain insights generated from this workflow.")

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

        # Integrate domain-specific knowledge if context is provided
        enhanced_task = step.task
        if step.context:
            # Try to determine domain from context or task
            from .knowledge import DomainType
            import re

            domain = DomainType.TECHNICAL  # Default

            # Heuristics to determine domain
            tech_keywords = ['code', 'api', 'function', 'method', 'class', 'module', 'programming', 'development', 'framework']
            business_keywords = ['customer', 'revenue', 'market', 'sales', 'business', 'process', 'workflow', 'stakeholder']
            regulatory_keywords = ['compliance', 'regulation', 'policy', 'requirement', 'standard', 'audit', 'control']

            lower_context = step.context.lower() + " " + step.task.lower()

            if any(keyword in lower_context for keyword in regulatory_keywords):
                domain = DomainType.REGULATORY
            elif any(keyword in lower_context for keyword in business_keywords):
                domain = DomainType.BUSINESS
            elif any(keyword in lower_context for keyword in tech_keywords):
                domain = DomainType.TECHNICAL

            # Integrate relevant knowledge
            enhanced_task = self.knowledge_fusion.integrate_knowledge(
                prompt=step.task,
                context=step.context,
                domain=domain
            )

        # Additionally, consider cross-domain insights if they might be relevant to the current step
        cross_domain_insights = self.cross_domain_recommender.generate_recommendations(
            context=f"{step.task} {step.context}",
            min_relationship_strength=0.4,
            max_recommendations=2
        )

        if cross_domain_insights:
            print(f"\n💡 CROSS-DOMAIN INSIGHTS FOR THIS STEP:")
            for insight in cross_domain_insights:
                print(f"   • {insight.title} (Confidence: {insight.confidence:.2f})")

                # Optionally integrate cross-domain insights into the task
                if insight.confidence > 0.6:  # Only for high-confidence insights
                    insight_summary = f"\n\nCROSS-DOMAIN INSIGHT: {insight.explanation[:200]}..."
                    enhanced_task += insight_summary

        # Execute
        try:
            record = await agent.execute(
                task=enhanced_task,
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
                step.task,  # Store original task
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

        # Integrate domain-specific knowledge if context is provided
        enhanced_task = step.task
        if step.context:
            # Try to determine domain from context or task
            from .knowledge import DomainType
            import re

            domain = DomainType.TECHNICAL  # Default

            # Heuristics to determine domain
            tech_keywords = ['code', 'api', 'function', 'method', 'class', 'module', 'programming', 'development', 'framework']
            business_keywords = ['customer', 'revenue', 'market', 'sales', 'business', 'process', 'workflow', 'stakeholder']
            regulatory_keywords = ['compliance', 'regulation', 'policy', 'requirement', 'standard', 'audit', 'control']

            lower_context = step.context.lower() + " " + step.task.lower()

            if any(keyword in lower_context for keyword in regulatory_keywords):
                domain = DomainType.REGULATORY
            elif any(keyword in lower_context for keyword in business_keywords):
                domain = DomainType.BUSINESS
            elif any(keyword in lower_context for keyword in tech_keywords):
                domain = DomainType.TECHNICAL

            # Integrate relevant knowledge
            enhanced_task = self.knowledge_fusion.integrate_knowledge(
                prompt=step.task,
                context=step.context,
                domain=domain
            )

        # Execute
        try:
            record = await agent.execute(
                task=enhanced_task,
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
                step.task,  # Store original task
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

    def get_knowledge_base(self):
        """Get access to the knowledge base for external operations.

        Returns:
            DomainKnowledgeBase instance
        """
        return self.knowledge_base

    def get_knowledge_fusion_engine(self):
        """Get access to the knowledge fusion engine.

        Returns:
            KnowledgeFusionEngine instance
        """
        return self.knowledge_fusion
