"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Advanced Project Management Module

This module implements advanced project management features as specified in
Epic #1: Project Setup & Management, specifically:
- Story 1.3: Start BMAD Workflow
- Story 1.4: Pause/Resume Projects
- Story 1.5: Manage Multiple Projects
- Story 1.8: Performance Statistics

As a developer,
I want advanced project management capabilities,
so that I can efficiently manage multiple DCAE projects and control their workflows.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from enum import Enum

from .config_management import DCAEConfig, DisciplineLevel
from .project_config import ProjectConfigManager, ProgressIndicator, LoggingErrorReporter


class WorkflowState(Enum):
    """Enumeration for workflow states."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class BMADWorkflowController:
    """Controller for starting and managing BMAD workflows as per Story 1.3."""

    def __init__(self, project_path: Union[str, Path] = "."):
        self.project_path = Path(project_path)
        self.config_manager = ProjectConfigManager(project_path)
        self.logger = LoggingErrorReporter()
        self.progress = ProgressIndicator()

    def start_workflow(self, stage_override: str = None) -> bool:
        """
        Start the BMAD workflow as per Story 1.3.

        Args:
            stage_override: Specific stage to start from (optional)

        Returns:
            True if successful, False otherwise
        """
        print("Starting BMAD Workflow...")

        # Check if we're in a valid DCAE project
        if not self._is_valid_project():
            print("Error: Not in a valid DCAE project directory")
            return False

        # Update project state to indicate workflow is running
        current_stage = stage_override or "business"
        self.config_manager.save_project_state(current_stage, completed=False)

        # Log the workflow start
        self.logger.log_event("INFO", f"BMAD workflow started at stage: {current_stage}", "workflow")

        # Update progress indicator
        self.progress.update_progress(current_stage, 0, {"status": "started"})

        # Execute the workflow stages
        success = self._execute_workflow_stages(current_stage)

        if success:
            print("✓ BMAD workflow completed successfully")
            self.logger.log_event("INFO", "BMAD workflow completed successfully", "workflow")
        else:
            print("✗ BMAD workflow failed")
            self.logger.log_event("ERROR", "BMAD workflow failed", "workflow")

        return success

    def _is_valid_project(self) -> bool:
        """Check if the current directory contains a valid DCAE project."""
        config_path = self.project_path / ".dcae/config.yaml"
        state_path = self.project_path / ".dcae/state.json"
        return config_path.exists() and state_path.exists()

    def _execute_workflow_stages(self, start_stage: str = "business") -> bool:
        """Execute the BMAD workflow stages."""
        stages = ["business", "architecture", "development", "quality_assurance"]
        start_idx = max(0, stages.index(start_stage) if start_stage in stages else 0)

        try:
            for i in range(start_idx, len(stages)):
                stage = stages[i]
                print(f"Executing {stage} stage...")

                # Update progress
                progress_percent = int((i + 1) / len(stages) * 100)
                self.progress.update_progress(stage, progress_percent, {"status": "in_progress"})

                # Execute the stage
                success = self._execute_single_stage(stage)
                if not success:
                    print(f"✗ Stage {stage} failed")
                    return False

                # Mark stage as completed
                self.config_manager.save_project_state(stage, completed=True)

                # Update progress
                self.progress.update_progress(stage, 100, {"status": "completed"})
                print(f"✓ {stage} stage completed")

            return True
        except Exception as e:
            self.logger.report_error(str(e), "workflow_execution", "BMADController")
            return False

    def _execute_single_stage(self, stage: str) -> bool:
        """Execute a single stage of the BMAD workflow."""
        # This would normally execute the actual BMAD process for each stage
        # For now, we'll simulate with delays and logging

        stage_simulations = {
            "business": lambda: self._simulate_business_stage(),
            "architecture": lambda: self._simulate_architecture_stage(),
            "development": lambda: self._simulate_development_stage(),
            "quality_assurance": lambda: self._simulate_qa_stage()
        }

        simulation = stage_simulations.get(stage)
        if simulation:
            try:
                simulation()
                return True
            except Exception as e:
                self.logger.report_error(f"Stage {stage} execution failed: {str(e)}", "stage_execution", stage)
                return False
        else:
            self.logger.report_error(f"Unknown stage: {stage}", "stage_execution", "workflow")
            return False

    def _simulate_business_stage(self):
        """Simulate the business (requirements) stage."""
        print("  Running business stage (requirements analysis)...")
        # Simulate business stage work
        self.logger.log_event("INFO", "Business stage: Requirements analysis", "business")

    def _simulate_architecture_stage(self):
        """Simulate the architecture stage."""
        print("  Running architecture stage (system design)...")
        # Simulate architecture stage work
        self.logger.log_event("INFO", "Architecture stage: System design", "architecture")

    def _simulate_development_stage(self):
        """Simulate the development stage."""
        print("  Running development stage (implementation)...")
        # Simulate development stage work
        self.logger.log_event("INFO", "Development stage: Implementation", "development")

    def _simulate_qa_stage(self):
        """Simulate the quality assurance stage."""
        print("  Running QA stage (testing and validation)...")
        # Simulate QA stage work
        self.logger.log_event("INFO", "QA stage: Testing and validation", "quality_assurance")


class ProjectPauseResumeManager:
    """Manager for pausing and resuming projects as per Story 1.4."""

    def __init__(self, project_path: Union[str, Path] = "."):
        self.project_path = Path(project_path)
        self.config_manager = ProjectConfigManager(project_path)
        self.logger = LoggingErrorReporter()
        self.pause_file = self.project_path / ".dcae/pause-state.json"

    def pause_workflow(self) -> bool:
        """
        Pause the current workflow as per Story 1.4.

        Returns:
            True if successful, False otherwise
        """
        print("Pausing workflow...")

        # Get current state
        current_state = self.config_manager.get_project_state()
        current_stage = current_state.get("current_stage", "unknown")

        # Save pause information
        pause_info = {
            "timestamp": datetime.now().isoformat(),
            "current_stage": current_stage,
            "reason": "manual_pause",
            "original_state": current_state
        }

        # Write pause information to file
        self.pause_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pause_file, 'w', encoding='utf-8') as f:
            json.dump(pause_info, f, indent=2)

        # Update state to paused
        self.config_manager.save_project_state(current_stage, completed=False)

        # Log the pause
        self.logger.log_event("INFO", f"Workflow paused at stage: {current_stage}", "pause_resume")

        print(f"✓ Workflow paused at stage: {current_stage}")
        return True

    def resume_workflow(self) -> bool:
        """
        Resume the paused workflow as per Story 1.4.

        Returns:
            True if successful, False otherwise
        """
        if not self.pause_file.exists():
            print("Error: No paused workflow found")
            return False

        # Read pause information
        with open(self.pause_file, 'r', encoding='utf-8') as f:
            pause_info = json.load(f)

        # Get the stage to resume from
        resume_stage = pause_info.get("current_stage", "business")
        print(f"Resuming workflow from stage: {resume_stage}")

        # Log the resume
        self.logger.log_event("INFO", f"Workflow resuming from stage: {resume_stage}", "pause_resume")

        # Clear the pause file
        self.pause_file.unlink()

        # Update state to show resumed
        self.config_manager.save_project_state(resume_stage, completed=False)

        print(f"✓ Workflow resumed from stage: {resume_stage}")
        return True

    def is_workflow_paused(self) -> bool:
        """Check if there's a paused workflow."""
        return self.pause_file.exists()

    def get_pause_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the paused workflow."""
        if not self.pause_file.exists():
            return None

        with open(self.pause_file, 'r', encoding='utf-8') as f:
            return json.load(f)


class MultipleProjectManager:
    """Manager for handling multiple projects as per Story 1.5."""

    def __init__(self, projects_root: Union[str, Path] = "./dcae-projects"):
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(parents=True, exist_ok=True)
        self.logger = LoggingErrorReporter()

    def create_new_project(self, project_name: str, project_path: Union[str, Path] = None) -> bool:
        """
        Create a new DCAE project.

        Args:
            project_name: Name of the project
            project_path: Path where to create the project (optional)

        Returns:
            True if successful, False otherwise
        """
        if project_path is None:
            project_dir = self.projects_root / project_name.replace(" ", "_").lower()
        else:
            project_dir = Path(project_path)

        # Check if project already exists
        if project_dir.exists() and any(project_dir.iterdir()):
            print(f"Error: Project directory {project_dir} already exists and is not empty")
            return False

        # Create the project directory
        project_dir.mkdir(parents=True, exist_ok=True)

        # Initialize DCAE project structure
        from .init import initialize_dcae_project
        success = initialize_dcae_project(str(project_dir))

        if success:
            print(f"✓ Project '{project_name}' created at {project_dir}")
            self.logger.log_event("INFO", f"New project created: {project_name} at {project_dir}", "project_management")
        else:
            print(f"✗ Failed to create project '{project_name}'")
            self.logger.log_event("ERROR", f"Failed to create project: {project_name}", "project_management")

        return success

    def get_managed_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of all managed projects.

        Returns:
            List of project dictionaries with details
        """
        projects = []

        for item in self.projects_root.iterdir():
            if item.is_dir():
                config_path = item / ".dcae/config.yaml"
                state_path = item / ".dcae/state.json"

                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)

                    project_info = {
                        "name": config.get("project", {}).get("name", item.name),
                        "path": str(item),
                        "version": config.get("project", {}).get("version", "unknown"),
                        "created_date": config.get("project", {}).get("created_date", "unknown"),
                        "has_state": state_path.exists()
                    }

                    # Add state info if available
                    if state_path.exists():
                        with open(state_path, 'r', encoding='utf-8') as f:
                            state = json.load(f)
                        project_info["current_stage"] = state.get("current_stage", "unknown")
                        project_info["stages"] = state.get("stages", {})

                    projects.append(project_info)

        return projects

    def get_project_status(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific project.

        Args:
            project_name: Name of the project

        Returns:
            Project status information or None if not found
        """
        projects = self.get_managed_projects()
        for project in projects:
            if project["name"] == project_name or Path(project["path"]).name == project_name:
                return project

        return None

    def switch_to_project(self, project_path: Union[str, Path]) -> bool:
        """
        Switch working directory to a specific project.

        Args:
            project_path: Path to the project

        Returns:
            True if successful, False otherwise
        """
        path = Path(project_path)
        if not path.exists() or not path.is_dir():
            print(f"Error: Project path {path} does not exist")
            return False

        config_path = path / ".dcae/config.yaml"
        if not config_path.exists():
            print(f"Error: {path} is not a valid DCAE project directory")
            return False

        # Change to the project directory
        os.chdir(path)
        print(f"✓ Switched to project: {path}")
        return True

    def remove_project(self, project_name: str, confirm: bool = True) -> bool:
        """
        Remove a project (with confirmation).

        Args:
            project_name: Name of the project to remove
            confirm: Whether to ask for confirmation

        Returns:
            True if successful, False otherwise
        """
        projects = self.get_managed_projects()
        project_to_remove = None

        for project in projects:
            if project["name"] == project_name or Path(project["path"]).name == project_name:
                project_to_remove = project
                break

        if not project_to_remove:
            print(f"Error: Project '{project_name}' not found")
            return False

        if confirm:
            response = input(f"Are you sure you want to remove project '{project_name}'? This will delete all project files. (y/N): ")
            if response.lower() != 'y':
                print("Project removal cancelled")
                return False

        try:
            import shutil
            shutil.rmtree(project_to_remove["path"])
            print(f"✓ Project '{project_name}' removed successfully")
            self.logger.log_event("INFO", f"Project removed: {project_name}", "project_management")
            return True
        except Exception as e:
            print(f"Error removing project: {e}")
            self.logger.report_error(f"Failed to remove project {project_name}: {str(e)}", "removal", "project_management")
            return False


class PerformanceStatisticsManager:
    """Manager for collecting and managing performance statistics as per Story 1.8."""

    def __init__(self, project_path: Union[str, Path] = "."):
        self.project_path = Path(project_path)
        self.stats_file = self.project_path / ".dcae/performance-stats.json"
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = LoggingErrorReporter()

        # Initialize stats file if it doesn't exist
        if not self.stats_file.exists():
            self._initialize_stats_file()

    def _initialize_stats_file(self):
        """Initialize the performance statistics file."""
        initial_stats = {
            "collection_enabled": True,
            "last_collection": None,
            "metrics": {
                "execution_times": [],
                "resource_usage": [],
                "error_rates": [],
                "throughput": []
            },
            "summary": {
                "total_executions": 0,
                "average_execution_time": 0,
                "error_rate": 0,
                "last_updated": datetime.now().isoformat()
            }
        }

        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(initial_stats, f, indent=2)

    def record_metric(self, metric_type: str, value: Union[int, float], unit: str = "",
                      context: Dict[str, Any] = None):
        """
        Record a performance metric.

        Args:
            metric_type: Type of metric (execution_time, resource_usage, etc.)
            value: Value of the metric
            unit: Unit of measurement
            context: Additional context about the metric
        """
        if not self.stats_file.exists():
            self._initialize_stats_file()

        with open(self.stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        if not stats["collection_enabled"]:
            return

        # Create metric entry
        metric_entry = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }

        # Add to appropriate metric collection
        if metric_type not in stats["metrics"]:
            stats["metrics"][metric_type] = []

        stats["metrics"][metric_type].append(metric_entry)

        # Keep only last 1000 entries per metric type to manage file size
        if len(stats["metrics"][metric_type]) > 1000:
            stats["metrics"][metric_type] = stats["metrics"][metric_type][-1000:]

        # Update summary
        stats["summary"]["total_executions"] += 1
        stats["summary"]["last_updated"] = datetime.now().isoformat()

        # Calculate average execution time if this is an execution time metric
        if metric_type == "execution_times":
            exec_times = [m["value"] for m in stats["metrics"]["execution_times"]]
            if exec_times:
                stats["summary"]["average_execution_time"] = sum(exec_times) / len(exec_times)

        # Calculate error rate if this is an error rate metric
        if metric_type == "error_rates":
            error_rates = [m["value"] for m in stats["metrics"]["error_rates"]]
            if error_rates:
                stats["summary"]["error_rate"] = sum(error_rates) / len(error_rates)

        # Update last collection timestamp
        stats["last_collection"] = datetime.now().isoformat()

        # Save updated statistics
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        self.logger.log_event("INFO", f"Recorded metric: {metric_type} = {value}{unit}", "performance")

    def get_statistics(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        if not self.stats_file.exists():
            self._initialize_stats_file()

        with open(self.stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of performance statistics."""
        stats = self.get_statistics()
        return stats.get("summary", {})

    def enable_collection(self, enable: bool = True):
        """Enable or disable performance statistics collection."""
        if not self.stats_file.exists():
            self._initialize_stats_file()

        with open(self.stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        stats["collection_enabled"] = enable

        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        status = "enabled" if enable else "disabled"
        print(f"✓ Performance statistics collection {status}")
        self.logger.log_event("INFO", f"Performance statistics collection {status}", "performance")

    def export_statistics(self, export_path: Union[str, Path]) -> bool:
        """
        Export performance statistics to a file.

        Args:
            export_path: Path to export the statistics

        Returns:
            True if successful, False otherwise
        """
        try:
            stats = self.get_statistics()

            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, default=str)

            print(f"✓ Performance statistics exported to {export_file}")
            self.logger.log_event("INFO", f"Performance statistics exported to {export_file}", "performance")
            return True
        except Exception as e:
            print(f"Error exporting statistics: {e}")
            self.logger.report_error(f"Failed to export statistics: {str(e)}", "export", "performance")
            return False


# Convenience functions for Epic #1 stories
def start_bmad_workflow(project_path: str = ".", stage: str = None):
    """Start the BMAD workflow as per Story 1.3."""
    controller = BMADWorkflowController(project_path)
    return controller.start_workflow(stage)


def pause_current_project():
    """Pause the current project workflow as per Story 1.4."""
    manager = ProjectPauseResumeManager()
    return manager.pause_workflow()


def resume_current_project():
    """Resume the current project workflow as per Story 1.4."""
    manager = ProjectPauseResumeManager()
    return manager.resume_workflow()


def create_new_dcae_project(project_name: str, projects_root: str = "./dcae-projects"):
    """Create a new DCAE project as part of Story 1.5."""
    manager = MultipleProjectManager(projects_root)
    return manager.create_new_project(project_name)


def list_managed_projects(projects_root: str = "./dcae-projects"):
    """List all managed projects as per Story 1.5."""
    manager = MultipleProjectManager(projects_root)
    return manager.get_managed_projects()


def collect_performance_statistics():
    """Collect performance statistics as per Story 1.8."""
    stats_manager = PerformanceStatisticsManager()

    # Example metrics collection
    import random
    import time

    # Simulate some performance metrics
    execution_time = random.uniform(1.0, 10.0)
    cpu_usage = random.uniform(10.0, 90.0)
    error_rate = random.uniform(0.0, 5.0)

    stats_manager.record_metric("execution_times", execution_time, "seconds",
                               {"stage": "simulation", "operation": "calculation"})
    stats_manager.record_metric("resource_usage", cpu_usage, "% CPU",
                               {"stage": "simulation", "resource": "cpu"})
    stats_manager.record_metric("error_rates", error_rate, "%",
                               {"stage": "simulation", "type": "processing"})

    print("✓ Sample performance statistics collected")
    return stats_manager.get_summary()


def manage_projects_interactively():
    """Interactive function to manage multiple projects."""
    print("DCAE Multiple Project Manager")
    print("=" * 35)

    manager = MultipleProjectManager()

    while True:
        print("\nOptions:")
        print("1. List projects")
        print("2. Create new project")
        print("3. Switch to project")
        print("4. Remove project")
        print("5. Show project status")
        print("6. Back to main menu")

        choice = input("\nSelect an option (1-6): ").strip()

        if choice == "1":
            projects = manager.get_managed_projects()
            if projects:
                print(f"\nFound {len(projects)} project(s):")
                for i, proj in enumerate(projects, 1):
                    print(f"  {i}. {proj['name']} - {proj['current_stage'] if 'current_stage' in proj else 'Unknown'}")
            else:
                print("No projects found.")

        elif choice == "2":
            project_name = input("Enter project name: ").strip()
            if project_name:
                manager.create_new_project(project_name)

        elif choice == "3":
            project_name = input("Enter project name or path: ").strip()
            if project_name:
                manager.switch_to_project(project_name)

        elif choice == "4":
            project_name = input("Enter project name to remove: ").strip()
            if project_name:
                manager.remove_project(project_name)

        elif choice == "5":
            project_name = input("Enter project name: ").strip()
            if project_name:
                status = manager.get_project_status(project_name)
                if status:
                    print(f"\nProject Status: {status}")
                else:
                    print(f"Project '{project_name}' not found.")

        elif choice == "6":
            break
        else:
            print("Invalid option. Please select 1-6.")


def main():
    """Main function to handle advanced project management CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="DCAE Advanced Project Management Tool"
    )

    parser.add_argument(
        "action",
        choices=[
            "start-workflow", "pause-workflow", "resume-workflow",
            "create-project", "list-projects", "switch-project",
            "remove-project", "collect-stats", "manage-projects",
            "show-stats"
        ],
        help="Advanced project management action to perform"
    )

    parser.add_argument("--project-path", help="Path to project directory")
    parser.add_argument("--project-name", help="Project name")
    parser.add_argument("--stage", help="Specific stage to start from")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive actions")
    parser.add_argument("--export-path", help="Path to export statistics")

    args = parser.parse_args()

    project_path = args.project_path or "."

    if args.action == "start-workflow":
        controller = BMADWorkflowController(project_path)
        success = controller.start_workflow(args.stage)
        sys.exit(0 if success else 1)

    elif args.action == "pause-workflow":
        manager = ProjectPauseResumeManager(project_path)
        success = manager.pause_workflow()
        sys.exit(0 if success else 1)

    elif args.action == "resume-workflow":
        manager = ProjectPauseResumeManager(project_path)
        success = manager.resume_workflow()
        sys.exit(0 if success else 1)

    elif args.action == "create-project":
        if not args.project_name:
            print("Error: --project-name is required for create-project")
            sys.exit(1)

        manager = MultipleProjectManager()
        success = manager.create_new_project(args.project_name)
        sys.exit(0 if success else 1)

    elif args.action == "list-projects":
        manager = MultipleProjectManager()
        projects = manager.get_managed_projects()
        print(f"Managed projects ({len(projects)}):")
        for proj in projects:
            print(f"  - {proj['name']} ({proj['current_stage'] if 'current_stage' in proj else 'unknown'})")

    elif args.action == "switch-project":
        if not args.project_path:
            print("Error: --project-path is required for switch-project")
            sys.exit(1)

        manager = MultipleProjectManager()
        success = manager.switch_to_project(args.project_path)
        sys.exit(0 if success else 1)

    elif args.action == "remove-project":
        if not args.project_name:
            print("Error: --project-name is required for remove-project")
            sys.exit(1)

        manager = MultipleProjectManager()
        success = manager.remove_project(args.project_name, confirm=not args.confirm)
        sys.exit(0 if success else 1)

    elif args.action == "collect-stats":
        summary = collect_performance_statistics()
        print("Current Statistics Summary:")
        print(json.dumps(summary, indent=2))

    elif args.action == "show-stats":
        stats_manager = PerformanceStatisticsManager(project_path)
        stats = stats_manager.get_statistics()
        print("Performance Statistics:")
        print(json.dumps(stats, indent=2))

    elif args.action == "manage-projects":
        manage_projects_interactively()


if __name__ == "__main__":
    main()