"""
BMAD (Business Manager, Architect, Developer) Workflow Implementation

This module implements the core orchestration engine for the BMAD workflow,
managing transitions between phases and tracking state throughout the process.
"""

import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import threading
import time
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod


class WorkflowPhase(Enum):
    """Enumeration of the different phases in the BMAD workflow."""
    INITIALIZATION = "initialization"
    BUSINESS = "business"  # Requirements Analysis
    ARCHITECTURE = "architecture"  # Architecture Design
    DEVELOPMENT = "development"  # Code Development
    QUALITY_ASSURANCE = "quality_assurance"  # Quality Assurance
    COMPLETED = "completed"


class DisciplineLevel(Enum):
    """Enumeration for discipline levels that affect workflow strictness."""
    FAST = "fast"
    BALANCED = "balanced"
    STRICT = "strict"


@dataclass
class WorkflowState:
    """Represents the current state of a BMAD workflow."""
    workflow_id: str
    current_phase: WorkflowPhase
    created_at: datetime
    updated_at: datetime
    phase_started_at: datetime
    phase_completed_at: Optional[datetime]
    completed_phases: List[WorkflowPhase]
    project_config: Dict[str, Any]
    metadata: Dict[str, Any]


class WorkflowCheckpoint:
    """Represents a checkpoint in the workflow where it can be paused/resumed."""

    def __init__(self, phase: WorkflowPhase, step: str, data: Dict[str, Any]):
        self.phase = phase
        self.step = step
        self.data = data
        self.timestamp = datetime.now()


class PhaseInterface(ABC):
    """Abstract interface for workflow phases."""

    @abstractmethod
    def execute(self, workflow_state: WorkflowState) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute the phase and return (success, message, output_data)."""
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the phase."""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Get the current status of the phase."""
        pass


class BMADOrchestrator:
    """Main orchestrator for the BMAD workflow."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.state_file = self.project_path / ".dcae" / "workflow_state.json"
        self.checkpoint_file = self.project_path / ".dcae" / "workflow_checkpoint.json"
        self.workflow_state: Optional[WorkflowState] = None
        self.checkpoints: List[WorkflowCheckpoint] = []
        self.lock = threading.Lock()

        # Initialize the .dcae directory if it doesn't exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state if available
        self.load_state()

    def initialize_workflow(self, project_config: Dict[str, Any],
                          initial_phase: WorkflowPhase = WorkflowPhase.BUSINESS) -> bool:
        """Initialize a new BMAD workflow."""
        with self.lock:
            workflow_id = f"bmwf_{int(time.time())}_{os.urandom(4).hex()}"

            self.workflow_state = WorkflowState(
                workflow_id=workflow_id,
                current_phase=initial_phase,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                phase_started_at=datetime.now(),
                phase_completed_at=None,
                completed_phases=[],
                project_config=project_config,
                metadata={}
            )

            self.save_state()
            return True

    def load_state(self) -> bool:
        """Load the current workflow state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)

                # Convert string representations back to appropriate types
                data['current_phase'] = WorkflowPhase(data['current_phase'])
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                data['phase_started_at'] = datetime.fromisoformat(data['phase_started_at'])

                if data['phase_completed_at']:
                    data['phase_completed_at'] = datetime.fromisoformat(data['phase_completed_at'])

                data['completed_phases'] = [WorkflowPhase(phase) for phase in data['completed_phases']]

                self.workflow_state = WorkflowState(**{k: v for k, v in data.items()
                                                     if k in WorkflowState.__annotations__})
                return True
            except Exception as e:
                print(f"Error loading workflow state: {e}")
                return False
        return False

    def save_state(self) -> bool:
        """Save the current workflow state to file."""
        if self.workflow_state:
            try:
                # Convert the state to a serializable format
                state_dict = asdict(self.workflow_state)
                state_dict['current_phase'] = self.workflow_state.current_phase.value
                state_dict['created_at'] = self.workflow_state.created_at.isoformat()
                state_dict['updated_at'] = self.workflow_state.updated_at.isoformat()
                state_dict['phase_started_at'] = self.workflow_state.phase_started_at.isoformat()

                if self.workflow_state.phase_completed_at:
                    state_dict['phase_completed_at'] = self.workflow_state.phase_completed_at.isoformat()
                else:
                    state_dict['phase_completed_at'] = None

                state_dict['completed_phases'] = [phase.value for phase in self.workflow_state.completed_phases]

                with open(self.state_file, 'w') as f:
                    json.dump(state_dict, f, indent=2)

                return True
            except Exception as e:
                print(f"Error saving workflow state: {e}")
                return False
        return False

    def transition_to_phase(self, target_phase: WorkflowPhase) -> bool:
        """Transition to a new phase in the workflow."""
        if not self.workflow_state:
            print("No workflow state initialized")
            return False

        # Validate the phase transition is allowed
        valid_transitions = {
            WorkflowPhase.INITIALIZATION: [WorkflowPhase.BUSINESS],
            WorkflowPhase.BUSINESS: [WorkflowPhase.ARCHITECTURE],
            WorkflowPhase.ARCHITECTURE: [WorkflowPhase.DEVELOPMENT],
            WorkflowPhase.DEVELOPMENT: [WorkflowPhase.QUALITY_ASSURANCE],
            WorkflowPhase.QUALITY_ASSURANCE: [WorkflowPhase.COMPLETED],
        }

        current = self.workflow_state.current_phase
        if target_phase not in valid_transitions.get(current, []):
            print(f"Invalid phase transition from {current.value} to {target_phase.value}")
            return False

        # Update the state for the new phase
        with self.lock:
            # Mark the current phase as completed
            self.workflow_state.completed_phases.append(self.workflow_state.current_phase)
            self.workflow_state.phase_completed_at = datetime.now()

            # Transition to the new phase
            self.workflow_state.current_phase = target_phase
            self.workflow_state.phase_started_at = datetime.now()
            self.workflow_state.updated_at = datetime.now()

            if target_phase == WorkflowPhase.COMPLETED:
                # Workflow is complete
                self.workflow_state.metadata['completed_at'] = datetime.now().isoformat()

            self.save_state()
            return True

    def get_current_phase(self) -> Optional[WorkflowPhase]:
        """Get the current phase of the workflow."""
        if self.workflow_state:
            return self.workflow_state.current_phase
        return None

    def get_workflow_progress(self) -> Dict[str, Any]:
        """Get the current progress and status of the workflow."""
        if not self.workflow_state:
            return {"status": "not_initialized"}

        total_phases = len(WorkflowPhase) - 2  # Exclude INITIALIZATION and COMPLETED
        completed_count = len(self.workflow_state.completed_phases)

        if self.workflow_state.current_phase != WorkflowPhase.COMPLETED:
            completed_count += 1  # Count current phase as partially complete

        progress_percentage = int((completed_count / total_phases) * 100)

        return {
            "workflow_id": self.workflow_state.workflow_id,
            "current_phase": self.workflow_state.current_phase.value,
            "completed_phases": [phase.value for phase in self.workflow_state.completed_phases],
            "progress_percentage": progress_percentage,
            "created_at": self.workflow_state.created_at.isoformat(),
            "updated_at": self.workflow_state.updated_at.isoformat(),
            "discipline_level": self.workflow_state.project_config.get("discipline_level", "balanced")
        }

    def pause_workflow(self) -> bool:
        """Pause the workflow at the current checkpoint."""
        if not self.workflow_state:
            return False

        # Create a checkpoint at the current state
        checkpoint = WorkflowCheckpoint(
            phase=self.workflow_state.current_phase,
            step="paused_by_user",
            data={"state_at_pause": self.get_workflow_progress()}
        )

        self.checkpoints.append(checkpoint)
        self.workflow_state.metadata['paused_at'] = datetime.now().isoformat()
        self.save_state()
        return True

    def resume_workflow(self) -> bool:
        """Resume the workflow from the last checkpoint."""
        if not self.workflow_state:
            return False

        # Check if the workflow was paused
        if 'paused_at' in self.workflow_state.metadata:
            del self.workflow_state.metadata['paused_at']
            self.workflow_state.updated_at = datetime.now()
            self.save_state()
            return True

        return False

    def is_workflow_paused(self) -> bool:
        """Check if the workflow is currently paused."""
        if not self.workflow_state:
            return False

        return 'paused_at' in self.workflow_state.metadata


def main():
    """Example usage of the BMAD workflow orchestrator."""
    import tempfile
    import shutil

    # Create a temporary project directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        dcae_dir = project_path / ".dcae"
        dcae_dir.mkdir(parents=True)

        # Initialize the orchestrator
        orchestrator = BMADOrchestrator(str(project_path))

        # Sample project configuration respecting discipline level
        project_config = {
            "project_name": "Demo Project",
            "discipline_level": "balanced",
            "llm_preferences": {
                "primary": "openai",
                "secondary": "anthropic"
            },
            "features": ["requirements_analysis", "architecture_design", "development", "qa"]
        }

        print("=== BMAD Workflow Orchestration Demo ===")

        # Initialize the workflow
        success = orchestrator.initialize_workflow(project_config)
        print(f"Workflow initialization: {'SUCCESS' if success else 'FAILED'}")

        # Show initial state
        progress = orchestrator.get_workflow_progress()
        print(f"Initial state: {progress}")

        # Simulate workflow progression
        print("\n--- Progressing through phases ---")

        # Transition through phases
        phases_to_execute = [WorkflowPhase.BUSINESS, WorkflowPhase.ARCHITECTURE,
                           WorkflowPhase.DEVELOPMENT, WorkflowPhase.QUALITY_ASSURANCE]

        for target_phase in phases_to_execute:
            print(f"Transitioning to {target_phase.value}...")
            success = orchestrator.transition_to_phase(target_phase)
            print(f"Transition: {'SUCCESS' if success else 'FAILED'}")

            if success:
                progress = orchestrator.get_workflow_progress()
                print(f"Progress: {progress['progress_percentage']}% complete")
                print(f"Current phase: {progress['current_phase']}")

            # Simulate work in each phase
            time.sleep(0.5)

        # Final state
        final_progress = orchestrator.get_workflow_progress()
        print(f"\nFinal workflow state: {final_progress}")

        print("\n--- Pausing and Resuming Demo ---")

        # Pause the workflow
        paused = orchestrator.pause_workflow()
        print(f"Pause workflow: {'SUCCESS' if paused else 'FAILED'}")
        print(f"Is paused: {orchestrator.is_workflow_paused()}")

        # Resume the workflow
        resumed = orchestrator.resume_workflow()
        print(f"Resume workflow: {'SUCCESS' if resumed else 'FAILED'}")
        print(f"Is paused after resume: {orchestrator.is_workflow_paused()}")

        print("\nBMAD workflow orchestration demo completed!")


if __name__ == "__main__":
    main()