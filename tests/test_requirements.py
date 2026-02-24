"""
Tests for the DCAE Requirements Management Module
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
import yaml
import json

from dcae.requirements import (
    create_requirements_template,
    load_requirements,
    save_requirements,
    validate_requirements,
    add_requirement,
    edit_requirement,
    input_requirements_interactively,
    print_requirements_summary
)


def test_create_requirements_template():
    """Test that create_requirements_template creates a proper template."""
    template = create_requirements_template("Test Project")

    assert template["project_name"] == "Test Project"
    assert template["description"] == ""
    assert isinstance(template["functional_requirements"], list)
    assert isinstance(template["non_functional_requirements"], list)
    assert isinstance(template["constraints"], list)
    assert isinstance(template["assumptions"], list)
    assert isinstance(template["acceptance_criteria"], list)
    assert template["metadata"]["version"] == "1.0"
    assert template["metadata"]["created_date"] != ""
    assert template["metadata"]["last_modified"] != ""


def test_save_and_load_requirements_yaml():
    """Test saving and loading requirements in YAML format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        requirements_path = project_path / "requirements.yaml"

        # Create test requirements
        test_reqs = create_requirements_template("Test Project")
        test_reqs["description"] = "Test description"
        test_reqs["functional_requirements"] = [{"id": "FR001", "description": "Test requirement", "priority": "high"}]

        # Save requirements
        success = save_requirements(test_reqs, requirements_path)
        assert success is True

        # Verify file exists
        assert requirements_path.exists()

        # Load requirements
        loaded_reqs = load_requirements(requirements_path)
        assert loaded_reqs is not None
        assert loaded_reqs["project_name"] == "Test Project"
        assert loaded_reqs["description"] == "Test description"
        assert len(loaded_reqs["functional_requirements"]) == 1
        assert loaded_reqs["functional_requirements"][0]["id"] == "FR001"


def test_save_and_load_requirements_json():
    """Test saving and loading requirements in JSON format."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        requirements_path = project_path / "requirements.json"

        # Create test requirements
        test_reqs = create_requirements_template("Test Project")
        test_reqs["description"] = "Test description"
        test_reqs["functional_requirements"] = [{"id": "FR001", "description": "Test requirement", "priority": "high"}]

        # Save requirements
        success = save_requirements(test_reqs, requirements_path)
        assert success is True

        # Verify file exists
        assert requirements_path.exists()

        # Load requirements
        loaded_reqs = load_requirements(requirements_path)
        assert loaded_reqs is not None
        assert loaded_reqs["project_name"] == "Test Project"
        assert loaded_reqs["description"] == "Test description"
        assert len(loaded_reqs["functional_requirements"]) == 1
        assert loaded_reqs["functional_requirements"][0]["id"] == "FR001"


def test_validate_requirements_valid():
    """Test validation of valid requirements."""
    valid_reqs = create_requirements_template("Test Project")
    valid_reqs["description"] = "A valid project description"
    valid_reqs["functional_requirements"] = [
        {"id": "FR001", "description": "Test requirement", "priority": "high"},
        "Another requirement as a string"
    ]

    errors = validate_requirements(valid_reqs)
    assert len(errors) == 0


def test_validate_requirements_invalid():
    """Test validation of invalid requirements."""
    invalid_reqs = create_requirements_template("")
    # Empty project name

    errors = validate_requirements(invalid_reqs)
    assert len(errors) > 0
    assert "Project name is required" in errors

    # Test with empty functional requirements
    invalid_reqs["project_name"] = "Test Project"
    invalid_reqs["description"] = "A"
    # Still has no functional requirements and short description

    errors = validate_requirements(invalid_reqs)
    # At this point, should have 2 errors: no functional requirements and short description
    assert len(errors) >= 2
    assert any("functional requirement" in error.lower() for error in errors)
    assert any("description should be more detailed" in error.lower() or "short" in error.lower() for error in errors)


def test_add_requirement():
    """Test adding requirements to the requirements document."""
    reqs = create_requirements_template("Test Project")
    reqs["description"] = "Test description"
    reqs["functional_requirements"] = []

    # Add functional requirement
    new_req = {"id": "FR001", "description": "New requirement", "priority": "medium"}
    success = add_requirement(reqs, "functional", new_req)
    assert success is True
    assert len(reqs["functional_requirements"]) == 1
    assert reqs["functional_requirements"][0]["id"] == "FR001"

    # Add non-functional requirement
    new_non_func_req = {"id": "NFR001", "category": "security", "description": "Security requirement", "priority": "high"}
    success = add_requirement(reqs, "non_functional", new_non_func_req)
    assert success is True
    assert len(reqs["non_functional_requirements"]) == 1
    assert reqs["non_functional_requirements"][0]["id"] == "NFR001"

    # Add constraint
    new_constraint = {"id": "C001", "description": "Time constraint"}
    success = add_requirement(reqs, "constraint", new_constraint)
    assert success is True
    assert len(reqs["constraints"]) == 1
    assert reqs["constraints"][0]["id"] == "C001"

    # Test invalid requirement type
    success = add_requirement(reqs, "invalid_type", {})
    assert success is False


def test_edit_requirement():
    """Test editing requirements in the requirements document."""
    reqs = create_requirements_template("Test Project")
    reqs["description"] = "Test description"
    reqs["functional_requirements"] = [
        {"id": "FR001", "description": "Original requirement", "priority": "medium"}
    ]

    # Edit the requirement
    updated_req = {"id": "FR001", "description": "Updated requirement", "priority": "high"}
    success = edit_requirement(reqs, "functional", 0, updated_req)
    assert success is True
    assert reqs["functional_requirements"][0]["description"] == "Updated requirement"
    assert reqs["functional_requirements"][0]["priority"] == "high"

    # Test editing with invalid index
    success = edit_requirement(reqs, "functional", 99, updated_req)
    assert success is False

    # Test invalid requirement type
    success = edit_requirement(reqs, "invalid_type", 0, updated_req)
    assert success is False


def test_print_requirements_summary(capsys):
    """Test printing requirements summary."""
    reqs = create_requirements_template("Test Project")
    reqs["description"] = "Test description"
    reqs["functional_requirements"] = [
        {"id": "FR001", "description": "Test functional requirement", "priority": "high"}
    ]
    reqs["non_functional_requirements"] = [
        {"id": "NFR001", "category": "performance", "description": "Test non-functional requirement", "priority": "medium"}
    ]

    # This test just verifies that the function runs without errors
    # The actual output check would require mocking the print function
    print_requirements_summary(reqs)

    # Capture output to verify it ran
    captured = capsys.readouterr()
    # Basic check that some output was produced
    assert "Project: Test Project" in captured.out


if __name__ == "__main__":
    # Run tests
    test_create_requirements_template()
    test_save_and_load_requirements_yaml()
    test_save_and_load_requirements_json()
    test_validate_requirements_valid()
    test_validate_requirements_invalid()
    test_add_requirement()
    test_edit_requirement()
    print("All tests passed!")