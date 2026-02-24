import os
import tempfile
import unittest
from pathlib import Path
from src.dcae.code_structure_generator import CodeStructureGenerator, ProjectType, FrameworkType


class TestCodeStructureGenerator(unittest.TestCase):
    """Test cases for CodeStructureGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        # Don't initialize the generator here since each test does it with a specific project path

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_fastapi_structure(self):
        """Test generating FastAPI project structure."""
        project_path = os.path.join(self.temp_dir, "test_fastapi_project")

        # Initialize generator with project path
        generator = CodeStructureGenerator(project_path)

        # Mock architecture spec for FastAPI
        architecture_spec = {
            "project_type": "web_api",
            "framework": "FastAPI",
            "components": [
                {
                    "name": "user_service",
                    "type": "service",
                    "dependencies": []
                }
            ]
        }

        result = generator.generate_structure_from_architecture(architecture_spec)

        # Verify project was created
        self.assertTrue(os.path.exists(project_path))

        # Verify expected directories exist
        expected_dirs = [
            os.path.join(project_path, "src"),
            os.path.join(project_path, "tests"),
            os.path.join(project_path, "src", "models"),
            os.path.join(project_path, "src", "schemas"),
            os.path.join(project_path, "src", "routes"),
            os.path.join(project_path, "src", "services"),
            os.path.join(project_path, "src", "database"),
            os.path.join(project_path, "src", "config"),
        ]

        for dir_path in expected_dirs:
            with self.subTest(directory=dir_path):
                self.assertTrue(os.path.exists(dir_path))

    def test_generate_flask_structure(self):
        """Test generating Flask project structure."""
        project_path = os.path.join(self.temp_dir, "test_flask_project")

        # Initialize generator with project path
        generator = CodeStructureGenerator(project_path)

        # Mock architecture spec for Flask
        architecture_spec = {
            "project_type": "web_api",
            "framework": "Flask",
            "components": [
                {
                    "name": "auth_service",
                    "type": "service",
                    "dependencies": []
                }
            ]
        }

        result = generator.generate_structure_from_architecture(architecture_spec)

        # Verify project was created
        self.assertTrue(os.path.exists(project_path))

        # Verify expected directories exist for Flask
        expected_dirs = [
            os.path.join(project_path, "app"),
            os.path.join(project_path, "tests"),
            os.path.join(project_path, "app", "models"),
            os.path.join(project_path, "app", "views"),
            os.path.join(project_path, "app", "utils"),
            os.path.join(project_path, "app", "templates"),
            os.path.join(project_path, "app", "static"),
        ]

        for dir_path in expected_dirs:
            with self.subTest(directory=dir_path):
                self.assertTrue(os.path.exists(dir_path))

    def test_generate_django_structure(self):
        """Test generating Django project structure."""
        project_path = os.path.join(self.temp_dir, "test_django_project")

        # Initialize generator with project path
        generator = CodeStructureGenerator(project_path)

        # Mock architecture spec for Django
        architecture_spec = {
            "project_type": "web_application",
            "framework": "Django",
            "components": [
                {
                    "name": "blog_app",
                    "type": "django_app",
                    "dependencies": []
                }
            ]
        }

        result = generator.generate_structure_from_architecture(architecture_spec)

        # Verify project was created
        self.assertTrue(os.path.exists(project_path))

        # Verify expected directories exist for Django
        expected_dirs = [
            os.path.join(project_path, "blog_app"),
            os.path.join(project_path, "tests"),
            os.path.join(project_path, "blog_app", "models"),
            os.path.join(project_path, "blog_app", "views"),
            os.path.join(project_path, "blog_app", "migrations"),
        ]

        for dir_path in expected_dirs:
            with self.subTest(directory=dir_path):
                self.assertTrue(os.path.exists(dir_path))

    def test_create_requirements_txt(self):
        """Test creating requirements.txt file."""
        project_path = os.path.join(self.temp_dir, "test_requirements_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = CodeStructureGenerator(project_path)

        # Generate structure which will create config files including requirements
        architecture_spec = {
            "project_type": "web_api",
            "framework": "FastAPI",
            "components": []
        }

        generator.generate_structure_from_architecture(architecture_spec)

        # Check that the requirements files were created in the requirements directory
        requirements_path = os.path.join(project_path, "requirements", "base.txt")
        self.assertTrue(os.path.exists(requirements_path))

        with open(requirements_path, 'r') as f:
            content = f.read()
            self.assertIn("Base requirements", content)

        with open(requirements_path, 'r') as f:
            content = f.read()
            self.assertIn("fastapi", content.lower())
            self.assertIn("uvicorn", content.lower())

    def test_create_config_files(self):
        """Test creating configuration files."""
        project_path = os.path.join(self.temp_dir, "test_config_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = CodeStructureGenerator(project_path)

        # Generate structure which will create config files including requirements
        architecture_spec = {
            "project_type": "web_api",
            "framework": "Flask",
            "components": []
        }

        generator.generate_structure_from_architecture(architecture_spec)

        config_paths = [
            os.path.join(project_path, "requirements", "base.txt"),
            os.path.join(project_path, "pyproject.toml"),
            os.path.join(project_path, "README.md")
        ]

        for config_path in config_paths:
            with self.subTest(config_file=config_path):
                self.assertTrue(os.path.exists(config_path))


if __name__ == '__main__':
    unittest.main()