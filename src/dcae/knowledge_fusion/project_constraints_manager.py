"""
Project Constraints Manager

This module handles the identification, storage, and validation of project-specific constraints
that affect development decisions and implementation choices.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path
import json
import yaml
from datetime import datetime
import ast
import re


class Constraint(BaseModel):
    """
    Represents a single project-specific constraint
    """
    id: str = Field(..., description="Unique identifier for the constraint")
    name: str = Field(..., description="Human-readable name of the constraint")
    category: str = Field(..., description="Category of the constraint (technical, architectural, budgetary, etc.)")
    description: str = Field(..., description="Detailed description of the constraint")
    severity: str = Field(default="medium", description="Severity level: low, medium, high, critical")
    active: bool = Field(default=True, description="Whether the constraint is currently active")
    source: str = Field(default="unknown", description="Source of the constraint information")
    created_at: datetime = Field(default_factory=datetime.now, description="When the constraint was first identified")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the constraint was last updated")
    related_files: List[str] = Field(default_factory=list, description="Files or components affected by this constraint")


class ProjectConstraintsManager:
    """
    Manages project-specific constraints including storage, retrieval, and validation
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the constraints manager

        Args:
            storage_path: Path to store/load constraints data. Defaults to project config directory
        """
        self.storage_path = storage_path or Path.home() / ".dcae" / "constraints.json"
        self.constraints: Dict[str, Constraint] = {}

        # Ensure storage directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing constraints
        self.load_constraints()

    def add_constraint(self, constraint: Constraint) -> bool:
        """
        Add a new constraint to the manager

        Args:
            constraint: Constraint object to add

        Returns:
            bool: True if constraint was added successfully
        """
        try:
            self.constraints[constraint.id] = constraint
            constraint.updated_at = datetime.now()
            self.save_constraints()
            return True
        except Exception as e:
            print(f"Error adding constraint {constraint.id}: {str(e)}")
            return False

    def remove_constraint(self, constraint_id: str) -> bool:
        """
        Remove a constraint by ID

        Args:
            constraint_id: ID of the constraint to remove

        Returns:
            bool: True if constraint was removed successfully
        """
        if constraint_id in self.constraints:
            del self.constraints[constraint_id]
            self.save_constraints()
            return True
        return False

    def get_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """
        Get a constraint by ID

        Args:
            constraint_id: ID of the constraint to retrieve

        Returns:
            Constraint object if found, None otherwise
        """
        return self.constraints.get(constraint_id)

    def get_constraints_by_category(self, category: str) -> List[Constraint]:
        """
        Get all constraints in a specific category

        Args:
            category: Category to filter by

        Returns:
            List of constraints in the specified category
        """
        return [c for c in self.constraints.values() if c.category.lower() == category.lower()]

    def get_active_constraints(self) -> List[Constraint]:
        """
        Get all active constraints

        Returns:
            List of active constraints
        """
        return [c for c in self.constraints.values() if c.active]

    def validate_against_constraint(self, item_to_validate: Any, constraint_id: str) -> tuple[bool, str]:
        """
        Validate an item against a specific constraint

        Args:
            item_to_validate: Item to validate against the constraint
            constraint_id: ID of the constraint to validate against

        Returns:
            Tuple of (is_valid, message) indicating validation result
        """
        constraint = self.get_constraint(constraint_id)
        if not constraint:
            return False, f"Constraint {constraint_id} not found"

        if not constraint.active:
            return True, f"Constraint {constraint_id} is inactive"

        # This is a placeholder implementation - specific validation logic
        # would need to be implemented based on the constraint type
        # For now, we'll return a generic validation result
        return True, f"Item passes validation against constraint {constraint_id}"

    def check_compliance(self, items_to_check: List[Any]) -> Dict[str, List[tuple]]:
        """
        Check compliance of multiple items against all active constraints

        Args:
            items_to_check: List of items to check for compliance

        Returns:
            Dictionary mapping constraint IDs to lists of (item, is_valid, message) tuples
        """
        results = {}

        for constraint_id, constraint in self.constraints.items():
            if not constraint.active:
                continue

            constraint_results = []
            for item in items_to_check:
                is_valid, message = self.validate_against_constraint(item, constraint_id)
                constraint_results.append((item, is_valid, message))

            results[constraint_id] = constraint_results

        return results

    def save_constraints(self) -> bool:
        """
        Save constraints to persistent storage

        Returns:
            bool: True if saved successfully
        """
        try:
            constraints_dict = {
                cid: constraint.dict() for cid, constraint in self.constraints.items()
            }

            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(constraints_dict, f, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Error saving constraints: {str(e)}")
            return False

    def load_constraints(self) -> bool:
        """
        Load constraints from persistent storage

        Returns:
            bool: True if loaded successfully
        """
        try:
            if not self.storage_path.exists():
                # Create an empty constraints file if it doesn't exist
                self.save_constraints()
                return True

            with open(self.storage_path, 'r', encoding='utf-8') as f:
                constraints_dict = json.load(f)

            self.constraints = {}
            for cid, constraint_data in constraints_dict.items():
                # Convert datetime strings back to datetime objects
                if 'created_at' in constraint_data:
                    constraint_data['created_at'] = datetime.fromisoformat(constraint_data['created_at'])
                if 'updated_at' in constraint_data:
                    constraint_data['updated_at'] = datetime.fromisoformat(constraint_data['updated_at'])

                self.constraints[cid] = Constraint(**constraint_data)

            return True
        except Exception as e:
            print(f"Error loading constraints: {str(e)}")
            # Initialize with empty constraints if there's an error
            self.constraints = {}
            return False

    def catalog_existing_constraints(self) -> List[Constraint]:
        """
        Catalog existing project constraints by analyzing project documentation and configuration

        Returns:
            List of discovered constraints
        """
        discovered_constraints = []

        # Analyze project context file for constraints
        project_context_path = Path("D:/software_dev_project/DCAE/_bmad-output/project-context.md")
        if project_context_path.exists():
            constraints_from_context = self._extract_constraints_from_context(project_context_path)
            discovered_constraints.extend(constraints_from_context)

        # Analyze configuration files for constraints
        config_constraints = self._extract_constraints_from_configs()
        discovered_constraints.extend(config_constraints)

        # Add any constraints found in code comments or documentation
        code_constraints = self._extract_constraints_from_codebase()
        discovered_constraints.extend(code_constraints)

        return discovered_constraints

    def _extract_constraints_from_context(self, context_path: Path) -> List[Constraint]:
        """
        Extract constraints from project context file

        Args:
            context_path: Path to project context file

        Returns:
            List of constraints extracted from context
        """
        constraints = []

        try:
            with open(context_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract constraints based on common patterns in the context file
            # Technical constraints
            if "Python 3.11+" in content:
                constraints.append(Constraint(
                    id="tech-python-version",
                    name="Python Version Constraint",
                    category="technical",
                    description="Project requires Python 3.11 or higher",
                    severity="high",
                    source="project-context.md"
                ))

            if "Windows encoding" in content:
                constraints.append(Constraint(
                    id="tech-windows-encoding",
                    name="Windows Encoding Constraint",
                    category="technical",
                    description="Must handle Windows encoding properly using sys.stdout/stderr wrapper",
                    severity="high",
                    source="project-context.md"
                ))

            # Anti-pattern constraints
            if "Don't hardcode API keys" in content:
                constraints.append(Constraint(
                    id="sec-no-hardcoded-keys",
                    name="No Hardcoded API Keys",
                    category="security",
                    description="Never hardcode API keys or sensitive information in source code",
                    severity="critical",
                    source="project-context.md"
                ))

            # Performance constraints
            if "token counting" in content:
                constraints.append(Constraint(
                    id="perf-token-counting",
                    name="Token Counting Constraint",
                    category="performance",
                    description="Implement proper token counting to track API usage",
                    severity="medium",
                    source="project-context.md"
                ))

        except Exception as e:
            print(f"Error extracting constraints from context: {str(e)}")

        return constraints

    def _extract_constraints_from_configs(self) -> List[Constraint]:
        """
        Extract constraints from configuration files

        Returns:
            List of constraints extracted from configuration files
        """
        constraints = []
        config_dir = Path("D:/software_dev_project/DCAE/config")

        if config_dir.exists():
            # Look for any configuration-defined constraints
            for config_file in config_dir.glob("*.yaml"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)

                    # Extract any constraints defined in the config
                    if config_data and isinstance(config_data, dict):
                        # Example: constraints might be defined under a 'constraints' key
                        if 'constraints' in config_data:
                            for constraint_data in config_data['constraints']:
                                constraints.append(Constraint(
                                    id=f"cfg-{constraint_data.get('id', 'unknown')}",
                                    name=constraint_data.get('name', 'Unnamed constraint'),
                                    category=constraint_data.get('category', 'general'),
                                    description=constraint_data.get('description', ''),
                                    severity=constraint_data.get('severity', 'medium'),
                                    source=str(config_file)
                                ))

                except Exception as e:
                    print(f"Error parsing config file {config_file}: {str(e)}")

        return constraints

    def _extract_constraints_from_codebase(self) -> List[Constraint]:
        """
        Extract constraints from codebase analysis

        Returns:
            List of constraints extracted from codebase
        """
        constraints = []

        # This analyzes the codebase to identify technical and architectural constraints
        src_dir = Path("D:/software_dev_project/DCAE/src")

        if src_dir.exists():
            # Walk through Python files to identify constraints
            for py_file in src_dir.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Parse the file to get AST
                    try:
                        tree = ast.parse(content)

                        # Look for specific patterns that indicate constraints
                        # Import constraints
                        imports = self._analyze_imports(tree)
                        constraints.extend(imports)

                        # Type hint constraints
                        type_hints = self._analyze_type_hints(tree)
                        constraints.extend(type_hints)

                    except SyntaxError:
                        # If we can't parse the file, just do text-based analysis
                        text_constraints = self._analyze_file_text(content, py_file)
                        constraints.extend(text_constraints)

                except Exception as e:
                    print(f"Error analyzing file {py_file}: {str(e)}")

        return constraints

    def _analyze_imports(self, tree: ast.AST) -> List[Constraint]:
        """
        Analyze import statements to identify dependency constraints

        Args:
            tree: AST of the Python file

        Returns:
            List of constraints related to imports
        """
        constraints = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Check if import is from a specific required library
                    if alias.name in ['pydantic', 'pydantic_settings', 'typer', 'anthropic', 'openai']:
                        constraints.append(Constraint(
                            id=f"dep-required-{alias.name}",
                            name=f"Required Dependency: {alias.name}",
                            category="technical",
                            description=f"Project requires {alias.name} dependency",
                            severity="high",
                            source="codebase analysis"
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module in ['pydantic', 'pydantic_settings', 'typer', 'anthropic', 'openai']:
                    constraints.append(Constraint(
                        id=f"dep-required-{node.module}",
                        name=f"Required Dependency: {node.module}",
                        category="technical",
                        description=f"Project requires {node.module} dependency",
                        severity="high",
                        source="codebase analysis"
                    ))

        return constraints

    def _analyze_type_hints(self, tree: ast.AST) -> List[Constraint]:
        """
        Analyze type hints to identify type constraints

        Args:
            tree: AST of the Python file

        Returns:
            List of constraints related to type hints
        """
        constraints = []

        for node in ast.walk(tree):
            # Function annotations
            if isinstance(node, ast.FunctionDef):
                if node.returns:
                    constraints.append(Constraint(
                        id=f"type-hint-{node.name}-return",
                        name=f"Return Type Hint for {node.name}",
                        category="technical",
                        description=f"Function {node.name} has return type annotation",
                        severity="medium",
                        source="codebase analysis"
                    ))

                for arg in node.args.args:
                    if hasattr(arg, 'annotation') and arg.annotation:
                        constraints.append(Constraint(
                            id=f"type-hint-{node.name}-{arg.arg}",
                            name=f"Parameter Type Hint for {node.name}.{arg.arg}",
                            category="technical",
                            description=f"Parameter {arg.arg} in function {node.name} has type annotation",
                            severity="medium",
                            source="codebase analysis"
                        ))

        return constraints

    def _analyze_file_text(self, content: str, file_path: Path) -> List[Constraint]:
        """
        Perform text-based analysis to identify constraints

        Args:
            content: File content as string
            file_path: Path to the analyzed file

        Returns:
            List of constraints found through text analysis
        """
        constraints = []

        # Look for specific patterns that indicate constraints
        patterns = [
            (r'#\s*TODO:', 'development_process', 'Medium', 'TODO items represent pending constraints'),
            (r'#\s*FIXME:', 'development_process', 'High', 'FIXME items represent immediate constraints'),
            (r'#\s*HACK:', 'development_process', 'Medium', 'HACK comments indicate constraint workarounds'),
            (r'#\s*NOTE:', 'development_process', 'Low', 'NOTE comments may indicate constraints'),
            (r'#\s*WARNING:', 'development_process', 'High', 'WARNING comments indicate important constraints'),
        ]

        for pattern, category, severity, desc in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                constraints.append(Constraint(
                    id=f"text-{file_path.name}-{pattern.split()[0][1:]}",
                    name=f"{pattern.split()[0][1:]} comments in {file_path.name}",
                    category=category,
                    description=f"File {file_path} contains {len(matches)} {pattern.split()[0][1:]} comments indicating {desc}",
                    severity=severity.lower(),
                    source=str(file_path)
                ))

        # Look for specific technical constraints in comments
        if re.search(r'async.*await|asyncio', content, re.IGNORECASE):
            constraints.append(Constraint(
                id=f"tech-async-{file_path.name.replace('.', '-').replace('/', '-')}",
                name=f"Async/await requirement in {file_path.name}",
                category="technical",
                description=f"File {file_path.name} contains async/await patterns indicating async requirement",
                severity="high",
                source=str(file_path)
            ))

        return constraints

    def analyze_architecture_constraints(self) -> List[Constraint]:
        """
        Analyze the project architecture to identify structural constraints

        Returns:
            List of architectural constraints found in the codebase
        """
        constraints = []
        src_dir = Path("D:/software_dev_project/DCAE/src")

        if src_dir.exists():
            # Identify directory structure constraints
            dirs = [d for d in src_dir.iterdir() if d.is_dir()]

            for directory in dirs:
                if directory.name in ['knowledge_fusion', 'product_knowledge', 'llm_management', 'discipline_control', 'testing_documentation', 'task_management']:
                    constraints.append(Constraint(
                        id=f"arch-dir-{directory.name}",
                        name=f"Architecture Directory: {directory.name}",
                        category="architectural",
                        description=f"Project follows {directory.name} directory structure pattern",
                        severity="medium",
                        source="codebase architecture analysis"
                    ))

            # Analyze main module structure
            main_modules = list(src_dir.glob("*.py"))
            for module in main_modules:
                constraints.append(Constraint(
                    id=f"arch-module-{module.stem}",
                    name=f"Core Module: {module.stem}",
                    category="architectural",
                    description=f"Project has core module {module.stem}.py as part of architecture",
                    severity="medium",
                    source="codebase architecture analysis"
                ))

        return constraints

    def analyze_technical_constraints(self) -> List[Constraint]:
        """
        Analyze technical constraints by examining implementation patterns

        Returns:
            List of technical constraints found in the codebase
        """
        constraints = []
        src_dir = Path("D:/software_dev_project/DCAE/src")

        if src_dir.exists():
            # Look for configuration patterns
            config_related_files = list(src_dir.rglob("*config*.py")) + list(src_dir.rglob("*setting*.py"))

            for config_file in config_related_files:
                constraints.append(Constraint(
                    id=f"tech-config-file-{config_file.stem}",
                    name=f"Configuration Pattern: {config_file.stem}",
                    category="technical",
                    description=f"Project uses {config_file.stem} for configuration management",
                    severity="medium",
                    source=str(config_file)
                ))

            # Look for testing patterns
            test_dir = Path("D:/software_dev_project/DCAE/tests")
            if test_dir.exists():
                constraints.append(Constraint(
                    id="tech-testing-framework",
                    name="Testing Framework Requirement",
                    category="technical",
                    description="Project requires comprehensive test suite in tests/ directory",
                    severity="high",
                    source="codebase structure"
                ))

        return constraints


def create_default_project_constraints() -> List[Constraint]:
    """
    Create a set of default project constraints based on the project context

    Returns:
        List of default project constraints
    """
    return [
        Constraint(
            id="tech-python-requirement",
            name="Python Version Requirement",
            category="technical",
            description="Project must use Python 3.11 or higher as specified in project context",
            severity="high",
            source="project-context.md"
        ),
        Constraint(
            id="tech-async-requirement",
            name="Async/Await Requirement",
            category="technical",
            description="Use asyncio for all async operations; prefer AsyncOpenAI for OpenAI interactions",
            severity="high",
            source="project-context.md"
        ),
        Constraint(
            id="security-no-hardcoded-keys",
            name="No Hardcoded Sensitive Information",
            category="security",
            description="Never hardcode API keys or sensitive information in source code",
            severity="critical",
            source="project-context.md"
        ),
        Constraint(
            id="coding-style-black-ruff",
            name="Code Formatting Requirement",
            category="development_process",
            description="Use black for code formatting and ruff for linting",
            severity="medium",
            source="project-context.md"
        ),
        Constraint(
            id="platform-windows-encoding",
            name="Windows Platform Compatibility",
            description="Handle Windows encoding properly using sys.stdout/stderr wrapper as shown in dcae.py lines 31-33",
            category="technical",
            severity="high",
            source="project-context.md"
        )
    ]


if __name__ == "__main__":
    # Example usage
    manager = ProjectConstraintsManager()

    # Add default constraints if none exist
    if not manager.constraints:
        default_constraints = create_default_project_constraints()
        for constraint in default_constraints:
            manager.add_constraint(constraint)

    print(f"Loaded {len(manager.constraints)} constraints")
    print(f"Active constraints: {len(manager.get_active_constraints())}")

    # Catalog any existing constraints from documentation
    discovered = manager.catalog_existing_constraints()
    print(f"Discovered {len(discovered)} constraints from documentation")

    for constraint in discovered:
        print(f"- {constraint.name} ({constraint.category}): {constraint.description}")

    # Analyze codebase for technical constraints
    codebase_constraints = manager._extract_constraints_from_codebase()
    print(f"\nFound {len(codebase_constraints)} constraints from codebase analysis")

    # Analyze architecture constraints
    arch_constraints = manager.analyze_architecture_constraints()
    print(f"Found {len(arch_constraints)} architectural constraints")

    # Analyze technical constraints
    tech_constraints = manager.analyze_technical_constraints()
    print(f"Found {len(tech_constraints)} technical constraints")