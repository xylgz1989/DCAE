"""
Tests for the DCAE Project Initialization Module
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from dcae.init import initialize_dcae_project, PROJECT_STRUCTURE


def test_initialize_dcae_project_creates_structure():
    """Test that initialize_dcae_project creates the expected directory structure."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"

        # Run initialization
        success = initialize_dcae_project(str(project_path))

        # Verify success
        assert success is True

        # Verify directory structure was created
        for dirname in PROJECT_STRUCTURE["directories"]:
            dir_path = project_path / dirname
            assert dir_path.exists()
            assert dir_path.is_dir()


def test_initialize_dcae_project_creates_files():
    """Test that initialize_dcae_project creates the expected files."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"

        # Run initialization
        success = initialize_dcae_project(str(project_path))

        # Verify success
        assert success is True

        # Verify files were created
        for filepath in PROJECT_STRUCTURE["files"].keys():
            file_path = project_path / filepath
            assert file_path.exists()
            assert file_path.is_file()


def test_initialize_fails_if_directory_not_empty():
    """Test that initialize_dcae_project fails if directory is not empty."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"

        # Create a dummy file to make directory non-empty
        dummy_file = project_path / "dummy.txt"
        dummy_file.parent.mkdir(parents=True, exist_ok=True)
        dummy_file.write_text("dummy content")

        # Attempt initialization should fail
        success = initialize_dcae_project(str(project_path))

        # Verify failure
        assert success is False


def test_initialize_creates_config_with_project_name():
    """Test that the config file contains the project name."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "my_test_project"

        # Run initialization
        success = initialize_dcae_project(str(project_path))

        # Verify success
        assert success is True

        # Check that config contains the project name
        config_path = project_path / ".dcae" / "config.yaml"
        assert config_path.exists()

        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        assert config["project"]["name"] == "my_test_project"


if __name__ == "__main__":
    # Run tests
    test_initialize_dcae_project_creates_structure()
    test_initialize_dcae_project_creates_files()
    test_initialize_fails_if_directory_not_empty()
    test_initialize_creates_config_with_project_name()
    print("All tests passed!")