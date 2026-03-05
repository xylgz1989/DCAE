"""
BMAD Workflow Orchestrator

This module implements the workflow orchestrator that coordinates
between the different phases of the BMAD workflow.
"""

import json
import os
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import threading

from .bmad_workflow import (
    WorkflowPhase,
    WorkflowState,
    DisciplineLevel,
    BMADOrchestrator,
    PhaseInterface
)


@dataclass
class PhaseResult:
    """Result of executing a phase."""
    success: bool
    message: str
    data: Dict[str, Any]
    duration: float


class WorkflowOrchestrator:
    """Coordinates the execution of the entire BMAD workflow."""

    def __init__(self, project_path: str = ".", discipline_level: DisciplineLevel = DisciplineLevel.BALANCED):
        self.project_path = Path(project_path)
        self.discipline_level = discipline_level
        self.bmad_orchestrator = BMADOrchestrator(project_path)
        self.phases: Dict[WorkflowPhase, PhaseInterface] = {}
        self.results: List[PhaseResult] = []
        self.execution_log: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def register_phase_handler(self, phase: WorkflowPhase, handler: PhaseInterface):
        """Register a handler for a specific phase."""
        self.phases[phase] = handler

    def execute_phase(self, phase: WorkflowPhase, input_data: Dict[str, Any]) -> PhaseResult:
        """Execute a single phase."""
        if phase not in self.phases:
            return PhaseResult(
                success=False,
                message=f"No handler registered for phase: {phase.value}",
                data={},
                duration=0.0
            )

        start_time = time.time()
        handler = self.phases[phase]

        # Validate input
        if not handler.validate_input(input_data):
            return PhaseResult(
                success=False,
                message=f"Input validation failed for phase: {phase.value}",
                data={},
                duration=0.0
            )

        # Execute the phase
        success, message, output_data = handler.execute(self.bmad_orchestrator.workflow_state)

        duration = time.time() - start_time

        result = PhaseResult(
            success=success,
            message=message,
            data=output_data,
            duration=duration
        )

        # Log execution
        self.execution_log.append({
            "phase": phase.value,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data
        })

        return result

    def execute_workflow(self, start_phase: WorkflowPhase = WorkflowPhase.BUSINESS) -> Dict[str, Any]:
        """Execute the entire BMAD workflow from a given phase."""
        # Initialize the workflow if not already done
        if not self.bmad_orchestrator.workflow_state:
            project_config = {
                "project_name": "Default Project",
                "discipline_level": self.discipline_level.value,
                "llm_preferences": {
                    "primary": "openai",
                    "secondary": "anthropic"
                }
            }
            self.bmad_orchestrator.initialize_workflow(project_config, start_phase)

        execution_sequence = [
            WorkflowPhase.BUSINESS,
            WorkflowPhase.ARCHITECTURE,
            WorkflowPhase.DEVELOPMENT,
            WorkflowPhase.QUALITY_ASSURANCE
        ]

        # Find the starting index based on the requested start phase
        start_index = 0
        for i, phase in enumerate(execution_sequence):
            if phase == start_phase:
                start_index = i
                break

        results = {}

        # Execute phases in sequence
        for i in range(start_index, len(execution_sequence)):
            phase = execution_sequence[i]
            print(f"Executing phase: {phase.value}")

            # Prepare input data (in a real implementation, this would come from previous phase)
            input_data = {
                "previous_results": self.results[-1].data if self.results else {},
                "current_phase": phase.value,
                "workflow_state": self.bmad_orchestrator.get_workflow_progress()
            }

            # Execute the phase
            result = self.execute_phase(phase, input_data)
            self.results.append(result)

            results[phase.value] = {
                "success": result.success,
                "message": result.message,
                "duration": result.duration,
                "output_data": result.data
            }

            if not result.success:
                print(f"Phase {phase.value} failed: {result.message}")
                break

            # Transition to the next phase
            if i < len(execution_sequence) - 1:
                next_phase = execution_sequence[i + 1]
                transition_success = self.bmad_orchestrator.transition_to_phase(next_phase)
                if not transition_success:
                    print(f"Failed to transition to {next_phase.value}")
                    break

            print(f"Phase {phase.value} completed successfully in {result.duration:.2f}s")

        # Complete the workflow if all phases were successful
        if result.success and phase == WorkflowPhase.QUALITY_ASSURANCE:
            completion_success = self.bmad_orchestrator.transition_to_phase(WorkflowPhase.COMPLETED)
            if completion_success:
                print("Workflow completed successfully!")
            else:
                print("Failed to mark workflow as completed")

        # Return execution summary
        return {
            "workflow_id": self.bmad_orchestrator.workflow_state.workflow_id if self.bmad_orchestrator.workflow_state else None,
            "results": results,
            "total_duration": sum(r.duration for r in self.results),
            "overall_success": all(r.success for r in self.results),
            "execution_log": self.execution_log,
            "final_state": self.bmad_orchestrator.get_workflow_progress()
        }

    def pause_workflow(self) -> bool:
        """Pause the current workflow execution."""
        return self.bmad_orchestrator.pause_workflow()

    def resume_workflow(self) -> bool:
        """Resume the paused workflow execution."""
        return self.bmad_orchestrator.resume_workflow()

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow."""
        return self.bmad_orchestrator.get_workflow_progress()

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get the execution log for debugging and monitoring."""
        return self.execution_log.copy()


class BusinessPhaseHandler(PhaseInterface):
    """Handles the business/requirements analysis phase."""

    def __init__(self, discipline_level: DisciplineLevel):
        self.discipline_level = discipline_level
        self.status = "not_started"

    def execute(self, workflow_state: WorkflowState) -> tuple[bool, str, Dict[str, Any]]:
        """Execute the business/requirements analysis phase."""
        self.status = "executing"
        print(f"Executing Business Phase with discipline level: {self.discipline_level.value}")

        # Simulate requirements analysis work
        time.sleep(1.0)  # Simulate processing time

        # In a real implementation, this would analyze requirements
        # and produce validated requirements output
        requirements_output = {
            "requirements_list": [
                {"id": "REQ001", "title": "User authentication", "priority": "high", "status": "validated"},
                {"id": "REQ002", "title": "Data storage", "priority": "medium", "status": "validated"},
                {"id": "REQ003", "title": "Reporting", "priority": "low", "status": "validated"}
            ],
            "validation_passed": True,
            "confidence_score": 0.95
        }

        self.status = "completed"
        return True, "Business phase completed successfully", {"requirements": requirements_output}

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the business phase."""
        # For the first phase, we mainly need to check if the workflow is initialized
        return input_data is not None

    def get_status(self) -> str:
        """Get the current status of the phase."""
        return self.status


class ArchitecturePhaseHandler(PhaseInterface):
    """Handles the architecture design phase."""

    def __init__(self, discipline_level: DisciplineLevel):
        self.discipline_level = discipline_level
        self.status = "not_started"

    def execute(self, workflow_state: WorkflowState) -> tuple[bool, str, Dict[str, Any]]:
        """Execute the architecture design phase."""
        self.status = "executing"
        print(f"Executing Architecture Phase with discipline level: {self.discipline_level.value}")

        # Simulate architecture design work
        time.sleep(1.0)  # Simulate processing time

        # In a real implementation, this would design architecture
        # based on requirements from the business phase
        architecture_output = {
            "architecture_components": [
                {"name": "User Service", "type": "microservice", "responsibilities": ["authentication", "user management"]},
                {"name": "Data Service", "type": "microservice", "responsibilities": ["data storage", "data retrieval"]},
                {"name": "Reporting Service", "type": "microservice", "responsibilities": ["analytics", "reporting"]}
            ],
            "technology_stack": {
                "frontend": "React",
                "backend": "Node.js/Express",
                "database": "PostgreSQL",
                "message_queue": "Redis"
            },
            "design_patterns": ["MVC", "Observer", "Factory"],
            "validation_passed": True
        }

        self.status = "completed"
        return True, "Architecture phase completed successfully", {"architecture": architecture_output}

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the architecture phase."""
        # Needs requirements from the business phase
        return input_data is not None and 'previous_results' in input_data

    def get_status(self) -> str:
        """Get the current status of the phase."""
        return self.status


class DevelopmentPhaseHandler(PhaseInterface):
    """Handles the development/code generation phase."""

    def __init__(self, discipline_level: DisciplineLevel):
        self.discipline_level = discipline_level
        self.status = "not_started"

    def execute(self, workflow_state: WorkflowState) -> tuple[bool, str, Dict[str, Any]]:
        """Execute the development phase."""
        self.status = "executing"
        print(f"Executing Development Phase with discipline level: {self.discipline_level.value}")

        # Simulate code generation work
        time.sleep(1.0)  # Simulate processing time

        # In a real implementation, this would generate code
        # based on requirements and architecture
        development_output = {
            "generated_files": [
                "src/user_service.js",
                "src/data_service.js",
                "src/reporting_service.js",
                "src/models/user_model.js",
                "src/models/data_model.js",
                "tests/user_service.test.js"
            ],
            "code_quality_score": 0.85,
            "lines_of_code": 1250,
            "validation_passed": True
        }

        self.status = "completed"
        return True, "Development phase completed successfully", {"development": development_output}

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the development phase."""
        # Needs architecture design from the previous phase
        return input_data is not None and 'previous_results' in input_data

    def get_status(self) -> str:
        """Get the current status of the phase."""
        return self.status


class QualityAssurancePhaseHandler(PhaseInterface):
    """Handles the quality assurance phase."""

    def __init__(self, discipline_level: DisciplineLevel):
        self.discipline_level = discipline_level
        self.status = "not_started"

    def execute(self, workflow_state: WorkflowState) -> tuple[bool, str, Dict[str, Any]]:
        """Execute the QA phase."""
        self.status = "executing"
        print(f"Executing Quality Assurance Phase with discipline level: {self.discipline_level.value}")

        # Simulate QA work
        time.sleep(1.0)  # Simulate processing time

        # In a real implementation, this would test and validate
        # the generated code and architecture
        qa_output = {
            "test_results": {
                "passed": 24,
                "failed": 1,
                "skipped": 2
            },
            "code_coverage": 0.87,
            "security_scan_passed": True,
            "performance_metrics": {
                "response_time_avg": 0.23,
                "requests_per_second": 1200
            },
            "validation_passed": True,
            "recommendations": [
                "Improve error handling in user service",
                "Add caching for frequently accessed data"
            ]
        }

        self.status = "completed"
        return True, "QA phase completed successfully", {"qa": qa_output}

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for the QA phase."""
        # Needs development output from the previous phase
        return input_data is not None and 'previous_results' in input_data

    def get_status(self) -> str:
        """Get the current status of the phase."""
        return self.status


def main():
    """Example usage of the workflow orchestrator."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        dcae_dir = project_path / ".dcae"
        dcae_dir.mkdir(parents=True)

        print("=== BMAD Workflow Orchestrator Demo ===")

        # Create orchestrator with balanced discipline level
        orchestrator = WorkflowOrchestrator(str(project_path), DisciplineLevel.BALANCED)

        # Register handlers for each phase
        orchestrator.register_phase_handler(WorkflowPhase.BUSINESS, BusinessPhaseHandler(orchestrator.discipline_level))
        orchestrator.register_phase_handler(WorkflowPhase.ARCHITECTURE, ArchitecturePhaseHandler(orchestrator.discipline_level))
        orchestrator.register_phase_handler(WorkflowPhase.DEVELOPMENT, DevelopmentPhaseHandler(orchestrator.discipline_level))
        orchestrator.register_phase_handler(WorkflowPhase.QUALITY_ASSURANCE, QualityAssurancePhaseHandler(orchestrator.discipline_level))

        # Execute the workflow
        print("Starting BMAD workflow execution...")
        results = orchestrator.execute_workflow(WorkflowPhase.BUSINESS)

        print("\n=== Workflow Execution Summary ===")
        print(f"Workflow ID: {results['workflow_id']}")
        print(f"Overall Success: {results['overall_success']}")
        print(f"Total Duration: {results['total_duration']:.2f}s")
        print(f"Final State: {results['final_state']}")

        print("\nPhase Results:")
        for phase, result in results['results'].items():
            print(f"  {phase}: {'✓' if result['success'] else '✗'} ({result['duration']:.2f}s)")

        print("\nExecution completed successfully!")


if __name__ == "__main__":
    main()