"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Basic Framework Code Generator Module

This module implements the basic framework code generation functionality as specified in
Epic #4: Code Generation & Development, specifically Story 4.2: Generate Basic Framework Code.

As a developer,
I want to generate basic framework code based on the architecture and project structure,
so that I have foundational components to build upon for the implementation of the project.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import ast
import importlib.util

from .code_structure_generator import FrameworkType, ProjectType


class BasicFrameworkGenerator:
    """Main class for generating basic framework code."""

    def __init__(self, project_path: str):
        """
        Initialize the framework generator.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.framework_type = self._detect_framework_type()

    def _detect_framework_type(self) -> FrameworkType:
        """Detect the framework type based on project structure."""
        # Look for indicators of different frameworks
        if (self.project_path / "src" / "main.py").exists():
            main_content = (self.project_path / "src" / "main.py").read_text(encoding='utf-8')

            if "fastapi" in main_content.lower():
                return FrameworkType.FASTAPI
            elif "flask" in main_content.lower():
                return FrameworkType.FLASK
            elif "django" in main_content.lower():
                return FrameworkType.DJANGO

        # Default to generic if we can't determine
        return FrameworkType.GENERIC

    def generate_basic_framework_code(self, architecture_spec: Dict[str, Any]) -> bool:
        """
        Generate basic framework code based on architecture specification.

        Args:
            architecture_spec: Architecture specification from Epic #3

        Returns:
            True if successful, False otherwise
        """
        print(f"Generating basic framework code for {self.framework_type.value} project at: {self.project_path}")

        # Generate based on framework type
        if self.framework_type == FrameworkType.FASTAPI:
            self._generate_fastapi_framework_code(architecture_spec)
        elif self.framework_type == FrameworkType.FLASK:
            self._generate_flask_framework_code(architecture_spec)
        elif self.framework_type == FrameworkType.DJANGO:
            self._generate_django_framework_code(architecture_spec)
        else:
            self._generate_generic_framework_code(architecture_spec)

        print(f"[X] Basic framework code generated successfully at: {self.project_path}")
        return True

    def _generate_fastapi_framework_code(self, architecture_spec: Dict[str, Any]):
        """Generate FastAPI-specific basic framework code."""
        # Create models based on architecture components
        self._create_fastapi_models(architecture_spec)

        # Create services based on business logic components
        self._create_fastapi_services(architecture_spec)

        # Create API endpoints based on defined interfaces
        self._create_fastapi_endpoints(architecture_spec)

        # Create database integration if specified
        self._create_database_integration(architecture_spec)

        # Create dependency injection components
        self._create_fastapi_dependencies(architecture_spec)

    def _create_fastapi_models(self, architecture_spec: Dict[str, Any]):
        """Create Pydantic models based on architecture components."""
        models_path = self.project_path / "src" / "models"

        # Create base model
        base_model_content = '''"""
Pydantic base models for the application
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class BaseSchema(BaseModel):
    """Base schema with common fields."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
'''
        base_model_file = models_path / "base.py"
        self._write_file(base_model_file, base_model_content)

        # Create schema models based on architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").lower()
            responsibilities = component.get("responsibilities", [])

            if "data" in name.lower() or "model" in name.lower() or "entity" in name.lower():
                # Create specific model for this component
                model_content = f'''"""
{name.capitalize()} models
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from .base import BaseSchema


class {name.capitalize()}Create(BaseModel):
    """Schema for creating {name} objects."""
'''
                # Add fields based on responsibilities
                for idx, resp in enumerate(responsibilities[:5]):  # Limit to first 5 responsibilities
                    field_name = f"field_{idx+1}"
                    model_content += f'    {field_name}: str = Field(..., description="{resp}")\n'

                model_content += f'''

class {name.capitalize()}Update(BaseModel):
    """Schema for updating {name} objects."""
'''
                # Add optional fields for updates
                for idx, resp in enumerate(responsibilities[:5]):
                    field_name = f"field_{idx+1}"
                    model_content += f'    {field_name}: Optional[str] = Field(None, description="{resp}")\n'

                model_content += f'''

class {name.capitalize()}Response(BaseSchema):
    """Schema for {name} response objects."""
'''
                # Add fields for responses
                for idx, resp in enumerate(responsibilities[:5]):
                    field_name = f"field_{idx+1}"
                    model_content += f'    {field_name}: str = Field(..., description="{resp}")\n'

                model_file = models_path / f"{name}_schema.py"
                self._write_file(model_file, model_content)

    def _create_fastapi_services(self, architecture_spec: Dict[str, Any]):
        """Create service layer based on architecture components."""
        services_path = self.project_path / "src" / "services"

        # Create base service
        base_service_content = '''"""
Base service class for the application
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class BaseService(ABC, Generic[T]):
    """Base service class with common operations."""

    @abstractmethod
    async def create(self, obj: T) -> T:
        """Create a new object."""
        pass

    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """Get an object by ID."""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List objects with pagination."""
        pass

    @abstractmethod
    async def update(self, id: str, obj: T) -> Optional[T]:
        """Update an object."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an object."""
        pass
'''
        base_service_file = services_path / "base.py"
        self._write_file(base_service_file, base_service_content)

        # Create specific services based on architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").lower()
            responsibilities = component.get("responsibilities", [])

            if "business" in name.lower() or "service" in name.lower() or "logic" in name.lower():
                service_content = f'''"""
{name.capitalize()} service
"""
from typing import Optional, List
from .base import BaseService, T
from ..models.{name}_schema import {name.capitalize()}Create, {name.capitalize()}Update, {name.capitalize()}Response


class {name.capitalize()}Service(BaseService[{name.capitalize()}Response]):
    """Service for {name} operations."""

    async def create(self, obj: {name.capitalize()}Create) -> {name.capitalize()}Response:
        """Create a new {name}."""
        # Implementation for creating {name}
        # This would typically interact with a repository/database
        response_data = obj.dict()
        response_data['id'] = 'some-generated-id'  # In practice, this would come from DB
        return {name.capitalize()}Response(**response_data)

    async def get(self, id: str) -> Optional[{name.capitalize()}Response]:
        """Get a {name} by ID."""
        # Implementation for retrieving {name}
        # This would typically fetch from DB
        # For now, returning None as example
        return None

    async def list(self, skip: int = 0, limit: int = 100) -> List[{name.capitalize()}Response]:
        """List {name}s with pagination."""
        # Implementation for listing {name}s
        # This would typically query DB
        # For now, returning empty list as example
        return []

    async def update(self, id: str, obj: {name.capitalize()}Update) -> Optional[{name.capitalize()}Response]:
        """Update a {name}."""
        # Implementation for updating {name}
        # This would typically update DB record
        # For now, returning None as example
        return None

    async def delete(self, id: str) -> bool:
        """Delete a {name}."""
        # Implementation for deleting {name}
        # This would typically delete from DB
        # For now, returning True as example
        return True
'''
                service_file = services_path / f"{name}_service.py"
                self._write_file(service_file, service_content)

    def _create_fastapi_endpoints(self, architecture_spec: Dict[str, Any]):
        """Create API endpoints based on architecture interfaces."""
        endpoints_path = self.project_path / "src" / "api" / "v1" / "endpoints"

        # Create specific endpoint files based on components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").lower()

            # Only create endpoints for components that seem to be API-related
            if any(keyword in name.lower() for keyword in ["api", "endpoint", "service", "interface"]):
                endpoint_content = f'''"""
{name.capitalize()} API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel

from ...services.{name}_service import {name.capitalize()}Service
from ...models.{name}_schema import {name.capitalize()}Create, {name.capitalize()}Update, {name.capitalize()}Response
from ...core.security import get_current_user  # Assuming security module exists
from ...core.config import settings  # Assuming config module exists


router = APIRouter(prefix="/{name}", tags=["{name}"])


@router.get("/", response_model=List[{name.capitalize()}Response])
async def get_{name}s(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get a list of {name}s."""
    service = {name.capitalize()}Service()
    return await service.list(skip=skip, limit=limit)


@router.get("/{{item_id}}", response_model={name.capitalize()}Response)
async def get_{name}(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific {name} by ID."""
    service = {name.capitalize()}Service()
    result = await service.get(item_id)
    if not result:
        raise HTTPException(status_code=404, detail="{name.capitalize()} not found")
    return result


@router.post("/", response_model={name.capitalize()}Response)
async def create_{name}(
    item: {name.capitalize()}Create,
    current_user: dict = Depends(get_current_user)
):
    """Create a new {name}."""
    service = {name.capitalize()}Service()
    return await service.create(item)


@router.put("/{{item_id}}", response_model={name.capitalize()}Response)
async def update_{name}(
    item_id: str,
    item: {name.capitalize()}Update,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing {name}."""
    service = {name.capitalize()}Service()
    result = await service.update(item_id, item)
    if not result:
        raise HTTPException(status_code=404, detail="{name.capitalize()} not found")
    return result


@router.delete("/{{item_id}}", response_model=bool)
async def delete_{name}(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a {name}."""
    service = {name.capitalize()}Service()
    success = await service.delete(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="{name.capitalize()} not found")
    return success
'''
                endpoint_file = endpoints_path / f"{name}_endpoint.py"
                self._write_file(endpoint_file, endpoint_content)

    def _create_database_integration(self, architecture_spec: Dict[str, Any]):
        """Create database integration based on architecture specifications."""
        db_type = architecture_spec.get("technology_stack", {}).get("database", "sqlite").lower()

        # Create database module
        db_path = self.project_path / "src" / "database"
        db_path.mkdir(exist_ok=True)

        # Create database configuration
        db_config_content = f'''"""
Database configuration and setup
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

# Database URL - can be overridden by environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dcae_app.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={{'check_same_thread': False}} if DATABASE_URL.startswith("sqlite:") else {{}}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        db_config_file = db_path / "config.py"
        self._write_file(db_config_file, db_config_content)

        # Create base database model
        db_base_content = '''"""
Base database model
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from .config import Base
import uuid


class BaseDBModel(Base):
    """Base model with common columns."""
    __abstract__ = True

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
'''
        db_base_file = db_path / "base.py"
        self._write_file(db_base_file, db_base_content)

    def _create_fastapi_dependencies(self, architecture_spec: Dict[str, Any]):
        """Create dependency injection components."""
        deps_path = self.project_path / "src" / "api" / "dependencies"
        deps_path.mkdir(exist_ok=True)

        # Create common dependencies
        deps_content = '''"""
Common API dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
import os

from ..core.config import get_config
from ..database.config import get_db, SessionLocal
from ..core.security import verify_token


# Initialize security scheme
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from token."""
    config = get_config()

    try:
        payload = jwt.decode(
            credentials.credentials,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={{"WWW-Authenticate": "Bearer"}},
            )
        return {"username": username}
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={{"WWW-Authenticate": "Bearer"}},
        )


def get_db_session():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        deps_file = deps_path / "__init__.py"
        self._write_file(deps_file, deps_content)

    def _generate_flask_framework_code(self, architecture_spec: Dict[str, Any]):
        """Generate Flask-specific basic framework code."""
        # Create Flask models using SQLAlchemy
        self._create_flask_models(architecture_spec)

        # Create Flask services/blueprints
        self._create_flask_services(architecture_spec)

        # Create Flask routes based on architecture
        self._create_flask_routes(architecture_spec)

        # Create database integration
        self._create_flask_database_integration(architecture_spec)

    def _create_flask_models(self, architecture_spec: Dict[str, Any]):
        """Create Flask models using SQLAlchemy."""
        models_path = self.project_path / "src" / "models"

        # Create base model
        base_model_content = '''"""
SQLAlchemy base models for Flask application
"""
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from datetime import datetime
import uuid

db = SQLAlchemy()


class BaseModel(db.Model):
    """Base model with common fields."""
    __abstract__ = True

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
'''
        base_model_file = models_path / "base.py"
        self._write_file(base_model_file, base_model_content)

        # Create specific models based on architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").lower()
            responsibilities = component.get("responsibilities", [])

            if "data" in name.lower() or "model" in name.lower() or "entity" in name.lower():
                model_content = f'''"""
{name.capitalize()} model for Flask application
"""
from .base import db, BaseModel
from datetime import datetime
import uuid


class {name.capitalize()}(BaseModel):
    """{name.capitalize()} model."""
    __tablename__ = '{name.lower()}'

    # Add fields based on responsibilities
'''
                # Add fields based on responsibilities
                for idx, resp in enumerate(responsibilities[:5]):  # Limit to first 5 responsibilities
                    field_name = f"field_{idx+1}".replace(" ", "_").lower()
                    model_content += f'    {field_name} = db.Column(db.String(255), nullable=True, comment="{resp}")\n'

                model_content += f'''

    def to_dict(self):
        """Convert model to dictionary."""
        return {{
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
'''
                # Add the field values to the dictionary
                for idx, resp in enumerate(responsibilities[:5]):
                    field_name = f"field_{idx+1}".replace(" ", "_").lower()
                    model_content += f'            "{field_name}": getattr(self, "{field_name}", None),\n'

                model_content += '''        }}
'''
                model_file = models_path / f"{name}_model.py"
                self._write_file(model_file, model_content)

    def _create_flask_services(self, architecture_spec: Dict[str, Any]):
        """Create Flask services/blueprints."""
        # Create a services directory if it doesn't exist
        services_path = self.project_path / "src" / "services"
        services_path.mkdir(exist_ok=True)

        # Create base service
        base_service_content = '''"""
Base service class for Flask application
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseService(ABC):
    """Base service class with common operations."""

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Any:
        """Create a new object."""
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[Any]:
        """Get an object by ID."""
        pass

    @abstractmethod
    def list(self, page: int = 1, per_page: int = 10) -> List[Any]:
        """List objects with pagination."""
        pass

    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Any]:
        """Update an object."""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an object."""
        pass
'''
        base_service_file = services_path / "base.py"
        self._write_file(base_service_file, base_service_content)

    def _create_flask_routes(self, architecture_spec: Dict[str, Any]):
        """Create Flask routes based on architecture."""
        # Create blueprint routes based on components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").lower()

            # Create blueprint for this component
            bp_content = f'''"""
{name.capitalize()} blueprint for Flask application
"""
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import logging

from ..models.{name}_model import {name.capitalize()}
from ..database import db  # Assuming database setup exists

{name.lower()}_bp = Blueprint('{name.lower()}', __name__)
logger = logging.getLogger(__name__)


@{name.lower()}_bp.route('/', methods=['GET'])
def get_{name}s():
    """Get a list of {name}s."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Get paginated results
        {name}s = {name.capitalize()}.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({{
            'data': [item.to_dict() for item in {name}s.items],
            'pagination': {{
                'page': {name}s.page,
                'pages': {name}s.pages,
                'per_page': {name}s.per_page,
                'total': {name}s.total
            }}
        }}), 200
    except Exception as e:
        logger.error(f"Error getting {name}s: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500


@{name.lower()}_bp.route('/<id>', methods=['GET'])
def get_{name}(id: str):
    """Get a specific {name} by ID."""
    try:
        item = {name.capitalize()}.query.filter_by(id=id).first()

        if not item:
            return jsonify({{'error': '{name.capitalize()} not found'}}), 404

        return jsonify(item.to_dict()), 200
    except Exception as e:
        logger.error(f"Error getting {name} {{id}}: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500


@{name.lower()}_bp.route('/', methods=['POST'])
def create_{name}():
    """Create a new {name}."""
    try:
        data = request.get_json()

        # Validate input (basic validation)
        if not data:
            return jsonify({{'error': 'No data provided'}}), 400

        # Create new {name}
        new_item = {name.capitalize()}(**data)
        db.session.add(new_item)
        db.session.commit()

        return jsonify(new_item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating {name}: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500


@{name.lower()}_bp.route('/<id>', methods=['PUT'])
def update_{name}(id: str):
    """Update an existing {name}."""
    try:
        item = {name.capitalize()}.query.filter_by(id=id).first()

        if not item:
            return jsonify({{'error': '{name.capitalize()} not found'}}), 404

        data = request.get_json()
        if not data:
            return jsonify({{'error': 'No data provided'}}), 400

        # Update fields
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)

        db.session.commit()
        return jsonify(item.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating {name} {{id}}: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500


@{name.lower()}_bp.route('/<id>', methods=['DELETE'])
def delete_{name}(id: str):
    """Delete a {name}."""
    try:
        item = {name.capitalize()}.query.filter_by(id=id).first()

        if not item:
            return jsonify({{'error': '{name.capitalize()} not found'}}), 404

        db.session.delete(item)
        db.session.commit()

        return jsonify({{'success': True}}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting {name} {{id}}: {{e}}")
        return jsonify({{'error': 'Internal server error'}}), 500
'''
            routes_path = self.project_path / "src" / "routes"
            routes_path.mkdir(exist_ok=True)
            bp_file = routes_path / f"{name}_routes.py"
            self._write_file(bp_file, bp_content)

    def _create_flask_database_integration(self, architecture_spec: Dict[str, Any]):
        """Create Flask database integration."""
        db_path = self.project_path / "src" / "database"
        db_path.mkdir(exist_ok=True)

        # Create database initialization
        db_init_content = '''"""
Database initialization for Flask application
"""
from flask import Flask
from .config import db


def init_db(app: Flask):
    """Initialize database with the Flask app."""
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()
'''
        db_init_file = db_path / "__init__.py"
        self._write_file(db_init_file, db_init_content)

    def _generate_django_framework_code(self, architecture_spec: Dict[str, Any]):
        """Generate Django-specific basic framework code."""
        # Django generation would involve creating apps, models, views, etc.
        # This is a simplified version - a full implementation would be more complex

        # Create Django models based on architecture
        self._create_django_models(architecture_spec)

        # Create Django views
        self._create_django_views(architecture_spec)

        # Create Django serializers
        self._create_django_serializers(architecture_spec)

    def _create_django_models(self, architecture_spec: Dict[str, Any]):
        """Create Django models."""
        # For Django, models typically go in the apps
        # We'll assume there's an 'api' app created
        apps_path = self.project_path / "src" / "api"
        if apps_path.exists():
            models_path = apps_path / "models.py"

            # Read existing models file if it exists
            if models_path.exists():
                existing_content = models_path.read_text(encoding='utf-8')
            else:
                existing_content = '''"""
Django models for the API app
"""
from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime
'''

            # Add models based on architecture components
            components = architecture_spec.get("components", [])
            new_models = []

            for component in components:
                name = component.get("name", "").replace(" ", "").replace("-", "")
                responsibilities = component.get("responsibilities", [])

                if "data" in name.lower() or "model" in name.lower() or "entity" in name.lower():
                    model_def = f'''

class {name.capitalize()}(models.Model):
    """{name.capitalize()} model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
'''
                    # Add fields based on responsibilities
                    for idx, resp in enumerate(responsibilities[:5]):
                        field_name = f"field_{idx+1}".replace(" ", "_").lower()
                        model_def += f'    {field_name} = models.CharField(max_length=255, blank=True, null=True, help_text="{resp}")\n'

                    model_def += f'''
    def __str__(self):
        return f"{{self.id}}"

    class Meta:
        verbose_name = "{name.capitalize()}"
        verbose_name_plural = "{name.capitalize()}s"
'''
                    new_models.append(model_def)

            # Combine existing and new models
            combined_content = existing_content
            for model in new_models:
                if model not in combined_content:  # Avoid duplicates
                    combined_content += model

            self._write_file(models_path, combined_content)

    def _create_django_views(self, architecture_spec: Dict[str, Any]):
        """Create Django views."""
        apps_path = self.project_path / "src" / "api"
        if apps_path.exists():
            views_path = apps_path / "views.py"

            # Read existing views file if it exists
            if views_path.exists():
                existing_content = views_path.read_text(encoding='utf-8')
            else:
                existing_content = '''"""
Django views for the API app
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
'''

            # Add views based on architecture components
            components = architecture_spec.get("components", [])
            new_views = []

            for component in components:
                name = component.get("name", "").replace(" ", "").replace("-", "")

                if "api" in name.lower() or "view" in name.lower() or "endpoint" in name.lower():
                    view_def = f'''

@method_decorator(csrf_exempt, name='dispatch')
class {name.capitalize()}ListView(View):
    """List {name} objects."""

    def get(self, request):
        # Implementation for listing {name}s
        return JsonResponse({{'message': 'List {name}s endpoint'}})

    def post(self, request):
        # Implementation for creating {name}
        data = json.loads(request.body)
        return JsonResponse({{'message': 'Create {name} endpoint', 'data': data}})


@method_decorator(csrf_exempt, name='dispatch')
class {name.capitalize()}DetailView(View):
    """Detail view for {name} objects."""

    def get(self, request, pk):
        # Implementation for getting specific {name}
        return JsonResponse({{'message': f'Get {name} with id {{pk}} endpoint'}})

    def put(self, request, pk):
        # Implementation for updating {name}
        data = json.loads(request.body)
        return JsonResponse({{'message': f'Update {name} with id {{pk}} endpoint', 'data': data}})

    def delete(self, request, pk):
        # Implementation for deleting {name}
        return JsonResponse({{'message': f'Delete {name} with id {{pk}} endpoint'}})
'''
                    new_views.append(view_def)

            # Combine existing and new views
            combined_content = existing_content
            for view in new_views:
                if view not in combined_content:  # Avoid duplicates
                    combined_content += view

            self._write_file(views_path, combined_content)

    def _create_django_serializers(self, architecture_spec: Dict[str, Any]):
        """Create Django REST Framework serializers."""
        apps_path = self.project_path / "src" / "api"
        if apps_path.exists():
            serializers_path = apps_path / "serializers.py"

            # Create serializers content
            content = '''"""
Django REST Framework serializers for the API app
"""
from rest_framework import serializers
from .models import *
'''

            # Add serializers based on models
            components = architecture_spec.get("components", [])
            for component in components:
                name = component.get("name", "").replace(" ", "").replace("-", "")

                if "data" in name.lower() or "model" in name.lower() or "entity" in name.lower():
                    serializer_def = f'''

class {name.capitalize()}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {name.capitalize()}
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
'''
                    content += serializer_def

            self._write_file(serializers_path, content)

    def _generate_generic_framework_code(self, architecture_spec: Dict[str, Any]):
        """Generate generic framework code."""
        # Create generic modules based on architecture
        modules_path = self.project_path / "src" / "modules"
        modules_path.mkdir(exist_ok=True)

        # Create a base module structure
        base_module_content = '''"""
Base module with common functionality
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseModule(ABC):
    """Base module with common interface."""

    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Any:
        """Execute the module's main function."""
        pass

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate input data."""
        pass
'''
        base_module_file = modules_path / "base.py"
        self._write_file(base_module_file, base_module_content)

        # Create modules based on architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").lower()
            responsibilities = component.get("responsibilities", [])

            module_content = f'''"""
{name.capitalize()} module
"""
from .base import BaseModule
from typing import Any, Dict, List, Optional


class {name.capitalize()}Module(BaseModule):
    """Module for {name} functionality."""

    def __init__(self):
        """Initialize the {name} module."""
        pass

    def execute(self, data: Dict[str, Any]) -> Any:
        """Execute {name} functionality."""
        # Implementation based on responsibilities:
'''
            for resp in responsibilities:
                module_content += f'        # - {resp}\n'

            module_content += '''        return data

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate input data for {name} module."""
        # Add validation logic based on responsibilities
        return True
'''
            module_file = modules_path / f"{name}_module.py"
            self._write_file(module_file, module_content)

    def _write_file(self, file_path: Path, content: str):
        """Write content to a file, creating parent directories if needed."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)


def generate_basic_framework_code(architecture_spec: Dict[str, Any],
                                project_path: str = "./generated-project") -> bool:
    """
    Convenience function to generate basic framework code from architecture specification.

    Args:
        architecture_spec: Architecture specification from Epic #3
        project_path: Path where the project is located

    Returns:
        True if successful, False otherwise
    """
    generator = BasicFrameworkGenerator(project_path)
    return generator.generate_basic_framework_code(architecture_spec)


# Example usage and test function
def test_framework_generator():
    """Test the framework generator with a sample architecture."""
    # Create a sample architecture spec similar to what would be generated in Epic #3
    sample_arch = {
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
                "name": "User Management",
                "responsibilities": ["handle user registration", "authenticate users", "manage user profiles"]
            },
            {
                "name": "Product Catalog",
                "responsibilities": ["manage product listings", "handle inventory", "product search"]
            },
            {
                "name": "Order Processing",
                "responsibilities": ["process orders", "handle payments", "manage shipments"]
            }
        ],
        "integration_points": [
            {"name": "Database Connection", "type": "PostgreSQL"},
            {"name": "Message Queue", "type": "Redis"},
            {"name": "Authentication Service", "type": "OAuth2"}
        ]
    }

    # This would be tested in a real project directory
    # For now, just verifying the function exists
    print("Basic Framework Generator is ready to generate code from architecture specifications")
    return True


if __name__ == "__main__":
    test_framework_generator()