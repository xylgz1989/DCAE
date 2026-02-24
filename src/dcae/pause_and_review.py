"""
Review and Quality Assurance Module

This module implements the functionality for pausing development at key milestones
and requesting user review of generated artifacts.
"""

import os
import json
from enum import Enum
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
import pickle
import tempfile
import subprocess
import sys


class ReviewState(Enum):
    """Enumeration for different review states."""
    ACTIVE = "active"
    REVIEW_REQUESTED = "review_requested"
    MODIFICATION_REQUESTED = "modification_requested"
    APPROVED = "approved"


@dataclass
class ReviewCheckpoint:
    """Represents a point in the development process where review is requested."""
    id: str
    name: str
    description: str
    artifacts_path: str
    callback: Optional[Callable] = None


class ReviewManager:
    """Manages the review and quality assurance process."""

    def __init__(self, project_path: str):
        """
        Initialize the review manager.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.state_file = self.project_path / ".dcae" / "review_state.json"
        self.checkpoints_file = self.project_path / ".dcae" / "checkpoints.json"
        self.review_state = ReviewState.ACTIVE
        self.checkpoints: Dict[str, ReviewCheckpoint] = {}
        self.current_checkpoint: Optional[str] = None

        # Ensure .dcae directory exists
        self.project_path.mkdir(exist_ok=True)
        dcae_dir = self.project_path / ".dcae"
        dcae_dir.mkdir(exist_ok=True)

        self._load_state()

    def _save_state(self):
        """Save the current review state to file."""
        state_data = {
            "state": self.review_state.value,
            "current_checkpoint": self.current_checkpoint
        }

        with open(self.state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

    def _load_state(self):
        """Load the review state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)

                self.review_state = ReviewState(state_data.get("state", "active"))
                self.current_checkpoint = state_data.get("current_checkpoint")
            except Exception:
                # If there's an error loading state, reset to default
                self.review_state = ReviewState.ACTIVE
                self.current_checkpoint = None
        else:
            self.review_state = ReviewState.ACTIVE
            self.current_checkpoint = None

    def add_checkpoint(self, checkpoint: ReviewCheckpoint):
        """Add a review checkpoint to the manager."""
        self.checkpoints[checkpoint.id] = checkpoint

    def register_review_checkpoint(self,
                                  checkpoint_id: str,
                                  name: str,
                                  description: str,
                                  artifacts_path: str) -> ReviewCheckpoint:
        """Register a new review checkpoint."""
        checkpoint = ReviewCheckpoint(
            id=checkpoint_id,
            name=name,
            description=description,
            artifacts_path=artifacts_path
        )

        self.add_checkpoint(checkpoint)
        return checkpoint

    def trigger_review_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Trigger a review checkpoint and pause development until user review is complete.

        Args:
            checkpoint_id: ID of the checkpoint to trigger

        Returns:
            True if checkpoint exists and review was requested, False otherwise
        """
        if checkpoint_id not in self.checkpoints:
            print(f"Checkpoint {checkpoint_id} not found")
            return False

        checkpoint = self.checkpoints[checkpoint_id]
        self.current_checkpoint = checkpoint_id
        self.review_state = ReviewState.REVIEW_REQUESTED
        self._save_state()

        print(f"\n[PAUSE] Development paused at checkpoint: {checkpoint.name}")
        print(f"Description: {checkpoint.description}")
        print(f"Artifacts location: {checkpoint.artifacts_path}")
        print("\nPlease review the generated artifacts and make any necessary modifications.")

        # Show the generated artifacts
        self._display_artifacts(checkpoint.artifacts_path)

        # Wait for user input
        decision = self._wait_for_user_decision()

        # Process the user's decision
        return self._process_user_decision(decision)

    def _display_artifacts(self, artifacts_path: str):
        """Display the generated artifacts for review."""
        path = Path(artifacts_path)
        if path.exists():
            print(f"\nGenerated artifacts in {artifacts_path}:")
            for item in path.rglob("*"):
                if item.is_file():
                    print(f"  - {item.relative_to(path)}")

                    # Show content preview for code files
                    if item.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.md', '.txt']:
                        try:
                            with open(item, 'r', encoding='utf-8') as f:
                                content = f.read(500)  # Read first 500 chars for preview
                                print(f"    Preview: {content[:200]}{'...' if len(content) > 200 else ''}")
                        except:
                            pass  # Skip binary files or files with encoding issues
                    print()
        else:
            print(f"No artifacts found at {artifacts_path}")

    def _wait_for_user_decision(self) -> str:
        """Wait for user to make a decision about the review."""
        while True:
            print("\nPlease select an option:")
            print("1. Approve - Continue with current artifacts")
            print("2. Request Changes - Pause and allow modifications")
            print("3. Show Artifacts Again - Re-display the generated artifacts")
            print("4. Regenerate - Regenerate artifacts with modified requirements")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice in ['1', '2', '3', '4']:
                options = {'1': 'approve', '2': 'request_changes',
                          '3': 'show_again', '4': 'regenerate'}
                if choice != '3':  # Only return if not 'show again'
                    return options[choice]
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

    def _process_user_decision(self, decision: str) -> bool:
        """Process the user's decision and update state accordingly."""
        if decision == 'approve':
            print("\n[APPROVED] Continuing development...")
            self.review_state = ReviewState.APPROVED
            self.current_checkpoint = None
            self._save_state()
            return True

        elif decision == 'request_changes':
            print("\n[CHANGES REQUESTED] Development paused. Make your modifications.")
            print("Press Enter when modifications are complete...")
            input()  # Wait for user to press Enter

            # After modifications, ask if they're done
            print("\nAre your modifications complete?")
            while True:
                done = input("Enter 'yes' when done: ").strip().lower()
                if done == 'yes':
                    print("[MODIFICATIONS COMPLETE] Resuming development...")
                    self.review_state = ReviewState.ACTIVE
                    self.current_checkpoint = None
                    self._save_state()
                    return True
                else:
                    print("Waiting for 'yes' to confirm modifications are complete...")

        elif decision == 'regenerate':
            print("\n[REGENERATE] Development paused for regeneration...")
            print("You can now modify requirements or architecture before regenerating.")
            print("Press Enter when ready to continue...")
            input()

            # Set state to modification requested to indicate regeneration is needed
            self.review_state = ReviewState.MODIFICATION_REQUESTED
            self._save_state()
            return True

        else:  # This shouldn't happen with validated input
            print("\nUnknown decision. Resuming development...")
            self.review_state = ReviewState.ACTIVE
            self.current_checkpoint = None
            self._save_state()
            return True

    def is_review_pending(self) -> bool:
        """Check if a review is currently pending."""
        return self.review_state in [ReviewState.REVIEW_REQUESTED, ReviewState.MODIFICATION_REQUESTED]

    def approve_current_checkpoint(self):
        """Manually approve the current checkpoint."""
        if self.current_checkpoint:
            print(f"[MANUAL APPROVE] Approving checkpoint: {self.current_checkpoint}")
            self.review_state = ReviewState.APPROVED
            self.current_checkpoint = None
            self._save_state()

    def get_review_state(self) -> ReviewState:
        """Get the current review state."""
        return self.review_state

    def list_checkpoints(self) -> Dict[str, ReviewCheckpoint]:
        """List all registered checkpoints."""
        return self.checkpoints.copy()


class PauseAndReviewMechanism:
    """Implementation of the pause and request user review functionality."""

    def __init__(self, project_path: str):
        """
        Initialize the pause and review mechanism.

        Args:
            project_path: Path to the project root
        """
        self.review_manager = ReviewManager(project_path)
        self.setup_default_checkpoints()

    def setup_default_checkpoints(self):
        """Setup default review checkpoints for the development process."""
        # Checkpoint after initial project structure generation
        self.review_manager.register_review_checkpoint(
            "project-structure-complete",
            "Project Structure Generation Complete",
            "Review the generated project structure and initial files",
            "src"
        )

        # Checkpoint after framework code generation
        self.review_manager.register_review_checkpoint(
            "framework-code-complete",
            "Framework Code Generation Complete",
            "Review the generated framework-specific code",
            "src"
        )

        # Checkpoint after business logic generation
        self.review_manager.register_review_checkpoint(
            "business-logic-complete",
            "Business Logic Generation Complete",
            "Review the generated business logic components",
            "src/entities"
        )

        # Checkpoint after complete project generation
        self.review_manager.register_review_checkpoint(
            "project-generation-complete",
            "Complete Project Generation Complete",
            "Review the entire generated project before finalization",
            "."
        )

    def pause_at_milestone(self, milestone_id: str) -> bool:
        """
        Pause the development process at a specific milestone and request user review.

        Args:
            milestone_id: ID of the milestone/checkpoint to pause at

        Returns:
            True if the pause and review process completed successfully, False otherwise
        """
        print(f"\n[CHECKPOINT] Reached milestone: {milestone_id}")
        return self.review_manager.trigger_review_checkpoint(milestone_id)

    def continue_if_approved(self, milestone_id: str) -> bool:
        """
        Check if the specified milestone has been approved and development can continue.

        Args:
            milestone_id: ID of the milestone to check

        Returns:
            True if approved and development can continue, False otherwise
        """
        if self.review_manager.get_review_state() == ReviewState.APPROVED:
            # Reset state for next checkpoint
            self.review_manager.review_state = ReviewState.ACTIVE
            self.review_manager._save_state()
            print(f"[CONTINUE] Development continuing after approval for {milestone_id}")
            return True
        elif self.review_manager.is_review_pending():
            print(f"[WAITING] Review pending for {milestone_id}. Please review artifacts.")
            return False
        else:
            return True

    def is_ready_to_proceed(self) -> bool:
        """
        Check if the development process is ready to proceed.

        Returns:
            True if ready to proceed, False if paused for review
        """
        return not self.review_manager.is_review_pending()

    def list_available_checkpoints(self):
        """List all available review checkpoints."""
        checkpoints = self.review_manager.list_checkpoints()
        print("\nAvailable Review Checkpoints:")
        for cp_id, checkpoint in checkpoints.items():
            print(f"  - {cp_id}: {checkpoint.name}")
            print(f"    Description: {checkpoint.description}")
            print(f"    Location: {checkpoint.artifacts_path}")
            print()


# Example usage and testing function
def main():
    """Example usage of the pause and review mechanism."""
    import tempfile
    import os

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = os.path.join(temp_dir, "test_project")
        os.makedirs(project_path, exist_ok=True)

        # Initialize the pause and review mechanism
        pause_review = PauseAndReviewMechanism(project_path)

        print("DCAE Review & Quality Assurance - Pause and Request User Review")
        print("="*60)

        # List available checkpoints
        pause_review.list_available_checkpoints()

        print("\nSimulating development process with review checkpoints...")

        # Simulate reaching first milestone
        print("\n1. Generating project structure...")
        # In a real scenario, project structure would be generated here

        # Pause at first milestone
        print("\nPausing for review at 'project-structure-complete'...")
        result = pause_review.pause_at_milestone("project-structure-complete")
        print(f"Pause result: {result}")

        # Check if approved to continue
        if pause_review.continue_if_approved("project-structure-complete"):
            print("Continuing to next phase...")

        # Simulate reaching second milestone
        print("\n2. Generating framework code...")
        # In a real scenario, framework code would be generated here

        # Pause at second milestone
        print("\nPausing for review at 'framework-code-complete'...")
        result = pause_review.pause_at_milestone("framework-code-complete")
        print(f"Pause result: {result}")

        print("\nReview and Pause functionality demonstration completed.")


if __name__ == "__main__":
    main()