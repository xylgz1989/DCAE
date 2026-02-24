"""
Review and Quality Assurance - Modification Suggestions Module

This module implements the functionality for submitting and managing modification suggestions
based on review findings.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime
import re


class SuggestionStatus(Enum):
    """Enumeration for suggestion statuses."""
    SUBMITTED = "submitted"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    WONT_FIX = "wont_fix"


class SuggestionPriority(Enum):
    """Enumeration for suggestion priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SuggestionCategory(Enum):
    """Enumeration for suggestion categories."""
    CODE_IMPROVEMENT = "code_improvement"
    ARCHITECTURE_ADJUSTMENT = "architecture_adjustment"
    REQUIREMENTS_ALIGNMENT = "requirements_alignment"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    BUG_FIX = "bug_fix"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class ModificationSuggestion:
    """Represents a modification suggestion."""
    id: str
    title: str
    description: str
    category: SuggestionCategory
    priority: SuggestionPriority
    status: SuggestionStatus
    affected_files: List[str]
    proposed_solution: str
    implementation_complexity: str  # low, medium, high
    submitted_by: str
    submitted_date: str
    reviewed_by: Optional[str] = None
    reviewed_date: Optional[str] = None
    reason_rejected: Optional[str] = None
    implemented_by: Optional[str] = None
    implemented_date: Optional[str] = None
    associated_review_finding: Optional[str] = None  # ID of related review finding
    related_requirements: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None  # IDs of other suggestions this depends on


class SuggestionManager:
    """Manages the modification suggestions lifecycle."""

    def __init__(self, project_path: str):
        """
        Initialize the suggestion manager.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.suggestions_dir = self.project_path / ".dcae" / "suggestions"
        self.suggestions_file = self.suggestions_dir / "suggestions.json"

        # Ensure directories exist
        self.suggestions_dir.mkdir(parents=True, exist_ok=True)

        self.suggestions: List[ModificationSuggestion] = []
        self._load_suggestions()

    def _load_suggestions(self):
        """Load suggestions from storage."""
        if self.suggestions_file.exists():
            try:
                with open(self.suggestions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for item in data:
                    suggestion = ModificationSuggestion(
                        id=item['id'],
                        title=item['title'],
                        description=item['description'],
                        category=SuggestionCategory(item['category']),
                        priority=SuggestionPriority(item['priority']),
                        status=SuggestionStatus(item['status']),
                        affected_files=item['affected_files'],
                        proposed_solution=item['proposed_solution'],
                        implementation_complexity=item['implementation_complexity'],
                        submitted_by=item['submitted_by'],
                        submitted_date=item['submitted_date'],
                        reviewed_by=item.get('reviewed_by'),
                        reviewed_date=item.get('reviewed_date'),
                        reason_rejected=item.get('reason_rejected'),
                        implemented_by=item.get('implemented_by'),
                        implemented_date=item.get('implemented_date'),
                        associated_review_finding=item.get('associated_review_finding'),
                        related_requirements=item.get('related_requirements', []),
                        dependencies=item.get('dependencies', [])
                    )
                    self.suggestions.append(suggestion)
            except Exception as e:
                print(f"Warning: Could not load suggestions from file: {e}")
                self.suggestions = []

    def _save_suggestions(self):
        """Save suggestions to storage."""
        data = []
        for suggestion in self.suggestions:
            item = {
                'id': suggestion.id,
                'title': suggestion.title,
                'description': suggestion.description,
                'category': suggestion.category.value,
                'priority': suggestion.priority.value,
                'status': suggestion.status.value,
                'affected_files': suggestion.affected_files,
                'proposed_solution': suggestion.proposed_solution,
                'implementation_complexity': suggestion.implementation_complexity,
                'submitted_by': suggestion.submitted_by,
                'submitted_date': suggestion.submitted_date,
                'reviewed_by': suggestion.reviewed_by,
                'reviewed_date': suggestion.reviewed_date,
                'reason_rejected': suggestion.reason_rejected,
                'implemented_by': suggestion.implemented_by,
                'implemented_date': suggestion.implemented_date,
                'associated_review_finding': suggestion.associated_review_finding,
                'related_requirements': suggestion.related_requirements,
                'dependencies': suggestion.dependencies
            }
            data.append(item)

        with open(self.suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def submit_suggestion(self, title: str, description: str, category: SuggestionCategory,
                         priority: SuggestionPriority, affected_files: List[str],
                         proposed_solution: str, implementation_complexity: str,
                         submitted_by: str = "system",
                         associated_review_finding: Optional[str] = None,
                         related_requirements: Optional[List[str]] = None,
                         dependencies: Optional[List[str]] = None) -> str:
        """
        Submit a new modification suggestion.

        Args:
            title: Title of the suggestion
            description: Detailed description
            category: Category of the suggestion
            priority: Priority level
            affected_files: List of affected files
            proposed_solution: Proposed solution description
            implementation_complexity: Complexity estimate
            submitted_by: Who submitted the suggestion
            associated_review_finding: Related review finding ID
            related_requirements: Related requirement IDs
            dependencies: Dependent suggestion IDs

        Returns:
            ID of the created suggestion
        """
        suggestion_id = str(uuid.uuid4())

        suggestion = ModificationSuggestion(
            id=suggestion_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=SuggestionStatus.SUBMITTED,
            affected_files=affected_files,
            proposed_solution=proposed_solution,
            implementation_complexity=implementation_complexity,
            submitted_by=submitted_by,
            submitted_date=datetime.now().isoformat(),
            associated_review_finding=associated_review_finding,
            related_requirements=related_requirements or [],
            dependencies=dependencies or []
        )

        self.suggestions.append(suggestion)
        self._save_suggestions()

        print(f"Submitted suggestion: {suggestion_id} - {title}")
        return suggestion_id

    def update_suggestion_status(self, suggestion_id: str, status: SuggestionStatus,
                                 reviewed_by: Optional[str] = None,
                                 reason_rejected: Optional[str] = None) -> bool:
        """
        Update the status of a suggestion.

        Args:
            suggestion_id: ID of the suggestion to update
            status: New status
            reviewed_by: Who reviewed the suggestion
            reason_rejected: Reason for rejection (if applicable)

        Returns:
            True if successful, False otherwise
        """
        for suggestion in self.suggestions:
            if suggestion.id == suggestion_id:
                old_status = suggestion.status
                suggestion.status = status

                if status in [SuggestionStatus.IN_REVIEW, SuggestionStatus.ACCEPTED, SuggestionStatus.REJECTED]:
                    suggestion.reviewed_by = reviewed_by
                    suggestion.reviewed_date = datetime.now().isoformat()

                if status == SuggestionStatus.REJECTED:
                    suggestion.reason_rejected = reason_rejected

                self._save_suggestions()

                print(f"Updated suggestion {suggestion_id}: {old_status.value} -> {status.value}")
                return True

        print(f"Suggestion {suggestion_id} not found")
        return False

    def mark_as_implemented(self, suggestion_id: str, implemented_by: str) -> bool:
        """
        Mark a suggestion as implemented.

        Args:
            suggestion_id: ID of the suggestion to mark
            implemented_by: Who implemented the suggestion

        Returns:
            True if successful, False otherwise
        """
        for suggestion in self.suggestions:
            if suggestion.id == suggestion_id and suggestion.status == SuggestionStatus.ACCEPTED:
                suggestion.status = SuggestionStatus.IMPLEMENTED
                suggestion.implemented_by = implemented_by
                suggestion.implemented_date = datetime.now().isoformat()

                self._save_suggestions()

                print(f"Marked suggestion {suggestion_id} as implemented by {implemented_by}")
                return True
            elif suggestion.id == suggestion_id and suggestion.status != SuggestionStatus.ACCEPTED:
                print(f"Suggestion {suggestion_id} must be accepted before marking as implemented")
                return False

        print(f"Suggestion {suggestion_id} not found")
        return False

    def get_suggestion(self, suggestion_id: str) -> Optional[ModificationSuggestion]:
        """Get a specific suggestion by ID."""
        for suggestion in self.suggestions:
            if suggestion.id == suggestion_id:
                return suggestion
        return None

    def get_suggestions_by_status(self, status: SuggestionStatus) -> List[ModificationSuggestion]:
        """Get all suggestions with a specific status."""
        return [s for s in self.suggestions if s.status == status]

    def get_suggestions_by_priority(self, priority: SuggestionPriority) -> List[ModificationSuggestion]:
        """Get all suggestions with a specific priority."""
        return [s for s in self.suggestions if s.priority == priority]

    def get_suggestions_by_category(self, category: SuggestionCategory) -> List[ModificationSuggestion]:
        """Get all suggestions in a specific category."""
        return [s for s in self.suggestions if s.category == category]

    def get_suggestions_affecting_file(self, file_path: str) -> List[ModificationSuggestion]:
        """Get all suggestions that affect a specific file."""
        return [s for s in self.suggestions if file_path in s.affected_files]

    def get_all_suggestions(self) -> List[ModificationSuggestion]:
        """Get all suggestions."""
        return self.suggestions.copy()

    def get_suggestions_summary(self) -> Dict[str, Any]:
        """Get a summary of all suggestions."""
        summary = {
            "total_suggestions": len(self.suggestions),
            "by_status": {},
            "by_priority": {},
            "by_category": {}
        }

        # Count by status
        for suggestion in self.suggestions:
            status_val = suggestion.status.value
            summary["by_status"][status_val] = summary["by_status"].get(status_val, 0) + 1

            priority_val = suggestion.priority.value
            summary["by_priority"][priority_val] = summary["by_priority"].get(priority_val, 0) + 1

            category_val = suggestion.category.value
            summary["by_category"][category_val] = summary["by_category"].get(category_val, 0) + 1

        return summary


class ModificationSuggestionSubmitter:
    """Interface for submitting modification suggestions based on review findings."""

    def __init__(self, project_path: str):
        """
        Initialize the suggestion submitter.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.suggestion_manager = SuggestionManager(project_path)

    def submit_suggestion_from_finding(self, finding_id: str, finding_description: str,
                                      proposed_solution: str,
                                      priority_mapping: Optional[Dict[str, SuggestionPriority]] = None) -> str:
        """
        Submit a modification suggestion based on a review finding.

        Args:
            finding_id: ID of the associated review finding
            finding_description: Description of the issue found
            proposed_solution: Proposed solution
            priority_mapping: Mapping from finding severity to suggestion priority

        Returns:
            ID of the submitted suggestion
        """
        # Map the finding to appropriate category and priority
        if priority_mapping is None:
            # Default mapping based on common severity patterns
            if "critical" in finding_id.lower() or "critical" in finding_description.lower():
                priority = SuggestionPriority.CRITICAL
                category = SuggestionCategory.SECURITY if "security" in finding_description.lower() else SuggestionCategory.BUG_FIX
            elif "high" in finding_id.lower() or "high" in finding_description.lower():
                priority = SuggestionPriority.HIGH
                category = SuggestionCategory.BUG_FIX
            elif "medium" in finding_id.lower() or "medium" in finding_description.lower():
                priority = SuggestionPriority.MEDIUM
                category = SuggestionCategory.CODE_IMPROVEMENT
            else:
                priority = SuggestionPriority.LOW
                category = SuggestionCategory.CODE_IMPROVEMENT

        # Determine affected file from finding ID
        affected_file = finding_id.split(":")[0] if ":" in finding_id else "unknown"

        # Create a title from the finding
        title = f"Fix: {finding_description[:50]}..." if len(finding_description) > 50 else f"Fix: {finding_description}"

        # Submit the suggestion
        suggestion_id = self.suggestion_manager.submit_suggestion(
            title=title,
            description=finding_description,
            category=category,
            priority=priority,
            affected_files=[affected_file],
            proposed_solution=proposed_solution,
            implementation_complexity="medium",  # Default assumption
            submitted_by="review_system",
            associated_review_finding=finding_id
        )

        return suggestion_id

    def batch_submit_suggestions(self, findings_list: List[Dict[str, Any]],
                               priority_mapping: Optional[Dict[str, SuggestionPriority]] = None) -> List[str]:
        """
        Submit multiple suggestions from a list of review findings.

        Args:
            findings_list: List of findings dictionaries
            priority_mapping: Priority mapping to use

        Returns:
            List of submitted suggestion IDs
        """
        suggestion_ids = []
        for finding in findings_list:
            if 'id' in finding and 'issue_description' in finding:
                suggestion_id = self.submit_suggestion_from_finding(
                    finding_id=finding['id'],
                    finding_description=finding['issue_description'],
                    proposed_solution=finding.get('recommendation', 'No specific solution provided'),
                    priority_mapping=priority_mapping
                )
                suggestion_ids.append(suggestion_id)

        print(f"Batch submitted {len(suggestion_ids)} suggestions from findings")
        return suggestion_ids

    def create_manual_suggestion(self, title: str, description: str, category: SuggestionCategory,
                                priority: SuggestionPriority, affected_files: List[str],
                                proposed_solution: str, implementation_complexity: str = "medium") -> str:
        """
        Create a manual suggestion not tied to a review finding.

        Args:
            title: Title of the suggestion
            description: Detailed description
            category: Category of the suggestion
            priority: Priority level
            affected_files: List of affected files
            proposed_solution: Proposed solution description
            implementation_complexity: Estimated complexity

        Returns:
            ID of the submitted suggestion
        """
        suggestion_id = self.suggestion_manager.submit_suggestion(
            title=title,
            description=description,
            category=category,
            priority=priority,
            affected_files=affected_files,
            proposed_solution=proposed_solution,
            implementation_complexity=implementation_complexity,
            submitted_by="manual"
        )

        print(f"Created manual suggestion: {suggestion_id}")
        return suggestion_id

    def list_suggestions_with_filters(self, status: Optional[SuggestionStatus] = None,
                                     priority: Optional[SuggestionPriority] = None,
                                     category: Optional[SuggestionCategory] = None) -> List[ModificationSuggestion]:
        """
        List suggestions with optional filters.

        Args:
            status: Filter by status
            priority: Filter by priority
            category: Filter by category

        Returns:
            List of matching suggestions
        """
        suggestions = self.suggestion_manager.get_all_suggestions()

        if status:
            suggestions = [s for s in suggestions if s.status == status]
        if priority:
            suggestions = [s for s in suggestions if s.priority == priority]
        if category:
            suggestions = [s for s in suggestions if s.category == category]

        return suggestions

    def print_suggestions_summary(self):
        """Print a summary of all suggestions."""
        summary = self.suggestion_manager.get_suggestions_summary()

        print("\n" + "="*60)
        print("SUGGESTIONS SUMMARY")
        print("="*60)
        print(f"Total Suggestions: {summary['total_suggestions']}")

        print("\nBy Status:")
        for status, count in summary["by_status"].items():
            print(f"  {status.replace('_', ' ').title()}: {count}")

        print("\nBy Priority:")
        for priority, count in summary["by_priority"].items():
            print(f"  {priority.replace('_', ' ').title()}: {count}")

        print("\nBy Category:")
        for category, count in summary["by_category"].items():
            print(f"  {category.replace('_', ' ').title()}: {count}")

        print("="*60)


def main():
    """Example usage of the modification suggestion system."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Initialize the suggestion submitter
        submitter = ModificationSuggestionSubmitter(str(project_path))

        print("DCAE Review & Quality Assurance - Modification Suggestions")
        print("="*60)

        # Submit some sample suggestions
        suggestion1 = submitter.create_manual_suggestion(
            title="Improve Password Validation",
            description="The current password validation is too weak and should include complexity requirements.",
            category=SuggestionCategory.SECURITY,
            priority=SuggestionPriority.HIGH,
            affected_files=["src/auth.py", "src/models/user.py"],
            proposed_solution="Add complexity validation using a password strength library",
            implementation_complexity="medium"
        )

        suggestion2 = submitter.create_manual_suggestion(
            title="Add Error Handling",
            description="Missing error handling in API endpoints could cause crashes.",
            category=SuggestionCategory.BUG_FIX,
            priority=SuggestionPriority.HIGH,
            affected_files=["src/api/handlers.py"],
            proposed_solution="Wrap API calls in try-catch blocks with proper error responses",
            implementation_complexity="low"
        )

        # Simulate submitting suggestions from review findings
        findings = [
            {
                "id": "security_hardcoded_password_main.py:10",
                "issue_description": "Hardcoded password found in configuration",
                "recommendation": "Move credentials to environment variables"
            },
            {
                "id": "performance_nested_loops_calc.py:25",
                "issue_description": "Nested loops causing O(n^2) complexity",
                "recommendation": "Use a hash map to reduce complexity to O(n)"
            }
        ]

        finding_suggestions = submitter.batch_submit_suggestions(findings)

        # Print summary
        submitter.print_suggestions_summary()

        # List all high priority suggestions
        print("\nHigh Priority Suggestions:")
        high_priority = submitter.list_suggestions_with_filters(
            priority=SuggestionPriority.HIGH
        )
        for suggestion in high_priority:
            print(f"  - {suggestion.title} ({suggestion.status.value})")

        # Update status of a suggestion
        print(f"\nUpdating suggestion {suggestion1} status to ACCEPTED...")
        submitter.suggestion_manager.update_suggestion_status(
            suggestion1, SuggestionStatus.ACCEPTED, reviewed_by="admin"
        )

        # Mark a suggestion as implemented
        print(f"\nMarking suggestion {suggestion2} as implemented...")
        submitter.suggestion_manager.mark_as_implemented(suggestion2, "developer1")

        print("\nFinal suggestions summary after updates:")
        submitter.print_suggestions_summary()

        print(f"\nModification suggestions system demonstrated successfully.")
        print(f"Suggestions are stored in: {project_path}/.dcae/suggestions/")


if __name__ == "__main__":
    main()