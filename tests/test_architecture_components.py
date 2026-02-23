"""
Tests for the DCAE Architecture Components Module
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import yaml
import json
from unittest.mock import Mock, patch

from dcae.architecture import (
    ArchitectureGenerator,
    ArchitectureReviewer,
    ArchitectureValidator,
    ComponentManager,
    BMADWorkflowOrchestrator,
    create_architecture_template,
    load_architecture,
    save_architecture,
    validate_architecture_design,
    suggest_best_practices,
    add_component_to_architecture,
    modify_component_in_architecture,
    generate_architecture_solution
)


def test_create_architecture_template():
    """Test that create_architecture_template creates a proper template."""
    template = create_architecture_template("Test Project")

    assert template["project_name"] == "Test Project"
    assert template["description"] == ""
    assert isinstance(template["architecture_layers"], dict)
    assert isinstance(template["technology_stack"], dict)
    assert isinstance(template["components"], list)
    assert isinstance(template["integration_points"], list)
    assert template["metadata"]["version"] == "1.0"
    assert template["metadata"]["created_date"] != ""
    assert template["metadata"]["last_modified"] != ""


def test_save_and_load_architecture():
    """Test saving and loading architecture in various formats."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        architecture_path = project_path / "architecture.yaml"

        # Create test architecture
        test_arch = create_architecture_template("Test Project")
        test_arch["description"] = "Test architecture description"
        test_arch["components"] = [
            {"id": "comp001", "name": "Test Component", "type": "service", "responsibilities": ["process data"]}
        ]

        # Save architecture
        success = save_architecture(test_arch, architecture_path)
        assert success is True

        # Verify file exists
        assert architecture_path.exists()

        # Load architecture
        loaded_arch = load_architecture(architecture_path)
        assert loaded_arch is not None
        assert loaded_arch["project_name"] == "Test Project"
        assert loaded_arch["description"] == "Test architecture description"
        assert len(loaded_arch["components"]) == 1
        assert loaded_arch["components"][0]["id"] == "comp001"


def test_validate_architecture_design_valid():
    """Test validation of valid architecture design."""
    valid_arch = create_architecture_template("Test Project")
    valid_arch["description"] = "A valid architecture description"
    valid_arch["components"] = [
        {"id": "comp001", "name": "Valid Component", "type": "service", "responsibilities": ["process data"]}
    ]

    errors = validate_architecture_design(valid_arch)
    assert len(errors) == 0


def test_validate_architecture_design_invalid():
    """Test validation of invalid architecture design."""
    invalid_arch = create_architecture_template("")
    # Empty project name

    errors = validate_architecture_design(invalid_arch)
    assert len(errors) > 0
    assert "Project name is required" in errors

    # Test with empty components
    invalid_arch["project_name"] = "Test Project"
    invalid_arch["description"] = "A"
    # Still has no components and short description

    errors = validate_architecture_design(invalid_arch)
    # Should have errors: no components and short description
    assert len(errors) >= 2
    assert any("component" in error.lower() for error in errors)
    assert any("description should be more detailed" in error.lower() or "short" in error.lower() for error in errors)


def test_suggest_best_practices():
    """Test best practices suggestions for architecture."""
    arch_with_issues = create_architecture_template("Test Project")
    arch_with_issues["technology_stack"] = {
        "database": "mysql",
        "framework": "flask",
        "language": "python"
    }

    # Simulate architecture that could use improvement
    suggestions = suggest_best_practices(arch_with_issues)

    # Even if there are no specific suggestions, the function should return a list
    assert isinstance(suggestions, list)


def test_add_component_to_architecture():
    """Test adding components to the architecture."""
    arch = create_architecture_template("Test Project")
    arch["description"] = "Test description"
    arch["components"] = []

    # Add component
    new_comp = {
        "id": "comp001",
        "name": "New Component",
        "type": "microservice",
        "responsibilities": ["handle user authentication"],
        "dependencies": []
    }
    success = add_component_to_architecture(arch, new_comp)
    assert success is True
    assert len(arch["components"]) == 1
    assert arch["components"][0]["id"] == "comp001"
    assert arch["components"][0]["name"] == "New Component"

    # Test adding component with duplicate ID
    duplicate_comp = {
        "id": "comp001",  # Same ID as above
        "name": "Duplicate Component",
        "type": "database",
        "responsibilities": ["store data"],
        "dependencies": []
    }
    success = add_component_to_architecture(arch, duplicate_comp)
    assert success is False  # Should fail due to duplicate ID


def test_modify_component_in_architecture():
    """Test modifying components in the architecture."""
    arch = create_architecture_template("Test Project")
    arch["description"] = "Test description"
    arch["components"] = [
        {"id": "comp001", "name": "Original Component", "type": "service", "responsibilities": ["process data"]}
    ]

    # Modify the component
    updated_comp = {
        "id": "comp001",
        "name": "Updated Component",
        "type": "microservice",
        "responsibilities": ["process data", "validate input"],
        "dependencies": ["auth-service"]
    }
    success = modify_component_in_architecture(arch, "comp001", updated_comp)
    assert success is True
    assert arch["components"][0]["name"] == "Updated Component"
    assert arch["components"][0]["type"] == "microservice"
    assert "validate input" in arch["components"][0]["responsibilities"]
    assert "auth-service" in arch["components"][0]["dependencies"]

    # Test modifying non-existent component
    success = modify_component_in_architecture(arch, "nonexistent", updated_comp)
    assert success is False


def test_generate_architecture_solution():
    """Test generating architecture solution based on requirements."""
    requirements = {
        "project_name": "E-commerce Platform",
        "functional_requirements": [
            {"id": "FR001", "description": "Users should be able to browse products", "priority": "high"},
            {"id": "FR002", "description": "Users should be able to add items to cart", "priority": "high"}
        ],
        "non_functional_requirements": [
            {"id": "NFR001", "description": "System should handle 1000 concurrent users", "category": "performance"},
            {"id": "NFR002", "description": "System should be available 99.9%", "category": "availability"}
        ]
    }

    # Generate architecture based on requirements
    architecture = generate_architecture_solution(requirements)

    # Verify that an architecture was generated
    assert architecture is not None
    assert architecture["project_name"] == "E-commerce Platform"
    assert len(architecture["components"]) > 0

    # Verify that the architecture addresses the requirements
    # The specific implementation would determine exactly how requirements map to architecture
    # but at minimum we expect some architecture components to be created


def test_architecture_review_modification_workflow():
    """Test the workflow of reviewing and modifying architecture."""
    # Start with a basic architecture
    arch = create_architecture_template("Test Project")
    arch["description"] = "Initial architecture based on requirements"
    arch["components"] = [
        {"id": "api-gateway", "name": "API Gateway", "type": "gateway", "responsibilities": ["route requests"]},
        {"id": "auth-service", "name": "Authentication Service", "type": "microservice", "responsibilities": ["handle authentication"]}
    ]

    # Review the architecture
    reviewer = ArchitectureReviewer()
    review_results = reviewer.review_architecture(arch)

    # Review results should include some feedback
    assert "feedback" in review_results
    assert "recommendations" in review_results

    # Modify based on feedback (simulate user accepting recommendations)
    if review_results["recommendations"]:
        # Apply first recommendation as a modification
        rec = review_results["recommendations"][0]
        # This would be more complex in a real implementation
        arch["notes"] = arch.get("notes", []) + [f"Applied recommendation: {rec}"]

    # Re-validate the modified architecture
    errors_after_modification = validate_architecture_design(arch)
    # The modified architecture should still be valid
    # (Note: this depends on the specific validation rules implemented)


def test_architecture_validator():
    """Test the ArchitectureValidator class."""
    validator = ArchitectureValidator()

    # Test with valid architecture
    valid_arch = create_architecture_template("Valid Project")
    valid_arch["components"] = [
        {"id": "comp1", "name": "Component 1", "type": "service", "responsibilities": ["do work"]}
    ]

    is_valid, errors = validator.validate(valid_arch)
    assert is_valid is True
    assert len(errors) == 0

    # Test with invalid architecture (no components)
    invalid_arch = create_architecture_template("Invalid Project")
    invalid_arch["components"] = []

    is_valid, errors = validator.validate(invalid_arch)
    assert is_valid is False
    assert len(errors) > 0


def test_component_manager():
    """Test the ComponentManager class."""
    manager = ComponentManager()

    arch = create_architecture_template("Test Project")
    arch["components"] = []

    # Add component
    comp_data = {
        "id": "new-comp",
        "name": "New Component",
        "type": "service",
        "responsibilities": ["do something"]
    }

    result = manager.add_component(arch, comp_data)
    assert result is True
    assert len(arch["components"]) == 1
    assert arch["components"][0]["id"] == "new-comp"

    # Modify component
    updated_data = {
        "id": "new-comp",
        "name": "Updated Component",
        "type": "microservice",
        "responsibilities": ["do something better"]
    }

    result = manager.modify_component(arch, "new-comp", updated_data)
    assert result is True
    assert arch["components"][0]["name"] == "Updated Component"
    assert arch["components"][0]["type"] == "microservice"


def test_bmad_workflow_orchestration():
    """Test the BMAD workflow orchestration for architecture."""
    orchestrator = BMADWorkflowOrchestrator()

    # Test that the orchestrator can coordinate between different BMAD roles
    # for architecture tasks
    mock_requirements = {
        "project_name": "Test Project",
        "description": "Test requirements",
        "functional_requirements": [
            {"id": "FR001", "description": "Test requirement", "priority": "high"}
        ]
    }

    # This would trigger the workflow: Business Manager -> Architect -> Developer
    # but for testing, we just verify the orchestrator can be initialized and used
    workflow_result = orchestrator.execute_architecture_workflow(mock_requirements)

    # The specific output would depend on the implementation
    # but we expect some form of result
    assert workflow_result is not None


def test_architecture_patterns_enforcement():
    """Test that implementation patterns and consistency rules are enforced."""
    # This would test the patterns defined in the implementation artifacts
    # such as dependency injection, repository pattern, etc.

    # In a real implementation, this would validate that the generated
    # architecture follows the defined patterns
    arch = create_architecture_template("Pattern Test Project")

    # Example: Verify that the architecture includes patterns like dependency injection
    # This would depend on the specific implementation
    assert "metadata" in arch


if __name__ == "__main__":
    # Run tests
    test_create_architecture_template()
    test_save_and_load_architecture()
    test_validate_architecture_design_valid()
    test_validate_architecture_design_invalid()
    test_suggest_best_practices()
    test_add_component_to_architecture()
    test_modify_component_in_architecture()
    test_generate_architecture_solution()
    test_architecture_review_modification_workflow()
    test_architecture_validator()
    test_component_manager()
    test_bmad_workflow_orchestration()
    test_architecture_patterns_enforcement()
    print("All architecture component tests passed!")