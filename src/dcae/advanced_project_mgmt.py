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
            print("[SUCCESS] BMAD workflow completed successfully")
            self.logger.log_event("INFO", "BMAD workflow completed successfully", "workflow")
        else:
            print("[ERROR] BMAD workflow failed")
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
                    print(f"[ERROR] Stage {stage} failed")
                    return False

                # Mark stage as completed
                self.config_manager.save_project_state(stage, completed=True)

                # Update progress
                self.progress.update_progress(stage, 100, {"status": "completed"})
                print(f"[SUCCESS] {stage} stage completed")

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

    def pause_workflow(self, reason: str = "manual_pause", additional_data: Dict[str, Any] = None) -> bool:
        """
        Pause the current workflow as per Story 1.4.

        Args:
            reason: Reason for pausing the workflow
            additional_data: Additional data to store with the pause state

        Returns:
            True if successful, False otherwise
        """
        print("Pausing workflow...")

        # Get current state
        current_state = self.config_manager.get_project_state()
        current_stage = current_state.get("current_stage", "unknown")

        # Prepare pause information with comprehensive data
        pause_info = {
            "timestamp": datetime.now().isoformat(),
            "current_stage": current_stage,
            "reason": reason,
            "original_state": current_state,
            "workflow_state": WorkflowState.PAUSED.value,
            "additional_data": additional_data or {},
            "dcae_version": "1.0.0",  # Could be dynamically retrieved
            "environment_info": {
                "platform": sys.platform,
                "python_version": sys.version
            }
        }

        try:
            # Write pause information to file
            self.pause_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pause_file, 'w', encoding='utf-8') as f:
                json.dump(pause_info, f, indent=2, default=str)

            # Update project state to reflect paused status
            self.config_manager.save_project_state(current_stage, completed=False)

            # Log the pause with detailed information
            self.logger.log_event("INFO", f"Workflow paused at stage: {current_stage} (Reason: {reason})", "pause_resume")

            print(f"[SUCCESS] Workflow paused at stage: {current_stage} (Reason: {reason})")
            return True
        except Exception as e:
            self.logger.report_error(f"Failed to pause workflow: {str(e)}", "pause_operation", "ProjectPauseResumeManager")
            print(f"[ERROR] Failed to pause workflow: {str(e)}")
            return False

    def resume_workflow(self) -> bool:
        """
        Resume the paused workflow as per Story 1.4.

        Returns:
            True if successful, False otherwise
        """
        if not self.pause_file.exists():
            print("Error: No paused workflow found")
            return False

        try:
            # Read pause information
            with open(self.pause_file, 'r', encoding='utf-8') as f:
                pause_info = json.load(f)

            # Validate pause information integrity
            if not self._validate_pause_data(pause_info):
                print("Error: Corrupted or invalid pause state data")
                return False

            # Get the stage to resume from
            resume_stage = pause_info.get("current_stage", "business")
            reason = pause_info.get("reason", "unknown")

            print(f"Resuming workflow from stage: {resume_stage} (Paused for: {reason})")

            # Restore any original state information if available
            original_state = pause_info.get("original_state")
            if original_state:
                # Optionally restore the original state, but update current stage to the one we're resuming from
                current_stages = original_state.get("stages", {})
                for stage_name, stage_info in current_stages.items():
                    if stage_name == resume_stage:
                        current_stages[stage_name]["completed"] = False  # Mark as not completed since we're resuming

                # Update state to reflect resumption
                self.config_manager.save_project_state(resume_stage, completed=False)

            # Log the resume with details
            self.logger.log_event("INFO", f"Workflow resuming from stage: {resume_stage} (Paused for: {reason})", "pause_resume")

            # Optionally backup the pause file before removing it
            import shutil
            backup_path = self.pause_file.with_suffix('.json.backup')
            shutil.copy2(self.pause_file, backup_path)

            # Clear the pause file
            self.pause_file.unlink()

            print(f"[SUCCESS] Workflow resumed from stage: {resume_stage}")
            return True
        except json.JSONDecodeError:
            print("[ERROR] Pause state file is corrupted")
            self.logger.report_error("Pause state file is corrupted", "resume_operation", "ProjectPauseResumeManager")
            return False
        except Exception as e:
            print(f"[ERROR] Error resuming workflow: {str(e)}")
            self.logger.report_error(f"Failed to resume workflow: {str(e)}", "resume_operation", "ProjectPauseResumeManager")
            return False

    def _validate_pause_data(self, pause_info: Dict[str, Any]) -> bool:
        """
        Validate the integrity of pause data before using it for resume.

        Args:
            pause_info: Dictionary containing pause information

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["timestamp", "current_stage", "reason", "original_state"]
        for field in required_fields:
            if field not in pause_info:
                self.logger.report_error(f"Missing required field '{field}' in pause data", "validation", "ProjectPauseResumeManager")
                return False

        # Additional validation could go here
        return True

    def is_workflow_paused(self) -> bool:
        """Check if there's a paused workflow."""
        if not self.pause_file.exists():
            return False

        # Additional check: verify the file is not empty and contains valid JSON
        try:
            with open(self.pause_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return False  # Empty file doesn't represent a valid pause
                # Verify it's valid JSON
                json.loads(content)
            return True
        except (json.JSONDecodeError, IOError):
            return False  # Invalid JSON or inaccessible file means not properly paused

    def get_pause_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the paused workflow."""
        if not self.pause_file.exists():
            return None

        try:
            with open(self.pause_file, 'r', encoding='utf-8') as f:
                pause_data = json.load(f)

            # Validate the pause data before returning
            if not self._validate_pause_data(pause_data):
                self.logger.report_error("Pause data validation failed", "get_pause_info", "ProjectPauseResumeManager")
                return None

            return pause_data
        except (json.JSONDecodeError, IOError) as e:
            self.logger.report_error(f"Failed to read pause info: {str(e)}", "get_pause_info", "ProjectPauseResumeManager")
            return None

    def cleanup_pause_state(self) -> bool:
        """Clean up the pause state file after successful resume or manual reset."""
        try:
            if self.pause_file.exists():
                self.pause_file.unlink()
                print("[SUCCESS] Pause state cleaned up successfully")
                return True
            else:
                print("[INFO] No pause state to clean up")
                return True
        except Exception as e:
            self.logger.report_error(f"Failed to clean up pause state: {str(e)}", "cleanup", "ProjectPauseResumeManager")
            return False

    def get_pause_duration(self) -> Optional[float]:
        """Get the duration in seconds since the workflow was paused."""
        pause_info = self.get_pause_info()
        if not pause_info or "timestamp" not in pause_info:
            return None

        try:
            pause_time = datetime.fromisoformat(pause_info["timestamp"].replace('Z', '+00:00'))
            duration = (datetime.now(pause_time.tzinfo) - pause_time).total_seconds()
            return duration
        except ValueError:
            # Handle case where timestamp format isn't standard ISO format
            try:
                # Attempt to parse without timezone
                timestamp_str = pause_info["timestamp"].split('.')[0]  # Remove microseconds if present
                pause_time = datetime.fromisoformat(timestamp_str)
                duration = (datetime.now() - pause_time).total_seconds()
                return duration
            except ValueError:
                self.logger.report_error("Unable to parse pause timestamp", "duration_calc", "ProjectPauseResumeManager")
                return None


class MultipleProjectManager:
    """Manager for handling multiple projects as per Story 1.5."""

    def __init__(self, projects_root: Union[str, Path] = "./dcae-projects"):
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(parents=True, exist_ok=True)
        self.logger = LoggingErrorReporter()
        self.integrate_with_existing_systems()

    def create_new_project(self, project_name: str, project_path: Union[str, Path] = None) -> bool:
        """
        Create a new DCAE project with enhanced organization and configuration.

        Args:
            project_name: Name of the project
            project_path: Path where to create the project (optional)

        Returns:
            True if successful, False otherwise
        """
        if project_path is None:
            # Sanitize project name for use as directory
            sanitized_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            sanitized_name = sanitized_name.replace(" ", "_").lower()

            # Ensure unique project identifier
            project_dir = self.projects_root / sanitized_name
            counter = 1
            original_project_dir = project_dir
            while project_dir.exists():
                project_dir = original_project_dir.parent / f"{original_project_dir.name}_{counter}"
                counter += 1
        else:
            project_dir = Path(project_path)

        # Check if project already exists
        if project_dir.exists() and any(project_dir.iterdir()):
            print(f"Error: Project directory {project_dir} already exists and is not empty")
            return False

        # Create the project directory
        project_dir.mkdir(parents=True, exist_ok=True)

        # Initialize DCAE project structure
        try:
            from .init import initialize_dcae_project
            success = initialize_dcae_project(str(project_dir))

            if success:
                # Generate additional project metadata
                metadata_path = project_dir / ".dcae/metadata.json"
                metadata = {
                    "project_id": f"dcae-{project_dir.name}-{int(datetime.now().timestamp())}",
                    "creation_timestamp": datetime.now().isoformat(),
                    "created_by": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
                    "dcae_version": "1.0.0",
                    "framework_type": "dcae"
                }

                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)

                print(f"[SUCCESS] Project '{project_name}' created at {project_dir}")
                print(f"  - Unique ID: {metadata['project_id']}")
                self.logger.log_event("INFO", f"New project created: {project_name} at {project_dir} with ID {metadata['project_id']}", "project_management")
            else:
                print(f"[ERROR] Failed to create project '{project_name}'")
                self.logger.log_event("ERROR", f"Failed to create project: {project_name}", "project_management")

            return success
        except Exception as e:
            print(f"[ERROR] Error during project creation: {str(e)}")
            self.logger.report_error(f"Failed to create project {project_name}: {str(e)}", "project_creation", "MultipleProjectManager")
            return False

    def get_managed_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of all managed projects with comprehensive details.

        Returns:
            List of project dictionaries with detailed information
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
                        "has_state": state_path.exists(),
                        "directory": item.name,
                        "full_path": str(item.absolute()),
                        "project_type": config.get("project", {}).get("type", "dcae"),
                        "workflow_progress": 0,
                        "workflow_status": "not_started"
                    }

                    # Add state info if available
                    if state_path.exists():
                        with open(state_path, 'r', encoding='utf-8') as f:
                            state = json.load(f)

                        project_info["current_stage"] = state.get("current_stage", "unknown")

                        # Calculate workflow progress
                        stages = state.get("stages", {})
                        completed_stages = 0
                        total_stages = len(stages)
                        for stage_name, stage_info in stages.items():
                            if stage_info.get("completed", False):
                                completed_stages += 1

                        if total_stages > 0:
                            project_info["workflow_progress"] = int((completed_stages / total_stages) * 100)

                        # Determine workflow status
                        if completed_stages == total_stages and total_stages > 0:
                            project_info["workflow_status"] = "completed"
                        elif completed_stages > 0:
                            project_info["workflow_status"] = "in_progress"
                        else:
                            project_info["workflow_status"] = "not_started"

                        project_info["stages"] = stages

                    # Add additional metadata if present
                    metadata_path = item / ".dcae/metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        project_info["metadata"] = metadata

                    # Check for pause state
                    pause_path = item / ".dcae/pause-state.json"
                    if pause_path.exists():
                        project_info["is_paused"] = True
                        try:
                            with open(pause_path, 'r', encoding='utf-8') as f:
                                pause_data = json.load(f)
                            project_info["pause_info"] = pause_data
                        except:
                            project_info["is_paused"] = True
                    else:
                        project_info["is_paused"] = False

                    projects.append(project_info)

        return projects

    def get_project_status(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive status of a specific project.

        Args:
            project_name: Name of the project

        Returns:
            Project status information or None if not found
        """
        projects = self.get_managed_projects()
        for project in projects:
            if project["name"] == project_name or Path(project["path"]).name == project_name:
                # Add additional status information
                status_info = project.copy()

                # Add disk usage information
                try:
                    import subprocess
                    result = subprocess.run(['du', '-sh', str(Path(project["path"]))],
                                          capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        status_info["disk_usage"] = result.stdout.split()[0] if result.stdout else "unknown"
                    else:
                        # Alternative calculation for Windows systems
                        total_size = 0
                        project_path = Path(project["path"])
                        for dirpath, dirnames, filenames in os.walk(project_path):
                            for filename in filenames:
                                filepath = Path(dirpath) / filename
                                try:
                                    total_size += filepath.stat().st_size
                                except:
                                    continue  # Skip files that can't be accessed
                        status_info["disk_usage_bytes"] = total_size
                        # Format as human readable
                        if total_size > 1024**3:
                            status_info["disk_usage"] = f"{total_size / 1024**3:.2f} GB"
                        elif total_size > 1024**2:
                            status_info["disk_usage"] = f"{total_size / 1024**2:.2f} MB"
                        elif total_size > 1024:
                            status_info["disk_usage"] = f"{total_size / 1024:.2f} KB"
                        else:
                            status_info["disk_usage"] = f"{total_size} bytes"
                except:
                    status_info["disk_usage"] = "unable to determine"

                # Add file count information
                try:
                    file_count = sum([len(files) for r, d, files in os.walk(Path(project["path"]))])
                    status_info["file_count"] = file_count
                except:
                    status_info["file_count"] = "unable to determine"

                # Add recent activity information
                try:
                    latest_mod_time = 0
                    project_path = Path(project["path"])
                    for item in project_path.rglob("*"):
                        if item.is_file():
                            mod_time = item.stat().st_mtime
                            if mod_time > latest_mod_time:
                                latest_mod_time = mod_time

                    if latest_mod_time > 0:
                        from datetime import datetime
                        status_info["last_modified"] = datetime.fromtimestamp(latest_mod_time).isoformat()
                    else:
                        status_info["last_modified"] = "unknown"
                except:
                    status_info["last_modified"] = "unknown"

                return status_info

        return None

    def switch_to_project(self, project_path: Union[str, Path]) -> bool:
        """
        Switch working directory to a specific project with proper context management.

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

        # Store current project context before switching (for future state preservation)
        current_dir = Path.cwd()

        # Change to the project directory
        os.chdir(path)
        print(f"[SUCCESS] Switched to project: {path}")

        # Update environment to reflect new project configuration
        # This would typically involve updating the configuration manager to point to the new project
        try:
            from .project_config import ProjectConfigManager
            config_manager = ProjectConfigManager(path)

            # Log the project switch
            self.logger.log_event("INFO", f"Switched to project: {path.name}", "project_management")

            return True
        except Exception as e:
            # If there's an issue, revert back to previous directory
            os.chdir(current_dir)
            print(f"Error: Could not fully initialize new project context: {e}")
            self.logger.report_error(f"Failed to switch project context: {str(e)}", "project_switch", "MultipleProjectManager")
            return False

    def remove_project(self, project_name: str, confirm: bool = True) -> bool:
        """
        Remove a project with comprehensive safety checks and confirmation.

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

        # Perform safety checks
        if project_to_remove.get("is_paused", False):
            print(f"Warning: Project '{project_name}' is currently paused. This may affect workflow continuity.")

        # Additional safety check for active processes could go here in a real implementation

        if confirm:
            print(f"About to remove project '{project_name}' located at: {project_to_remove['path']}")
            print(f"This will delete {project_to_remove.get('file_count', 'an unknown number of')} files.")
            response = input(f"Are you sure you want to remove this project? This will delete ALL project files. (Type 'DELETE {project_name.upper()}' to confirm): ")

            if response != f'DELETE {project_name.upper()}':
                print("Project removal cancelled - confirmation did not match exactly.")
                return False

        try:
            import shutil
            shutil.rmtree(project_to_remove["path"])
            print(f"[SUCCESS] Project '{project_name}' removed successfully")
            self.logger.log_event("INFO", f"Project removed: {project_name}", "project_management")
            return True
        except Exception as e:
            print(f"Error removing project: {e}")
            self.logger.report_error(f"Failed to remove project {project_name}: {str(e)}", "removal", "project_management")
            return False


    def integrate_with_existing_systems(self):
        """
        Integrate with existing DCAE components to ensure consistency.

        This ensures compatibility with ProjectConfigManager, BMADWorkflowController,
        logging and error reporting systems, and state management patterns.
        """
        # Integration with ProjectConfigManager is handled through the initialization process
        # Each project's configuration is automatically managed by ProjectConfigManager

        # Integration with logging and error reporting
        self.logger.log_event("INFO", "MultipleProjectManager initialized and integrated with DCAE systems", "integration")

        # Integration with state management is handled automatically through the .dcae/state.json files
        # Integration with workflow management is available through BMADWorkflowController when switching projects

        return True


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
        print(f"[SUCCESS] Performance statistics collection {status}")
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

            print(f"[SUCCESS] Performance statistics exported to {export_file}")
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


def pause_current_project(reason: str = "manual_pause"):
    """Pause the current project workflow as per Story 1.4."""
    manager = ProjectPauseResumeManager()
    return manager.pause_workflow(reason)


def resume_current_project():
    """Resume the current project workflow as per Story 1.4."""
    manager = ProjectPauseResumeManager()
    return manager.resume_workflow()


def is_project_paused():
    """Check if the current project is paused as per Story 1.4."""
    manager = ProjectPauseResumeManager()
    return manager.is_workflow_paused()


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

    print("[SUCCESS] Sample performance statistics collected")
    return stats_manager.get_summary()


def manage_projects_interactively():
    """Interactive function to manage multiple projects with comprehensive menu."""
    print("DCAE Multiple Project Manager")
    print("=" * 40)

    manager = MultipleProjectManager()

    while True:
        print("\nOptions:")
        print("1. List projects")
        print("2. Create new project")
        print("3. Switch to project")
        print("4. Remove project")
        print("5. Show project status")
        print("6. View project details")
        print("7. Start workflow in project")
        print("8. Show all projects summary")
        print("9. Back to main menu")

        choice = input("\nSelect an option (1-9): ").strip()

        if choice == "1":
            projects = manager.get_managed_projects()
            if projects:
                print(f"\nFound {len(projects)} project(s):")
                print(f"{'#':<3} {'Name':<20} {'Workflow':<15} {'Progress':<10} {'Status':<12} {'Paused':<8}")
                print("-" * 75)
                for i, proj in enumerate(projects, 1):
                    name = proj.get('name', 'Unknown')[:18]
                    current_stage = proj.get('current_stage', 'Unknown')
                    progress = f"{proj.get('workflow_progress', 0)}%"
                    status = proj.get('workflow_status', 'unknown')
                    paused = "Yes" if proj.get('is_paused', False) else "No"

                    print(f"{i:<3} {name:<20} {current_stage:<15} {progress:<10} {status:<12} {paused:<8}")
            else:
                print("No projects found.")

        elif choice == "2":
            project_name = input("Enter project name: ").strip()
            if project_name:
                manager.create_new_project(project_name)

        elif choice == "3":
            projects = manager.get_managed_projects()
            if not projects:
                print("No projects found. Create a project first.")
                continue

            print("\nAvailable projects:")
            for i, proj in enumerate(projects, 1):
                print(f"  {i}. {proj['name']}")

            selection = input("Enter project number or name: ").strip()
            if selection.isdigit():
                idx = int(selection) - 1
                if 0 <= idx < len(projects):
                    project_path = projects[idx]['path']
                    manager.switch_to_project(project_path)
                else:
                    print("Invalid selection.")
            else:
                # Assume it's a project name
                manager.switch_to_project(selection)

        elif choice == "4":
            project_name = input("Enter project name to remove: ").strip()
            if project_name:
                manager.remove_project(project_name)

        elif choice == "5":
            project_name = input("Enter project name: ").strip()
            if project_name:
                status = manager.get_project_status(project_name)
                if status:
                    print(f"\nProject Status Details for '{project_name}':")
                    print(f"  Name: {status.get('name', 'Unknown')}")
                    print(f"  Path: {status.get('path', 'Unknown')}")
                    print(f"  Current Stage: {status.get('current_stage', 'Unknown')}")
                    print(f"  Workflow Progress: {status.get('workflow_progress', 0)}%")
                    print(f"  Workflow Status: {status.get('workflow_status', 'Not Started')}")
                    print(f"  Is Paused: {'Yes' if status.get('is_paused', False) else 'No'}")
                    print(f"  Disk Usage: {status.get('disk_usage', 'Unknown')}")
                    print(f"  File Count: {status.get('file_count', 'Unknown')}")
                    print(f"  Last Modified: {status.get('last_modified', 'Unknown')}")
                else:
                    print(f"Project '{project_name}' not found.")

        elif choice == "6":  # View detailed project information
            project_name = input("Enter project name to view details: ").strip()
            if project_name:
                status = manager.get_project_status(project_name)
                if status:
                    print(f"\nDetailed Information for '{project_name}':")
                    print(f"  Full Path: {status.get('full_path', 'Unknown')}")
                    print(f"  Directory Name: {status.get('directory', 'Unknown')}")
                    print(f"  Created Date: {status.get('created_date', 'Unknown')}")
                    print(f"  Version: {status.get('version', 'Unknown')}")

                    if 'stages' in status:
                        print(f"  Stages: {len(status['stages'])} defined")
                        for stage_name, stage_info in status['stages'].items():
                            completed = "[DONE]" if stage_info.get('completed', False) else "[TODO]"
                            timestamp = stage_info.get('timestamp', 'No timestamp')
                            print(f"    {completed} {stage_name}: {timestamp}")
                else:
                    print(f"Project '{project_name}' not found.")

        elif choice == "7":  # Start workflow in specific project
            project_name = input("Enter project name to start workflow: ").strip()
            if project_name:
                projects = manager.get_managed_projects()
                project_found = False
                for proj in projects:
                    if proj['name'] == project_name or Path(proj['path']).name == project_name:
                        # Temporarily switch to the project and start workflow
                        original_dir = Path.cwd()
                        try:
                            os.chdir(proj['path'])
                            controller = BMADWorkflowController(proj['path'])
                            print(f"Starting workflow in project '{project_name}'...")
                            success = controller.start_workflow()
                            if success:
                                print("Workflow started successfully!")
                            else:
                                print("Failed to start workflow.")
                        finally:
                            os.chdir(original_dir)
                        project_found = True
                        break
                if not project_found:
                    print(f"Project '{project_name}' not found.")

        elif choice == "8":  # Show all projects summary
            projects = manager.get_managed_projects()
            if projects:
                print(f"\nProjects Summary Report:")
                print(f"Total Projects: {len(projects)}")

                # Calculate stats
                total_paused = sum(1 for p in projects if p.get('is_paused', False))
                total_completed = sum(1 for p in projects if p.get('workflow_status') == 'completed')
                total_in_progress = sum(1 for p in projects if p.get('workflow_status') == 'in_progress')
                total_not_started = sum(1 for p in projects if p.get('workflow_status') == 'not_started')

                print(f"Projects Completed: {total_completed}")
                print(f"Projects In Progress: {total_in_progress}")
                print(f"Projects Not Started: {total_not_started}")
                print(f"Projects Paused: {total_paused}")

                # Calculate average progress
                if projects:
                    avg_progress = sum(p.get('workflow_progress', 0) for p in projects) / len(projects)
                    print(f"Average Workflow Progress: {avg_progress:.1f}%")
            else:
                print("No projects found.")

        elif choice == "9":
            break
        else:
            print("Invalid option. Please select 1-9.")
        print()  # Extra newline for readability


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