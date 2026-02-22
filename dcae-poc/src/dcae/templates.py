"""Template functions for project initialization."""

from pathlib import Path


def create_project_template(project_name: str, output_dir: Path):
    """Create a new DCAE project from template.

    Args:
        project_name: Name of the project
        output_dir: Output directory path
    """
    project_dir = output_dir / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (project_dir / "workflows").mkdir(exist_ok=True)
    (project_dir / "skills").mkdir(exist_ok=True)
    (project_dir / "agents").mkdir(exist_ok=True)
    (project_dir / "artifacts").mkdir(exist_ok=True)

    # Create config file
    config_template = f"""# {project_name} Configuration

project:
  name: "{project_name}"

agents:
  pm:
    name: "Product Manager"
    role: "analysis"
    model: "claude-3-5-sonnet-20241022"
    consensus:
      enabled: false

  architect:
    name: "Architect"
    role: "architecture"
    model: "claude-3-5-sonnet-20241022"
    consensus:
      enabled: true
      models:
        - claude-3-5-sonnet-20241022
        - gpt-4o
      voting_strategy: "unanimous"

  developer:
    name: "Developer"
    role: "coding"
    model: "claude-3-5-sonnet-20241022"
    consensus:
      enabled: true
      models:
        - claude-3-5-sonnet-20241022
        - gpt-4o-mini
      voting_strategy: "majority"

skills:
  brainstorming:
    mandatory_for: ["architect"]
  tdd:
    mandatory_for: ["coding"]
  code_review:
    mandatory_for: ["coding"]

storage:
  type: "sqlite"
  path: "./dcae-poc.db"
"""

    (project_dir / "config.yaml").write_text(config_template, encoding="utf-8")

    # Create example workflow
    workflow_template = f"""name: {project_name} Workflow
description: Example workflow for {project_name}

steps:
  - agent: pm
    task: "Analyze requirements and create product brief"

  - agent: architect
    skill: brainstorming
    task: "Design system architecture"

  - agent: developer
    skill: tdd
    task: "Implement core features"
"""

    (project_dir / "workflows" / "main.yaml").write_text(
        workflow_template, encoding="utf-8"
    )

    # Create README
    readme_template = f"""# {project_name}

DCAE-powered development project.

## Getting Started

Initialize your environment variables:

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

Run the workflow:

```bash
dcae run workflows/main.yaml
```

## Project Structure

```
{project_name}/
├── config.yaml          # Project configuration
├── workflows/           # Workflow definitions
├── skills/              # Custom skills
├── agents/              # Custom agents
├── artifacts/           # Generated artifacts
└── dcae-poc.db         # Decision database
```
"""

    (project_dir / "README.md").write_text(readme_template, encoding="utf-8")
