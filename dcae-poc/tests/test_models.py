"""Test data models."""

from dcae.models import (
    VoteResult,
    ConsensusResult,
    ConsensusStatus,
    DecisionRecord,
    WorkflowStep,
)


def test_vote_result():
    """Test VoteResult dataclass."""
    vote = VoteResult(
        model="claude-3.5-sonnet",
        output="Test output",
        approved=True,
        confidence=0.8,
        reasoning="Good output",
        duration_ms=1000,
    )

    assert vote.model == "claude-3.5-sonnet"
    assert vote.approved is True
    assert vote.confidence == 0.8


def test_consensus_result():
    """Test ConsensusResult dataclass."""
    votes = [
        VoteResult("claude-3.5", "Output 1", True, 0.8, "", 1000),
        VoteResult("gpt-4o", "Output 2", True, 0.7, "", 1200),
    ]

    result = ConsensusResult(
        topic="Test topic",
        status=ConsensusStatus.CONSENSUS_REACHED,
        votes=votes,
        final_output="Output 1",
        confidence=0.8,
    )

    assert result.status == ConsensusStatus.CONSENSUS_REACHED
    assert result.get_approval_rate() == 1.0


def test_workflow_step():
    """Test WorkflowStep dataclass."""
    step = WorkflowStep(
        agent="pm",
        task="Write requirements",
        skill="brainstorming",
    )

    assert step.agent == "pm"
    assert step.skill == "brainstorming"
    assert step.dependencies == []
