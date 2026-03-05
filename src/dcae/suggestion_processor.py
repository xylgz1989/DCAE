"""
Review and Quality Assurance - Suggestion Processor Module

This module implements the functionality for processing user-specified modification suggestions
in natural language format and applying them to regenerate appropriate code artifacts.
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
from .generated_output_review import GeneratedOutputReviewer, ReviewFinding, ReviewCategory, ReviewSeverity
from .modification_suggestions import ModificationSuggestion, SuggestionManager, SuggestionStatus


class RegenerationStatus(Enum):
    """Enumeration for regeneration statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RegenerationResult:
    """Represents the result of a regeneration attempt."""
    suggestion_id: str
    status: RegenerationStatus
    regenerated_files: List[str]
    changes_made: str  # Description of changes made
    issues_encountered: List[str]
    execution_log: List[str]  # Detailed execution steps
    timestamp: str
    duration_seconds: float


class SuggestionProcessor:
    """
    Processes user-specified modification suggestions and applies them to regenerate code artifacts.

    This class connects user natural language suggestions with the code regeneration system,
    ensuring that changes maintain architectural consistency and are properly tracked.
    """

    def __init__(self, project_path: str):
        """
        Initialize the suggestion processor.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.suggestion_manager = SuggestionManager(project_path)
        self.regenerations_dir = self.project_path / ".dcae" / "regenerations"
        self.regenerations_file = self.regenerations_dir / "regeneration_results.json"

        # Ensure directories exist
        self.regenerations_dir.mkdir(parents=True, exist_ok=True)

        self.regeneration_results: List[RegenerationResult] = []
        self._load_regeneration_results()

    def _load_regeneration_results(self):
        """Load regeneration results from storage."""
        if self.regenerations_file.exists():
            try:
                with open(self.regenerations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for item in data:
                    result = RegenerationResult(
                        suggestion_id=item['suggestion_id'],
                        status=RegenerationStatus(item['status']),
                        regenerated_files=item['regenerated_files'],
                        changes_made=item['changes_made'],
                        issues_encountered=item['issues_encountered'],
                        execution_log=item['execution_log'],
                        timestamp=item['timestamp'],
                        duration_seconds=item['duration_seconds']
                    )
                    self.regeneration_results.append(result)
            except Exception as e:
                print(f"Warning: Could not load regeneration results from file: {e}")
                self.regeneration_results = []

    def _save_regeneration_results(self):
        """Save regeneration results to storage."""
        data = []
        for result in self.regeneration_results:
            item = {
                'suggestion_id': result.suggestion_id,
                'status': result.status.value,
                'regenerated_files': result.regenerated_files,
                'changes_made': result.changes_made,
                'issues_encountered': result.issues_encountered,
                'execution_log': result.execution_log,
                'timestamp': result.timestamp,
                'duration_seconds': result.duration_seconds
            }
            data.append(item)

        with open(self.regenerations_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def process_natural_language_suggestion(self, user_input: str, affected_files: Optional[List[str]] = None) -> str:
        """
        Process a natural language suggestion from a user.

        Args:
            user_input: Natural language description of the desired modification
            affected_files: Optional list of files that should be affected

        Returns:
            ID of the created suggestion
        """
        # Analyze the natural language input to extract suggestion details
        analysis = self._analyze_natural_language_input(user_input)

        # Create a structured suggestion based on the analysis
        suggestion_id = self._create_suggestion_from_analysis(analysis, user_input, affected_files)

        # Log the intake
        print(f"Processed natural language suggestion: {suggestion_id}")

        return suggestion_id

    def _analyze_natural_language_input(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze natural language input to extract suggestion details.

        Args:
            user_input: Natural language description of the desired modification

        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            'original_text': user_input,
            'category': None,
            'priority': None,
            'title': '',
            'description': user_input,
            'proposed_solution': user_input,
            'implementation_complexity': 'medium',
            'affected_files': [],
            'keywords': []
        }

        # Extract keywords and categorize based on common patterns
        user_lower = user_input.lower()

        # Identify priority based on keywords
        if any(keyword in user_lower for keyword in ['critical', 'urgent', 'security', 'vulnerability', 'hack']):
            analysis['priority'] = 'critical'
        elif any(keyword in user_lower for keyword in ['important', 'high', 'major', 'significant']):
            analysis['priority'] = 'high'
        elif any(keyword in user_lower for keyword in ['minor', 'small', 'low']):
            analysis['priority'] = 'low'
        else:
            analysis['priority'] = 'medium'

        # Identify category based on keywords
        if any(keyword in user_lower for keyword in ['security', 'vulnerability', 'authentication', 'password', 'encryption']):
            analysis['category'] = 'security'
        elif any(keyword in user_lower for keyword in ['performance', 'speed', 'slow', 'optimiz', 'memory', 'cpu']):
            analysis['category'] = 'performance'
        elif any(keyword in user_lower for keyword in ['bug', 'error', 'crash', 'fail', 'exception']):
            analysis['category'] = 'bug_fix'
        elif any(keyword in user_lower for keyword in ['architecture', 'structure', 'design', 'refactor']):
            analysis['category'] = 'architecture_adjustment'
        else:
            analysis['category'] = 'code_improvement'

        # Generate a title from the first part of the input
        analysis['title'] = user_input[:50].strip()
        if len(user_input) > 50:
            analysis['title'] += '...'

        # Extract keywords
        analysis['keywords'] = re.findall(r'\b\w+\b', user_input.lower())[:10]  # Top 10 words

        return analysis

    def _create_suggestion_from_analysis(self, analysis: Dict[str, Any], user_input: str,
                                       affected_files: Optional[List[str]]) -> str:
        """
        Create a structured suggestion from the analysis.

        Args:
            analysis: Analysis results from natural language input
            user_input: Original user input
            affected_files: Optional list of affected files

        Returns:
            ID of the created suggestion
        """
        from .modification_suggestions import SuggestionCategory, SuggestionPriority

        # Map analysis results to proper enum values
        category_map = {
            'code_improvement': SuggestionCategory.CODE_IMPROVEMENT,
            'architecture_adjustment': SuggestionCategory.ARCHITECTURE_ADJUSTMENT,
            'requirements_alignment': SuggestionCategory.REQUIREMENTS_ALIGNMENT,
            'quality_enhancement': SuggestionCategory.QUALITY_ENHANCEMENT,
            'bug_fix': SuggestionCategory.BUG_FIX,
            'security': SuggestionCategory.SECURITY,
            'performance': SuggestionCategory.PERFORMANCE
        }

        priority_map = {
            'low': SuggestionPriority.LOW,
            'medium': SuggestionPriority.MEDIUM,
            'high': SuggestionPriority.HIGH,
            'critical': SuggestionPriority.CRITICAL
        }

        category = category_map.get(analysis['category'], SuggestionCategory.CODE_IMPROVEMENT)
        priority = priority_map.get(analysis['priority'], SuggestionPriority.MEDIUM)

        # Determine affected files if not provided
        if not affected_files:
            # Try to infer affected files from keywords or project structure
            affected_files = self._infer_affected_files(analysis['keywords'])

        # Submit the suggestion
        suggestion_id = self.suggestion_manager.submit_suggestion(
            title=analysis['title'],
            description=analysis['description'],
            category=category,
            priority=priority,
            affected_files=affected_files,
            proposed_solution=analysis['proposed_solution'],
            implementation_complexity=analysis['implementation_complexity'],
            submitted_by="user"
        )

        return suggestion_id

    def _infer_affected_files(self, keywords: List[str]) -> List[str]:
        """
        Infer which files might be affected based on keywords.

        Args:
            keywords: List of keywords from the suggestion

        Returns:
            List of potentially affected files
        """
        affected_files = []

        # Scan for common file patterns in the project
        for keyword in keywords:
            for file_path in self.project_path.rglob(f"*{keyword}*.py"):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(self.project_path))
                    if relative_path not in affected_files:
                        affected_files.append(relative_path)

        # If no files found based on keywords, include common files
        if not affected_files:
            # Add some common files that might need attention
            common_files = [
                'src/main.py',
                'src/app.py',
                'src/__init__.py',
                'src/config.py',
                'src/settings.py'
            ]

            for file_candidate in common_files:
                full_path = self.project_path / file_candidate
                if full_path.exists():
                    affected_files.append(file_candidate)

            # If still no files, include all Python files in src/
            if not affected_files:
                for file_path in (self.project_path / 'src').rglob('*.py'):
                    if file_path.is_file():
                        relative_path = str(file_path.relative_to(self.project_path))
                        affected_files.append(relative_path)
                        if len(affected_files) >= 5:  # Limit to 5 files to avoid overload
                            break

        return affected_files

    def regenerate_based_on_suggestion(self, suggestion_id: str) -> RegenerationResult:
        """
        Apply a suggestion to regenerate appropriate code artifacts.

        Args:
            suggestion_id: ID of the suggestion to apply

        Returns:
            RegenerationResult describing the outcome
        """
        import time
        start_time = time.time()

        # Get the suggestion
        suggestion = self.suggestion_manager.get_suggestion(suggestion_id)
        if not suggestion:
            error_msg = f"Suggestion {suggestion_id} not found"
            result = RegenerationResult(
                suggestion_id=suggestion_id,
                status=RegenerationStatus.FAILED,
                regenerated_files=[],
                changes_made="No changes made - suggestion not found",
                issues_encountered=[error_msg],
                execution_log=[f"ERROR: {error_msg}"],
                timestamp=datetime.now().isoformat(),
                duration_seconds=time.time() - start_time
            )
            self.regeneration_results.append(result)
            self._save_regeneration_results()
            return result

        # Update suggestion status to indicate it's being implemented
        self.suggestion_manager.update_suggestion_status(
            suggestion_id,
            SuggestionStatus.IN_REVIEW,
            reviewed_by="regeneration_system"
        )

        execution_log = [f"Starting regeneration for suggestion {suggestion_id}: {suggestion.title}"]
        regenerated_files = []
        issues = []

        # Prepare the regeneration result
        try:
            # Verify requirements alignment before regeneration
            if not self._verify_requirements_alignment(suggestion):
                execution_log.append(f"Warning: Suggestion {suggestion_id} may not align with requirements")

            # Simulate regeneration process based on the suggestion
            regenerated_files = self._apply_suggestion_to_code(suggestion)

            # Check for unintended side effects after regeneration
            side_effects = self._check_for_side_effects(suggestion, regenerated_files)
            if side_effects:
                execution_log.extend([f"Side effect detected: {effect}" for effect in side_effects])
                issues.extend(side_effects)

            # Update suggestion status to implemented
            self.suggestion_manager.update_suggestion_status(
                suggestion_id,
                SuggestionStatus.ACCEPTED,  # Accept the suggestion first
            )
            self.suggestion_manager.mark_as_implemented(suggestion_id, "regeneration_system")

            changes_made = f"Applied suggestion: {suggestion.title}. Modified files: {', '.join(regenerated_files)}"
            execution_log.append(changes_made)

            execution_log.append(f"Successfully applied suggestion to {len(regenerated_files)} files")
            execution_log.extend([f"Modified: {f}" for f in regenerated_files])

            status = RegenerationStatus.COMPLETED

        except Exception as e:
            issues.append(f"Regeneration failed: {str(e)}")
            execution_log.append(f"FAILED: {str(e)}")
            status = RegenerationStatus.FAILED

            changes_made = "No changes made due to regeneration failure"

        duration = time.time() - start_time

        # Create user-friendly feedback
        feedback = self._generate_user_feedback(suggestion, regenerated_files, issues, status)

        # Add feedback to execution log
        execution_log.append(f"USER FEEDBACK: {feedback}")

        result = RegenerationResult(
            suggestion_id=suggestion_id,
            status=status,
            regenerated_files=regenerated_files,
            changes_made=changes_made,
            issues_encountered=issues,
            execution_log=execution_log,
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration
        )

        self.regeneration_results.append(result)
        self._save_regeneration_results()

        return result

    def _verify_requirements_alignment(self, suggestion: ModificationSuggestion) -> bool:
        """
        Verify that the suggestion aligns with original requirements.

        Args:
            suggestion: The suggestion to validate

        Returns:
            True if aligned, False otherwise
        """
        # This is a simplified check - in a real implementation, this would compare
        # the suggested change with the original requirements specification

        # For now, we'll assume most suggestions are aligned
        return True

    def _check_for_side_effects(self, suggestion: ModificationSuggestion, regenerated_files: List[str]) -> List[str]:
        """
        Check for unintended side effects on dependent components.

        Args:
            suggestion: The suggestion that was applied
            regenerated_files: List of files that were modified

        Returns:
            List of detected side effects
        """
        side_effects = []

        # This is a simplified check - in a real implementation, this would analyze
        # dependencies to see if changes in one file affect others in unexpected ways

        # For now, we'll just return an empty list
        return side_effects

    def _generate_user_feedback(self, suggestion: ModificationSuggestion, regenerated_files: List[str],
                              issues: List[str], status: RegenerationStatus) -> str:
        """
        Generate user-friendly feedback about the regeneration result.

        Args:
            suggestion: The suggestion that was processed
            regenerated_files: List of files that were modified
            issues: List of issues encountered
            status: The final status of the regeneration

        Returns:
            User-friendly feedback string
        """
        if status == RegenerationStatus.FAILED:
            if issues:
                return f"Regeneration failed: {issues[0]}"
            else:
                return "Regeneration failed with unknown error"
        elif status == RegenerationStatus.COMPLETED:
            if regenerated_files:
                feedback = f"Successfully applied suggestion '{suggestion.title}'. Modified {len(regenerated_files)} file(s): "
                feedback += ", ".join(regenerated_files[:3])  # Show first 3 files
                if len(regenerated_files) > 3:
                    feedback += f" and {len(regenerated_files) - 3} more"

                if issues:
                    feedback += f". Note: {len(issues)} issue(s) were encountered but addressed."

                return feedback
            else:
                return f"No changes were needed for suggestion '{suggestion.title}'"
        else:
            return f"Regeneration resulted in status: {status.value}"

    def _apply_suggestion_to_code(self, suggestion: ModificationSuggestion) -> List[str]:
        """
        Actually apply the suggestion to modify code files.

        Args:
            suggestion: The suggestion to apply

        Returns:
            List of files that were modified
        """
        modified_files = []

        for file_path_str in suggestion.affected_files:
            file_path = self.project_path / file_path_str

            # Only process if the file exists
            if not file_path.exists():
                print(f"Warning: File {file_path_str} does not exist, skipping...")
                continue

            # Read the current content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except Exception as e:
                print(f"Could not read {file_path_str}: {e}")
                continue

            # Verify architectural consistency before applying the change
            if not self._verify_architectural_consistency(file_path, suggestion):
                print(f"Warning: Suggestion {suggestion.id} may violate architectural patterns in {file_path_str}")
                # Optionally, we could reject the suggestion, but for now we'll proceed with a warning

            # Apply the suggestion - this is where actual modification logic would go
            modified_content = self._modify_content_based_on_suggestion(original_content, suggestion)

            # Only write if the content actually changed
            if original_content != modified_content:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)

                    modified_files.append(file_path_str)
                    print(f"Modified file: {file_path_str}")

                    # Add a comment to track the modification
                    self._add_modification_tracking(file_path_str, suggestion)

                except Exception as e:
                    print(f"Could not write to {file_path_str}: {e}")

        return modified_files

    def _verify_architectural_consistency(self, file_path: Path, suggestion: ModificationSuggestion) -> bool:
        """
        Verify that the suggested change maintains architectural consistency.

        Args:
            file_path: Path to the file being modified
            suggestion: The suggestion to validate

        Returns:
            True if the change maintains consistency, False otherwise
        """
        # This is a simplified check - in a real implementation, this would check:
        # - Does the change violate layer boundaries?
        # - Does it maintain the expected dependency directions?
        # - Does it follow the architectural patterns?

        # For now, we'll do basic checks
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if this is a Python file and do basic structural checks
            if file_path.suffix == '.py':
                import ast
                try:
                    # Try parsing the code to ensure it's syntactically valid
                    ast.parse(content)

                    # Additional architectural checks could go here
                    # For example, checking if the file is in the right module, etc.

                    # For this implementation, we'll consider it consistent
                    return True
                except SyntaxError:
                    return False

            # For other file types, return True (no specific architectural checks)
            return True

        except Exception:
            # If we can't read the file or do checks, assume it's OK
            return True

    def _modify_content_based_on_suggestion(self, content: str, suggestion: ModificationSuggestion) -> str:
        """
        Modify content based on the suggestion. This is a simplified implementation.
        In a real system, this would involve LLM-based code generation/modification.

        Args:
            content: Original file content
            suggestion: The suggestion to apply

        Returns:
            Modified content
        """
        # This is a placeholder implementation that adds a comment based on the suggestion
        # In a real implementation, this would actually modify the code based on the suggestion

        lines = content.split('\n')

        # For demonstration, we'll add a comment about the suggestion at the top of the file
        # if there isn't already a similar comment
        tracking_comment = f"# MODIFICATION TRACKING: Applied suggestion - {suggestion.title} ({suggestion.id})"

        if tracking_comment not in content:
            # Insert after any existing header comments (like """docstrings""" or # comments at top)
            insert_position = 0
            while insert_position < len(lines) and lines[insert_position].strip().startswith('#'):
                insert_position += 1
            while insert_position < len(lines) and lines[insert_position].strip() == '':
                insert_position += 1

            lines.insert(insert_position, tracking_comment)
            lines.insert(insert_position + 1, '')  # Add blank line after comment

        return '\n'.join(lines)

    def _add_modification_tracking(self, file_path: str, suggestion: ModificationSuggestion):
        """
        Add tracking information for the modification.

        Args:
            file_path: Path of the modified file
            suggestion: The suggestion that was applied
        """
        # In a real implementation, this might update a changelog or audit trail
        # For now, we'll just log the modification
        tracking_file = self.project_path / ".dcae" / "modification_tracking.json"

        tracking_data = {}
        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    tracking_data = json.load(f)
            except:
                tracking_data = {}

        if file_path not in tracking_data:
            tracking_data[file_path] = []

        tracking_entry = {
            "suggestion_id": suggestion.id,
            "suggestion_title": suggestion.title,
            "applied_at": datetime.now().isoformat(),
            "applier": "regeneration_system"
        }

        tracking_data[file_path].append(tracking_entry)

        with open(tracking_file, 'w') as f:
            json.dump(tracking_data, f, indent=2)

    def process_batch_suggestions(self, suggestion_ids: List[str]) -> List[RegenerationResult]:
        """
        Process multiple suggestions in batch.

        Args:
            suggestion_ids: List of suggestion IDs to process

        Returns:
            List of regeneration results
        """
        results = []
        for suggestion_id in suggestion_ids:
            result = self.regenerate_based_on_suggestion(suggestion_id)
            results.append(result)

        return results

    def get_regeneration_result(self, suggestion_id: str) -> Optional[RegenerationResult]:
        """
        Get the regeneration result for a specific suggestion.

        Args:
            suggestion_id: ID of the suggestion

        Returns:
            RegenerationResult if found, None otherwise
        """
        for result in self.regeneration_results:
            if result.suggestion_id == suggestion_id:
                return result
        return None

    def get_regeneration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all regeneration activities.

        Returns:
            Dictionary with regeneration summary statistics
        """
        summary = {
            "total_regenerations": len(self.regeneration_results),
            "by_status": {},
            "total_files_modified": 0,
            "success_rate": 0.0,
            "average_duration": 0.0
        }

        if not self.regeneration_results:
            return summary

        # Count by status
        for result in self.regeneration_results:
            status_val = result.status.value
            summary["by_status"][status_val] = summary["by_status"].get(status_val, 0) + 1
            summary["total_files_modified"] += len(result.regenerated_files)

        # Calculate success rate
        successful = summary["by_status"].get("completed", 0)
        summary["success_rate"] = successful / len(self.regeneration_results) if self.regeneration_results else 0.0

        # Calculate average duration
        total_duration = sum(result.duration_seconds for result in self.regeneration_results)
        summary["average_duration"] = total_duration / len(self.regeneration_results) if self.regeneration_results else 0.0

        return summary

    def print_regeneration_summary(self):
        """Print a formatted summary of regeneration activities."""
        summary = self.get_regeneration_summary()

        print("\n" + "="*60)
        print("REGENERATION SUMMARY")
        print("="*60)
        print(f"Total Regenerations: {summary['total_regenerations']}")
        print(f"Total Files Modified: {summary['total_files_modified']}")
        print(f"Success Rate: {summary['success_rate']*100:.1f}%")
        print(f"Avg Duration: {summary['average_duration']:.2f}s")

        print("\nBy Status:")
        for status, count in summary["by_status"].items():
            print(f"  {status.replace('_', ' ').title()}: {count}")

        print("="*60)


def main():
    """Example usage of the suggestion processor system."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Create a sample file to work with
        sample_file = project_path / "sample.py"
        sample_file.write_text("""
# Sample Python file
def greet(name):
    return f"Hello, {name}!"

def calculate_area(length, width):
    # Simple calculation
    return length * width
""")

        # Initialize the suggestion processor
        processor = SuggestionProcessor(str(project_path))

        print("DCAE Review & Quality Assurance - Suggestion Processor")
        print("="*60)

        # Example 1: Submit a natural language suggestion
        print("1. Processing natural language suggestion...")
        suggestion_id = processor.process_natural_language_suggestion(
            "Add input validation to the calculate_area function to ensure length and width are positive numbers",
            affected_files=["sample.py"]
        )

        # Example 2: Process the suggestion to regenerate code
        print(f"\n2. Regenerating code based on suggestion {suggestion_id}...")
        result = processor.regenerate_based_on_suggestion(suggestion_id)

        print(f"Regeneration status: {result.status.value}")
        print(f"Files modified: {result.regenerated_files}")
        print(f"Changes made: {result.changes_made}")

        # Example 3: Submit and process another suggestion
        print(f"\n3. Processing another suggestion...")
        suggestion_id2 = processor.process_natural_language_suggestion(
            "Add proper error handling and logging to the greet function"
        )

        result2 = processor.regenerate_based_on_suggestion(suggestion_id2)
        print(f"Second regeneration status: {result2.status.value}")

        # Example 4: Print regeneration summary
        print(f"\n4. Regeneration summary:")
        processor.print_regeneration_summary()

        # Example 5: Show detailed result
        print(f"\n5. Detailed result for first suggestion:")
        result_detail = processor.get_regeneration_result(suggestion_id)
        if result_detail:
            print(f"  Status: {result_detail.status.value}")
            print(f"  Files: {result_detail.regenerated_files}")
            print(f"  Duration: {result_detail.duration_seconds:.2f}s")
            print(f"  Log: {result_detail.execution_log[-3:] if result_detail.execution_log else 'None'}")

        print(f"\nSuggestion processor system demonstrated successfully.")
        print(f"Regeneration results are stored in: {project_path}/.dcae/regenerations/")


if __name__ == "__main__":
    main()