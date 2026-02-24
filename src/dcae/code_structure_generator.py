"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Code Structure Generator Module

This module implements the code structure generation functionality as specified in
Epic #4: Code Generation & Development, specifically Story 4.1: Generate Code Structure.

As a developer,
I want to generate an appropriate code structure based on the architecture and requirements,
so that I have a solid foundation to build upon for the implementation of the project.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import jinja2
from datetime import datetime


class ProjectType(Enum):
    """Enumeration for different project types."""
    MONOLITHIC = "monolithic"
    MICROSERVICES = "microservices"
    LAYERED = "layered"
    CLIENT_SERVER = "client-server"


class FrameworkType(Enum):
    """Enumeration for different framework types."""
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    NODE_EXPRESS = "node-express"
    SPRING_BOOT = "spring-boot"
    GO_ECHO = "go-echo"
    GENERIC = "generic"


class CodeStructureGenerator:
    """Main class for generating code structure based on architecture decisions."""

    def __init__(self, project_path: str):
        """
        Initialize the structure generator.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.templates_path = Path(__file__).parent / "templates"
        self.loader = jinja2.FileSystemLoader(searchpath=str(self.templates_path))
        self.env = jinja2.Environment(loader=self.loader)

    def generate_structure_from_architecture(self, architecture_spec: Dict[str, Any]) -> bool:
        """
        Generate code structure based on architecture specification.

        Args:
            architecture_spec: Architecture specification from Epic #3

        Returns:
            True if successful, False otherwise
        """
        print(f"Generating code structure for project at: {self.project_path}")

        # Determine project type from architecture
        project_type = self._determine_project_type(architecture_spec)
        framework_type = self._determine_framework_type(architecture_spec)

        print(f"Detected project type: {project_type.value}")
        print(f"Detected framework: {framework_type.value}")

        # Create project structure based on type
        self._create_project_directories(project_type, framework_type)
        self._create_standard_files(project_type, framework_type)
        self._create_framework_specific_files(project_type, framework_type)
        self._create_readme(architecture_spec)
        self._create_config_files(framework_type)

        print(f"[X] Code structure generated successfully at: {self.project_path}")
        return True

    def _determine_project_type(self, architecture_spec: Dict[str, Any]) -> ProjectType:
        """
        Determine project type from architecture specification.

        Args:
            architecture_spec: Architecture specification from Epic #3

        Returns:
            Detected project type
        """
        # Check architecture style
        arch_style = architecture_spec.get("architecture_style", "").lower()
        if "microservice" in arch_style:
            return ProjectType.MICROSERVICES
        elif "layer" in arch_style:
            return ProjectType.LAYERED
        elif "client" in arch_style or "server" in arch_style:
            return ProjectType.CLIENT_SERVER
        else:
            # Default to monolithic if not specified
            return ProjectType.MONOLITHIC

    def _determine_framework_type(self, architecture_spec: Dict[str, Any]) -> FrameworkType:
        """
        Determine framework type from architecture specification.

        Args:
            architecture_spec: Architecture specification from Epic #3

        Returns:
            Detected framework type
        """
        # Check technology stack
        tech_stack = architecture_spec.get("technology_stack", {})
        language = tech_stack.get("language", "").lower()
        framework = tech_stack.get("framework", "").lower()

        # Determine based on language and framework
        if language == "python":
            if "fastapi" in framework:
                return FrameworkType.FASTAPI
            elif "flask" in framework:
                return FrameworkType.FLASK
            elif "django" in framework:
                return FrameworkType.DJANGO
        elif language == "javascript" or language == "node":
            if "express" in framework:
                return FrameworkType.NODE_EXPRESS
        elif language == "java":
            if "spring" in framework:
                return FrameworkType.SPRING_BOOT
        elif language == "go":
            if "echo" in framework:
                return FrameworkType.GO_ECHO

        # Default to generic if not specified
        return FrameworkType.GENERIC

    def _create_project_directories(self, project_type: ProjectType, framework_type: FrameworkType):
        """Create the main project directory structure."""
        directories = self._get_directory_structure(project_type, framework_type)

        for directory in directories:
            full_path = self.project_path / directory
            full_path.mkdir(parents=True, exist_ok=True)

        print(f"  [X] Created {len(directories)} directories")

    def _get_directory_structure(self, project_type: ProjectType, framework_type: FrameworkType) -> List[str]:
        """Get directory structure based on project and framework type."""
        base_dirs = [
            "src",
            "tests",
            "docs",
            "configs",
            "scripts",
            "requirements"
        ]

        if framework_type == FrameworkType.DJANGO:
            # Django specific structure
            return base_dirs + [
                "src/apps",
                "src/templates",
                "src/static",
                "src/media"
            ]
        elif framework_type == FrameworkType.FASTAPI or framework_type == FrameworkType.FLASK:
            # FastAPI/Flask specific structure
            return base_dirs + [
                "src/api",
                "src/core",
                "src/models",
                "src/services",
                "src/utils",
                "tests/test_api",
                "tests/test_models",
                "tests/test_services"
            ]
        elif project_type == ProjectType.MICROSERVICES:
            # Microservices structure with individual services
            return base_dirs + [
                "services/service1",
                "services/service2",
                "shared",
                "docker",
                "kubernetes"
            ]
        else:
            # Generic structure
            return base_dirs + [
                "src/modules",
                "src/common",
                "tests/unit",
                "tests/integration"
            ]

    def _create_standard_files(self, project_type: ProjectType, framework_type: FrameworkType):
        """Create standard project files."""
        # Create main application file
        main_file = self.project_path / "src" / "main.py"
        main_content = self._get_main_file_content(framework_type)
        self._write_file(main_file, main_content)

        # Create __init__.py files
        init_files = [
            self.project_path / "src" / "__init__.py",
            self.project_path / "tests" / "__init__.py",
            self.project_path / "src" / "utils" / "__init__.py"
        ]

        for init_file in init_files:
            if not init_file.exists():
                self._write_file(init_file, "")

        # Create .gitignore
        gitignore_content = self._get_gitignore_content(framework_type)
        self._write_file(self.project_path / ".gitignore", gitignore_content)

        print(f"  [X] Created standard files")

    def _get_main_file_content(self, framework_type: FrameworkType) -> str:
        """Get main file content based on framework type."""
        if framework_type == FrameworkType.FASTAPI:
            return '''"""
Main application entry point for FastAPI project
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="DCAE Generated API",
    description="API generated by DCAE framework",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the DCAE generated API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        elif framework_type == FrameworkType.FLASK:
            return '''"""
Main application entry point for Flask project
"""
from flask import Flask, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    @app.route('/')
    def home():
        """Root endpoint."""
        return jsonify({"message": "Welcome to the DCAE generated API!"})

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy"})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
'''
        elif framework_type == FrameworkType.DJANGO:
            return '''"""
Django settings and configuration
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Add your apps here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'''
        else:
            return '''"""
Main application entry point
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger.info("Application starting...")
    print("Welcome to the DCAE generated application!")
    logger.info("Application started successfully")

if __name__ == "__main__":
    main()
'''

    def _get_gitignore_content(self, framework_type: FrameworkType) -> str:
        """Get .gitignore content based on framework type."""
        base_ignore = '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/
'''

        if framework_type == FrameworkType.DJANGO:
            django_specific = '''
# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/
.env
'''
            return base_ignore + django_specific

        return base_ignore

    def _create_framework_specific_files(self, project_type: ProjectType, framework_type: FrameworkType):
        """Create files specific to the chosen framework."""
        if framework_type in [FrameworkType.FASTAPI, FrameworkType.FLASK]:
            self._create_api_structure(framework_type)

        if framework_type == FrameworkType.DJANGO:
            self._create_django_structure()

        print(f"  [X] Created framework-specific files")

    def _create_api_structure(self, framework_type: FrameworkType):
        """Create API-specific structure for FastAPI/Flask."""
        # Create API modules
        api_path = self.project_path / "src" / "api"

        # Create v1 subdirectory
        v1_path = api_path / "v1"
        v1_path.mkdir(exist_ok=True)

        # Create endpoints subdirectory
        endpoints_path = v1_path / "endpoints"
        endpoints_path.mkdir(exist_ok=True)

        # Create basic API endpoint
        if framework_type == FrameworkType.FASTAPI:
            endpoint_content = '''"""
API endpoints for v1
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["v1"])

# Example model
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

# Example in-memory storage (replace with database)
items = [
    Item(id=1, name="Item 1", description="First item"),
    Item(id=2, name="Item 2", description="Second item")
]

@router.get("/items/", response_model=List[Item])
async def get_items(skip: int = 0, limit: int = 20):
    """Get a list of items."""
    return items[skip:skip+limit]

@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get a specific item by ID."""
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/items/", response_model=Item)
async def create_item(item: Item):
    """Create a new item."""
    items.append(item)
    return item
'''
        else:  # Flask
            endpoint_content = '''"""
API endpoints for v1
"""
from flask import Blueprint, jsonify, request
from typing import List, Optional

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Example in-memory storage (replace with database)
items = [
    {"id": 1, "name": "Item 1", "description": "First item"},
    {"id": 2, "name": "Item 2", "description": "Second item"}
]

@api_bp.route('/items/', methods=['GET'])
def get_items():
    """Get a list of items."""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))
    result = items[skip:skip+limit]
    return jsonify(result)

@api_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific item by ID."""
    for item in items:
        if item['id'] == item_id:
            return jsonify(item)
    return jsonify({'error': 'Item not found'}), 404

@api_bp.route('/items/', methods=['POST'])
def create_item():
    """Create a new item."""
    data = request.get_json()
    new_item = {
        'id': len(items) + 1,
        'name': data.get('name'),
        'description': data.get('description')
    }
    items.append(new_item)
    return jsonify(new_item), 201
'''

        endpoint_file = endpoints_path / f"{'items' if framework_type == FrameworkType.FASTAPI else 'items'}_endpoint.py"
        self._write_file(endpoint_file, endpoint_content)

        # Create core structure
        core_path = self.project_path / "src" / "core"

        # Create config module
        config_content = '''"""
Application configuration module
"""
import os
from typing import Optional

class Config:
    """Base configuration class."""

    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DATABASE_URL: str = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    DEBUG: bool = os.environ.get('FLASK_DEBUG', '').lower() == 'true'
    TESTING: bool = False

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DCAE Generated API"

    # Security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS settings
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
    ]

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = "sqlite:///test.db"

def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.environ.get('ENVIRONMENT', 'development').lower()

    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
'''
        config_file = core_path / "config.py"
        self._write_file(config_file, config_content)

        # Create security module
        security_content = '''"""
Security utilities and middleware
"""
import secrets
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, os.environ.get('SECRET_KEY'), algorithm="HS256")
    return encoded_jwt
'''
        security_file = core_path / "security.py"
        self._write_file(security_file, security_content)

    def _create_django_structure(self):
        """Create Django-specific structure."""
        # Create urls.py
        urls_content = '''"""
URL configuration for the project
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add your app URLs here
    # path('myapp/', include('myapp.urls')),
]
'''
        urls_file = self.project_path / "src" / "urls.py"
        self._write_file(urls_file, urls_content)

        # Create wsgi.py
        wsgi_content = '''"""
WSGI config for the project
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
application = get_wsgi_application()
'''
        wsgi_file = self.project_path / "src" / "wsgi.py"
        self._write_file(wsgi_file, wsgi_content)

    def _create_readme(self, architecture_spec: Dict[str, Any]):
        """Create a comprehensive README file."""
        project_name = architecture_spec.get("project_name", "DCAE Generated Project")
        description = architecture_spec.get("description", "A project generated by DCAE framework")

        readme_content = f'''# {project_name}

{description}

## Project Structure

This project was generated by the DCAE (Disciplined Consensus-Driven Agentic Engineering) framework based on the architecture decisions made during the design phase.

### Directory Structure

- `src/` - Main source code
- `tests/` - Unit and integration tests
- `docs/` - Project documentation
- `configs/` - Configuration files for different environments
- `scripts/` - Utility and deployment scripts
- `requirements/` - Dependency files

### Architecture

Based on the architectural decisions:
- Project Type: {architecture_spec.get("architecture_style", "Monolithic")}
- Technology Stack: {architecture_spec.get("technology_stack", {}).get("language", "Python")} with {architecture_spec.get("technology_stack", {}).get("framework", "Generic Framework")}
- Components: {", ".join([comp.get("name", "Unnamed Component") for comp in architecture_spec.get("components", [])][:3])}

## Getting Started

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   # On Windows
   venv\\Scripts\\activate

   # On macOS/Linux
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements/base.txt
   ```

### Running the Application

```bash
# For API projects
python src/main.py

# For Django projects
python manage.py runserver
```

## Development

### Project Guidelines

- Follow the coding standards defined in the architecture documentation
- Write unit tests for all new functionality
- Use type hints where appropriate
- Follow the architectural patterns established in the design phase

### Testing

Run the test suite with:
```bash
python -m pytest tests/
```

## Contributing

Please read the architecture and requirements documentation before making changes to ensure alignment with the system design.

## License

This project is licensed under the terms defined in the LICENSE file.
'''
        readme_file = self.project_path / "README.md"
        self._write_file(readme_file, readme_content)

    def _create_config_files(self, framework_type: FrameworkType):
        """Create configuration files."""
        # Create requirements files
        base_reqs = '''# Base requirements
-r requirements/base.txt
'''
        base_req_file = self.project_path / "requirements" / "base.txt"
        self._write_file(base_req_file, base_reqs)

        dev_reqs = '''# Development requirements
-r requirements/base.txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
pre-commit>=2.20.0
'''
        dev_req_file = self.project_path / "requirements" / "dev.txt"
        self._write_file(dev_req_file, dev_reqs)

        prod_reqs = '''# Production requirements
-r requirements/base.txt
gunicorn>=20.1.0
'''+ ('''uvicorn[standard]>=0.18.0
''' if framework_type in [FrameworkType.FASTAPI, FrameworkType.FLASK] else '') + '''
'''
        prod_req_file = self.project_path / "requirements" / "prod.txt"
        self._write_file(prod_req_file, prod_reqs)

        # Create pyproject.toml
        pyproject_content = '''[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "dcae-generated-project"
dynamic = ["version"]
description = "A project generated by DCAE framework"
readme = "README.md"
authors = [{name = "DCAE Framework", email = "dcae@example.com"}]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    # Add your dependencies here
]

[project.optional-dependencies]
dev = [
    # Development dependencies are in requirements/dev.txt
]

[tool.setuptools_scm]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''
        pyproject_file = self.project_path / "pyproject.toml"
        self._write_file(pyproject_file, pyproject_content)

    def _write_file(self, file_path: Path, content: str):
        """Write content to a file, creating parent directories if needed."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)


def generate_code_structure_from_architecture(architecture_spec: Dict[str, Any],
                                             project_path: str = "./generated-project") -> bool:
    """
    Convenience function to generate code structure from architecture specification.

    Args:
        architecture_spec: Architecture specification from Epic #3
        project_path: Path where to generate the project

    Returns:
        True if successful, False otherwise
    """
    generator = CodeStructureGenerator(project_path)
    return generator.generate_structure_from_architecture(architecture_spec)


# Example usage and test function
def create_sample_architecture_spec() -> Dict[str, Any]:
    """Create a sample architecture specification for testing."""
    return {
        "project_name": "Sample API Project",
        "description": "A sample API project generated by DCAE framework",
        "architecture_style": "Layered Architecture",
        "technology_stack": {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql",
            "message_queue": "redis"
        },
        "components": [
            {
                "name": "API Layer",
                "responsibilities": ["Handle HTTP requests", "Validate input", "Return responses"]
            },
            {
                "name": "Business Logic Layer",
                "responsibilities": ["Process business rules", "Coordinate operations"]
            },
            {
                "name": "Data Access Layer",
                "responsibilities": ["Database operations", "Data validation"]
            }
        ],
        "integration_points": [
            {"name": "Database Connection", "type": "PostgreSQL"},
            {"name": "Message Queue", "type": "Redis"},
            {"name": "Authentication Service", "type": "OAuth2"}
        ]
    }


if __name__ == "__main__":
    # Example usage
    import tempfile

    # Create a sample architecture specification
    sample_arch = create_sample_architecture_spec()

    # Generate structure in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "sample-project"
        print(f"Generating sample project at: {project_path}")

        success = generate_code_structure_from_architecture(sample_arch, str(project_path))

        if success:
            print(f"[X] Sample project generated successfully!")
            print(f"Contents of project root: {list(project_path.iterdir())}")
        else:
            print("✗ Failed to generate project")