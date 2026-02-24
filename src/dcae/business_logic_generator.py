"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Business Logic Generator Module

This module implements the business logic generation functionality as specified in
Epic #4: Code Generation & Development, specifically Story 4.3: Generate Business Logic.

As a developer,
I want to generate business logic components based on the architecture and requirements,
so that I have properly structured business rules and operations that align with the system design.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import re

from .code_structure_generator import FrameworkType
from .basic_framework_generator import BasicFrameworkGenerator


class BusinessLogicGenerator:
    """Main class for generating business logic components."""

    def __init__(self, project_path: str):
        """
        Initialize the business logic generator.

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

    def generate_business_logic_from_architecture(self, architecture_spec: Dict[str, Any],
                                               requirements_spec: Optional[Dict[str, Any]] = None) -> bool:
        """
        Generate business logic based on architecture and requirements.

        Args:
            architecture_spec: Architecture specification from Epic #3
            requirements_spec: Requirements specification from Epic #2 (optional)

        Returns:
            True if successful, False otherwise
        """
        print(f"Generating business logic for {self.framework_type.value} project at: {self.project_path}")

        # Extract business rules from architecture and requirements
        business_rules = self._extract_business_rules(architecture_spec, requirements_spec)

        # Generate business services based on components and rules
        self._generate_business_services(architecture_spec, business_rules)

        # Generate validation logic
        self._generate_validation_logic(architecture_spec, business_rules)

        # Generate entity management logic
        self._generate_entity_management_logic(architecture_spec, business_rules)

        # Generate workflow logic
        self._generate_workflow_logic(architecture_spec, business_rules)

        print(f"[X] Business logic generated successfully at: {self.project_path}")
        return True

    def _extract_business_rules(self, architecture_spec: Dict[str, Any],
                               requirements_spec: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extract business rules from architecture and requirements.

        Args:
            architecture_spec: Architecture specification
            requirements_spec: Requirements specification

        Returns:
            List of extracted business rules
        """
        business_rules = []

        # Extract from architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "")
            responsibilities = component.get("responsibilities", [])

            # Each responsibility could be a business rule
            for idx, responsibility in enumerate(responsibilities):
                rule = {
                    "id": f"BR_{name.upper().replace(' ', '_')}_{idx+1}",
                    "name": f"{name} - {responsibility}",
                    "description": responsibility,
                    "component": name,
                    "type": "operation",
                    "conditions": [],
                    "actions": [responsibility]
                }
                business_rules.append(rule)

        # Extract from requirements if provided
        if requirements_spec:
            fr_list = requirements_spec.get("functional_requirements", [])
            nfr_list = requirements_spec.get("non_functional_requirements", [])

            for fr in fr_list:
                rule = {
                    "id": f"FR_{fr.get('id', 'UNDEFINED')}",
                    "name": fr.get("title", fr.get("description", "Unknown")),
                    "description": fr.get("description", ""),
                    "type": "functional_requirement",
                    "conditions": [],
                    "actions": [fr.get("description", "")]
                }
                business_rules.append(rule)

            for nfr in nfr_list:
                rule = {
                    "id": f"NFR_{nfr.get('id', 'UNDEFINED')}",
                    "name": nfr.get("title", nfr.get("description", "Unknown")),
                    "description": nfr.get("description", ""),
                    "type": "non_functional_requirement",
                    "conditions": [],
                    "actions": [nfr.get("description", "")]
                }
                business_rules.append(rule)

        return business_rules

    def _generate_business_services(self, architecture_spec: Dict[str, Any], business_rules: List[Dict[str, Any]]):
        """Generate business service classes based on architecture components and business rules."""
        services_path = self.project_path / "src" / "services"

        # Generate services based on architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").replace("-", "_").lower()
            responsibilities = component.get("responsibilities", [])

            # Only generate services for components that seem to have business logic
            if any(word in name.lower() for word in ["service", "business", "logic", "manager", "handler"]):
                if self.framework_type == FrameworkType.FASTAPI:
                    self._generate_fastapi_business_service(name, responsibilities, business_rules)
                elif self.framework_type == FrameworkType.FLASK:
                    self._generate_flask_business_service(name, responsibilities, business_rules)
                elif self.framework_type == FrameworkType.DJANGO:
                    self._generate_django_business_service(name, responsibilities, business_rules)
                else:
                    self._generate_generic_business_service(name, responsibilities, business_rules)

    def _generate_fastapi_business_service(self, name: str, responsibilities: List[str], business_rules: List[Dict[str, Any]]):
        """Generate FastAPI-specific business service."""
        services_path = self.project_path / "src" / "services"

        # Get business rules related to this service
        service_rules = [rule for rule in business_rules if name.lower() in rule['component'].lower() or name.lower() in rule['name'].lower()]

        service_content = f'''"""
{name.capitalize()} business service
"""
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging
from datetime import datetime

from ..models.{name}_schema import {name.capitalize()}Create, {name.capitalize()}Update, {name.capitalize()}Response
from ..database.config import get_db_context
from ..database.base import BaseDBModel


logger = logging.getLogger(__name__)


class {name.capitalize()}ServiceProtocol(ABC):
    """Protocol defining the interface for {name} business service."""

    @abstractmethod
    async def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation."""
        pass

    @abstractmethod
    async def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate business rules."""
        pass

    @abstractmethod
    async def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        pass


class {name.capitalize()}Service({name.capitalize()}ServiceProtocol):
    """Implementation of {name} business service."""

    def __init__(self):
        """Initialize the {name} service."""
        self.business_rules = self._load_business_rules()
        logger.info("{name.capitalize()} service initialized")

    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules specific to {name} service."""
        rules = {{
'''

        # Add business rules to the service
        for idx, rule in enumerate(service_rules):
            service_content += f'            "rule_{idx+1}": "{rule["description"]}",\n'

        service_content += f'''        }}
        return rules

    async def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation based on responsibilities."""
        try:
            # Validate input
            is_valid = await self.validate_business_rules(data)
            if not is_valid:
                raise ValueError("Business rules validation failed")

            # Apply business logic based on responsibilities:
'''

        for idx, resp in enumerate(responsibilities):
            service_content += f'            # Responsibility {idx+1}: {resp}\n'

        service_content += f'''            # Process the operation
            result = {{
                "status": "success",
                "processed_data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "operation": "{name}_business_operation"
            }}

            logger.info(f"Processed business operation for {name}")
            return result

        except Exception as e:
            logger.error(f"Error processing business operation: {{e}}")
            raise

    async def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate data against business rules."""
        try:
            # Apply validation rules
            for rule_id, rule_desc in self.business_rules.items():
                # Example validation - would be customized based on actual rules
                if not self._apply_business_rule(rule_desc, data):
                    logger.warning(f"Business rule failed: {{rule_desc}}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error during business rule validation: {{e}}")
            return False

    def _apply_business_rule(self, rule_description: str, data: Dict[str, Any]) -> bool:
        """Apply a specific business rule to the data."""
        # This is a simplified implementation
        # In a real system, this would contain specific validation logic
        # based on the rule description

        # Example rules - in practice, this would be more sophisticated
        if "required" in rule_description.lower():
            # Check for required fields
            required_fields = ["id", "name"]  # Example fields
            for field in required_fields:
                if field not in data:
                    return False
                if not data[field]:  # Empty or None
                    return False
        elif "unique" in rule_description.lower():
            # Check for uniqueness constraints
            # This would require database lookup in practice
            pass

        return True

    async def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        try:
            # Retrieve entity from database
            # This is a simplified example - would require actual DB integration
            async with get_db_context() as db:
                # Query would go here
                entity_state = {{
                    "id": entity_id,
                    "state": "active",  # Example state
                    "last_updated": datetime.utcnow().isoformat()
                }}
                return entity_state
        except Exception as e:
            logger.error(f"Error retrieving entity state: {{e}}")
            return None

    async def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a multi-step business workflow."""
        results = []

        for step in workflow_steps:
            try:
                step_result = await self._execute_workflow_step(step)
                results.append(step_result)

                # Check if workflow should continue based on business rules
                if not await self.validate_business_rules({{"results": results}}):
                    break

            except Exception as e:
                logger.error(f"Error executing workflow step: {{e}}")
                return {{"status": "error", "error": str(e), "results": results}}

        return {{"status": "success", "results": results}}

    async def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step in a workflow."""
        step_type = step.get("type", "default")
        step_data = step.get("data", {{}})

        # Execute based on step type
        if step_type == "validation":
            is_valid = await self.validate_business_rules(step_data)
            return {{"step_type": step_type, "result": is_valid, "data": step_data}}
        elif step_type == "transformation":
            # Transform the data according to business rules
            transformed_data = self._transform_data(step_data)
            return {{"step_type": step_type, "result": "success", "data": transformed_data}}
        else:
            # Default processing
            return {{"step_type": step_type, "result": "processed", "data": step_data}}

    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to business rules."""
        # Apply transformations based on loaded business rules
        transformed = data.copy()

        # Example transformation - in reality, this would be based on specific rules
        if "name" in transformed and transformed["name"]:
            transformed["name"] = transformed["name"].upper()  # Example transformation

        return transformed
'''

        service_file = services_path / f"{name}_business_service.py"
        self._write_file(service_file, service_content)

    def _generate_flask_business_service(self, name: str, responsibilities: List[str], business_rules: List[Dict[str, Any]]):
        """Generate Flask-specific business service."""
        services_path = self.project_path / "src" / "services"

        # Get business rules related to this service
        service_rules = [rule for rule in business_rules if 'component' in rule and name.lower() in rule['component'].lower()]

        service_content = f'''"""
{name.capitalize()} business service for Flask
"""
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging
from datetime import datetime
from functools import wraps

# Assuming Flask-SQLAlchemy models exist
# from ..models.{name}_model import {name.capitalize()}


logger = logging.getLogger(__name__)


class {name.capitalize()}ServiceProtocol(ABC):
    """Protocol defining the interface for {name} business service."""

    @abstractmethod
    def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation."""
        pass

    @abstractmethod
    def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate business rules."""
        pass

    @abstractmethod
    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        pass


class {name.capitalize()}Service({name.capitalize()}ServiceProtocol):
    """Implementation of {name} business service for Flask."""

    def __init__(self):
        """Initialize the {name} service."""
        self.business_rules = self._load_business_rules()
        logger.info("{name.capitalize()} service initialized")

    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules specific to {name} service."""
        rules = {{
'''

        # Add business rules to the service
        for idx, rule in enumerate(service_rules):
            service_content += f'            "rule_{idx+1}": "{rule["description"]}",\n'

        service_content += f'''        }}
        return rules

    def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation based on responsibilities."""
        try:
            # Validate input
            is_valid = self.validate_business_rules(data)
            if not is_valid:
                raise ValueError("Business rules validation failed")

            # Apply business logic based on responsibilities:
'''

        for idx, resp in enumerate(responsibilities):
            service_content += f'            # Responsibility {idx+1}: {resp}\n'

        service_content += f'''            # Process the operation
            result = {{
                "status": "success",
                "processed_data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "operation": "{name}_business_operation"
            }}

            logger.info(f"Processed business operation for {name}")
            return result

        except Exception as e:
            logger.error(f"Error processing business operation: {{e}}")
            raise

    def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate data against business rules."""
        try:
            # Apply validation rules
            for rule_id, rule_desc in self.business_rules.items():
                if not self._apply_business_rule(rule_desc, data):
                    logger.warning(f"Business rule failed: {{rule_desc}}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error during business rule validation: {{e}}")
            return False

    def _apply_business_rule(self, rule_description: str, data: Dict[str, Any]) -> bool:
        """Apply a specific business rule to the data."""
        # This is a simplified implementation
        # In a real system, this would contain specific validation logic
        # based on the rule description

        # Example rules - in practice, this would be more sophisticated
        if "required" in rule_description.lower():
            # Check for required fields
            required_fields = ["id", "name"]  # Example fields
            for field in required_fields:
                if field not in data:
                    return False
                if not data[field]:  # Empty or None
                    return False
        elif "unique" in rule_description.lower():
            # Check for uniqueness constraints
            # This would require database lookup in practice
            pass

        return True

    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        try:
            # Retrieve entity from database
            # This is a simplified example - would require actual DB integration
            # entity = {name.capitalize()}.query.filter_by(id=entity_id).first()
            # if entity:
            #     return entity.to_dict()

            entity_state = {{
                "id": entity_id,
                "state": "active",  # Example state
                "last_updated": datetime.utcnow().isoformat()
            }}
            return entity_state
        except Exception as e:
            logger.error(f"Error retrieving entity state: {{e}}")
            return None

    def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a multi-step business workflow."""
        results = []

        for step in workflow_steps:
            try:
                step_result = self._execute_workflow_step(step)
                results.append(step_result)

                # Check if workflow should continue based on business rules
                if not self.validate_business_rules({{"results": results}}):
                    break

            except Exception as e:
                logger.error(f"Error executing workflow step: {{e}}")
                return {{"status": "error", "error": str(e), "results": results}}

        return {{"status": "success", "results": results}}

    def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step in a workflow."""
        step_type = step.get("type", "default")
        step_data = step.get("data", {{}})

        # Execute based on step type
        if step_type == "validation":
            is_valid = self.validate_business_rules(step_data)
            return {{"step_type": step_type, "result": is_valid, "data": step_data}}
        elif step_type == "transformation":
            # Transform the data according to business rules
            transformed_data = self._transform_data(step_data)
            return {{"step_type": step_type, "result": "success", "data": transformed_data}}
        else:
            # Default processing
            return {{"step_type": step_type, "result": "processed", "data": step_data}}

    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to business rules."""
        # Apply transformations based on loaded business rules
        transformed = data.copy()

        # Example transformation - in reality, this would be based on specific rules
        if "name" in transformed and transformed["name"]:
            transformed["name"] = transformed["name"].upper()  # Example transformation

        return transformed
'''

        service_file = services_path / f"{name}_business_service.py"
        self._write_file(service_file, service_content)

    def _generate_django_business_service(self, name: str, responsibilities: List[str], business_rules: List[Dict[str, Any]]):
        """Generate Django-specific business service."""
        # For Django, services might be placed in a 'services' directory inside the app
        apps_path = self.project_path / "src" / "api"  # Assuming 'api' app
        if not apps_path.exists():
            apps_path = self.project_path / "src"

        services_path = apps_path / "services"
        services_path.mkdir(exist_ok=True)

        # Get business rules related to this service
        service_rules = [rule for rule in business_rules if 'component' in rule and name.lower() in rule['component'].lower()]

        service_content = f'''"""
{name.capitalize()} business service for Django
"""
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging
from datetime import datetime

# Assuming Django models exist
# from .models import {name.capitalize()}


logger = logging.getLogger(__name__)


class {name.capitalize()}ServiceProtocol(ABC):
    """Protocol defining the interface for {name} business service."""

    @abstractmethod
    def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation."""
        pass

    @abstractmethod
    def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate business rules."""
        pass

    @abstractmethod
    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        pass


class {name.capitalize()}Service({name.capitalize()}ServiceProtocol):
    """Implementation of {name} business service for Django."""

    def __init__(self):
        """Initialize the {name} service."""
        self.business_rules = self._load_business_rules()
        logger.info("{name.capitalize()} service initialized")

    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules specific to {name} service."""
        rules = {{
'''

        # Add business rules to the service
        for idx, rule in enumerate(service_rules):
            service_content += f'            "rule_{idx+1}": "{rule["description"]}",\n'

        service_content += f'''        }}
        return rules

    def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation based on responsibilities."""
        try:
            # Validate input
            is_valid = self.validate_business_rules(data)
            if not is_valid:
                raise ValueError("Business rules validation failed")

            # Apply business logic based on responsibilities:
'''

        for idx, resp in enumerate(responsibilities):
            service_content += f'            # Responsibility {idx+1}: {resp}\n'

        service_content += f'''            # Process the operation
            result = {{
                "status": "success",
                "processed_data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "operation": "{name}_business_operation"
            }}

            logger.info(f"Processed business operation for {name}")
            return result

        except Exception as e:
            logger.error(f"Error processing business operation: {{e}}")
            raise

    def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate data against business rules."""
        try:
            # Apply validation rules
            for rule_id, rule_desc in self.business_rules.items():
                if not self._apply_business_rule(rule_desc, data):
                    logger.warning(f"Business rule failed: {{rule_desc}}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error during business rule validation: {{e}}")
            return False

    def _apply_business_rule(self, rule_description: str, data: Dict[str, Any]) -> bool:
        """Apply a specific business rule to the data."""
        # This is a simplified implementation
        # In a real system, this would contain specific validation logic
        # based on the rule description

        # Example rules - in practice, this would be more sophisticated
        if "required" in rule_description.lower():
            # Check for required fields
            required_fields = ["id", "name"]  # Example fields
            for field in required_fields:
                if field not in data:
                    return False
                if not data[field]:  # Empty or None
                    return False
        elif "unique" in rule_description.lower():
            # Check for uniqueness constraints
            # This would require database lookup in practice
            pass

        return True

    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        try:
            # Retrieve entity from database
            # This is a simplified example - would require actual DB integration
            # try:
            #     entity = {name.capitalize()}.objects.get(id=entity_id)
            #     return {{'id': entity.id, 'name': entity.name}}  # Example
            # except {name.capitalize()}.DoesNotExist:
            #     return None

            entity_state = {{
                "id": entity_id,
                "state": "active",  # Example state
                "last_updated": datetime.utcnow().isoformat()
            }}
            return entity_state
        except Exception as e:
            logger.error(f"Error retrieving entity state: {{e}}")
            return None

    def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a multi-step business workflow."""
        results = []

        for step in workflow_steps:
            try:
                step_result = self._execute_workflow_step(step)
                results.append(step_result)

                # Check if workflow should continue based on business rules
                if not self.validate_business_rules({{"results": results}}):
                    break

            except Exception as e:
                logger.error(f"Error executing workflow step: {{e}}")
                return {{"status": "error", "error": str(e), "results": results}}

        return {{"status": "success", "results": results}}

    def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step in a workflow."""
        step_type = step.get("type", "default")
        step_data = step.get("data", {{}})

        # Execute based on step type
        if step_type == "validation":
            is_valid = self.validate_business_rules(step_data)
            return {{"step_type": step_type, "result": is_valid, "data": step_data}}
        elif step_type == "transformation":
            # Transform the data according to business rules
            transformed_data = self._transform_data(step_data)
            return {{"step_type": step_type, "result": "success", "data": transformed_data}}
        else:
            # Default processing
            return {{"step_type": step_type, "result": "processed", "data": step_data}}

    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to business rules."""
        # Apply transformations based on loaded business rules
        transformed = data.copy()

        # Example transformation - in reality, this would be based on specific rules
        if "name" in transformed and transformed["name"]:
            transformed["name"] = transformed["name"].upper()  # Example transformation

        return transformed
'''

        service_file = services_path / f"{name}_business_service.py"
        self._write_file(service_file, service_content)

    def _generate_generic_business_service(self, name: str, responsibilities: List[str], business_rules: List[Dict[str, Any]]):
        """Generate generic business service."""
        services_path = self.project_path / "src" / "services"

        # Get business rules related to this service
        service_rules = [rule for rule in business_rules if 'component' in rule and name.lower() in rule['component'].lower()]

        service_content = f'''"""
{name.capitalize()} generic business service
"""
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class {name.capitalize()}ServiceProtocol(ABC):
    """Protocol defining the interface for {name} business service."""

    @abstractmethod
    def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation."""
        pass

    @abstractmethod
    def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate business rules."""
        pass

    @abstractmethod
    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        pass


class {name.capitalize()}Service({name.capitalize()}ServiceProtocol):
    """Generic implementation of {name} business service."""

    def __init__(self):
        """Initialize the {name} service."""
        self.business_rules = self._load_business_rules()
        logger.info("{name.capitalize()} service initialized")

    def _load_business_rules(self) -> Dict[str, Any]:
        """Load business rules specific to {name} service."""
        rules = {{
'''

        # Add business rules to the service
        for idx, rule in enumerate(service_rules):
            service_content += f'            "rule_{idx+1}": "{rule["description"]}",\n'

        service_content += f'''        }}
        return rules

    def process_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a business operation based on responsibilities."""
        try:
            # Validate input
            is_valid = self.validate_business_rules(data)
            if not is_valid:
                raise ValueError("Business rules validation failed")

            # Apply business logic based on responsibilities:
'''

        for idx, resp in enumerate(responsibilities):
            service_content += f'            # Responsibility {idx+1}: {resp}\n'

        service_content += f'''            # Process the operation
            result = {{
                "status": "success",
                "processed_data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "operation": "{name}_business_operation"
            }}

            logger.info(f"Processed business operation for {name}")
            return result

        except Exception as e:
            logger.error(f"Error processing business operation: {{e}}")
            raise

    def validate_business_rules(self, data: Dict[str, Any]) -> bool:
        """Validate data against business rules."""
        try:
            # Apply validation rules
            for rule_id, rule_desc in self.business_rules.items():
                if not self._apply_business_rule(rule_desc, data):
                    logger.warning(f"Business rule failed: {{rule_desc}}")
                    return False

            return True
        except Exception as e:
            logger.error(f"Error during business rule validation: {{e}}")
            return False

    def _apply_business_rule(self, rule_description: str, data: Dict[str, Any]) -> bool:
        """Apply a specific business rule to the data."""
        # This is a simplified implementation
        # In a real system, this would contain specific validation logic
        # based on the rule description

        # Example rules - in practice, this would be more sophisticated
        if "required" in rule_description.lower():
            # Check for required fields
            required_fields = ["id", "name"]  # Example fields
            for field in required_fields:
                if field not in data:
                    return False
                if not data[field]:  # Empty or None
                    return False
        elif "unique" in rule_description.lower():
            # Check for uniqueness constraints
            # This would require database lookup in practice
            pass

        return True

    def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the state of an entity."""
        try:
            # In a generic implementation, this would be a simple dict lookup
            # or could interface with a data provider

            entity_state = {{
                "id": entity_id,
                "state": "active",  # Example state
                "last_updated": datetime.utcnow().isoformat()
            }}
            return entity_state
        except Exception as e:
            logger.error(f"Error retrieving entity state: {{e}}")
            return None

    def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a multi-step business workflow."""
        results = []

        for step in workflow_steps:
            try:
                step_result = self._execute_workflow_step(step)
                results.append(step_result)

                # Check if workflow should continue based on business rules
                if not self.validate_business_rules({{"results": results}}):
                    break

            except Exception as e:
                logger.error(f"Error executing workflow step: {{e}}")
                return {{"status": "error", "error": str(e), "results": results}}

        return {{"status": "success", "results": results}}

    def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step in a workflow."""
        step_type = step.get("type", "default")
        step_data = step.get("data", {{}})

        # Execute based on step type
        if step_type == "validation":
            is_valid = self.validate_business_rules(step_data)
            return {{"step_type": step_type, "result": is_valid, "data": step_data}}
        elif step_type == "transformation":
            # Transform the data according to business rules
            transformed_data = self._transform_data(step_data)
            return {{"step_type": step_type, "result": "success", "data": transformed_data}}
        else:
            # Default processing
            return {{"step_type": step_type, "result": "processed", "data": step_data}}

    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to business rules."""
        # Apply transformations based on loaded business rules
        transformed = data.copy()

        # Example transformation - in reality, this would be based on specific rules
        if "name" in transformed and transformed["name"]:
            transformed["name"] = transformed["name"].upper()  # Example transformation

        return transformed
'''

        service_file = services_path / f"{name}_business_service.py"
        self._write_file(service_file, service_content)

    def _generate_validation_logic(self, architecture_spec: Dict[str, Any], business_rules: List[Dict[str, Any]]):
        """Generate validation logic based on business rules."""
        # Create a validation directory if it doesn't exist
        validation_path = self.project_path / "src" / "validation"
        validation_path.mkdir(exist_ok=True)

        # Create base validation module
        base_validator_content = '''"""
Base validation classes and utilities
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import re


class BaseValidator(ABC):
    """Base validator class with common functionality."""

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate the provided data."""
        pass

    @abstractmethod
    def get_errors(self) -> List[str]:
        """Get list of validation errors."""
        pass


class ValidatorRegistry:
    """Registry for validators to allow pluggable validation."""

    def __init__(self):
        self._validators = {}

    def register(self, name: str, validator: BaseValidator):
        """Register a validator with a name."""
        self._validators[name] = validator

    def get(self, name: str) -> Optional[BaseValidator]:
        """Get a registered validator by name."""
        return self._validators.get(name)

    def validate(self, name: str, data: Any) -> Dict[str, Union[bool, List[str]]]:
        """Validate data using a registered validator."""
        validator = self.get(name)
        if not validator:
            return {"valid": False, "errors": [f"Validator '{name}' not found"]}

        is_valid = validator.validate(data)
        return {"valid": is_valid, "errors": validator.get_errors() if not is_valid else []}


# Predefined common validators
class RequiredValidator(BaseValidator):
    """Validator to check if a value is provided and not empty."""

    def __init__(self):
        self.errors = []

    def validate(self, data: Any) -> bool:
        """Validate that data is not None, not empty string, and not empty collection."""
        self.errors = []

        if data is None:
            self.errors.append("Value is required")
            return False

        if isinstance(data, str) and not data.strip():
            self.errors.append("Value cannot be empty")
            return False

        if isinstance(data, (list, tuple, dict)) and len(data) == 0:
            self.errors.append("Value cannot be empty")
            return False

        return True

    def get_errors(self) -> List[str]:
        return self.errors


class RegexValidator(BaseValidator):
    """Validator to check if a value matches a regular expression."""

    def __init__(self, pattern: str, error_message: str = "Value does not match required pattern"):
        self.pattern = pattern
        self.error_message = error_message
        self.errors = []

    def validate(self, data: str) -> bool:
        """Validate that data matches the pattern."""
        self.errors = []

        if not isinstance(data, str):
            self.errors.append("Value must be a string")
            return False

        if not re.match(self.pattern, data):
            self.errors.append(self.error_message)
            return False

        return True

    def get_errors(self) -> List[str]:
        return self.errors


class LengthValidator(BaseValidator):
    """Validator to check string length."""

    def __init__(self, min_length: int = 0, max_length: Optional[int] = None):
        self.min_length = min_length
        self.max_length = max_length
        self.errors = []

    def validate(self, data: str) -> bool:
        """Validate string length."""
        self.errors = []

        if not isinstance(data, str):
            self.errors.append("Value must be a string")
            return False

        length = len(data)

        if length < self.min_length:
            self.errors.append(f"Value must be at least {self.min_length} characters")
            return False

        if self.max_length and length > self.max_length:
            self.errors.append(f"Value must be no more than {self.max_length} characters")
            return False

        return True

    def get_errors(self) -> List[str]:
        return self.errors


# Global registry instance
validator_registry = ValidatorRegistry()

# Register common validators
validator_registry.register("required", RequiredValidator())
validator_registry.register("email", RegexValidator(r'^[^@]+@[^@]+\.[^@]+$', "Invalid email format"))
validator_registry.register("phone", RegexValidator(r'^\+?1?\d{9,15}$', "Invalid phone number format"))
'''

        base_validator_file = validation_path / "base.py"
        self._write_file(base_validator_file, base_validator_content)

        # Create validation modules based on architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").replace("-", "_").lower()
            responsibilities = component.get("responsibilities", [])

            # Create component-specific validator
            validator_content = f'''"""
Validators for {name} component
"""
from .base import BaseValidator, validator_registry
from typing import Any, List


class {name.capitalize()}Validator(BaseValidator):
    """Validator for {name} component data."""

    def __init__(self):
        self.errors = []

    def validate(self, data: Any) -> bool:
        """Validate {name} component data."""
        self.errors = []

        # Validate based on component responsibilities:
'''
            for idx, resp in enumerate(responsibilities):
                validator_content += f'        # Rule {idx+1}: {resp}\n'

            validator_content += '''
        # Perform validations
        if not self._validate_required_fields(data):
            return False

        if not self._validate_business_rules(data):
            return False

        return True

    def _validate_required_fields(self, data: Any) -> bool:
        """Validate required fields based on component responsibilities."""
        # This is an example implementation - in practice, it would be more specific
        if isinstance(data, dict):
            # Example: Check for common required fields
            required_fields = ["id", "name"]  # Customize based on responsibilities
            for field in required_fields:
                if field not in data or not data[field]:
                    self.errors.append(f"'{field}' is required for {name} component")
                    return False
        return True

    def _validate_business_rules(self, data: Any) -> bool:
        """Validate data against specific business rules."""
        # Apply business rules extracted from architecture and requirements
        # This would contain specific validation logic based on the rules
        return True

    def get_errors(self) -> List[str]:
        return self.errors


# Register the component validator
validator_registry.register(f"{name}_validator", {name.capitalize()}Validator())
'''

            validator_file = validation_path / f"{name}_validator.py"
            self._write_file(validator_file, validator_content)

    def _generate_entity_management_logic(self, architecture_spec: Dict[str, Any], business_rules: List[Dict[str, Any]]):
        """Generate entity management logic based on architecture components."""
        # Create an entities directory if it doesn't exist
        entities_path = self.project_path / "src" / "entities"
        entities_path.mkdir(exist_ok=True)

        # Create base entity module
        base_entity_content = '''"""
Base entity classes and management utilities
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime
import uuid


T = TypeVar('T')


class BaseEntity(Generic[T]):
    """Base entity with common properties."""

    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = 1

    def update_timestamp(self):
        """Update the timestamp when the entity is modified."""
        self.updated_at = datetime.utcnow()
        self.version += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> T:
        """Create entity instance from dictionary representation."""
        # This is a simplified implementation - in practice, subclasses would override
        entity = cls.__new__(cls)
        entity.id = data.get('id', str(uuid.uuid4()))
        entity.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
        entity.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else entity.created_at
        entity.version = data.get('version', 1)
        return entity


class EntityManagerProtocol(ABC):
    """Protocol defining the interface for entity management."""

    @abstractmethod
    def create(self, entity_data: Dict[str, Any]) -> Any:
        """Create a new entity."""
        pass

    @abstractmethod
    def get(self, entity_id: str) -> Optional[Any]:
        """Get an entity by ID."""
        pass

    @abstractmethod
    def update(self, entity_id: str, entity_data: Dict[str, Any]) -> Optional[Any]:
        """Update an entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity."""
        pass

    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """List entities with optional filters."""
        pass
'''

        base_entity_file = entities_path / "base.py"
        self._write_file(base_entity_file, base_entity_content)

        # Create entity managers based on architecture components
        components = architecture_spec.get("components", [])
        for component in components:
            name = component.get("name", "").replace(" ", "_").replace("-", "_").lower()
            responsibilities = component.get("responsibilities", [])

            # Only create entity managers for components that seem to manage data/entities
            if any(word in name.lower() for word in ["data", "entity", "model", "repository", "manager"]):
                entity_content = f'''"""
Entity management for {name} component
"""
from .base import BaseEntity, EntityManagerProtocol
from typing import Any, Dict, List, Optional
import logging


logger = logging.getLogger(__name__)


class {name.capitalize()}Entity(BaseEntity['{name.capitalize()}Entity']):
    """Entity class for {name} component."""

    def __init__(self, id: Optional[str] = None, **kwargs):
        super().__init__(id)
        # Initialize properties based on responsibilities:
'''

                for idx, resp in enumerate(responsibilities):
                    field_name = f"field_{idx+1}"
                    entity_content += f'        self.{field_name} = kwargs.get("{field_name}", None)  # From responsibility: {resp}\n'

                entity_content += f'''

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary with all properties."""
        base_dict = super().to_dict()
        # Add component-specific properties
'''

                for idx, resp in enumerate(responsibilities):
                    field_name = f"field_{idx+1}"
                    entity_content += f'        base_dict["{field_name}"] = getattr(self, "{field_name}", None)\n'

                entity_content += '''        return base_dict


class {name.capitalize()}EntityManager(EntityManagerProtocol):
    """Entity manager for {name} component."""

    def __init__(self):
        """Initialize the {name} entity manager."""
        self.entities = {{}}  # In practice, this would interface with a data store
        logger.info(f"{name.capitalize()} entity manager initialized")

    def create(self, entity_data: Dict[str, Any]) -> {name.capitalize()}Entity:
        """Create a new {name} entity."""
        try:
            entity = {name.capitalize()}Entity(**entity_data)
            self.entities[entity.id] = entity
            logger.info(f"Created {name} entity with ID: {{entity.id}}")
            return entity
        except Exception as e:
            logger.error(f"Error creating {name} entity: {{e}}")
            raise

    def get(self, entity_id: str) -> Optional[{name.capitalize()}Entity]:
        """Get a {name} entity by ID."""
        try:
            entity = self.entities.get(entity_id)
            if entity:
                logger.debug(f"Retrieved {name} entity with ID: {{entity_id}}")
            else:
                logger.warning(f"{name} entity not found with ID: {{entity_id}}")
            return entity
        except Exception as e:
            logger.error(f"Error retrieving {name} entity: {{e}}")
            return None

    def update(self, entity_id: str, entity_data: Dict[str, Any]) -> Optional[{name.capitalize()}Entity]:
        """Update a {name} entity."""
        try:
            existing_entity = self.get(entity_id)
            if not existing_entity:
                logger.warning(f"Cannot update {name} entity - not found with ID: {{entity_id}}")
                return None

            # Update entity properties
            for key, value in entity_data.items():
                if hasattr(existing_entity, key):
                    setattr(existing_entity, key, value)

            existing_entity.update_timestamp()
            logger.info(f"Updated {name} entity with ID: {{entity_id}}")
            return existing_entity
        except Exception as e:
            logger.error(f"Error updating {name} entity: {{e}}")
            return None

    def delete(self, entity_id: str) -> bool:
        """Delete a {name} entity."""
        try:
            if entity_id in self.entities:
                del self.entities[entity_id]
                logger.info(f"Deleted {name} entity with ID: {{entity_id}}")
                return True
            else:
                logger.warning(f"Cannot delete {name} entity - not found with ID: {{entity_id}}")
                return False
        except Exception as e:
            logger.error(f"Error deleting {name} entity: {{e}}")
            return False

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[{name.capitalize()}Entity]:
        """List {name} entities with optional filters."""
        try:
            entities = list(self.entities.values())

            if filters:
                # Apply filters - this is a basic implementation
                filtered_entities = []
                for entity in entities:
                    match = True
                    for filter_key, filter_value in filters.items():
                        if hasattr(entity, filter_key):
                            if getattr(entity, filter_key) != filter_value:
                                match = False
                                break
                        else:
                            match = False
                            break
                    if match:
                        filtered_entities.append(entity)
                entities = filtered_entities

            logger.info(f"Retrieved {{len(entities)}} {name} entities")
            return entities
        except Exception as e:
            logger.error(f"Error listing {name} entities: {{e}}")
            return []
'''

                entity_file = entities_path / f"{name}_entity.py"
                self._write_file(entity_file, entity_content)

    def _generate_workflow_logic(self, architecture_spec: Dict[str, Any], business_rules: List[Dict[str, Any]]):
        """Generate workflow logic based on business processes in architecture."""
        # Create a workflows directory if it doesn't exist
        workflows_path = self.project_path / "src" / "workflows"
        workflows_path.mkdir(exist_ok=True)

        # Create base workflow module
        base_workflow_content = '''"""
Base workflow classes and utilities
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Enum for workflow statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseWorkflowStep:
    """Base class for workflow steps."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.status = WorkflowStatus.PENDING

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow step."""
        self.started_at = datetime.utcnow()
        self.status = WorkflowStatus.RUNNING

        try:
            result = await self._execute_impl(context)
            self.completed_at = datetime.utcnow()
            self.status = WorkflowStatus.COMPLETED
            return result
        except Exception as e:
            self.completed_at = datetime.utcnow()
            self.status = WorkflowStatus.FAILED
            logger.error(f"Workflow step {{self.name}} failed: {{e}}")
            raise

    @abstractmethod
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation of the workflow step."""
        pass


class BaseWorkflow:
    """Base class for workflows."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[BaseWorkflowStep] = []
        self.context: Dict[str, Any] = {}
        self.status = WorkflowStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def add_step(self, step: BaseWorkflowStep):
        """Add a step to the workflow."""
        self.steps.append(step)

    async def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the entire workflow."""
        self.context = initial_context or {}
        self.started_at = datetime.utcnow()
        self.status = WorkflowStatus.RUNNING

        try:
            for step in self.steps:
                logger.info(f"Executing workflow step: {{step.name}}")
                self.context = {**self.context, **await step.execute(self.context)}

                # Check if workflow should continue
                if self._should_cancel():
                    self.status = WorkflowStatus.CANCELLED
                    break
            else:
                # All steps completed successfully
                self.status = WorkflowStatus.COMPLETED

        except Exception as e:
            logger.error(f"Workflow {{self.name}} failed: {{e}}")
            self.status = WorkflowStatus.FAILED
            raise
        finally:
            self.completed_at = datetime.utcnow()

        return self.context

    def _should_cancel(self) -> bool:
        """Check if the workflow should be cancelled."""
        # This could check for cancellation flags, business rule violations, etc.
        return False

    def get_status_report(self) -> Dict[str, Any]:
        """Get a status report of the workflow."""
        return {
            "workflow_name": self.name,
            "status": self.status.value,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None
                }
                for step in self.steps
            ],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
'''

        base_workflow_file = workflows_path / "base.py"
        self._write_file(base_workflow_file, base_workflow_content)

    def _write_file(self, file_path: Path, content: str):
        """Write content to a file, creating parent directories if needed."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)


def generate_business_logic_from_architecture(architecture_spec: Dict[str, Any],
                                           requirements_spec: Optional[Dict[str, Any]] = None,
                                           project_path: str = "./generated-project") -> bool:
    """
    Convenience function to generate business logic from architecture specification.

    Args:
        architecture_spec: Architecture specification from Epic #3
        requirements_spec: Requirements specification from Epic #2 (optional)
        project_path: Path where the project is located

    Returns:
        True if successful, False otherwise
    """
    generator = BusinessLogicGenerator(project_path)
    return generator.generate_business_logic_from_architecture(architecture_spec, requirements_spec)


# Example usage and test function
def test_business_logic_generator():
    """Test the business logic generator with sample specifications."""
    # Create sample architecture and requirements specs
    sample_arch = {
        "project_name": "Sample Business Application",
        "description": "A sample business application with multiple components",
        "architecture_style": "Layered Architecture",
        "technology_stack": {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql"
        },
        "components": [
            {
                "name": "User Management Service",
                "responsibilities": [
                    "handle user registration",
                    "authenticate users",
                    "manage user profiles",
                    "validate user data"
                ]
            },
            {
                "name": "Order Processing System",
                "responsibilities": [
                    "process orders",
                    "validate order data",
                    "calculate totals",
                    "handle payment processing"
                ]
            },
            {
                "name": "Inventory Manager",
                "responsibilities": [
                    "track stock levels",
                    "update inventory",
                    "handle stock transfers"
                ]
            }
        ]
    }

    sample_reqs = {
        "functional_requirements": [
            {"id": "FR001", "title": "User Registration", "description": "Users should be able to register with email and password"},
            {"id": "FR002", "title": "Order Creation", "description": "Users should be able to create orders with multiple items"}
        ],
        "non_functional_requirements": [
            {"id": "NFR001", "title": "Performance", "description": "System should handle 1000 concurrent users"},
            {"id": "NFR002", "title": "Security", "description": "All data should be encrypted in transit"}
        ]
    }

    print("Business Logic Generator is ready to generate code from architecture and requirements")
    return True


if __name__ == "__main__":
    test_business_logic_generator()