import os
import tempfile
import unittest
from pathlib import Path
import shutil

from src.dcae.pause_and_review import PauseAndReviewMechanism, ReviewManager, ReviewState, ReviewCheckpoint


class TestPauseAndReviewMechanism(unittest.TestCase):
    """Test cases for the pause and review mechanism."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_review_manager_initialization(self):
        """Test initializing the review manager."""
        manager = ReviewManager(self.project_path)

        self.assertEqual(manager.review_state, ReviewState.ACTIVE)
        self.assertIsNone(manager.current_checkpoint)
        self.assertEqual(len(manager.checkpoints), 0)

        # State file is not automatically created on initialization, only when state changes
        # Verify .dcae directory was created (which should happen on initialization)
        dcae_dir = os.path.join(self.project_path, ".dcae")
        self.assertTrue(os.path.exists(dcae_dir))

    def test_register_review_checkpoint(self):
        """Test registering a review checkpoint."""
        manager = ReviewManager(self.project_path)

        checkpoint = manager.register_review_checkpoint(
            "test-checkpoint",
            "Test Checkpoint",
            "A test checkpoint description",
            "src"
        )

        self.assertEqual(checkpoint.id, "test-checkpoint")
        self.assertEqual(checkpoint.name, "Test Checkpoint")
        self.assertIn("test-checkpoint", manager.checkpoints)

    def test_add_checkpoint_method(self):
        """Test adding a checkpoint using the add_checkpoint method."""
        manager = ReviewManager(self.project_path)

        checkpoint = ReviewCheckpoint(
            id="direct-checkpoint",
            name="Direct Checkpoint",
            description="Added directly",
            artifacts_path="test/path"
        )

        manager.add_checkpoint(checkpoint)

        self.assertIn("direct-checkpoint", manager.checkpoints)
        self.assertEqual(manager.checkpoints["direct-checkpoint"].name, "Direct Checkpoint")

    def test_pause_and_review_mechanism_initialization(self):
        """Test initializing the pause and review mechanism."""
        pause_review = PauseAndReviewMechanism(self.project_path)

        self.assertIsNotNone(pause_review.review_manager)
        self.assertGreater(len(pause_review.review_manager.list_checkpoints()), 0)

    def test_is_ready_to_proceed_when_active(self):
        """Test that is_ready_to_proceed returns True when review state is ACTIVE."""
        pause_review = PauseAndReviewMechanism(self.project_path)

        # By default, state should be ACTIVE
        self.assertTrue(pause_review.is_ready_to_proceed())

    def test_list_available_checkpoints(self):
        """Test listing available checkpoints."""
        pause_review = PauseAndReviewMechanism(self.project_path)

        # Get checkpoints
        checkpoints = pause_review.review_manager.list_checkpoints()

        # Should have default checkpoints
        self.assertGreater(len(checkpoints), 0)
        self.assertIn("project-structure-complete", checkpoints)


class TestReviewManagerStates(unittest.TestCase):
    """Test cases for review manager state management."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_state_transitions(self):
        """Test various review state transitions."""
        manager = ReviewManager(self.project_path)

        # Start in ACTIVE state
        self.assertEqual(manager.review_state, ReviewState.ACTIVE)

        # Move to REVIEW_REQUESTED
        manager.review_state = ReviewState.REVIEW_REQUESTED
        self.assertEqual(manager.review_state, ReviewState.REVIEW_REQUESTED)

        # Move to APPROVED
        manager.review_state = ReviewState.APPROVED
        self.assertEqual(manager.review_state, ReviewState.APPROVED)

    def test_is_review_pending(self):
        """Test the is_review_pending method."""
        manager = ReviewManager(self.project_path)

        # Should not be pending when ACTIVE
        self.assertFalse(manager.is_review_pending())

        # Should be pending when REVIEW_REQUESTED
        manager.review_state = ReviewState.REVIEW_REQUESTED
        self.assertTrue(manager.is_review_pending())

        # Should be pending when MODIFICATION_REQUESTED
        manager.review_state = ReviewState.MODIFICATION_REQUESTED
        self.assertTrue(manager.is_review_pending())


if __name__ == '__main__':
    unittest.main()