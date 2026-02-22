"""Data models for DCAE."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class VotingStrategy(str, Enum):
    """Voting strategy types."""

    UNANIMOUS = "unanimous"
    MAJORITY = "majority"
    WEIGHTED = "weighted"


class ConsensusStatus(str, Enum):
    """Consensus status."""

    PENDING = "pending"
    CONSENSUS_REACHED = "consensus_reached"
    NO_CONSENSUS = "no_consensus"
    TIMEOUT = "timeout"


@dataclass
class VoteResult:
    """Result from a single model vote."""

    model: str
    output: str
    approved: bool
    confidence: float
    reasoning: str = ""
    duration_ms: int = 0

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "model": self.model,
            "output": self.output,
            "approved": self.approved,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VoteResult":
        """Create from dict."""
        return cls(
            model=data.get("model", ""),
            output=data.get("output", ""),
            approved=data.get("approved", False),
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning", ""),
            duration_ms=data.get("duration_ms", 0),
        )


@dataclass
class ConsensusResult:
    """Aggregated consensus result."""

    topic: str
    status: ConsensusStatus
    votes: list[VoteResult] = field(default_factory=list)
    final_output: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    duration_ms: int = 0

    def get_approval_rate(self) -> float:
        """Calculate approval rate."""
        if not self.votes:
            return 0.0
        return sum(1 for v in self.votes if v.approved) / len(self.votes)

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            "topic": self.topic,
            "status": self.status.value,
            "votes": [v.to_dict() for v in self.votes],
            "final_output": self.final_output,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConsensusResult":
        """Create from dict."""
        return cls(
            topic=data.get("topic", ""),
            status=ConsensusStatus(data.get("status", ConsensusStatus.PENDING)),
            votes=[VoteResult.from_dict(v) for v in data.get("votes", [])],
            final_output=data.get("final_output", ""),
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning", ""),
            duration_ms=data.get("duration_ms", 0),
        )


@dataclass
class DecisionRecord:
    """Record of a decision made during workflow execution."""

    id: str
    timestamp: datetime
    agent: str
    task: str
    skill: Optional[str]
    consensus_enabled: bool
    consensus_result: Optional[ConsensusResult]
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    agent: str
    task: str
    skill: Optional[str] = None
    context: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)


@dataclass
class Workflow:
    """Workflow definition."""

    name: str
    description: str
    steps: list[WorkflowStep]
