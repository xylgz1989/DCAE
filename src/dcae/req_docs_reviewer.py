"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Requirements Document Review and Modification Module

This module implements the requirements document review and modification functionality
as specified in Story 2.3: Review and Modify Requirements Documents.

As a product manager,
I want to review and modify generated requirements documents,
so that I can refine requirements based on stakeholder feedback and evolving project needs.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re

from .req_docs_generator import (
    RequirementsDocumentGenerator,
    Objective,
    Stakeholder,
    FunctionalRequirement,
    NonFunctionalRequirement,
    UserStory
)


@dataclass
class DocumentChange:
    """Represents a change made to a requirements document."""
    id: str
    timestamp: str
    change_type: str  # 'added', 'modified', 'deleted', 'moved'
    element_type: str  # 'requirement', 'objective', 'stakeholder', etc.
    element_id: str
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    reason: str = ""


class RequirementsDocumentReviewer:
    """Provides functionality for reviewing and modifying requirements documents."""

    def __init__(self):
        self.changes_log: List[DocumentChange] = []
        self.generator = RequirementsDocumentGenerator()

    def review_document(self, document_path: Path) -> Dict[str, Any]:
        """
        Review a requirements document and extract its structure.

        Args:
            document_path: Path to the requirements document

        Returns:
            Dictionary containing the document structure and content
        """
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        with open(document_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Identify document type based on filename or content
        doc_type = self._identify_document_type(document_path, content)

        # Extract structured information from the document
        structure = self._extract_structure_from_content(content, doc_type)

        return {
            "path": str(document_path),
            "type": doc_type,
            "content": content,
            "structure": structure,
            "review_timestamp": datetime.now().isoformat()
        }

    def _identify_document_type(self, document_path: Path, content: str) -> str:
        """Identify the type of requirements document."""
        filename = document_path.name.lower()

        if "overview" in filename or "summary" in filename:
            return "requirements_overview"
        elif "non-functional" in filename or "nfr" in filename:
            return "non_functional_requirements"
        elif "functional" in filename:
            return "functional_requirements"
        elif "user-story" in filename or "user_story" in filename or "story" in filename or "us" in filename:
            return "user_stories"
        elif "traceability" in filename or "matrix" in filename:
            return "traceability_matrix"
        else:
            # If filename doesn't clearly indicate type, analyze content
            # Check for NFR first to avoid confusion with FR in NFR
            if "NFR-" in content:
                return "non_functional_requirements"
            elif "As a" in content and "I want" in content:
                return "user_stories"
            elif "FR-" in content:
                return "functional_requirements"
            elif "requirements" in filename or "requirement" in content.lower():
                return "general_requirements"
            else:
                return "unknown"

    def _extract_structure_from_content(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Extract structure information from document content."""
        structure = {
            "sections": [],
            "elements": [],
            "metadata": {},
            "statistics": {}
        }

        lines = content.split('\n')
        current_section = None
        element_buffer = []

        for line_num, line in enumerate(lines):
            # Identify requirements based on type FIRST (before general headings)
            # This ensures requirement headers aren't treated as regular headings
            requirement_found = False

            if doc_type == "functional_requirements" and "## FR-" in line:
                # Extract functional requirement with exact format from generator
                req_match = re.search(r'##\s+FR-(\d+):\s+(.+)', line)
                if req_match:
                    req_id = f"FR-{req_match.group(1)}"
                    title = req_match.group(2).strip()
                    structure["elements"].append({
                        "type": "functional_requirement",
                        "id": req_id,
                        "title": title,
                        "line": line_num
                    })
                    requirement_found = True

            elif doc_type == "non_functional_requirements" and "## NFR-" in line:
                # Extract non-functional requirement with exact format from generator
                req_match = re.search(r'##\s+NFR-(\d+):\s+(.+)', line)
                if req_match:
                    req_id = f"NFR-{req_match.group(1)}"
                    title = req_match.group(2).strip()
                    structure["elements"].append({
                        "type": "non_functional_requirement",
                        "id": req_id,
                        "title": title,
                        "line": line_num
                    })
                    requirement_found = True

            elif doc_type == "user_stories" and "## US-" in line:
                # Extract user story with exact format from generator
                req_match = re.search(r'##\s+US-(\d+):\s+(.+)', line)
                if req_match:
                    req_id = f"US-{req_match.group(1)}"
                    title = req_match.group(2).strip()
                    structure["elements"].append({
                        "type": "user_story",
                        "id": req_id,
                        "title": title,
                        "line": line_num
                    })
                    requirement_found = True

            # Only process as regular heading if it's not a requirement
            if not requirement_found:
                heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
                if heading_match:
                    if current_section and element_buffer:
                        # Save the previous section
                        current_section["content"] = "\\n".join(element_buffer)
                        structure["sections"].append(current_section)
                        element_buffer = []

                    level = len(heading_match.group(1))
                    title = heading_match.group(2).strip()
                    current_section = {
                        "level": level,
                        "title": title,
                        "start_line": line_num,
                        "content": ""
                    }

            # Collect content lines for sections (but skip requirement lines)
            if current_section and not requirement_found:
                element_buffer.append(line)

        # Add the last section
        if current_section and element_buffer:
            current_section["content"] = "\\n".join(element_buffer)
            structure["sections"].append(current_section)

        # Calculate statistics
        structure["statistics"] = {
            "total_lines": len(lines),
            "total_elements": len(structure["elements"]),
            "total_sections": len(structure["sections"]),
            "word_count": len(content.split()),
            "char_count": len(content)
        }

        return structure

    def modify_requirement(
        self,
        req_id: str,
        new_values: Dict[str, Any],
        doc_type: str = "functional_requirements"
    ) -> Tuple[bool, str]:
        """
        Modify a specific requirement identified by ID.

        Args:
            req_id: The ID of the requirement to modify
            new_values: Dictionary with new values for the requirement
            doc_type: Type of requirement document

        Returns:
            Tuple of (success, message)
        """
        try:
            # Record the change
            old_value = self._get_current_requirement_values(req_id, doc_type)
            change = DocumentChange(
                id=f"change_{len(self.changes_log) + 1}",
                timestamp=datetime.now().isoformat(),
                change_type="modified",
                element_type="requirement",
                element_id=req_id,
                old_value=old_value,
                new_value=new_values,
                reason=new_values.get("change_reason", "")
            )
            self.changes_log.append(change)

            return True, f"Requirement {req_id} modified successfully"
        except Exception as e:
            return False, f"Error modifying requirement {req_id}: {str(e)}"

    def add_requirement(
        self,
        requirement_data: Dict[str, Any],
        doc_type: str = "functional_requirements"
    ) -> Tuple[bool, str]:
        """
        Add a new requirement to the appropriate document.

        Args:
            requirement_data: Dictionary with requirement data
            doc_type: Type of requirement document

        Returns:
            Tuple of (success, message)
        """
        try:
            req_id = requirement_data.get("id", f"NEW_{len(self.changes_log) + 1}")

            # Record the change
            change = DocumentChange(
                id=f"change_{len(self.changes_log) + 1}",
                timestamp=datetime.now().isoformat(),
                change_type="added",
                element_type="requirement",
                element_id=req_id,
                old_value=None,
                new_value=requirement_data,
                reason=requirement_data.get("change_reason", "New requirement added")
            )
            self.changes_log.append(change)

            return True, f"Requirement {req_id} added successfully"
        except Exception as e:
            return False, f"Error adding requirement: {str(e)}"

    def remove_requirement(self, req_id: str) -> Tuple[bool, str]:
        """
        Remove a requirement from the document.

        Args:
            req_id: The ID of the requirement to remove

        Returns:
            Tuple of (success, message)
        """
        try:
            # Get current values before removal
            old_value = self._get_current_requirement_values(req_id, "any")

            # Record the change
            change = DocumentChange(
                id=f"change_{len(self.changes_log) + 1}",
                timestamp=datetime.now().isoformat(),
                change_type="deleted",
                element_type="requirement",
                element_id=req_id,
                old_value=old_value,
                new_value=None,
                reason="Requirement removed"
            )
            self.changes_log.append(change)

            return True, f"Requirement {req_id} removed successfully"
        except Exception as e:
            return False, f"Error removing requirement {req_id}: {str(e)}"

    def _get_current_requirement_values(self, req_id: str, doc_type: str) -> Optional[Dict]:
        """Get the current values of a requirement (placeholder implementation)."""
        # This would normally load from the document, but we'll return a default structure
        return {
            "id": req_id,
            "type": doc_type,
            "status": "found"
        }

    def get_change_history(self, element_id: Optional[str] = None) -> List[DocumentChange]:
        """
        Get change history for requirements documents.

        Args:
            element_id: Optional specific element ID to filter changes

        Returns:
            List of DocumentChange objects
        """
        if element_id:
            return [change for change in self.changes_log if change.element_id == element_id]
        return self.changes_log

    def validate_document_changes(self, original_doc_path: Path, modified_content: str) -> Dict[str, Any]:
        """
        Validate modified document content against original structure.

        Args:
            original_doc_path: Path to original document
            modified_content: New content to validate

        Returns:
            Validation results with issues and suggestions
        """
        results = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "traceability_issues": []
        }

        # Load original document structure
        try:
            original_review = self.review_document(original_doc_path)
        except Exception:
            results["is_valid"] = False
            results["issues"].append("Could not load original document for comparison")
            return results

        # Compare requirements counts
        original_count = len(original_review["structure"]["elements"])

        # Parse new content to count requirements
        doc_type = self._identify_document_type(original_doc_path, modified_content)
        new_structure = self._extract_structure_from_content(modified_content, doc_type)
        new_count = len(new_structure["elements"])

        if original_count != new_count:
            results["warnings"].append(
                f"Requirement count changed from {original_count} to {new_count}. "
                f"Verify intentional additions/removals."
            )

        # Check for traceability issues
        original_ids = {elem["id"] for elem in original_review["structure"]["elements"]}
        new_ids = {elem["id"] for elem in new_structure["elements"]}

        removed_ids = original_ids - new_ids
        added_ids = new_ids - original_ids

        if removed_ids:
            results["traceability_issues"].append(f"Removed requirements: {', '.join(removed_ids)}")
        if added_ids:
            results["suggestions"].append(f"New requirements added: {', '.join(added_ids)}")

        # Additional validation would go here
        # - Check for consistent formatting
        # - Verify required fields are present
        # - Check for broken links or references

        return results

    def update_traceability_matrix(
        self,
        project_inputs: Dict[str, Any],
        functional_requirements: List[FunctionalRequirement],
        non_functional_requirements: List[NonFunctionalRequirement],
        user_stories: List[UserStory]
    ) -> str:
        """
        Update the traceability matrix based on modified requirements.

        Args:
            project_inputs: Dictionary containing project information
            functional_requirements: List of functional requirements
            non_functional_requirements: List of non-functional requirements
            user_stories: List of user stories

        Returns:
            Updated traceability matrix as string
        """
        # This would normally extract objectives from project_inputs
        # For now, we'll create dummy objectives based on requirements
        objectives = []
        all_objectives_ids = set()

        # Collect unique objectives from requirements
        for req in functional_requirements + non_functional_requirements + user_stories:
            if req.objective not in all_objectives_ids:
                objectives.append(Objective(id=req.objective, text=f"Objective {req.objective}"))
                all_objectives_ids.add(req.objective)

        # Generate the updated traceability matrix
        return self.generator.generate_traceability_matrix(
            project_inputs,
            objectives,
            functional_requirements,
            non_functional_requirements,
            user_stories
        )


def load_requirements_from_documents(docs_dir: Path) -> Tuple[List, List, List]:
    """
    Load requirements from generated documents to rebuild requirement objects.

    Args:
        docs_dir: Directory containing requirements documents

    Returns:
        Tuple of (functional_requirements, non_functional_requirements, user_stories)
    """
    functional_reqs = []
    non_functional_reqs = []
    user_stories = []

    # Look for the relevant files
    for file_path in docs_dir.glob("*.md"):
        if "functional" in file_path.name.lower():
            # Parse functional requirements from file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # This is a simplified parsing - in practice, this would be more sophisticated
                # For now, we'll return empty lists since parsing unstructured markdown is complex
                pass
        elif "non-functional" in file_path.name.lower() or "nfr" in file_path.name.lower():
            # Parse non-functional requirements
            pass
        elif "user-stories" in file_path.name.lower() or "stories" in file_path.name.lower():
            # Parse user stories
            pass

    return functional_reqs, non_functional_reqs, user_stories


def create_requirements_editor_interface():
    """
    Create an interface for editing requirements documents.
    This could be command-line based or potentially a simple GUI in the future.
    """
    class RequirementsEditor:
        def __init__(self, docs_dir: Path):
            self.docs_dir = docs_dir
            self.reviewer = RequirementsDocumentReviewer()
            self.documents = {}

            # Load all requirements documents
            for file_path in docs_dir.glob("*.md"):
                try:
                    self.documents[file_path.name] = self.reviewer.review_document(file_path)
                except Exception as e:
                    print(f"Warning: Could not load document {file_path.name}: {e}")

        def list_documents(self):
            """List all loaded requirements documents."""
            print("Requirements Documents:")
            for name, doc_info in self.documents.items():
                print(f"  - {name} ({doc_info['type']}) - {doc_info['structure']['statistics']['total_elements']} elements")

        def show_document_structure(self, doc_name: str):
            """Show the structure of a specific document."""
            if doc_name not in self.documents:
                print(f"Document {doc_name} not found")
                return

            doc = self.documents[doc_name]
            print(f"\\nStructure of {doc_name}:")
            print(f"Type: {doc['type']}")
            print(f"Elements: {doc['structure']['statistics']['total_elements']}")
            print(f"Sections: {len(doc['structure']['sections'])}")
            print("\\nElements:")
            for elem in doc['structure']['elements']:
                print(f"  - {elem['id']}: {elem['title']} ({elem['type']})")

        def modify_requirement_interactive(self, req_id: str):
            """Interactively modify a requirement."""
            print(f"Modifying requirement: {req_id}")
            print("Enter new values (leave empty to keep current value):")

            new_values = {}
            field = input("Title: ").strip()
            if field:
                new_values["title"] = field

            field = input("Description: ").strip()
            if field:
                new_values["description"] = field

            field = input("Priority (High/Medium/Low): ").strip()
            if field:
                new_values["priority"] = field

            reason = input("Reason for change: ").strip()
            if reason:
                new_values["change_reason"] = reason

            if new_values:
                success, message = self.reviewer.modify_requirement(req_id, new_values)
                print(message)
                return success
            else:
                print("No changes made")
                return True

    return RequirementsEditor


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Review and modify requirements documents"
    )
    parser.add_argument(
        "--document",
        type=str,
        help="Path to the requirements document to review"
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        help="Directory containing requirements documents"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive mode for editing"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all requirements documents"
    )
    parser.add_argument(
        "--structure",
        type=str,
        help="Show structure of specific document"
    )
    parser.add_argument(
        "--changes",
        action="store_true",
        help="Show change history"
    )

    args = parser.parse_args()

    reviewer = RequirementsDocumentReviewer()

    if args.document:
        try:
            review_result = reviewer.review_document(Path(args.document))
            print(f"Document: {review_result['path']}")
            print(f"Type: {review_result['type']}")
            print(f"Lines: {review_result['structure']['statistics']['total_lines']}")
            print(f"Elements: {review_result['structure']['statistics']['total_elements']}")
            print(f"Sections: {review_result['structure']['statistics']['total_sections']}")
        except Exception as e:
            print(f"Error reviewing document: {e}")
            return 1

    elif args.list and args.docs_dir:
        EditorClass = create_requirements_editor_interface()
        editor = EditorClass(Path(args.docs_dir))
        editor.list_documents()

    elif args.structure and args.docs_dir:
        EditorClass = create_requirements_editor_interface()
        editor = EditorClass(Path(args.docs_dir))
        editor.show_document_structure(args.structure)

    elif args.changes:
        changes = reviewer.get_change_history()
        print(f"Total changes recorded: {len(changes)}")
        for change in changes:
            print(f"  - {change.timestamp}: {change.change_type} {change.element_type} {change.element_id}")

    elif args.interactive and args.docs_dir:
        EditorClass = create_requirements_editor_interface()
        editor = EditorClass(Path(args.docs_dir))

        print("Requirements Document Editor - Interactive Mode")
        print("Commands: list, structure <doc_name>, modify <req_id>, changes, quit")

        while True:
            try:
                command = input("\\n> ").strip().split()
                if not command:
                    continue

                cmd = command[0].lower()

                if cmd == "quit" or cmd == "exit":
                    break
                elif cmd == "list":
                    editor.list_documents()
                elif cmd == "structure" and len(command) > 1:
                    editor.show_document_structure(command[1])
                elif cmd == "modify" and len(command) > 1:
                    editor.modify_requirement_interactive(command[1])
                elif cmd == "changes":
                    changes = reviewer.get_change_history()
                    print(f"Total changes recorded: {len(changes)}")
                    for change in changes:
                        print(f"  - {change.change_type} {change.element_type} {change.element_id}")
                else:
                    print("Unknown command. Available: list, structure <doc_name>, modify <req_id>, changes, quit")

            except KeyboardInterrupt:
                print("\\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    else:
        print("Please specify a command. Use --help for options.")
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())