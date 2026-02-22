"""Skill management for Superpowers methodology enforcement."""

import yaml
from pathlib import Path
from typing import Dict, Optional


class Skill:
    """Represents a Superpowers skill."""

    def __init__(self, name: str, config: Dict):
        """Initialize a skill.

        Args:
            name: Skill name
            config: Skill configuration
        """
        self.name = name
        self.description = config.get("description", "")
        self.mandatory_for = config.get("mandatory_for", [])
        self.prompts = config.get("prompts", {})
        self.instructions = config.get("instructions", [])

    def get_prompt_for_phase(self, phase: str) -> Optional[str]:
        """Get the prompt for a specific phase.

        Args:
            phase: Phase name (e.g., "red", "green", "refactor")

        Returns:
            Prompt string or None
        """
        return self.prompts.get(phase)

    def is_mandatory_for(self, agent_role: str) -> bool:
        """Check if this skill is mandatory for an agent role.

        Args:
            agent_role: Agent role

        Returns:
            True if mandatory
        """
        # Handle cases where mandatory_for might be a string (e.g., from YAML) instead of list
        if isinstance(self.mandatory_for, str):
            return agent_role == self.mandatory_for or agent_role in self.mandatory_for.split(",")
        else:
            return agent_role in self.mandatory_for


class SkillManager:
    """Manager for loading and managing Superpowers skills."""

    def __init__(self, skills_dir: Path):
        """Initialize the skill manager.

        Args:
            skills_dir: Directory containing skill definitions
        """
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self._load_skills()

    def _load_skills(self):
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            return

        for skill_file in self.skills_dir.glob("*.yaml"):
            try:
                with open(skill_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                # Handle cases where YAML might return string instead of dict
                if config is None:
                    print(f"Warning: Empty YAML file: {skill_file}")
                    continue

                if not isinstance(config, dict):
                    # Try to parse the string content
                    if isinstance(config, str):
                        # The content might be embedded in a string, try to re-parse
                        try:
                            import re
                            # Extract YAML content if it's embedded in quotes
                            match = re.search(r'"(.+)"', config, re.DOTALL)
                            if match:
                                config = yaml.safe_load(match.group(1))
                            else:
                                # Just try to parse the raw string
                                config = yaml.safe_load(config)
                        except Exception as e:
                            print(f"Warning: Failed to parse skill file {skill_file}: {e}")
                            continue
                    else:
                        print(f"Warning: Unexpected config type {type(config)} in {skill_file}")
                        continue

                if not isinstance(config, dict):
                    print(f"Warning: Config is still not a dict in {skill_file}")
                    continue

                skill_name = skill_file.stem
                self.skills[skill_name] = Skill(skill_name, config)

            except Exception as e:
                print(f"Error loading skill {skill_file}: {e}")
                continue

    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name.

        Args:
            name: Skill name

        Returns:
            Skill instance or None
        """
        return self.skills.get(name)

    def get_mandatory_skills_for(self, agent_role: str) -> list[Skill]:
        """Get all mandatory skills for an agent role.

        Args:
            agent_role: Agent role

        Returns:
            List of mandatory skills
        """
        return [
            skill
            for skill in self.skills.values()
            if skill.is_mandatory_for(agent_role)
        ]

    def inject_skill_instructions(
        self, prompt: str, skill: Skill, phase: Optional[str] = None
    ) -> str:
        """Inject skill instructions into a prompt.

        Args:
            prompt: Original prompt
            skill: Skill to inject
            phase: Optional phase for phase-specific prompts

        Returns:
            Enhanced prompt with skill instructions
        """
        instructions = []

        # Add skill description
        if skill.description:
            instructions.append(f"### Methodology: {skill.name}")
            instructions.append(skill.description)

        # Add phase-specific prompt if provided
        if phase:
            phase_prompt = skill.get_prompt_for_phase(phase)
            if phase_prompt:
                instructions.append(f"\n### {phase.upper()} Phase:")
                instructions.append(phase_prompt)

        # Add general instructions
        if skill.instructions:
            instructions.append("\n### Instructions:")
            for instruction in skill.instructions:
                instructions.append(f"- {instruction}")

        if instructions:
            return "\n\n".join(instructions) + "\n\n" + prompt

        return prompt
