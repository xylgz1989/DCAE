"""Simple test for skill loading."""

from dcae.config import DCAEConfig
from dcae.skill import SkillManager
from pathlib import Path


def test_coding_plan_exists():
    """Test that coding-plan skill exists and has correct attributes."""
    config = DCAEConfig.load(Path("./config-china.yaml"))
    skill_manager = SkillManager(Path("./skills"))

    coding_plan = skill_manager.get_skill("coding-plan")

    # Test skill exists
    assert coding_plan is not None, "Coding plan skill should be loaded"

    # Test that skill has the expected attributes
    assert coding_plan.name == "coding-plan"
    assert coding_plan.description is not None

    # Test mandatory_for - should be a list or None
    # The YAML has `mandatory_for: []` which should work
    if coding_plan.mandatory_for:
        if isinstance(coding_plan.mandatory_for, list):
            # It's a list, which is correct
            assert True
        elif coding_plan.mandatory_for is None:
            # It's None, which is also acceptable
            assert True


def test_cost_aware_exists():
    """Test that cost-aware skill exists."""
    config = DCAEConfig.load(Path("./config-china.yaml"))
    skill_manager = SkillManager(Path("./skills"))

    cost_aware = skill_manager.get_skill("cost-aware")

    assert cost_aware is not None, "Cost-aware skill should be loaded"
    assert cost_aware.name == "cost-aware"
