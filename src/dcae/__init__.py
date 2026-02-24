"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Package initialization
"""

__version__ = "1.0.0"
__author__ = "DCAE Development Team"
__email__ = "dcae@example.com"

# Import main components
from .init import initialize_dcae_project
from .requirements import (
    create_requirements_template,
    load_requirements,
    save_requirements,
    validate_requirements,
    add_requirement,
    edit_requirement,
    input_requirements_interactively,
    print_requirements_summary
)
from .req_docs_generator import (
    generate_preliminary_requirements_documents,
    create_sample_project_inputs,
    RequirementsDocumentGenerator
)
from .req_docs_reviewer import (
    RequirementsDocumentReviewer,
    DocumentChange,
    create_requirements_editor_interface
)
from .cli import DCAECLI

__all__ = [
    "initialize_dcae_project",
    "create_requirements_template",
    "load_requirements",
    "save_requirements",
    "validate_requirements",
    "add_requirement",
    "edit_requirement",
    "input_requirements_interactively",
    "print_requirements_summary",
    "generate_preliminary_requirements_documents",
    "create_sample_project_inputs",
    "RequirementsDocumentGenerator",
    "RequirementsDocumentReviewer",
    "DocumentChange",
    "create_requirements_editor_interface",
    "DCAECLI",
    "__version__"
]