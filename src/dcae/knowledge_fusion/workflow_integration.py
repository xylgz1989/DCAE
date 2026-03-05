"""
Development Workflow Integration for Constraints

This module integrates constraint awareness into the development workflow,
providing tools to enforce constraints at key points in the development process.
"""

from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import subprocess
import sys
from enum import Enum
from .constraint_storage import ProjectConstraintStorage
from .constraint_validation import DevelopmentValidator, ValidationIssue
from .project_constraints_manager import ProjectConstraintsManager


class WorkflowStage(Enum):
    """Enumeration of development workflow stages where constraints apply"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    PRE_COMMIT = "pre_commit"
    PULL_REQUEST = "pull_request"
    BUILD = "build"
    TEST = "test"
    DEPLOY = "deploy"


class WorkflowIntegrator:
    """
    Integrates constraint awareness into the development workflow
    """

    def __init__(self, storage: ProjectConstraintStorage):
        self.storage = storage
        self.validator = DevelopmentValidator(storage)
        self.constraints_manager = ProjectConstraintsManager()

        # Stage-specific validation callbacks
        self.stage_callbacks: Dict[WorkflowStage, List[Callable]] = {
            WorkflowStage.CODE_GENERATION: [],
            WorkflowStage.CODE_REVIEW: [],
            WorkflowStage.PRE_COMMIT: [],
            WorkflowStage.PULL_REQUEST: [],
            WorkflowStage.BUILD: [],
            WorkflowStage.TEST: [],
            WorkflowStage.DEPLOY: [],
        }

    def register_callback(self, stage: WorkflowStage, callback: Callable):
        """
        Register a callback function to be executed at a specific workflow stage

        Args:
            stage: The workflow stage to register for
            callback: The function to call during this stage
        """
        self.stage_callbacks[stage].append(callback)

    def execute_stage(self, stage: WorkflowStage, context: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Execute validation for a specific workflow stage

        Args:
            stage: The workflow stage to execute
            context: Contextual information for the stage

        Returns:
            List of validation issues found during the stage
        """
        issues = []

        # Execute registered callbacks for this stage
        for callback in self.stage_callbacks[stage]:
            try:
                callback_issues = callback(context)
                if isinstance(callback_issues, list):
                    issues.extend(callback_issues)
            except Exception as e:
                issues.append(ValidationIssue(
                    constraint_id="callback-error",
                    constraint_name="Callback Execution Error",
                    severity="critical",
                    message=f"Error executing callback for {stage.value}: {str(e)}"
                ))

        # Execute default validation for the stage
        if stage == WorkflowStage.PRE_COMMIT:
            issues.extend(self.pre_commit_validation(context))
        elif stage == WorkflowStage.PULL_REQUEST:
            issues.extend(self.pull_request_validation(context))
        elif stage == WorkflowStage.CODE_GENERATION:
            issues.extend(self.code_generation_validation(context))
        elif stage == WorkflowStage.CODE_REVIEW:
            issues.extend(self.code_review_validation(context))

        return issues

    def pre_commit_validation(self, context: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Execute pre-commit validation

        Args:
            context: Context containing 'file_paths' key with list of files to validate

        Returns:
            List of validation issues found
        """
        file_paths = context.get('file_paths', [])
        if not file_paths:
            return []

        # Convert string paths to Path objects if needed
        path_objects = [Path(p) if isinstance(p, str) else p for p in file_paths]

        is_valid, issues = self.validator.pre_commit_validation(path_objects)

        return issues

    def pull_request_validation(self, context: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Execute pull request validation

        Args:
            context: Context containing 'file_paths' key with list of files in PR

        Returns:
            List of validation issues found
        """
        file_paths = context.get('file_paths', [])
        if not file_paths:
            return []

        # Convert string paths to Path objects if needed
        path_objects = [Path(p) if isinstance(p, str) else p for p in file_paths]

        pr_issues = self.validator.validate_pull_request(path_objects)
        all_issues = []
        for file_issues in pr_issues.values():
            all_issues.extend(file_issues)
        return all_issues

    def code_generation_validation(self, context: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Execute validation during code generation

        Args:
            context: Context containing 'generated_code' and 'file_path'

        Returns:
            List of validation issues found
        """
        generated_code = context.get('generated_code', '')
        file_path = context.get('file_path', 'unknown')

        if not generated_code or file_path == 'unknown':
            return []

        # Create a Path object for the file
        file_path_obj = Path(file_path) if isinstance(file_path, str) else file_path

        return self.validator.validator.validate_code_content(generated_code, file_path_obj)

    def code_review_validation(self, context: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Execute validation during code review

        Args:
            context: Context containing 'code_diff' or 'file_path'

        Returns:
            List of validation issues found
        """
        issues = []

        # Check for code diff if provided
        code_diff = context.get('code_diff', '')
        file_path = context.get('file_path', '')

        if code_diff:
            # For now, treat the diff as code content to validate
            # In practice, this would require more sophisticated diff analysis
            if file_path:
                file_path_obj = Path(file_path) if isinstance(file_path, str) else file_path
                issues.extend(self.validator.validator.validate_code_content(code_diff, file_path_obj))

        return issues

    def install_pre_commit_hook(self, project_root: Path) -> bool:
        """
        Install a Git pre-commit hook to validate constraints

        Args:
            project_root: Root directory of the Git repository

        Returns:
            True if installation was successful
        """
        hook_content = '''#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

# Add the project root to the Python path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.dcae.knowledge_fusion.workflow_integration import WorkflowIntegrator
    from src.dcae.knowledge_fusion.constraint_storage import ProjectConstraintStorage

    # Initialize the workflow integrator
    storage = ProjectConstraintStorage()
    integrator = WorkflowIntegrator(storage)

    # Get the files staged for commit
    result = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                          capture_output=True, text=True, cwd=project_root)
    file_paths = [project_root / line.strip() for line in result.stdout.split('\\n') if line.strip() and line.strip().endswith('.py')]

    if file_paths:
        issues = integrator.execute_stage("pre_commit", {"file_paths": file_paths})

        critical_issues = [issue for issue in issues if issue.severity.lower() in ["critical", "high"]]

        if critical_issues:
            print(f"\\n❌ Pre-commit validation failed with {len(critical_issues)} critical or high severity issues:")
            for issue in critical_issues[:10]:  # Show first 10 issues
                print(f"  - {issue}")

            if len(critical_issues) > 10:
                print(f"  ... and {len(critical_issues) - 10} more issues")

            sys.exit(1)
        else:
            print(f"✅ Pre-commit validation passed for {len(file_paths)} files")

except ImportError as e:
    print(f"Error importing constraint validation: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error during pre-commit validation: {e}")
    sys.exit(1)

sys.exit(0)
'''

        # Path for the Git hooks directory
        hooks_dir = project_root / '.git' / 'hooks'
        pre_commit_hook_path = hooks_dir / 'pre-commit'

        try:
            # Create hooks directory if it doesn't exist
            hooks_dir.mkdir(parents=True, exist_ok=True)

            # Write the hook script
            with open(pre_commit_hook_path, 'w') as f:
                f.write(hook_content)

            # Make the script executable
            import stat
            current_permissions = os.stat(pre_commit_hook_path).st_mode
            os.chmod(pre_commit_hook_path, current_permissions | stat.S_IEXEC)

            print(f"Pre-commit hook installed at {pre_commit_hook_path}")
            return True

        except Exception as e:
            print(f"Failed to install pre-commit hook: {e}")
            return False

    def add_constraint_to_workflow(self, constraint: str, severity: str = "medium",
                                  description: str = "", category: str = "development_process") -> bool:
        """
        Add a constraint to the workflow system

        Args:
            constraint: The constraint text or ID
            severity: The severity level
            description: Description of the constraint
            category: Category of the constraint

        Returns:
            True if constraint was added successfully
        """
        # Create a new constraint
        from .constraint_storage import Constraint
        from datetime import datetime

        new_constraint = Constraint(
            id=f"workflow-{category.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=constraint,
            category=category,
            description=description or f"Constraint: {constraint}",
            severity=severity
        )

        return self.storage.save_constraint(new_constraint)

    def generate_workflow_documentation(self) -> str:
        """
        Generate documentation for the constraint-aware workflow

        Returns:
            Documentation string
        """
        doc_parts = [
            "# Constraint-Aware Development Workflow",
            "",
            "This project implements constraint awareness at key points in the development process.",
            "",
            "## Workflow Stages",
            "",
            "### Code Generation",
            "Constraints are validated when generating new code to ensure compliance from the start.",
            "",
            "### Code Review",
            "Constraints are checked during code review to catch violations early.",
            "",
            "### Pre-Commit Hook",
            "Before committing code, all changed files are validated against project constraints.",
            "If critical or high-severity issues are found, the commit will be rejected.",
            "",
            "### Pull Request",
            "Pull requests are validated against all relevant constraints before merging.",
            "",
            "## Constraint Categories",
            "",
            "Constraints are categorized to enable targeted validation:",
            "- Technical: Language, framework, and platform requirements",
            "- Security: Protection against vulnerabilities and exposure of sensitive information",
            "- Performance: Resource usage and efficiency considerations",
            "- Coding Standards: Style, naming, and structural requirements",
            "- Process: Development workflow and methodology requirements",
            "",
            "## Enforcement",
            "",
            "Constraint violations are classified by severity:",
            "- Critical: Would cause system failure or security breach",
            "- High: Significant impact on functionality or maintainability",
            "- Medium: Noticeable impact on code quality or performance",
            "- Low: Minor deviations from best practices",
            "",
            "Critical and high severity violations block code commits and pull requests.",
        ]

        return "\n".join(doc_parts)


class DCAEConstraintIntegration:
    """
    Specialized integration for the DCAE (Distributed Coding Agent Environment) project
    """

    def __init__(self):
        self.storage = ProjectConstraintStorage()
        self.integrator = WorkflowIntegrator(self.storage)

        # Register default callbacks for DCAE-specific workflows
        self._register_dcae_callbacks()

    def _register_dcae_callbacks(self):
        """Register default callbacks for DCAE workflows"""

        def dcae_code_generation_callback(context):
            """Validate constraints during DCAE code generation"""
            issues = []
            if 'generated_code' in context:
                # Check for common DCAE-specific issues
                code = context['generated_code']

                # Example: Ensure proper async usage
                if 'async def' in code and 'asyncio' not in code:
                    issues.append(ValidationIssue(
                        constraint_id="dcae-async-usage",
                        constraint_name="Async Usage Constraint",
                        severity="medium",
                        message="Async function defined but no asyncio usage detected",
                        file_path=context.get('file_path', 'unknown')
                    ))

            return issues

        def dcae_review_callback(context):
            """Validate constraints during DCAE code review"""
            issues = []

            # Add DCAE-specific review checks here
            return issues

        # Register the callbacks
        self.integrator.register_callback(WorkflowStage.CODE_GENERATION, dcae_code_generation_callback)
        self.integrator.register_callback(WorkflowStage.CODE_REVIEW, dcae_review_callback)

    def validate_agent_output(self, code_output: str, file_path: str = "unknown") -> List[ValidationIssue]:
        """
        Validate output from a coding agent against project constraints

        Args:
            code_output: The code generated by an agent
            file_path: Path where the code will be saved

        Returns:
            List of validation issues found
        """
        context = {
            'generated_code': code_output,
            'file_path': file_path
        }

        return self.integrator.execute_stage(WorkflowStage.CODE_GENERATION, context)

    def install_integration(self, project_root: Path) -> bool:
        """
        Install the constraint integration into a project

        Args:
            project_root: Root directory of the project

        Returns:
            True if installation was successful
        """
        # Install the pre-commit hook
        success = self.integrator.install_pre_commit_hook(project_root)

        if success:
            print("Constraint-aware workflow successfully installed.")
            print("\nTo complete the integration:")
            print("1. Review the generated constraints to ensure they match your project requirements")
            print("2. Customize severity levels as needed")
            print("3. Add project-specific constraints using add_constraint_to_workflow()")

        return success


def initialize_constraint_workflow(project_root: Path) -> DCAEConstraintIntegration:
    """
    Initialize the constraint-aware workflow for a project

    Args:
            project_root: Root directory of the project

    Returns:
        DCAEConstraintIntegration instance
    """
    integration = DCAEConstraintIntegration()

    # Install the integration
    integration.install_integration(project_root)

    return integration


if __name__ == "__main__":
    # Example usage
    project_root = Path(__file__).parent.parent.parent  # Go to project root
    integration = DCAEConstraintIntegration()

    print("DCAE Constraint Integration initialized")
    print(f"Active constraints: {len(integration.storage.list_constraints())}")

    # Example: Validate some code
    sample_code = '''
async def example_function():
    return "Hello World"
'''

    issues = integration.validate_agent_output(sample_code, "test.py")
    print(f"\nFound {len(issues)} issues in sample code:")
    for issue in issues:
        print(f"  - {issue}")

    # Show documentation
    print("\n" + integration.integrator.generate_workflow_documentation())