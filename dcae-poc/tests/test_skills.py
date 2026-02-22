"""Test skill loading and prompt injection."""

from dcae.config import DCAEConfig
from dcae.skill import SkillManager
from pathlib import Path
import yaml


def test_skill_loading():
    """Test that skills can be loaded."""
    config = DCAEConfig.load(Path("./config-china.yaml"))
    skill_manager = SkillManager(Path("./skills"))

    # Test that new skills exist
    coding_plan = skill_manager.get_skill("coding-plan")
    cost_aware = skill_manager.get_skill("cost-aware")

    assert coding_plan is not None, "Coding plan skill should be loaded"
    assert cost_aware is not None, "Cost-aware skill should be loaded"


def test_skill_properties():
    """Test skill properties."""
    config = DCAEConfig.load(Path("./config-china.yaml"))
    skill_manager = SkillManager(Path("./skills"))

    coding_plan = skill_manager.get_skill("coding-plan")

    # Test skill properties
    assert coding_plan.name == "coding-plan"
    assert coding_plan.description is not None, "Description should exist"
    assert coding_plan.mandatory_for is not None, "Mandatory_for should exist"


def test_mandatory_for_check():
    """Test mandatory_for functionality."""
    config = DCAEConfig.load(Path("./config-china.yaml"))
    skill_manager = SkillManager(Path("./skills"))

    coding_plan = skill_manager.get_skill("coding-plan")
    cost_aware = skill_manager.get_skill("cost-aware")

    # coding-plan is mandatory for analysis and pm
    assert coding_plan.is_mandatory_for("analysis"), "Coding-plan should be mandatory for analysis"
    assert coding_plan.is_mandatory_for("pm"), "Coding-plan should be mandatory for pm"
    assert coding_plan.is_mandatory_for("coding") is False, "Coding-plan should NOT be mandatory for coding"

    # cost-aware is mandatory for all (including "all" as string)
    assert cost_aware.is_mandatory_for("analysis"), "Cost-aware should be mandatory for analysis"
    assert cost_aware.is_mandatory_for("pm"), "Cost-aware should be mandatory for pm"
    assert cost_aware.is_mandatory_for("coding"), "Cost-aware should be mandatory for coding"
    # Also test that the Skill class handles string "all"
    assert skill_manager.get_skill("coding-plan").is_mandatory_for("coding") == True


def test_skill_prompt_injection():
    """Test that prompt injection works."""
    config = DCAEConfig.load(Path("./config-china.yaml"))
    skill_manager = SkillManager(Path("./skills"))

    coding_plan = skill_manager.get_skill("coding-plan")

    original_prompt = "编写用户登录功能的代码"

    # Inject coding-plan skill - should add instructions
    enhanced_prompt = skill_manager.inject_skill_instructions(
        original_prompt, coding_plan, "initial"
    )

    # Check that something was added
    assert len(enhanced_prompt) > len(original_prompt)
