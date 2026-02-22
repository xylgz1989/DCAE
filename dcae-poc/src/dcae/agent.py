"""Agent implementation for BMAD workflow."""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from anthropic import Anthropic
from openai import AsyncOpenAI

from .config import AgentConfig, DCAEConfig, LLMConfig
from .consensus import SimpleConsensusEngine
from .models import ConsensusResult, DecisionRecord
from .skill import Skill, SkillManager


class Agent:
    """BMAD Agent implementation."""

    def __init__(
        self,
        name: str,
        config: AgentConfig,
        llm_config: DCAEConfig,
        skill_manager: Optional[SkillManager] = None,
    ):
        """Initialize an agent.

        Args:
            name: Agent identifier
            config: Agent configuration
            llm_config: Global LLM configuration
            skill_manager: Skill manager for injecting skills
        """
        self.name = name
        self.config = config
        self.llm_config = llm_config
        self.skill_manager = skill_manager

        # Initialize LLM client based on model
        self.client = self._create_client(config.model)

        self.consensus_engine = SimpleConsensusEngine(llm_config)

    def _create_client(self, model: str):
        """Create the appropriate LLM client for the model.

        Args:
            model: Model identifier

        Returns:
            LLM client instance
        """
        if "claude" in model.lower():
            return Anthropic(
                api_key=self.llm_config.llm_config.get("claude", LLMConfig(api_key="", base_url="", model="")).api_key
            )
        elif "gpt" in model.lower():
            return AsyncOpenAI(
                api_key=self.llm_config.llm_config.get("openai", LLMConfig(api_key="", base_url="", model="")).api_key
            )
        elif "glm" in model.lower():
            # Zhipu AI (GLM) - use OpenAI compatible client
            glm_config = self.llm_config.llm_config.get("glm")
            if glm_config:
                return AsyncOpenAI(
                    api_key=glm_config.api_key,
                    base_url=glm_config.base_url
                )
        elif "qwen" in model.lower():
            # Qwen (Alibaba) - use DashScope async client or OpenAI compatible
            qwen_config = self.llm_config.llm_config.get("qwen") or self.llm_config.llm_config.get("qwen-coding")
            if qwen_config:
                # Use OpenAI compatible API for better async support
                return AsyncOpenAI(
                    api_key=qwen_config.api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )
        else:
            return None

    async def execute(
        self,
        task: str,
        context: str = "",
        skill: Optional[str] = None,
        skill_phase: Optional[str] = None,
    ) -> DecisionRecord:
        """Execute a task with optional consensus.

        Args:
            task: Task description
            context: Additional context
            skill: Skill to inject
            skill_phase: Phase for phase-specific skill prompts

        Returns:
            DecisionRecord
        """
        decision_id = str(uuid.uuid4())
        timestamp = datetime.now()

        # Inject skill instructions if provided
        prompt = task
        if skill and self.skill_manager:
            skill_obj = self.skill_manager.get_skill(skill)
            if skill_obj:
                prompt = self.skill_manager.inject_skill_instructions(
                    prompt, skill_obj, skill_phase
                )

        # Execute with or without consensus
        if self.config.consensus.enabled:
            consensus_result = await self.consensus_engine.execute_agent_consensus(
                self.config, prompt, context
            )
            output = consensus_result.final_output
        else:
            consensus_result = None
            output = await self._execute_single_model(prompt, context)

        # Create decision record
        record = DecisionRecord(
            id=decision_id,
            timestamp=timestamp,
            agent=self.name,
            task=task,
            skill=skill,
            consensus_enabled=self.config.consensus.enabled,
            consensus_result=consensus_result,
            output=output,
            metadata={
                "skill_phase": skill_phase,
                "model": self.config.model,
            },
        )

        return record

    async def _execute_single_model(
        self, prompt: str, context: str
    ) -> str:
        """Execute task with a single model.

        Args:
            prompt: Task prompt
            context: Additional context

        Returns:
            Model response
        """
        full_prompt = f"{context}\n\nTask: {prompt}" if context else prompt
        model = self.config.model

        if isinstance(self.client, Anthropic):
            # Claude API
            message = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": full_prompt}],
            )
            return message.content[0].text

        elif isinstance(self.client, AsyncOpenAI):
            # OpenAI API (or GLM via OpenAI-compatible interface)
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=4096,
            )
            return response.choices[0].message.content

        elif "qwen" in model.lower():
            # Qwen via DashScope
            response = await self.client.call(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=4096,
            )
            return response.output.choices[0].message.content

        else:
            raise ValueError("No LLM client available")

    def get_mandatory_skills(self) -> list[Skill]:
        """Get mandatory skills for this agent.

        Returns:
            List of mandatory skills
        """
        if not self.skill_manager:
            return []

        return self.skill_manager.get_mandatory_skills_for(self.config.role)


class AgentFactory:
    """Factory for creating agents."""

    def __init__(
        self, config: DCAEConfig, skill_manager: Optional[SkillManager] = None
    ):
        """Initialize the agent factory.

        Args:
            config: DCAE configuration
            skill_manager: Skill manager
        """
        self.config = config
        self.skill_manager = skill_manager
        self._agents: dict[str, Agent] = {}

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get or create an agent.

        Args:
            name: Agent name

        Returns:
            Agent instance or None
        """
        if name not in self._agents:
            agent_config = self.config.agents.get(name)
            if agent_config:
                self._agents[name] = Agent(
                    name=name,
                    config=agent_config,
                    llm_config=self.config,
                    skill_manager=self.skill_manager,
                )

        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        """List available agents.

        Returns:
            List of agent names
        """
        return list(self.config.agents.keys())
