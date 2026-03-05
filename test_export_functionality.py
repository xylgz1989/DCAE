#!/usr/bin/env python3
"""
Test script for requirements export functionality.
This script tests the export and sharing functionality created for Story 2.5.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dcae.requirements import create_requirements_template, save_requirements
from dcae.requirements_export import RequirementsExporter, export_requirements, create_shareable_link


def test_export_functionality():
    """Test the export functionality of requirements."""
    print("Testing requirements export functionality...")

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create sample requirements
        requirements = create_requirements_template("Test Project")
        requirements["description"] = "This is a test project for export functionality"

        # Add some functional requirements
        requirements["functional_requirements"] = [
            {
                "id": "FR001",
                "description": "User can log in to the system",
                "priority": "high"
            },
            {
                "id": "FR002",
                "description": "User can view their dashboard",
                "priority": "medium"
            }
        ]

        # Add some non-functional requirements
        requirements["non_functional_requirements"] = [
            {
                "id": "NFR001",
                "category": "Performance",
                "description": "System should respond within 2 seconds",
                "priority": "high"
            }
        ]

        # Add some constraints
        requirements["constraints"] = [
            {
                "id": "C001",
                "description": "Must use Python 3.8 or higher"
            }
        ]

        # Add some assumptions
        requirements["assumptions"] = [
            {
                "id": "A001",
                "description": "Internet connection is available"
            }
        ]

        # Add some acceptance criteria
        requirements["acceptance_criteria"] = [
            {
                "id": "AC001",
                "description": "Login succeeds with valid credentials"
            }
        ]

        # Save the requirements to a temporary file
        requirements_path = temp_path / "test_requirements.yaml"
        save_requirements(requirements, requirements_path)
        print(f"[OK] Created test requirements at {requirements_path}")

        # Test TXT export
        txt_path = temp_path / "test_export.txt"
        success = export_requirements(requirements_path, txt_path, "txt")
        if success:
            print(f"[OK] Successfully exported to TXT: {txt_path}")
            assert txt_path.exists(), "TXT export file should exist"
        else:
            print("[ERROR] Failed to export to TXT")
            return False

        # Test CSV export
        csv_path = temp_path / "test_export.csv"
        success = export_requirements(requirements_path, csv_path, "csv")
        if success:
            print(f"[OK] Successfully exported to CSV: {csv_path}")
            assert csv_path.exists(), "CSV export file should exist"
        else:
            print("[ERROR] Failed to export to CSV")
            return False

        # Test JSON export
        json_path = temp_path / "test_export.json"
        success = export_requirements(requirements_path, json_path, "json")
        if success:
            print(f"[OK] Successfully exported to JSON: {json_path}")
            assert json_path.exists(), "JSON export file should exist"
        else:
            print("[ERROR] Failed to export to JSON")
            return False

        # Test YAML export
        yaml_path = temp_path / "test_export.yaml"
        success = export_requirements(requirements_path, yaml_path, "yaml")
        if success:
            print(f"[OK] Successfully exported to YAML: {yaml_path}")
            assert yaml_path.exists(), "YAML export file should exist"
        else:
            print("[ERROR] Failed to export to YAML")
            return False

        # Test creating a shareable link
        share_link = create_shareable_link(requirements_path, 24)
        if share_link:
            print(f"[OK] Successfully created shareable link: {share_link}")
        else:
            print("[ERROR] Failed to create shareable link")
            return False

    print("All export functionality tests passed!")
    return True


def test_requirements_exporter_class():
    """Test the RequirementsExporter class directly."""
    print("\nTesting RequirementsExporter class...")

    # Create sample requirements
    requirements = {
        "project_name": "Test Export Project",
        "description": "A test project to validate export functionality",
        "functional_requirements": [
            {
                "id": "FR001",
                "description": "The system shall allow user registration",
                "priority": "high"
            }
        ],
        "non_functional_requirements": [
            {
                "id": "NFR001",
                "category": "Security",
                "description": "All user passwords must be encrypted",
                "priority": "high"
            }
        ],
        "constraints": [
            {
                "id": "C001",
                "description": "System must be compatible with browsers from 2020 onwards"
            }
        ],
        "assumptions": [
            {
                "id": "A001",
                "description": "Users have basic computer literacy"
            }
        ],
        "acceptance_criteria": [
            {
                "id": "AC001",
                "description": "Registration form validates email format"
            }
        ],
        "metadata": {
            "created_date": "2026-03-02",
            "version": "1.0",
            "authors": ["Test Author"]
        }
    }

    # Create an exporter instance
    exporter = RequirementsExporter(requirements)

    # Test export to different formats using the exporter object
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test TXT export
        txt_path = temp_path / "direct_test.txt"
        success = exporter.export_to_txt(txt_path)
        if success and txt_path.exists():
            print(f"[OK] Direct TXT export successful: {txt_path}")
        else:
            print("[ERROR] Direct TXT export failed")
            return False

        # Test CSV export
        csv_path = temp_path / "direct_test.csv"
        success = exporter.export_to_csv(csv_path)
        if success and csv_path.exists():
            print(f"[OK] Direct CSV export successful: {csv_path}")
        else:
            print("[ERROR] Direct CSV export failed")
            return False

        # Test JSON export
        json_path = temp_path / "direct_test.json"
        success = exporter._export_to_json(json_path)
        if success and json_path.exists():
            print(f"[OK] Direct JSON export successful: {json_path}")
        else:
            print("[ERROR] Direct JSON export failed")
            return False

        # Test YAML export
        yaml_path = temp_path / "direct_test.yaml"
        success = exporter._export_to_yaml(yaml_path)
        if success and yaml_path.exists():
            print(f"[OK] Direct YAML export successful: {yaml_path}")
        else:
            print("[ERROR] Direct YAML export failed")
            return False

    print("All RequirementsExporter class tests passed!")
    return True


if __name__ == "__main__":
    print("Running requirements export functionality tests...\n")

    # Run tests
    success1 = test_export_functionality()
    success2 = test_requirements_exporter_class()

    if success1 and success2:
        print("\n[SUCCESS] All tests passed! Export functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n[ERROR] Some tests failed!")
        sys.exit(1)