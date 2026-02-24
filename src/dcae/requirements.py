"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Requirements Management Module

This module implements the requirements input and editing functionality as specified in
Story 2.1: Input and Edit Requirements.

As a product manager,
I want to input and edit project requirements in the DCAE framework,
so that I can provide clear specifications for the subsequent BMAD workflow phases.
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import re


# Define the requirements structure
REQUIREMENTS_SCHEMA = {
    "project_name": "",
    "description": "",
    "functional_requirements": [],
    "non_functional_requirements": [],
    "constraints": [],
    "assumptions": [],
    "acceptance_criteria": [],
    "metadata": {
        "created_date": "",
        "last_modified": "",
        "version": "1.0",
        "authors": []
    }
}


def create_requirements_template(project_name: str = "") -> Dict[str, Any]:
    """Create a template for project requirements."""
    template = REQUIREMENTS_SCHEMA.copy()
    template["project_name"] = project_name
    template["metadata"]["created_date"] = datetime.now().isoformat()
    template["metadata"]["last_modified"] = datetime.now().isoformat()

    return template


def load_requirements(requirements_path: Path) -> Optional[Dict[str, Any]]:
    """Load requirements from a file."""
    if not requirements_path.exists():
        return None

    with open(requirements_path, 'r', encoding='utf-8') as f:
        if requirements_path.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        elif requirements_path.suffix.lower() == '.json':
            return json.load(f)

    return None


def save_requirements(requirements: Dict[str, Any], requirements_path: Path) -> bool:
    """Save requirements to a file."""
    try:
        # Update the last modified timestamp
        requirements["metadata"]["last_modified"] = datetime.now().isoformat()

        # Ensure parent directory exists
        requirements_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine format based on file extension
        if requirements_path.suffix.lower() in ['.yaml', '.yml']:
            with open(requirements_path, 'w', encoding='utf-8') as f:
                yaml.dump(requirements, f, default_flow_style=False, allow_unicode=True, indent=2)
        elif requirements_path.suffix.lower() == '.json':
            with open(requirements_path, 'w', encoding='utf-8') as f:
                json.dump(requirements, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Error saving requirements: {e}")
        return False


def validate_requirements(requirements: Dict[str, Any]) -> List[str]:
    """Validate requirements for completeness and clarity."""
    errors = []

    # Check for essential fields
    if not requirements.get("project_name"):
        errors.append("Project name is required")

    if not requirements.get("description"):
        errors.append("Project description is required")

    # Check that functional requirements exist
    func_reqs = requirements.get("functional_requirements", [])
    if not func_reqs:
        errors.append("At least one functional requirement is required")

    # Validate functional requirements
    for i, req in enumerate(func_reqs):
        if isinstance(req, dict):
            if not req.get("id") or not req.get("description"):
                errors.append(f"Functional requirement #{i+1} must have an id and description")
        elif isinstance(req, str):
            if not req.strip():
                errors.append(f"Functional requirement #{i+1} cannot be empty")
        else:
            errors.append(f"Functional requirement #{i+1} must be a string or dictionary")

    # Validate non-functional requirements
    non_func_reqs = requirements.get("non_functional_requirements", [])
    for i, req in enumerate(non_func_reqs):
        if isinstance(req, dict):
            if not req.get("category") or not req.get("description"):
                errors.append(f"Non-functional requirement #{i+1} must have a category and description")
        elif isinstance(req, str):
            if not req.strip():
                errors.append(f"Non-functional requirement #{i+1} cannot be empty")
        else:
            errors.append(f"Non-functional requirement #{i+1} must be a string or dictionary")

    # Check for reasonable length in descriptions
    desc = requirements.get("description", "")
    if len(desc.strip()) < 10:
        errors.append("Project description should be more detailed (at least 10 characters)")

    return errors


def add_requirement(requirements: Dict[str, Any], req_type: str, requirement: Dict[str, Any]) -> bool:
    """Add a requirement to the requirements document."""
    if req_type == "functional":
        requirements["functional_requirements"].append(requirement)
    elif req_type == "non_functional":
        requirements["non_functional_requirements"].append(requirement)
    elif req_type == "constraint":
        requirements["constraints"].append(requirement)
    elif req_type == "assumption":
        requirements["assumptions"].append(requirement)
    elif req_type == "acceptance":
        requirements["acceptance_criteria"].append(requirement)
    else:
        print(f"Unknown requirement type: {req_type}")
        return False

    return True


def edit_requirement(
    requirements: Dict[str, Any],
    req_type: str,
    index: int,
    new_requirement: Dict[str, Any]
) -> bool:
    """Edit an existing requirement in the requirements document."""
    try:
        if req_type == "functional":
            requirements["functional_requirements"][index] = new_requirement
        elif req_type == "non_functional":
            requirements["non_functional_requirements"][index] = new_requirement
        elif req_type == "constraint":
            requirements["constraints"][index] = new_requirement
        elif req_type == "assumption":
            requirements["assumptions"][index] = new_requirement
        elif req_type == "acceptance":
            requirements["acceptance_criteria"][index] = new_requirement
        else:
            print(f"Unknown requirement type: {req_type}")
            return False

        return True
    except IndexError:
        print(f"Invalid index {index} for requirement type {req_type}")
        return False


def input_requirements_interactively(project_name: str = "") -> Dict[str, Any]:
    """Interactive input for requirements gathering."""
    print("=== DCAE Requirements Input ===")
    print("Let's gather requirements for your project.")
    print()

    requirements = create_requirements_template(project_name)

    # Basic project info
    if not requirements["project_name"]:
        requirements["project_name"] = input("Project Name: ").strip()

    requirements["description"] = input("Project Description: ").strip()

    print("\nNow let's add functional requirements.")
    print("Enter each requirement and press Enter. Leave blank when finished.\n")

    # Functional requirements
    func_count = 0
    while True:
        req_desc = input(f"Functional Requirement #{func_count + 1} (or blank to finish): ").strip()
        if not req_desc:
            break

        # Create a requirement entry
        req = {
            "id": f"FR{func_count + 1:03d}",
            "description": req_desc,
            "priority": "medium"  # Default priority
        }

        requirements["functional_requirements"].append(req)
        func_count += 1

    print("\nNow let's add non-functional requirements.")
    print("Enter each requirement with a category (e.g., performance, security, usability).\n")

    # Non-functional requirements
    non_func_count = 0
    while True:
        category = input(f"Non-functional Requirement #{non_func_count + 1} Category (or blank to finish): ").strip()
        if not category:
            break

        description = input(f"Description for {category} requirement: ").strip()

        # Create a requirement entry
        req = {
            "id": f"NFR{non_func_count + 1:03d}",
            "category": category,
            "description": description,
            "priority": "medium"  # Default priority
        }

        requirements["non_functional_requirements"].append(req)
        non_func_count += 1

    print("\nAdding constraints (optional, leave blank to skip)")
    constraint_count = 0
    while True:
        constraint = input(f"Constraint #{constraint_count + 1} (or blank to finish): ").strip()
        if not constraint:
            break

        requirements["constraints"].append({
            "id": f"C{constraint_count + 1:03d}",
            "description": constraint
        })
        constraint_count += 1

    print("\nAdding assumptions (optional, leave blank to skip)")
    assumption_count = 0
    while True:
        assumption = input(f"Assumption #{assumption_count + 1} (or blank to finish): ").strip()
        if not assumption:
            break

        requirements["assumptions"].append({
            "id": f"A{assumption_count + 1:03d}",
            "description": assumption
        })
        assumption_count += 1

    print("\nFinally, add acceptance criteria (optional, leave blank to skip)")
    acceptance_count = 0
    while True:
        criterion = input(f"Acceptance Criterion #{acceptance_count + 1} (or blank to finish): ").strip()
        if not criterion:
            break

        requirements["acceptance_criteria"].append({
            "id": f"AC{acceptance_count + 1:03d}",
            "description": criterion
        })
        acceptance_count += 1

    # Validate before saving
    errors = validate_requirements(requirements)
    if errors:
        print("\nValidation errors found:")
        for error in errors:
            print(f"- {error}")
        confirm = input("\nDo you want to save anyway? (y/N): ")
        if confirm.lower() != 'y':
            print("Requirements not saved.")
            return None

    return requirements


def edit_requirements_interactively(requirements_path: Path) -> bool:
    """Interactive editing of existing requirements."""
    requirements = load_requirements(requirements_path)
    if not requirements:
        print(f"No requirements found at {requirements_path}")
        return False

    print("=== DCAE Requirements Editor ===")
    print(f"Editing requirements for: {requirements.get('project_name', 'Unknown Project')}")
    print()

    while True:
        print("\nOptions:")
        print("1. View current requirements")
        print("2. Add functional requirement")
        print("3. Add non-functional requirement")
        print("4. Add constraint")
        print("5. Add assumption")
        print("6. Add acceptance criterion")
        print("7. Remove requirement")
        print("8. Save and exit")
        print("9. Exit without saving")

        choice = input("\nEnter your choice (1-9): ").strip()

        if choice == "1":
            print_requirements_summary(requirements)
        elif choice == "2":
            req_desc = input("Enter functional requirement: ").strip()
            if req_desc:
                req = {
                    "id": f"FR{len(requirements['functional_requirements']) + 1:03d}",
                    "description": req_desc,
                    "priority": "medium"
                }
                requirements["functional_requirements"].append(req)
                print(f"Added: {req_desc}")
        elif choice == "3":
            category = input("Enter category (performance, security, etc.): ").strip()
            desc = input("Enter requirement description: ").strip()
            if category and desc:
                req = {
                    "id": f"NFR{len(requirements['non_functional_requirements']) + 1:03d}",
                    "category": category,
                    "description": desc,
                    "priority": "medium"
                }
                requirements["non_functional_requirements"].append(req)
                print(f"Added: {desc} ({category})")
        elif choice == "4":
            constraint = input("Enter constraint: ").strip()
            if constraint:
                req = {
                    "id": f"C{len(requirements['constraints']) + 1:03d}",
                    "description": constraint
                }
                requirements["constraints"].append(req)
                print(f"Added: {constraint}")
        elif choice == "5":
            assumption = input("Enter assumption: ").strip()
            if assumption:
                req = {
                    "id": f"A{len(requirements['assumptions']) + 1:03d}",
                    "description": assumption
                }
                requirements["assumptions"].append(req)
                print(f"Added: {assumption}")
        elif choice == "6":
            criterion = input("Enter acceptance criterion: ").strip()
            if criterion:
                req = {
                    "id": f"AC{len(requirements['acceptance_criteria']) + 1:03d}",
                    "description": criterion
                }
                requirements["acceptance_criteria"].append(req)
                print(f"Added: {criterion}")
        elif choice == "7":
            req_type = input("Type (functional/non_functional/constraint/assumption/acceptance): ").strip().lower()
            if req_type in ['functional', 'non_functional', 'constraint', 'assumption', 'acceptance']:
                req_list = requirements[f"{req_type}_requirements"] if req_type != 'non_functional' else requirements['non_functional_requirements']

                print(f"\nCurrent {req_type} requirements:")
                for i, req in enumerate(req_list):
                    desc = req.get('description', req) if isinstance(req, dict) else req
                    print(f"  {i}. {desc}")

                try:
                    idx = int(input("Enter index to remove: "))
                    if 0 <= idx < len(req_list):
                        removed = req_list.pop(idx)
                        desc = removed.get('description', removed) if isinstance(removed, dict) else removed
                        print(f"Removed: {desc}")
                    else:
                        print("Invalid index")
                except ValueError:
                    print("Invalid input")
            else:
                print("Invalid requirement type")
        elif choice == "8":
            errors = validate_requirements(requirements)
            if errors:
                print("\nValidation errors found:")
                for error in errors:
                    print(f"- {error}")
                confirm = input("\nDo you want to save anyway? (y/N): ")
                if confirm.lower() != 'y':
                    print("Requirements not saved.")
                    continue

            if save_requirements(requirements, requirements_path):
                print(f"Requirements saved to {requirements_path}")
                return True
            else:
                print("Failed to save requirements")
        elif choice == "9":
            print("Changes discarded.")
            return False
        else:
            print("Invalid choice")

    return True


def print_requirements_summary(requirements: Dict[str, Any]):
    """Print a summary of the requirements."""
    print(f"\nProject: {requirements.get('project_name', 'No name')}")
    print(f"Description: {requirements.get('description', 'No description')}")

    print(f"\nFunctional Requirements ({len(requirements.get('functional_requirements', []))}):")
    for i, req in enumerate(requirements.get('functional_requirements', [])):
        if isinstance(req, dict):
            print(f"  FR{i+1:03d}: {req.get('description', '')} [Priority: {req.get('priority', 'N/A')}]")
        else:
            print(f"  FR{i+1:03d}: {req}")

    print(f"\nNon-Functional Requirements ({len(requirements.get('non_functional_requirements', []))}):")
    for i, req in enumerate(requirements.get('non_functional_requirements', [])):
        if isinstance(req, dict):
            print(f"  NFR{i+1:03d}: {req.get('description', '')} ({req.get('category', 'N/A')}) [Priority: {req.get('priority', 'N/A')}]")
        else:
            print(f"  NFR{i+1:03d}: {req}")

    print(f"\nConstraints ({len(requirements.get('constraints', []))}):")
    for i, req in enumerate(requirements.get('constraints', [])):
        if isinstance(req, dict):
            print(f"  C{i+1:03d}: {req.get('description', '')}")
        else:
            print(f"  C{i+1:03d}: {req}")

    print(f"\nAssumptions ({len(requirements.get('assumptions', []))}):")
    for i, req in enumerate(requirements.get('assumptions', [])):
        if isinstance(req, dict):
            print(f"  A{i+1:03d}: {req.get('description', '')}")
        else:
            print(f"  A{i+1:03d}: {req}")

    print(f"\nAcceptance Criteria ({len(requirements.get('acceptance_criteria', []))}):")
    for i, req in enumerate(requirements.get('acceptance_criteria', [])):
        if isinstance(req, dict):
            print(f"  AC{i+1:03d}: {req.get('description', '')}")
        else:
            print(f"  AC{i+1:03d}: {req}")


def initialize_requirements_project(project_path: str, project_name: Optional[str] = None) -> bool:
    """Initialize requirements for a DCAE project."""
    base_path = Path(project_path).resolve()

    # Get project name from directory if not provided
    if not project_name:
        project_name = base_path.name

    # Check if DCAE project exists
    config_path = base_path / ".dcae" / "config.yaml"
    if not config_path.exists():
        print("Error: Not in a DCAE project directory. Initialize the project first with 'dcae init'.")
        return False

    # Create requirements file
    requirements_path = base_path / "requirements.yaml"

    if requirements_path.exists():
        print(f"Requirements file already exists at {requirements_path}")
        overwrite = input("Do you want to overwrite it? (y/N): ")
        if overwrite.lower() != 'y':
            return False

    # Create template requirements
    requirements = create_requirements_template(project_name)
    requirements["description"] = f"Initial requirements for {project_name}"

    # Save requirements
    if save_requirements(requirements, requirements_path):
        print(f"Created requirements file at {requirements_path}")
        return True
    else:
        print("Failed to create requirements file")
        return False


def main():
    """Main function to handle command-line interface for requirements."""
    parser = argparse.ArgumentParser(
        description="Manage project requirements for DCAE framework"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize requirements for the current project"
    )
    parser.add_argument(
        "--input",
        action="store_true",
        help="Interactively input requirements"
    )
    parser.add_argument(
        "--edit",
        action="store_true",
        help="Edit existing requirements"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing requirements"
    )
    parser.add_argument(
        "--project-path",
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    parser.add_argument(
        "--project-name",
        help="Name of the project (default: directory name)"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path)

    if args.init:
        success = initialize_requirements_project(str(project_path), args.project_name)
        if not success:
            sys.exit(1)
    elif args.input:
        requirements = input_requirements_interactively(args.project_name or project_path.name)
        if requirements:
            requirements_path = project_path / "requirements.yaml"
            if save_requirements(requirements, requirements_path):
                print(f"\nRequirements saved to {requirements_path}")
            else:
                print("Failed to save requirements")
                sys.exit(1)
    elif args.edit:
        requirements_path = project_path / "requirements.yaml"
        success = edit_requirements_interactively(requirements_path)
        if not success:
            sys.exit(1)
    elif args.validate:
        requirements_path = project_path / "requirements.yaml"
        requirements = load_requirements(requirements_path)
        if not requirements:
            print(f"No requirements found at {requirements_path}")
            sys.exit(1)

        errors = validate_requirements(requirements)
        if errors:
            print("Validation errors found:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            print("Requirements are valid!")
    else:
        print("Please specify an action: --init, --input, --edit, or --validate")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()