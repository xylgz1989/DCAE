"""Consensus engine for multi-LLM voting."""

import asyncio
import time
from typing import Any, Dict, Optional

from anthropic import Anthropic
from openai import AsyncOpenAI

from .config import AgentConfig, DCAEConfig, LLMConfig
from .models import ConsensusResult, ConsensusStatus, VoteResult, VotingStrategy


class SimpleConsensusEngine:
    """Simplified consensus engine - direct LLM API calls."""

    def __init__(self, config: DCAEConfig):
        """Initialize the consensus engine.

        Args:
            config: DCAE configuration
        """
        self.config = config
        self.timeout = config.consensus.get("timeout", 300)
        self.max_rounds = config.consensus.get("max_rounds", 3)

        # Initialize LLM clients
        self.clients: Dict[str, Any] = {}
        for provider, llm_cfg in config.llm_config.items():
            if provider == "claude":
                self.clients[provider] = Anthropic(api_key=llm_cfg.api_key)
            elif provider == "openai":
                self.clients[provider] = AsyncOpenAI(api_key=llm_cfg.api_key)
            elif provider == "glm":
                # Zhipu AI (GLM) - 使用 httpx 兼容的 OpenAI 客户端
                from openai import AsyncOpenAI
                self.clients[provider] = AsyncOpenAI(
                    api_key=llm_cfg.api_key,
                    base_url="https://open.bigmodel.cn/api/paas/v4"
                )
            elif provider == "qwen":
                # Qwen (Alibaba DashScope) - use OpenAI compatible API
                from openai import AsyncOpenAI
                self.clients[provider] = AsyncOpenAI(
                    api_key=llm_cfg.api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )

    def _get_client_and_provider(self, model_id: str) -> tuple[Any, str]:
        """Get the appropriate client for a model.

        Args:
            model_id: Model identifier

        Returns:
            Tuple of (client, provider)
        """
        if "claude" in model_id.lower():
            return self.clients.get("claude"), "claude"
        elif "gpt" in model_id.lower():
            return self.clients.get("openai"), "openai"
        elif "glm" in model_id.lower():
            return self.clients.get("glm"), "glm"
        elif "qwen" in model_id.lower():
            return self.clients.get("qwen"), "qwen"
        else:
            return self.clients.get("claude"), "claude"

    async def _call_claude(self, model: str, prompt: str, context: str = "") -> str:
        """Call Claude API.

        Args:
            model: Model identifier
            prompt: The prompt to send
            context: Additional context

        Returns:
            Model response
        """
        client = self.clients.get("claude")
        if not client:
            raise ValueError("Claude client not configured")

        full_prompt = f"{context}\n\nTask: {prompt}" if context else prompt

        message = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": full_prompt}],
        )

        return message.content[0].text

    async def _call_openai(self, model: str, prompt: str, context: str = "") -> str:
        """Call OpenAI API.

        Args:
            model: Model identifier
            prompt: The prompt to send
            context: Additional context

        Returns:
            Model response
        """
        client = self.clients.get("openai")
        if not client:
            raise ValueError("OpenAI client not configured")

        full_prompt = f"{context}\n\nTask: {prompt}" if context else prompt

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=4096,
        )

        return response.choices[0].message.content

    async def _call_glm(self, model: str, prompt: str, context: str = "") -> str:
        """Call GLM (Zhipu AI) API.

        Args:
            model: Model identifier
            prompt: The prompt to send
            context: Additional context

        Returns:
            Model response
        """
        client = self.clients.get("glm")
        if not client:
            raise ValueError("GLM client not configured")

        full_prompt = f"{context}\n\nTask: {prompt}" if context else prompt

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=4096,
        )

        return response.choices[0].message.content

    async def _call_qwen(self, model: str, prompt: str, context: str = "") -> str:
        """Call Qwen (Alibaba DashScope) API.

        Args:
            model: Model identifier
            prompt: The prompt to send
            context: Additional context

        Returns:
            Model response
        """
        client = self.clients.get("qwen")
        if not client:
            raise ValueError("Qwen client not configured")

        full_prompt = f"{context}\n\nTask: {prompt}" if context else prompt

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=4096,
        )

        return response.choices[0].message.content

    async def _evaluate_output(
        self, model: str, output: str, evaluation_criteria: str
    ) -> tuple[bool, float, str]:
        """Evaluate an output for approval.

        Args:
            model: Model to use for evaluation
            output: The output to evaluate
            evaluation_criteria: Criteria for evaluation

        Returns:
            Tuple of (approved, confidence, reasoning)
        """
        eval_prompt = f"""Evaluate the following output based on the given criteria.

Criteria: {evaluation_criteria}

Output to evaluate:
{output}

Provide your evaluation in this exact format:
APPROVED: [true/false]
CONFIDENCE: [0.0-1.0]
REASONING: [brief explanation]

Be thorough but concise."""

        client, provider = self._get_client_and_provider(model)
        if provider == "claude":
            response = await self._call_claude(model, eval_prompt)
        elif provider == "glm":
            response = await self._call_glm(model, eval_prompt)
        elif provider == "qwen":
            response = await self._call_qwen(model, eval_prompt)
        else:
            response = await self._call_openai(model, eval_prompt)

        # Parse the response
        approved = "APPROVED: true" in response.lower() or "通过" in response
        try:
            confidence = float(
                [line for line in response.split("\n") if "CONFIDENCE:" in line][
                    0
                ].split("CONFIDENCE:")[1].strip()
            )
        except (IndexError, ValueError):
            confidence = 0.5

        try:
            reasoning = [
                line for line in response.split("\n") if "REASONING:" in line
            ][0].split("REASONING:")[1].strip()
        except IndexError:
            reasoning = ""

        return approved, confidence, reasoning

    async def _execute_with_model(
        self, model: str, prompt: str, context: str
    ) -> VoteResult:
        """Execute a task with a single model.

        Args:
            model: Model identifier
            prompt: The task prompt
            context: Additional context

        Returns:
            VoteResult
        """
        start_time = time.time()

        try:
            client, provider = self._get_client_and_provider(model)

            if provider == "claude":
                output = await self._call_claude(model, prompt, context)
            elif provider == "glm":
                output = await self._call_glm(model, prompt, context)
            elif provider == "qwen":
                output = await self._call_qwen(model, prompt, context)
            else:
                output = await self._call_openai(model, prompt, context)

            duration_ms = int((time.time() - start_time) * 1000)

            # Auto-approve the output
            return VoteResult(
                model=model,
                output=output,
                approved=True,
                confidence=0.8,
                reasoning="Generated successfully",
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return VoteResult(
                model=model,
                output=f"Error: {str(e)}",
                approved=False,
                confidence=0.0,
                reasoning=f"Execution failed: {str(e)}",
                duration_ms=duration_ms,
            )

    async def execute(
        self,
        prompt: str,
        models: list[str],
        context: str = "",
        voting_strategy: str = "majority",
        threshold: float = 0.5,
    ) -> ConsensusResult:
        """Execute consensus voting across multiple models.

        Args:
            prompt: The task prompt
            models: List of models to use
            context: Additional context
            voting_strategy: How to aggregate votes
            threshold: Minimum threshold for consensus

        Returns:
            ConsensusResult
        """
        start_time = time.time()

        # Execute tasks in parallel
        tasks = [
            self._execute_with_model(model, prompt, context) for model in models
        ]
        votes = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_votes = [v for v in votes if isinstance(v, VoteResult)]

        # Aggregate votes based on strategy
        status = self._determine_consensus_status(
            valid_votes, VotingStrategy(voting_strategy), threshold
        )

        # Select final output
        final_output = self._select_final_output(valid_votes, status)
        confidence = valid_votes[0].confidence if valid_votes else 0.0

        duration_ms = int((time.time() - start_time) * 1000)

        return ConsensusResult(
            topic=prompt[:100],
            status=status,
            votes=valid_votes,
            final_output=final_output,
            confidence=confidence,
            reasoning=f"Consensus reached using {voting_strategy} strategy",
            duration_ms=duration_ms,
        )

    def _determine_consensus_status(
        self,
        votes: list[VoteResult],
        strategy: VotingStrategy,
        threshold: float,
    ) -> ConsensusStatus:
        """Determine if consensus was reached.

        Args:
            votes: List of vote results
            strategy: Voting strategy
            threshold: Threshold for consensus

        Returns:
            ConsensusStatus
        """
        if not votes:
            return ConsensusStatus.NO_CONSENSUS

        approval_count = sum(1 for v in votes if v.approved)
        total_count = len(votes)
        approval_rate = approval_count / total_count if total_count > 0 else 0

        if strategy == VotingStrategy.UNANIMOUS:
            if approval_rate >= 1.0:
                return ConsensusStatus.CONSENSUS_REACHED
        elif strategy == VotingStrategy.MAJORITY:
            if approval_rate >= threshold:
                return ConsensusStatus.CONSENSUS_REACHED
        elif strategy == VotingStrategy.WEIGHTED:
            if approval_rate >= threshold:
                return ConsensusStatus.CONSENSUS_REACHED

        return ConsensusStatus.NO_CONSENSUS

    def _select_final_output(
        self, votes: list[VoteResult], status: ConsensusStatus
    ) -> str:
        """Select the final output from votes.

        Args:
            votes: List of vote results
            status: Consensus status

        Returns:
            Selected output
        """
        if not votes:
            return "No outputs generated"

        # If consensus reached, pick the approved output with highest confidence
        approved = [v for v in votes if v.approved]
        if approved:
            return max(approved, key=lambda v: v.confidence).output

        # If no consensus, return the first output
        return votes[0].output

    async def execute_agent_consensus(
        self,
        agent_config: AgentConfig,
        prompt: str,
        context: str = "",
    ) -> ConsensusResult:
        """Execute consensus for a specific agent.

        Args:
            agent_config: Agent configuration
            prompt: Task prompt
            context: Additional context

        Returns:
            ConsensusResult
        """
        if not agent_config.consensus.enabled:
            # Single model execution
            return await self._execute_with_model(
                agent_config.model, prompt, context
            )

        # Multi-model consensus
        models = agent_config.consensus.models or [agent_config.model]
        return await self.execute(
            prompt=prompt,
            models=models,
            context=context,
            voting_strategy=agent_config.consensus.voting_strategy,
            threshold=agent_config.consensus.threshold,
        )
