"""
Tests for the DCAE Preliminary Requirements Document Generator Module
"""

import os
import tempfile
from pathlib import Path
import json
import yaml

from dcae.req_docs_generator import (
    generate_preliminary_requirements_documents,
    create_sample_project_inputs,
    RequirementsDocumentGenerator,
    Objective,
    Stakeholder,
    FunctionalRequirement,
    NonFunctionalRequirement,
    UserStory
)


def test_create_sample_project_inputs():
    """Test that create_sample_project_inputs creates proper sample data."""
    sample_inputs = create_sample_project_inputs()

    assert "project_name" in sample_inputs
    assert sample_inputs["project_name"] == "E-commerce Platform"
    assert "objectives" in sample_inputs
    assert len(sample_inputs["objectives"]) == 3
    assert "stakeholders" in sample_inputs
    assert len(sample_inputs["stakeholders"]) == 3


def test_generate_preliminary_requirements_documents():
    """Test generating preliminary requirements documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Use sample inputs
        project_inputs = create_sample_project_inputs()

        # Generate documents
        documents = generate_preliminary_requirements_documents(
            project_inputs,
            output_dir=project_path
        )

        # Verify documents were returned
        assert len(documents) == 5  # overview, functional, non-functional, user stories, traceability
        assert "requirements-overview.md" in documents
        assert "functional-requirements.md" in documents
        assert "non-functional-requirements.md" in documents
        assert "user-stories.md" in documents
        assert "traceability-matrix.md" in documents

        # Verify files were created in the output directory
        for filename in documents.keys():
            file_path = project_path / filename
            assert file_path.exists()

            # Read the file to ensure it has content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0  # Ensure file is not empty


def test_requirements_document_generator():
    """Test the RequirementsDocumentGenerator class directly."""
    generator = RequirementsDocumentGenerator()

    # Create sample inputs
    project_inputs = {
        "project_name": "Test Project",
        "version": "1.0",
        "project_vision": "A test project to verify functionality."
    }

    # Create sample requirements
    functional_reqs = [
        FunctionalRequirement(
            id="FR001",
            title="Login Functionality",
            objective="OBJ01",
            description="Users should be able to log in to the system",
            priority="High"
        )
    ]

    non_functional_reqs = [
        NonFunctionalRequirement(
            id="NFR001",
            title="Performance Requirement",
            objective="OBJ01",
            description="System should respond within 2 seconds",
            category="Performance",
            metrics="Response time < 2 seconds"
        )
    ]

    user_stories = [
        UserStory(
            id="US001",
            title="As a user, I want to log in",
            objective="OBJ01",
            description="User story for login functionality",
            actor="Registered User",
            goal="access personalized features",
            benefit="to get customized experience"
        )
    ]

    # Test individual document generation
    func_doc = generator.generate_functional_requirements(project_inputs, functional_reqs)
    assert "Functional Requirements" in func_doc
    assert "FR-001" in func_doc  # Note: the template adds a dash between FR and number

    nfr_doc = generator.generate_non_functional_requirements(project_inputs, non_functional_reqs)
    assert "Non-Functional Requirements" in nfr_doc
    assert "NFR-001" in nfr_doc  # Note: the template adds a dash between NFR and number

    user_stories_doc = generator.generate_user_stories(project_inputs, user_stories)
    assert "User Stories" in user_stories_doc
    assert "US-001" in user_stories_doc  # Note: the template adds a dash between US and number

    # Test overview document
    overview_doc = generator.generate_requirements_overview(
        project_inputs,
        functional_reqs,
        non_functional_reqs,
        user_stories
    )
    assert "Test Project" in overview_doc
    assert "Requirements Overview" in overview_doc

    # Test traceability matrix
    objectives = [Objective(id="OBJ01", text="Enable user authentication")]
    traceability_doc = generator.generate_traceability_matrix(
        project_inputs,
        objectives,
        functional_reqs,
        non_functional_reqs,
        user_stories
    )
    assert "Traceability Matrix" in traceability_doc
    assert "OBJ01" in traceability_doc


def test_generate_with_manual_requirements():
    """Test generating documents with manually specified requirements."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Create project inputs with manually specified requirements
        project_inputs = {
            "project_name": "Manual Req Test",
            "version": "1.0",
            "project_vision": "Test manual requirement input.",
            "objectives": [
                {
                    "id": "OBJ01",
                    "text": "Enable data processing",
                    "priority": "High"
                }
            ],
            "stakeholders": [
                {
                    "name": "Data Analyst",
                    "role": "User",
                    "interest": "Access to processed data"
                }
            ],
            "functional_requirements": [
                {
                    "id": "FR_MANUAL_001",
                    "title": "Data Processing Function",
                    "objective": "OBJ01",
                    "description": "System shall process raw data into insights",
                    "priority": "High",
                    "stakeholders": ["Data Analyst"],
                    "acceptance_criteria": [
                        "Data is transformed correctly",
                        "Processing completes within 5 minutes"
                    ]
                }
            ],
            "non_functional_requirements": [
                {
                    "id": "NFR_MANUAL_001",
                    "title": "Scalability Requirement",
                    "objective": "OBJ01",
                    "description": "System shall scale to handle 10K concurrent users",
                    "category": "Scalability",
                    "priority": "Medium",
                    "metrics": "Support 10K concurrent users"
                }
            ],
            "user_stories": [
                {
                    "id": "US_MANUAL_001",
                    "title": "As an analyst, I want processed data",
                    "objective": "OBJ01",
                    "actor": "Data Analyst",
                    "goal": "analyze business trends",
                    "benefit": "to make informed decisions",
                    "priority": "High"
                }
            ]
        }

        # Generate documents
        documents = generate_preliminary_requirements_documents(
            project_inputs,
            output_dir=project_path
        )

        # Verify documents were created
        assert len(documents) == 5

        # Check that manual requirements appear in the output
        func_content = documents["functional-requirements.md"]
        assert "FR-002" in func_content  # Manual requirement becomes FR-002 after auto-generated one
        assert "Data Processing Function" in func_content

        nfr_content = documents["non-functional-requirements.md"]
        assert "NFR-002" in nfr_content  # Manual requirement becomes NFR-002 after auto-generated one
        assert "Scalability Requirement" in nfr_content

        user_stories_content = documents["user-stories.md"]
        assert "US-002" in user_stories_content  # Manual requirement becomes US-002 after auto-generated one
        assert "As an analyst, I want processed data" in user_stories_content


if __name__ == "__main__":
    # Run tests
    test_create_sample_project_inputs()
    test_generate_preliminary_requirements_documents()
    test_requirements_document_generator()
    test_generate_with_manual_requirements()
    print("All tests passed!")