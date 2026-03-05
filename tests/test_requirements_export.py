"""
Unit tests for requirements export functionality.
These tests verify that the export functionality works as specified in Story 2.5.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
import tempfile
from dcae.requirements import create_requirements_template, save_requirements
from dcae.requirements_export import RequirementsExporter, export_requirements, create_shareable_link


class TestRequirementsExport(unittest.TestCase):
    """Test suite for requirements export functionality."""

    def setUp(self):
        """Set up test requirements data."""
        self.sample_requirements = create_requirements_template("Test Project")
        self.sample_requirements["description"] = "Test project for export functionality"

        # Add sample requirements of different types
        self.sample_requirements["functional_requirements"] = [
            {
                "id": "FR001",
                "description": "User can log in to the system",
                "priority": "high"
            },
            {
                "id": "FR002",
                "description": "User can view dashboard",
                "priority": "medium"
            }
        ]

        self.sample_requirements["non_functional_requirements"] = [
            {
                "id": "NFR001",
                "category": "Performance",
                "description": "System responds within 2 seconds",
                "priority": "high"
            }
        ]

        self.sample_requirements["constraints"] = [
            {
                "id": "C001",
                "description": "Must use Python 3.8 or higher"
            }
        ]

        self.sample_requirements["assumptions"] = [
            {
                "id": "A001",
                "description": "Internet connection available"
            }
        ]

        self.sample_requirements["acceptance_criteria"] = [
            {
                "id": "AC001",
                "description": "Login succeeds with valid credentials"
            }
        ]

    def test_requirements_exporter_initialization(self):
        """Test initializing RequirementsExporter with requirements data."""
        exporter = RequirementsExporter(self.sample_requirements)
        self.assertEqual(exporter.requirements, self.sample_requirements)

    def test_export_to_txt(self):
        """Test export to TXT format."""
        exporter = RequirementsExporter(self.sample_requirements)

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            success = exporter.export_to_txt(tmp_path)
            self.assertTrue(success)
            self.assertTrue(tmp_path.exists())

            # Check that the file contains expected content
            content = tmp_path.read_text(encoding='utf-8')
            self.assertIn("Test Project", content)
            self.assertIn("FR001", content)
            self.assertIn("User can log in", content)
            self.assertIn("NFR001", content)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_export_to_csv(self):
        """Test export to CSV format."""
        exporter = RequirementsExporter(self.sample_requirements)

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            success = exporter.export_to_csv(tmp_path)
            self.assertTrue(success)
            self.assertTrue(tmp_path.exists())

            # Check that the file contains expected content
            content = tmp_path.read_text(encoding='utf-8')
            self.assertIn("Type,ID,Description,Category,Priority,Extra Info", content)
            self.assertIn("Functional,FR001", content)
            self.assertIn("User can log in to the system", content)
            self.assertIn("Non-Functional,NFR001", content)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_export_to_json(self):
        """Test export to JSON format."""
        exporter = RequirementsExporter(self.sample_requirements)

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            success = exporter._export_to_json(tmp_path)
            self.assertTrue(success)
            self.assertTrue(tmp_path.exists())

            # Check that the file contains expected content
            content = tmp_path.read_text(encoding='utf-8')
            self.assertIn('"project_name": "Test Project"', content)
            self.assertIn("FR001", content)
            self.assertIn("User can log in to the system", content)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_export_to_yaml(self):
        """Test export to YAML format."""
        exporter = RequirementsExporter(self.sample_requirements)

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            success = exporter._export_to_yaml(tmp_path)
            self.assertTrue(success)
            self.assertTrue(tmp_path.exists())

            # Check that the file contains expected content
            content = tmp_path.read_text(encoding='utf-8')
            self.assertIn("project_name: Test Project", content)
            self.assertIn("FR001", content)
            self.assertIn("User can log in to the system", content)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_export_by_format(self):
        """Test export_by_format method with different formats."""
        exporter = RequirementsExporter(self.sample_requirements)

        formats_to_test = ['txt', 'csv', 'json', 'yaml']

        for fmt in formats_to_test:
            with tempfile.NamedTemporaryFile(suffix=f'.{fmt}', delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)

            try:
                success = exporter.export_by_format(tmp_path, fmt)
                self.assertTrue(success, f"Export to {fmt} should succeed")
                self.assertTrue(tmp_path.exists(), f"Export file for {fmt} should exist")
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

    def test_export_by_format_unsupported(self):
        """Test export_by_format with unsupported format."""
        exporter = RequirementsExporter(self.sample_requirements)

        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            success = exporter.export_by_format(tmp_path, 'xyz')
            self.assertFalse(success, "Export to unsupported format should fail")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_create_shareable_link(self):
        """Test creating a shareable link."""
        # First, save requirements to a file
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            success = save_requirements(self.sample_requirements, tmp_path)
            self.assertTrue(success)

            # Create shareable link
            link = create_shareable_link(tmp_path, expiration_hours=24)
            self.assertIsInstance(link, str)
            self.assertIn("dcae.example.com/share/", link)
            self.assertIn("_24h", link)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_convenience_export_function(self):
        """Test the convenience export_requirements function."""
        # First, save requirements to a file
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as req_file:
            req_path = Path(req_file.name)

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as out_file:
            out_path = Path(out_file.name)

        try:
            # Save requirements
            save_success = save_requirements(self.sample_requirements, req_path)
            self.assertTrue(save_success)

            # Export using convenience function
            export_success = export_requirements(req_path, out_path, 'txt')
            self.assertTrue(export_success)
            self.assertTrue(out_path.exists())

            # Check content
            content = out_path.read_text(encoding='utf-8')
            self.assertIn("Test Project", content)
            self.assertIn("FR001", content)
        finally:
            for path in [req_path, out_path]:
                if path.exists():
                    path.unlink()


if __name__ == '__main__':
    unittest.main()