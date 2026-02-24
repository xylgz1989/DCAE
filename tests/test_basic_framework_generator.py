import os
import tempfile
import unittest
from pathlib import Path
from src.dcae.basic_framework_generator import BasicFrameworkGenerator, FrameworkType


class TestBasicFrameworkGenerator(unittest.TestCase):
    """Test cases for BasicFrameworkGenerator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        # Don't initialize the generator here since each test does it with a specific project path

    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_fastapi_code(self):
        """Test generating FastAPI basic code."""
        project_path = os.path.join(self.temp_dir, "test_fastapi_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = BasicFrameworkGenerator(project_path)

        # Create architecture specification for FastAPI
        architecture_spec = {
            "framework": "FastAPI",
            "components": [
                {
                    "name": "user_service",
                    "type": "service",
                    "entities": [
                        {
                            "name": "User",
                            "attributes": [
                                {"name": "id", "type": "int", "required": True},
                                {"name": "email", "type": "str", "required": True},
                                {"name": "name", "type": "str", "required": False}
                            ]
                        }
                    ],
                    "endpoints": [
                        {
                            "path": "/users",
                            "method": "GET",
                            "handler": "get_users"
                        },
                        {
                            "path": "/users/{id}",
                            "method": "GET",
                            "handler": "get_user"
                        }
                    ]
                }
            ]
        }

        result = generator.generate_basic_framework_code(architecture_spec)

        # Verify the main app file was created
        app_path = os.path.join(project_path, "src", "main.py")
        self.assertTrue(os.path.exists(app_path))

        # Verify content contains FastAPI imports
        with open(app_path, 'r') as f:
            content = f.read()
            self.assertIn("from fastapi import FastAPI", content)
            self.assertIn("app = FastAPI()", content)

        # Verify models file was created
        models_path = os.path.join(project_path, "src", "models", "__init__.py")
        self.assertTrue(os.path.exists(models_path))

        # Verify routes file was created
        routes_path = os.path.join(project_path, "src", "routes", "__init__.py")
        self.assertTrue(os.path.exists(routes_path))

    def test_generate_flask_code(self):
        """Test generating Flask basic code."""
        project_path = os.path.join(self.temp_dir, "test_flask_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = BasicFrameworkGenerator(project_path)

        # Create architecture specification for Flask
        architecture_spec = {
            "framework": "Flask",
            "components": [
                {
                    "name": "auth_service",
                    "type": "service",
                    "entities": [
                        {
                            "name": "User",
                            "attributes": [
                                {"name": "id", "type": "int", "required": True},
                                {"name": "username", "type": "str", "required": True}
                            ]
                        }
                    ]
                }
            ]
        }

        result = generator.generate_basic_framework_code(architecture_spec)

        # Verify the main app file was created
        app_path = os.path.join(project_path, "app", "app.py")
        self.assertTrue(os.path.exists(app_path))

        # Verify content contains Flask imports
        with open(app_path, 'r') as f:
            content = f.read()
            self.assertIn("from flask import Flask", content)
            self.assertIn("app = Flask(__name__)", content)

        # Verify models directory and file were created
        models_path = os.path.join(project_path, "app", "models")
        self.assertTrue(os.path.exists(models_path))

    def test_generate_django_code(self):
        """Test generating Django basic code."""
        project_path = os.path.join(self.temp_dir, "test_django_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = BasicFrameworkGenerator(project_path)

        # Create architecture specification for Django
        architecture_spec = {
            "framework": "Django",
            "components": [
                {
                    "name": "blog_app",
                    "type": "django_app",
                    "entities": [
                        {
                            "name": "Post",
                            "attributes": [
                                {"name": "title", "type": "str", "required": True},
                                {"name": "content", "type": "str", "required": True}
                            ]
                        }
                    ]
                }
            ]
        }

        result = generator.generate_basic_framework_code(architecture_spec)

        # Verify Django app directory was created
        app_path = os.path.join(project_path, "blog_app")
        self.assertTrue(os.path.exists(app_path))

        # Verify models.py was created in the app
        models_path = os.path.join(app_path, "models.py")
        self.assertTrue(os.path.exists(models_path))

        # Verify views.py was created in the app
        views_path = os.path.join(app_path, "views.py")
        self.assertTrue(os.path.exists(views_path))

        # Verify apps.py was created in the app
        apps_path = os.path.join(app_path, "apps.py")
        self.assertTrue(os.path.exists(apps_path))

    def test_get_template_by_framework_fastapi(self):
        """Test getting FastAPI template."""
        project_path = os.path.join(self.temp_dir, "test_template_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = BasicFrameworkGenerator(project_path)

        template = generator._get_template_by_framework(FrameworkType.FASTAPI)

        # Verify it returns a non-empty template
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
        self.assertIn("FastAPI", template)

    def test_get_template_by_framework_flask(self):
        """Test getting Flask template."""
        project_path = os.path.join(self.temp_dir, "test_template_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = BasicFrameworkGenerator(project_path)

        template = generator._get_template_by_framework(FrameworkType.FLASK)

        # Verify it returns a non-empty template
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
        self.assertIn("Flask", template)

    def test_get_template_by_framework_django(self):
        """Test getting Django template."""
        project_path = os.path.join(self.temp_dir, "test_template_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = BasicFrameworkGenerator(project_path)

        template = generator._get_template_by_framework(FrameworkType.DJANGO)

        # Verify it returns a non-empty template
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
        self.assertIn("Django", template)

    def test_get_template_by_framework_invalid(self):
        """Test getting template for invalid framework."""
        project_path = os.path.join(self.temp_dir, "test_template_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize generator with project path
        generator = BasicFrameworkGenerator(project_path)

        with self.assertRaises(ValueError):
            generator._get_template_by_framework("InvalidFramework")


if __name__ == '__main__':
    unittest.main()