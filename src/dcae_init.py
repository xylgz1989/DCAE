"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Project Initialization Module

This module implements the project initialization functionality as specified in
Story 1.1: Project Initialization.

As a developer,
I want to initialize a new DCAE project,
so that I can start using the BMAD (Business Manager, Architect, Developer) workflow
for my development tasks.
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Define the project structure
PROJECT_STRUCTURE = {
    "directories": [
        ".dcae",  # DCAE-specific configuration directory
        "src",    # Source code
        "tests",  # Test files
        "docs",   # Documentation
        "artifacts",  # Generated outputs
        "config"  # Configuration files
    ],
    "files": {
        ".dcae/config.yaml": {
            "description": "DCAE framework configuration",
            "content": {
                "project": {
                    "name": "",
                    "created_date": "",
                    "version": "0.1.0"
                },
                "dcae": {
                    "version": "1.0.0",
                    "bmad_workflow": {
                        "enabled": True,
                        "discipline_level": "balanced",  # fast, balanced, strict
                        "consensus_enabled": False
                    },
                    "llm_providers": {
                        "openai": {
                            "enabled": False,
                            "api_key": "",
                            "model": "gpt-4o"
                        },
                        "anthropic": {
                            "enabled": False,
                            "api_key": "",
                            "model": "claude-3-5-sonnet-20241022"
                        },
                        "qwen": {
                            "enabled": False,
                            "api_key": "",
                            "model": "qwen-max"
                        },
                        "glm": {
                            "enabled": False,
                            "api_key": "",
                            "model": "glm-4"
                        }
                    }
                }
            }
        },
        ".dcae/state.json": {
            "description": "Project state tracking for BMAD workflow",
            "content": {
                "current_stage": "initialized",
                "stages": {
                    "business": {"completed": False, "timestamp": None},
                    "architecture": {"completed": False, "timestamp": None},
                    "development": {"completed": False, "timestamp": None},
                    "quality_assurance": {"completed": False, "timestamp": None}
                },
                "last_updated": ""
            }
        },
        "README.md": {
            "description": "Project documentation",
            "content": "# DCAE Project\n\nThis project uses the Disciplined Consensus-Driven Agentic Engineering framework.\n\n## BMAD Workflow\n\nThis project follows the BMAD (Business, Architect, Developer) workflow:\n\n- Business: Requirements and planning\n- Architect: System design and architecture\n- Developer: Implementation\n\n## Getting Started\n\n1. Configure your LLM providers in `.dcae/config.yaml`\n2. Run `dcae run` to start the workflow\n"
        },
        "dcae-config.yaml": {
            "description": "Primary DCAE configuration file",
            "content": {
                "project_metadata": {
                    "name": "",
                    "description": "",
                    "version": "0.1.0"
                },
                "workflow_settings": {
                    "active_discipline": "balanced",  # Can be 'fast', 'balanced', or 'strict'
                    "enable_consensus_validation": False,
                    "enable_methodology_enforcement": True
                },
                "integration_settings": {
                    "supported_llm_providers": [],
                    "external_tools": {
                        "version_control": True,
                        "package_managers": ["pip", "npm"]
                    }
                }
            }
        }
    }
}


def create_directory_structure(base_path: Path) -> None:
    """Create the required directory structure for a DCAE project."""
    print(f"Creating DCAE project structure in: {base_path}")

    for dirname in PROJECT_STRUCTURE["directories"]:
        dir_path = base_path / dirname
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created directory: {dir_path}")


def create_files(base_path: Path) -> None:
    """Create the required files with default content."""
    import json
    import yaml

    for filepath, fileinfo in PROJECT_STRUCTURE["files"].items():
        full_path = base_path / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        content = fileinfo["content"]

        # Update dynamic values
        if filepath == ".dcae/config.yaml":
            content["project"]["created_date"] = datetime.now().isoformat()
            content["project"]["name"] = base_path.name
        elif filepath == ".dcae/state.json":
            content["last_updated"] = datetime.now().isoformat()
        elif filepath == "dcae-config.yaml":
            content["project_metadata"]["name"] = base_path.name

        # Determine if YAML or JSON
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            with open(full_path, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        elif filepath.endswith('.json'):
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        else:
            # For README.md, use the string content directly
            with open(full_path, 'w', encoding='utf-8') as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    # If it's not a string but somehow got here, convert to string representation
                    f.write(str(content))

        print(f"  Created file: {full_path}")


def initialize_dcae_project(project_path: str) -> bool:
    """Initialize a new DCAE project at the specified path."""
    base_path = Path(project_path).resolve()

    # Check if directory already exists and is not empty
    if base_path.exists() and any(base_path.iterdir()):
        print(f"Error: Directory {base_path} already exists and is not empty.")
        print("Please choose an empty directory or a new location.")
        return False

    # Create the directory if it doesn't exist
    base_path.mkdir(parents=True, exist_ok=True)

    try:
        # Create directory structure
        create_directory_structure(base_path)

        # Create files with default content
        create_files(base_path)

        print(f"\n✓ Successfully initialized DCAE project at: {base_path}")
        print("\nNext steps:")
        print(f"1. Review and customize configuration in {base_path}/.dcae/config.yaml")
        print(f"2. Add your LLM API keys to the configuration")
        print(f"3. Run 'dcae run' to start the BMAD workflow")

        return True

    except Exception as e:
        print(f"Error initializing project: {e}")
        return False


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Initialize a new DCAE (Disciplined Consensus-Driven Agentic Engineering) project"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path where to create the new DCAE project (default: current directory)"
    )
    parser.add_argument(
        "--name",
        help="Name of the project (default: directory name)"
    )

    args = parser.parse_args()

    success = initialize_dcae_project(args.project_path)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()