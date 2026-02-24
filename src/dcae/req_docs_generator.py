"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Preliminary Requirements Document Generator Module

This module implements the preliminary requirements document generation functionality
as specified in Story 2.2: Generate Preliminary Requirements Documents.

As a product manager,
I want to generate preliminary requirements documents from initial project inputs,
so that I can establish a baseline for requirement discussions and traceability.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from jinja2 import Template, Environment, select_autoescape

# Templates for different types of requirements documents
DEFAULT_TEMPLATES = {
    "functional_requirements": """
# Functional Requirements

## FR-{{ "%03d"|format(index) }}: {{ requirement.title }}

**Objective**: {{ requirement.objective }}

**Description**: {{ requirement.description }}

**Priority**: {{ requirement.priority | default('Medium') }}

**Stakeholders**: {{ requirement.stakeholders | join(', ') | default('N/A') }}

**Acceptance Criteria**:
{% for criterion in requirement.acceptance_criteria %}
- {{ criterion }}
{% endfor %}

**Traceability**: Links to objective "{{ requirement.traceability.objective }}"
""",
    "non_functional_requirements": """
# Non-Functional Requirements

## NFR-{{ "%03d"|format(index) }}: {{ requirement.category }} - {{ requirement.title }}

**Objective**: {{ requirement.objective }}

**Description**: {{ requirement.description }}

**Category**: {{ requirement.category }}

**Priority**: {{ requirement.priority | default('Medium') }}

**Metrics/Standards**: {{ requirement.metrics | default('TBD') }}

**Stakeholders**: {{ requirement.stakeholders | join(', ') | default('N/A') }}

**Traceability**: Links to objective "{{ requirement.traceability.objective }}"
""",
    "user_stories": """
# User Stories

## US-{{ "%03d"|format(index) }}: {{ requirement.title }}

**As a** {{ requirement.actor }},
**I want** {{ requirement.goal }},
**So that** {{ requirement.benefit }}.

**Objective**: {{ requirement.objective }}

**Acceptance Criteria**:
{% for criterion in requirement.acceptance_criteria %}
- {{ criterion }}
{% endfor %}

**Priority**: {{ requirement.priority | default('Medium') }}

**Estimate**: {{ requirement.estimate | default('TBD') }}

**Stakeholders**: {{ requirement.stakeholders | join(', ') | default('N/A') }}

**Traceability**: Links to objective "{{ requirement.traceability.objective }}"
""",
    "requirements_overview": """
# {{ project_name }} - Requirements Overview

**Document Version**: {{ version }}
**Date**: {{ date }}
**Author(s)**: {{ author | default('TBA') }}

## Project Vision
{{ project_vision }}

## Objectives
{% for objective in objectives %}
- {{ objective.text }} (ID: {{ objective.id }})
{% endfor %}

## Stakeholders
{% for stakeholder in stakeholders %}
- **{{ stakeholder.name }}**: {{ stakeholder.role }} - {{ stakeholder.interest }}
{% endfor %}

## Requirements Summary
- Total Functional Requirements: {{ functional_count }}
- Total Non-Functional Requirements: {{ non_functional_count }}
- Total User Stories: {{ user_stories_count }}

## Traceability Matrix
| Objective ID | Requirement ID | Requirement Type |
|--------------|----------------|------------------|
{% for link in traceability_links %}
| {{ link.objective_id }} | {{ link.requirement_id }} | {{ link.type }} |
{% endfor %}

""",
    "traceability_matrix": """
# Traceability Matrix for {{ project_name }}

Generated on: {{ date }}

## Mapping Table
| Objective | FR Requirements | NFR Requirements | User Stories |
|-----------|----------------|------------------|--------------|
{% for obj in objectives %}
| {{ obj.id }}: {{ obj.text }} | {% for req in obj.functional_requirements %}{{ req.id }}{% if not loop.last %}, {% endif %}{% endfor %} | {% for req in obj.non_functional_requirements %}{{ req.id }}{% if not loop.last %}, {% endif %}{% endfor %} | {% for req in obj.user_stories %}{{ req.id }}{% if not loop.last %}, {% endif %}{% endfor %} |
{% endfor %}

## Detailed Mappings
{% for obj in objectives %}
### Objective: {{ obj.id }} - {{ obj.text }}
{% if obj.functional_requirements %}
#### Functional Requirements:
{% for req in obj.functional_requirements %}
- {{ req.id }}: {{ req.title }}
{% endfor %}
{% endif %}
{% if obj.non_functional_requirements %}
#### Non-Functional Requirements:
{% for req in obj.non_functional_requirements %}
- {{ req.id }}: {{ req.title }}
{% endfor %}
{% endif %}
{% if obj.user_stories %}
#### User Stories:
{% for req in obj.user_stories %}
- {{ req.id }}: {{ req.title }}
{% endfor %}
{% endif %}

{% endfor %}
"""
}


@dataclass
class Objective:
    """Represents a high-level project objective."""
    id: str
    text: str
    priority: str = "Medium"
    description: str = ""


@dataclass
class Stakeholder:
    """Represents a project stakeholder."""
    name: str
    role: str
    interest: str
    contact: Optional[str] = None


@dataclass
class Requirement:
    """Base requirement class."""
    id: str
    title: str
    objective: str
    description: str
    priority: str = "Medium"
    stakeholders: List[str] = None
    acceptance_criteria: List[str] = None
    traceability: Dict[str, str] = None

    def __post_init__(self):
        if self.stakeholders is None:
            self.stakeholders = []
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.traceability is None:
            self.traceability = {}


@dataclass
class FunctionalRequirement(Requirement):
    """Functional requirement subclass."""
    type: str = "functional"


@dataclass
class NonFunctionalRequirement(Requirement):
    """Non-functional requirement subclass."""
    category: str = "Performance"
    metrics: str = ""
    type: str = "non_functional"


@dataclass
class UserStory(Requirement):
    """User story subclass."""
    actor: str = ""
    goal: str = ""
    benefit: str = ""
    estimate: str = "TBD"
    type: str = "user_story"

    def __post_init__(self):
        if self.stakeholders is None:
            self.stakeholders = []
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.traceability is None:
            self.traceability = {}


class RequirementsDocumentGenerator:
    """Generates preliminary requirements documents from project inputs."""

    def __init__(self, templates: Optional[Dict[str, str]] = None):
        """
        Initialize the requirements document generator.

        Args:
            templates: Optional custom templates. If not provided, default templates are used.
        """
        self.templates = templates or DEFAULT_TEMPLATES
        self.environment = Environment(
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_functional_requirements(
        self,
        project_inputs: Dict[str, Any],
        requirements: List[FunctionalRequirement]
    ) -> str:
        """
        Generate functional requirements document.

        Args:
            project_inputs: Dictionary containing project information
            requirements: List of functional requirements

        Returns:
            Generated document as a string
        """
        content = "# Functional Requirements\n\n"
        for i, req in enumerate(requirements, 1):
            template_str = self.templates["functional_requirements"]
            template = Template(template_str)
            content += template.render(
                index=i,
                requirement=req.__dict__
            )
            content += "\n\n"

        return content.strip()

    def generate_non_functional_requirements(
        self,
        project_inputs: Dict[str, Any],
        requirements: List[NonFunctionalRequirement]
    ) -> str:
        """
        Generate non-functional requirements document.

        Args:
            project_inputs: Dictionary containing project information
            requirements: List of non-functional requirements

        Returns:
            Generated document as a string
        """
        content = "# Non-Functional Requirements\n\n"
        for i, req in enumerate(requirements, 1):
            template_str = self.templates["non_functional_requirements"]
            template = Template(template_str)
            content += template.render(
                index=i,
                requirement=req.__dict__
            )
            content += "\n\n"

        return content.strip()

    def generate_user_stories(
        self,
        project_inputs: Dict[str, Any],
        requirements: List[UserStory]
    ) -> str:
        """
        Generate user stories document.

        Args:
            project_inputs: Dictionary containing project information
            requirements: List of user stories

        Returns:
            Generated document as a string
        """
        content = "# User Stories\n\n"
        for i, req in enumerate(requirements, 1):
            template_str = self.templates["user_stories"]
            template = Template(template_str)
            content += template.render(
                index=i,
                requirement=req.__dict__
            )
            content += "\n\n"

        return content.strip()

    def generate_requirements_overview(
        self,
        project_inputs: Dict[str, Any],
        functional_requirements: List[FunctionalRequirement],
        non_functional_requirements: List[NonFunctionalRequirement],
        user_stories: List[UserStory]
    ) -> str:
        """
        Generate a high-level requirements overview document.

        Args:
            project_inputs: Dictionary containing project information
            functional_requirements: List of functional requirements
            non_functional_requirements: List of non-functional requirements
            user_stories: List of user stories

        Returns:
            Generated document as a string
        """
        # Prepare traceability links
        traceability_links = []
        for req in functional_requirements:
            traceability_links.append({
                "objective_id": req.objective,
                "requirement_id": req.id,
                "type": "Functional"
            })
        for req in non_functional_requirements:
            traceability_links.append({
                "objective_id": req.objective,
                "requirement_id": req.id,
                "type": "Non-Functional"
            })
        for req in user_stories:
            traceability_links.append({
                "objective_id": req.objective,
                "requirement_id": req.id,
                "type": "User Story"
            })

        # Render the template
        template_str = self.templates["requirements_overview"]
        template = Template(template_str)

        rendered = template.render(
            project_name=project_inputs.get("project_name", "Untitled Project"),
            version=project_inputs.get("version", "1.0"),
            date=datetime.now().strftime("%Y-%m-%d"),
            author=project_inputs.get("author"),
            project_vision=project_inputs.get("project_vision", ""),
            objectives=project_inputs.get("objectives", []),
            stakeholders=project_inputs.get("stakeholders", []),
            functional_count=len(functional_requirements),
            non_functional_count=len(non_functional_requirements),
            user_stories_count=len(user_stories),
            traceability_links=traceability_links
        )

        return rendered.strip()

    def generate_traceability_matrix(
        self,
        project_inputs: Dict[str, Any],
        objectives: List[Objective],
        functional_requirements: List[FunctionalRequirement],
        non_functional_requirements: List[NonFunctionalRequirement],
        user_stories: List[UserStory]
    ) -> str:
        """
        Generate traceability matrix document.

        Args:
            project_inputs: Dictionary containing project information
            objectives: List of project objectives
            functional_requirements: List of functional requirements
            non_functional_requirements: List of non-functional requirements
            user_stories: List of user stories

        Returns:
            Generated document as a string
        """
        # Group requirements by objective
        objectives_with_requirements = []
        for obj in objectives:
            obj_dict = obj.__dict__.copy()
            obj_dict["functional_requirements"] = [
                req for req in functional_requirements if req.objective == obj.id
            ]
            obj_dict["non_functional_requirements"] = [
                req for req in non_functional_requirements if req.objective == obj.id
            ]
            obj_dict["user_stories"] = [
                req for req in user_stories if req.objective == obj.id
            ]
            objectives_with_requirements.append(obj_dict)

        # Render the template
        template_str = self.templates["traceability_matrix"]
        template = Template(template_str)

        rendered = template.render(
            project_name=project_inputs.get("project_name", "Untitled Project"),
            date=datetime.now().strftime("%Y-%m-%d"),
            objectives=objectives_with_requirements
        )

        return rendered.strip()


def generate_preliminary_requirements_documents(
    project_inputs: Dict[str, Any],
    output_dir: Optional[Path] = None
) -> Dict[str, str]:
    """
    Generate preliminary requirements documents from project inputs.

    Args:
        project_inputs: Dictionary containing project information
        output_dir: Optional directory to save documents. If not provided, returns content as strings.

    Returns:
        Dictionary with document names as keys and content as values
    """
    generator = RequirementsDocumentGenerator()

    # Extract inputs
    objectives = [
        Objective(
            id=obj.get("id", f"OBJ{i:02d}"),
            text=obj.get("text", f"Objective {i}"),
            priority=obj.get("priority", "Medium"),
            description=obj.get("description", "")
        )
        for i, obj in enumerate(project_inputs.get("objectives", []), 1)
    ]

    stakeholders = [
        Stakeholder(
            name=stake.get("name", f"Stakeholder {i}"),
            role=stake.get("role", "User"),
            interest=stake.get("interest", "General Interest"),
            contact=stake.get("contact")
        )
        for i, stake in enumerate(project_inputs.get("stakeholders", []), 1)
    ]

    # Generate requirements based on project vision and objectives
    functional_requirements = []
    non_functional_requirements = []
    user_stories = []

    # Create requirements based on objectives
    for i, obj in enumerate(objectives, 1):
        # Generate functional requirements
        func_req = FunctionalRequirement(
            id=f"FR{i:03d}",
            title=f"Support {obj.text.lower().replace(' ', '_')}",
            objective=obj.id,
            description=f"The system shall provide functionality to fulfill the objective: {obj.text}",
            priority=obj.priority,
            stakeholders=[stake.name for stake in stakeholders],
            acceptance_criteria=[f"Objective '{obj.text}' is satisfied by the system"]
        )
        functional_requirements.append(func_req)

        # Generate non-functional requirements
        nfr_req = NonFunctionalRequirement(
            id=f"NFR{i:03d}",
            title=f"{obj.text} Performance",
            objective=obj.id,
            description=f"The system performance shall meet the expectations for: {obj.text}",
            category="Performance",
            priority=obj.priority,
            stakeholders=[stake.name for stake in stakeholders],
            acceptance_criteria=[f"Performance benchmarks for '{obj.text}' are met"]
        )
        non_functional_requirements.append(nfr_req)

        # Generate user stories
        user_story = UserStory(
            id=f"US{i:03d}",
            title=f"As a user, I want to achieve {obj.text.lower()}",
            objective=obj.id,
            actor="End User",
            goal=obj.text.lower(),
            benefit=f"So that I can accomplish my goal regarding {obj.text}",
            description=f"Implementation of functionality to support: {obj.text}",
            priority=obj.priority,
            stakeholders=[stake.name for stake in stakeholders],
            acceptance_criteria=[f"The user can successfully perform actions related to {obj.text}"]
        )
        user_stories.append(user_story)

    # Add any manually specified requirements
    for i, req_data in enumerate(project_inputs.get("functional_requirements", []), len(functional_requirements)+1):
        req = FunctionalRequirement(
            id=req_data.get("id", f"FR{i:03d}"),
            title=req_data.get("title", f"Functional Requirement {i}"),
            objective=req_data.get("objective", "General"),
            description=req_data.get("description", ""),
            priority=req_data.get("priority", "Medium"),
            stakeholders=req_data.get("stakeholders", []),
            acceptance_criteria=req_data.get("acceptance_criteria", [])
        )
        functional_requirements.append(req)

    for i, req_data in enumerate(project_inputs.get("non_functional_requirements", []), len(non_functional_requirements)+1):
        req = NonFunctionalRequirement(
            id=req_data.get("id", f"NFR{i:03d}"),
            title=req_data.get("title", f"Non-Functional Requirement {i}"),
            objective=req_data.get("objective", "General"),
            description=req_data.get("description", ""),
            category=req_data.get("category", "Performance"),
            priority=req_data.get("priority", "Medium"),
            metrics=req_data.get("metrics", ""),
            stakeholders=req_data.get("stakeholders", []),
            acceptance_criteria=req_data.get("acceptance_criteria", [])
        )
        non_functional_requirements.append(req)

    for i, req_data in enumerate(project_inputs.get("user_stories", []), len(user_stories)+1):
        req = UserStory(
            id=req_data.get("id", f"US{i:03d}"),
            title=req_data.get("title", f"User Story {i}"),
            objective=req_data.get("objective", "General"),
            actor=req_data.get("actor", "User"),
            goal=req_data.get("goal", ""),
            benefit=req_data.get("benefit", ""),
            description=req_data.get("description", ""),
            priority=req_data.get("priority", "Medium"),
            estimate=req_data.get("estimate", "TBD"),
            stakeholders=req_data.get("stakeholders", []),
            acceptance_criteria=req_data.get("acceptance_criteria", [])
        )
        user_stories.append(req)

    # Generate documents
    documents = {}

    # Requirements overview
    documents["requirements-overview.md"] = generator.generate_requirements_overview(
        project_inputs,
        functional_requirements,
        non_functional_requirements,
        user_stories
    )

    # Functional requirements
    documents["functional-requirements.md"] = generator.generate_functional_requirements(
        project_inputs,
        functional_requirements
    )

    # Non-functional requirements
    documents["non-functional-requirements.md"] = generator.generate_non_functional_requirements(
        project_inputs,
        non_functional_requirements
    )

    # User stories
    documents["user-stories.md"] = generator.generate_user_stories(
        project_inputs,
        user_stories
    )

    # Traceability matrix
    documents["traceability-matrix.md"] = generator.generate_traceability_matrix(
        project_inputs,
        objectives,
        functional_requirements,
        non_functional_requirements,
        user_stories
    )

    # Save to output directory if specified
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in documents.items():
            file_path = output_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    return documents


def create_sample_project_inputs() -> Dict[str, Any]:
    """
    Create sample project inputs for demonstration purposes.

    Returns:
        Sample project inputs dictionary
    """
    return {
        "project_name": "E-commerce Platform",
        "version": "1.0",
        "project_vision": "Create a modern, scalable e-commerce platform that enables businesses to sell products online efficiently.",
        "objectives": [
            {
                "id": "OBJ01",
                "text": "Enable online product sales",
                "priority": "High",
                "description": "Allow businesses to list products and enable customers to purchase them online"
            },
            {
                "id": "OBJ02",
                "text": "Provide user account management",
                "priority": "High",
                "description": "Enable customers to create accounts, track orders, and manage preferences"
            },
            {
                "id": "OBJ03",
                "text": "Implement secure payment processing",
                "priority": "Critical",
                "description": "Process payments securely and efficiently with multiple payment options"
            }
        ],
        "stakeholders": [
            {
                "name": "Business Owner",
                "role": "Product Owner",
                "interest": "Revenue generation and customer satisfaction"
            },
            {
                "name": "End Customer",
                "role": "User",
                "interest": "Easy purchasing experience and reliable service"
            },
            {
                "name": "IT Department",
                "role": "Technical Stakeholder",
                "interest": "System reliability and security"
            }
        ]
    }


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate preliminary requirements documents from project inputs"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to input file containing project information (JSON or YAML)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./requirements-docs",
        help="Directory to save generated documents (default: ./requirements-docs)"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate documents using sample project inputs"
    )

    args = parser.parse_args()

    if args.sample:
        project_inputs = create_sample_project_inputs()
        print("Using sample project inputs...")
    elif args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file {input_path} does not exist.")
            return 1

        with open(input_path, 'r', encoding='utf-8') as f:
            if input_path.suffix.lower() in ['.yaml', '.yml']:
                project_inputs = yaml.safe_load(f)
            else:
                project_inputs = json.load(f)
    else:
        print("Error: Please specify either --input-file or --sample")
        parser.print_help()
        return 1

    output_dir = Path(args.output_dir)

    try:
        documents = generate_preliminary_requirements_documents(
            project_inputs,
            output_dir=output_dir
        )

        print(f"Generated {len(documents)} requirements documents in {output_dir}/:")
        for filename in documents.keys():
            print(f"  - {filename}")

        print("\nPreliminary requirements documents generation completed successfully!")
        return 0

    except Exception as e:
        print(f"Error generating requirements documents: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())