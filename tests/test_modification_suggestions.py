import os
import tempfile
import unittest
from pathlib import Path
import shutil

from src.dcae.modification_suggestions import (
    SuggestionManager,
    ModificationSuggestionSubmitter,
    SuggestionStatus,
    SuggestionPriority,
    SuggestionCategory,
    ModificationSuggestion
)


class TestSuggestionManager(unittest.TestCase):
    """Test cases for the suggestion manager."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_suggestion_manager_initialization(self):
        """Test initializing the suggestion manager."""
        manager = SuggestionManager(self.project_path)

        # Verify directory structure
        suggestions_dir = os.path.join(self.project_path, ".dcae", "suggestions")
        self.assertTrue(os.path.exists(suggestions_dir))

        # Verify initial state
        self.assertEqual(len(manager.suggestions), 0)

    def test_submit_suggestion(self):
        """Test submitting a new suggestion."""
        manager = SuggestionManager(self.project_path)

        suggestion_id = manager.submit_suggestion(
            title="Test Suggestion",
            description="This is a test suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.MEDIUM,
            affected_files=["test.py"],
            proposed_solution="Change this",
            implementation_complexity="low",
            submitted_by="test_user"
        )

        # Verify suggestion was created
        self.assertIsNotNone(suggestion_id)
        self.assertEqual(len(manager.suggestions), 1)

        suggestion = manager.suggestions[0]
        self.assertEqual(suggestion.title, "Test Suggestion")
        self.assertEqual(suggestion.category, SuggestionCategory.CODE_IMPROVEMENT)
        self.assertEqual(suggestion.status, SuggestionStatus.SUBMITTED)

    def test_update_suggestion_status(self):
        """Test updating a suggestion's status."""
        manager = SuggestionManager(self.project_path)

        # Submit a suggestion
        suggestion_id = manager.submit_suggestion(
            title="Test Suggestion",
            description="This is a test suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.MEDIUM,
            affected_files=["test.py"],
            proposed_solution="Change this",
            implementation_complexity="low",
            submitted_by="test_user"
        )

        # Update its status
        success = manager.update_suggestion_status(
            suggestion_id, SuggestionStatus.ACCEPTED, reviewed_by="admin"
        )

        self.assertTrue(success)

        # Verify the update
        suggestion = manager.get_suggestion(suggestion_id)
        self.assertEqual(suggestion.status, SuggestionStatus.ACCEPTED)
        self.assertEqual(suggestion.reviewed_by, "admin")

    def test_mark_as_implemented(self):
        """Test marking a suggestion as implemented."""
        manager = SuggestionManager(self.project_path)

        # Submit a suggestion
        suggestion_id = manager.submit_suggestion(
            title="Test Suggestion",
            description="This is a test suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.MEDIUM,
            affected_files=["test.py"],
            proposed_solution="Change this",
            implementation_complexity="low",
            submitted_by="test_user"
        )

        # First accept it
        manager.update_suggestion_status(suggestion_id, SuggestionStatus.ACCEPTED)

        # Then mark as implemented
        success = manager.mark_as_implemented(suggestion_id, "developer")

        self.assertTrue(success)

        # Verify the update
        suggestion = manager.get_suggestion(suggestion_id)
        self.assertEqual(suggestion.status, SuggestionStatus.IMPLEMENTED)
        self.assertEqual(suggestion.implemented_by, "developer")

    def test_get_suggestion_by_id(self):
        """Test retrieving a suggestion by ID."""
        manager = SuggestionManager(self.project_path)

        suggestion_id = manager.submit_suggestion(
            title="Test Suggestion",
            description="This is a test suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.MEDIUM,
            affected_files=["test.py"],
            proposed_solution="Change this",
            implementation_complexity="low",
            submitted_by="test_user"
        )

        suggestion = manager.get_suggestion(suggestion_id)

        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.title, "Test Suggestion")

    def test_get_suggestions_by_status(self):
        """Test retrieving suggestions by status."""
        manager = SuggestionManager(self.project_path)

        # Submit suggestions with different statuses
        suggestion1_id = manager.submit_suggestion(
            title="Suggestion 1",
            description="First suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.MEDIUM,
            affected_files=["test1.py"],
            proposed_solution="Change this",
            implementation_complexity="low",
            submitted_by="test_user"
        )

        suggestion2_id = manager.submit_suggestion(
            title="Suggestion 2",
            description="Second suggestion",
            category=SuggestionCategory.BUG_FIX,
            priority=SuggestionPriority.HIGH,
            affected_files=["test2.py"],
            proposed_solution="Fix that",
            implementation_complexity="medium",
            submitted_by="test_user"
        )

        # Update one to ACCEPTED
        manager.update_suggestion_status(suggestion2_id, SuggestionStatus.ACCEPTED)

        # Get suggestions by status
        submitted_suggestions = manager.get_suggestions_by_status(SuggestionStatus.SUBMITTED)
        accepted_suggestions = manager.get_suggestions_by_status(SuggestionStatus.ACCEPTED)

        self.assertEqual(len(submitted_suggestions), 1)
        self.assertEqual(len(accepted_suggestions), 1)
        self.assertEqual(submitted_suggestions[0].title, "Suggestion 1")
        self.assertEqual(accepted_suggestions[0].title, "Suggestion 2")

    def test_get_suggestions_by_priority(self):
        """Test retrieving suggestions by priority."""
        manager = SuggestionManager(self.project_path)

        # Submit suggestions with different priorities
        manager.submit_suggestion(
            title="Low Priority",
            description="Low priority suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.LOW,
            affected_files=["test.py"],
            proposed_solution="Change this",
            implementation_complexity="low",
            submitted_by="test_user"
        )

        manager.submit_suggestion(
            title="High Priority",
            description="High priority suggestion",
            category=SuggestionCategory.BUG_FIX,
            priority=SuggestionPriority.HIGH,
            affected_files=["test.py"],
            proposed_solution="Fix this",
            implementation_complexity="medium",
            submitted_by="test_user"
        )

        # Get suggestions by priority
        low_priority_suggestions = manager.get_suggestions_by_priority(SuggestionPriority.LOW)
        high_priority_suggestions = manager.get_suggestions_by_priority(SuggestionPriority.HIGH)

        self.assertEqual(len(low_priority_suggestions), 1)
        self.assertEqual(len(high_priority_suggestions), 1)
        self.assertEqual(low_priority_suggestions[0].title, "Low Priority")
        self.assertEqual(high_priority_suggestions[0].title, "High Priority")

    def test_get_suggestions_summary(self):
        """Test getting suggestions summary."""
        manager = SuggestionManager(self.project_path)

        # Submit suggestions
        manager.submit_suggestion(
            title="Suggestion 1",
            description="First suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.MEDIUM,
            affected_files=["test.py"],
            proposed_solution="Change this",
            implementation_complexity="low",
            submitted_by="test_user"
        )

        manager.submit_suggestion(
            title="Suggestion 2",
            description="Second suggestion",
            category=SuggestionCategory.BUG_FIX,
            priority=SuggestionPriority.HIGH,
            affected_files=["test.py"],
            proposed_solution="Fix that",
            implementation_complexity="medium",
            submitted_by="test_user"
        )

        summary = manager.get_suggestions_summary()

        self.assertEqual(summary["total_suggestions"], 2)
        self.assertIn("by_status", summary)
        self.assertIn("by_priority", summary)
        self.assertIn("by_category", summary)


class TestModificationSuggestionSubmitter(unittest.TestCase):
    """Test cases for the suggestion submitter."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_submitter_initialization(self):
        """Test initializing the suggestion submitter."""
        submitter = ModificationSuggestionSubmitter(self.project_path)

        self.assertIsNotNone(submitter.suggestion_manager)

    def test_submit_suggestion_from_finding(self):
        """Test submitting a suggestion from a review finding."""
        submitter = ModificationSuggestionSubmitter(self.project_path)

        suggestion_id = submitter.submit_suggestion_from_finding(
            finding_id="security_hardcoded_password_file.py:10",
            finding_description="Hardcoded password found in file",
            proposed_solution="Move password to environment variable"
        )

        # Verify suggestion was created
        self.assertIsNotNone(suggestion_id)

        suggestion = submitter.suggestion_manager.get_suggestion(suggestion_id)
        self.assertIsNotNone(suggestion)
        self.assertIn("password", suggestion.description.lower())

    def test_batch_submit_suggestions(self):
        """Test batch submitting multiple suggestions."""
        submitter = ModificationSuggestionSubmitter(self.project_path)

        findings = [
            {
                "id": "security_issue_1",
                "issue_description": "First security issue",
                "recommendation": "Recommendation 1"
            },
            {
                "id": "performance_issue_2",
                "issue_description": "Performance issue",
                "recommendation": "Recommendation 2"
            }
        ]

        suggestion_ids = submitter.batch_submit_suggestions(findings)

        # Verify both suggestions were created
        self.assertEqual(len(suggestion_ids), 2)

        # Verify they exist in manager
        for suggestion_id in suggestion_ids:
            suggestion = submitter.suggestion_manager.get_suggestion(suggestion_id)
            self.assertIsNotNone(suggestion)

    def test_create_manual_suggestion(self):
        """Test creating a manual suggestion."""
        submitter = ModificationSuggestionSubmitter(self.project_path)

        suggestion_id = submitter.create_manual_suggestion(
            title="Manual Improvement",
            description="This is a manually created suggestion",
            category=SuggestionCategory.CODE_IMPROVEMENT,
            priority=SuggestionPriority.MEDIUM,
            affected_files=["src/module.py"],
            proposed_solution="Improve this code"
        )

        self.assertIsNotNone(suggestion_id)

        suggestion = submitter.suggestion_manager.get_suggestion(suggestion_id)
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.title, "Manual Improvement")
        self.assertEqual(suggestion.category, SuggestionCategory.CODE_IMPROVEMENT)


if __name__ == '__main__':
    unittest.main()