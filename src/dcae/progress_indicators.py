"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Progress Indicators Module

This module implements progress tracking and performance metrics functionality as specified in
Epic #1: Project Setup & Management, Story 1.11: Progress Indicators

As a DCAE user,
I want to see clear progress indicators during development workflows,
So that I can track the status and completion of various tasks and phases in my project.

"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict
from enum import Enum


class ProgressStage(Enum):
    """Enumeration of workflow stages for progress tracking."""
    INITIAL = "initial"
    BUSINESS_ANALYSIS = "business_analysis"
    REQUIREMENTS = "requirements"
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"


@dataclass
class ProgressData:
    """Data class representing progress for a specific stage."""
    stage: ProgressStage
    progress: int  # Percentage 0-100
    updated: str
    details: Dict[str, Any]

    def __post_init__(self):
        # Clamp progress between 0 and 100
        self.progress = max(0, min(100, self.progress))

    def to_dict(self):
        """Convert to dictionary representation suitable for JSON serialization."""
        return {
            "stage": self.stage.value,
            "progress": self.progress,  # Already clamped in __post_init__
            "updated": self.updated,
            "details": self.details
        }


@dataclass
class PerformanceStat:
    """Data class representing a performance metric."""
    name: str
    value: Union[int, float, str]
    unit: str
    recorded: str

    def to_dict(self):
        """Convert to dictionary representation suitable for JSON serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "recorded": self.recorded
        }


class ProgressIndicator:
    """Advanced progress tracking and performance metrics system."""

    def __init__(self, config_path: Union[str, Path] = ".dcae/config.yaml",
                 indicators_path: Union[str, Path] = None):
        """
        Initialize the progress indicator system.

        Args:
            config_path: Path to DCAE configuration file
            indicators_path: Path to indicators file (default: .dcae/indicators.json)
        """
        self.config_path = Path(config_path)
        self.indicators_file = Path(indicators_path) if indicators_path else Path(".dcae/indicators.json")
        self.indicators_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize indicators file if it doesn't exist
        if not self.indicators_file.exists():
            self._initialize_indicators()

    def _initialize_indicators(self):
        """Initialize the indicators file with default values."""
        default_indicators = {
            "performance_stats": {
                "enabled": True,  # Default to enabled
                "collection_interval_minutes": 5,
                "stats": {},
                "last_collection": None
            },
            "workflow_progress": {
                "current_stage": ProgressStage.INITIAL.value,
                "overall_progress": 0,
                "stage_progress": {},
                "started_at": datetime.now().isoformat()
            },
            "display_options": {
                "enabled": True,
                "verbosity": "standard",  # minimal, standard, detailed
                "show_percentage": True,
                "show_eta": False
            }
        }

        with open(self.indicators_file, 'w', encoding='utf-8') as f:
            json.dump(default_indicators, f, indent=2)

    def update_progress(self, stage: Union[str, ProgressStage],
                       progress: int,
                       details: Dict[str, Any] = None) -> bool:
        """
        Update progress for a specific stage.

        Args:
            stage: Stage name or ProgressStage enum
            progress: Progress percentage (0-100)
            details: Additional details about the progress

        Returns:
            True if update was successful
        """
        try:
            if isinstance(stage, str):
                # Convert string to ProgressStage enum if possible
                try:
                    stage_enum = ProgressStage(stage.lower().replace(' ', '_'))
                except ValueError:
                    stage_enum = ProgressStage.DEVELOPMENT  # fallback
            else:
                stage_enum = stage

            if not self.indicators_file.exists():
                self._initialize_indicators()

            with open(self.indicators_file, 'r', encoding='utf-8') as f:
                indicators = json.load(f)

            stage_key = stage_enum.value

            # Create progress data
            progress_data = ProgressData(
                stage=stage_enum,
                progress=min(max(progress, 0), 100),  # Clamp between 0-100
                updated=datetime.now().isoformat(),
                details=details or {}
            )

            # Update stage progress
            indicators["workflow_progress"]["stage_progress"][stage_key] = progress_data.to_dict()

            # Calculate overall progress
            stages = indicators["workflow_progress"]["stage_progress"]
            if stages:
                total_progress = sum(stage_data["progress"] for stage_data in stages.values())
                overall_progress = total_progress / len(stages)
                indicators["workflow_progress"]["overall_progress"] = round(overall_progress, 2)

            # Update current stage
            indicators["workflow_progress"]["current_stage"] = stage_key

            # Save updated indicators
            with open(self.indicators_file, 'w', encoding='utf-8') as f:
                json.dump(indicators, f, indent=2)

            # Display progress if enabled and verbosity allows
            if self._is_display_enabled():
                self._display_progress(stage_key, progress, details)

            return True
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
            return False

    def _display_progress(self, stage: str, progress: int, details: Dict[str, Any] = None):
        """Display progress to console based on verbosity level."""
        with open(self.indicators_file, 'r', encoding='utf-8') as f:
            indicators = json.load(f)

        verbosity = indicators.get("display_options", {}).get("verbosity", "standard")
        show_percentage = indicators.get("display_options", {}).get("show_percentage", True)

        if verbosity == "minimal":
            # Only show stage transitions
            if progress in [0, 100]:
                print(f"{'->' if progress == 0 else 'OK'} {stage.replace('_', ' ').title()}")
        elif verbosity == "standard":
            if show_percentage:
                print(f"Progress: {stage.replace('_', ' ').title()} - {progress}% complete")
            else:
                print(f"Processing: {stage.replace('_', ' ').title()}")
        elif verbosity == "detailed":
            print(f"Detailed Progress: {stage.replace('_', ' ').title()} - {progress}% complete")
            if details:
                for key, value in details.items():
                    print(f"  {key}: {value}")

    def record_performance_stat(self, stat_name: str,
                               value: Union[int, float, str],
                               unit: str = "",
                               timestamp: datetime = None) -> bool:
        """
        Record a performance statistic.

        Args:
            stat_name: Name of the statistic
            value: Value of the statistic
            unit: Unit of measurement
            timestamp: Timestamp for the recording (defaults to now)

        Returns:
            True if recording was successful
        """
        try:
            if not self.indicators_file.exists():
                self._initialize_indicators()

            with open(self.indicators_file, 'r', encoding='utf-8') as f:
                indicators = json.load(f)

            if not indicators["performance_stats"]["enabled"]:
                return True  # Successfully "did nothing" when disabled

            if timestamp is None:
                timestamp = datetime.now()

            # Create stats entry
            stat_entry = PerformanceStat(
                name=stat_name,
                value=value,
                unit=unit,
                recorded=timestamp.isoformat()
            ).to_dict()

            # Add to stats collection
            if "stats" not in indicators["performance_stats"]:
                indicators["performance_stats"]["stats"] = {}

            if stat_name not in indicators["performance_stats"]["stats"]:
                indicators["performance_stats"]["stats"][stat_name] = []

            # Add the new entry
            indicators["performance_stats"]["stats"][stat_name].append(stat_entry)

            # Limit history to last 1000 entries per stat to prevent unlimited growth
            if len(indicators["performance_stats"]["stats"][stat_name]) > 1000:
                indicators["performance_stats"]["stats"][stat_name] = \
                    indicators["performance_stats"]["stats"][stat_name][-1000:]

            # Update last collection timestamp
            indicators["performance_stats"]["last_collection"] = timestamp.isoformat()

            # Save updated indicators
            with open(self.indicators_file, 'w', encoding='utf-8') as f:
                json.dump(indicators, f, indent=2)

            return True
        except Exception as e:
            print(f"Error recording performance stat: {str(e)}")
            return False

    def get_current_indicators(self) -> Dict[str, Any]:
        """Get current progress and performance indicators."""
        if not self.indicators_file.exists():
            self._initialize_indicators()

        with open(self.indicators_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of progress indicators."""
        indicators = self.get_current_indicators()

        summary = {
            "overall_progress": indicators["workflow_progress"]["overall_progress"],
            "current_stage": indicators["workflow_progress"]["current_stage"],
            "stages": [],
            "performance_stats_enabled": indicators["performance_stats"]["enabled"],
            "started_at": indicators["workflow_progress"].get("started_at", "unknown")
        }

        for stage, data in indicators["workflow_progress"]["stage_progress"].items():
            summary["stages"].append({
                "stage": stage,
                "progress": data["progress"],
                "updated": data["updated"],
                "completed": data["progress"] >= 100
            })

        return summary

    def display_progress_summary(self):
        """Display a summary of current progress indicators."""
        summary = self.get_progress_summary()

        print("\n" + "="*50)
        print("DCAE Progress Indicators Summary")
        print("="*50)
        print(f"Overall Progress: {summary['overall_progress']}%")
        print(f"Current Stage: {summary['current_stage'].replace('_', ' ').title()}")
        print(f"Started: {summary['started_at']}")

        print("\nStage Progress:")
        for stage_info in summary["stages"]:
            status = "OK" if stage_info["completed"] else "->"
            print(f"  {status} {stage_info['stage'].replace('_', ' ').title()}: "
                  f"{stage_info['progress']}%")

        if summary["performance_stats_enabled"]:
            print(f"\nPerformance Stats: Enabled")
            with open(self.indicators_file, 'r', encoding='utf-8') as f:
                indicators = json.load(f)
            last_collected = indicators["performance_stats"].get("last_collection", "None")
            print(f"Last Collection: {last_collected}")
        else:
            print(f"\nPerformance Stats: Disabled")

        print("="*50)

    def get_stage_completion_rate(self, stage: Union[str, ProgressStage]) -> int:
        """Get completion percentage for a specific stage."""
        stage_key = stage.value if isinstance(stage, ProgressStage) else stage
        indicators = self.get_current_indicators()

        stage_progress = indicators["workflow_progress"]["stage_progress"].get(stage_key, {})
        return stage_progress.get("progress", 0)

    def is_stage_complete(self, stage: Union[str, ProgressStage]) -> bool:
        """Check if a specific stage is complete."""
        return self.get_stage_completion_rate(stage) >= 100

    def get_performance_stats(self, stat_name: str = None) -> Dict[str, Any]:
        """
        Get performance statistics, either all or for a specific metric.

        Args:
            stat_name: Specific stat name to retrieve, or None for all stats

        Returns:
            Dictionary containing requested statistics
        """
        indicators = self.get_current_indicators()
        all_stats = indicators["performance_stats"]["stats"]

        if stat_name:
            return all_stats.get(stat_name, [])
        else:
            return all_stats

    def calculate_eta(self) -> Optional[float]:
        """
        Calculate estimated time of completion based on progress rate.
        Currently a placeholder implementation.

        Returns:
            Estimated time remaining in seconds, or None if unable to calculate
        """
        # This would be enhanced with more sophisticated time tracking
        # For now, returning None to indicate it's not yet implemented
        return None

    def _is_display_enabled(self) -> bool:
        """Check if progress display is enabled."""
        indicators = self.get_current_indicators()
        return indicators.get("display_options", {}).get("enabled", True)


# Example usage and demonstration
def demo_progress_indicators():
    """Demonstrate the progress indicators functionality."""
    print("Demo: DCAE Progress Indicators")
    print("-" * 30)

    # Initialize the progress indicator system
    progress_indicator = ProgressIndicator()

    # Simulate progress through different stages
    print("\n1. Starting requirements gathering...")
    progress_indicator.update_progress(ProgressStage.REQUIREMENTS, 0,
                                     {"task": "initial_analysis", "total_tasks": 5})

    time.sleep(0.5)  # Simulate work

    for i in range(1, 6):
        progress = i * 20
        progress_indicator.update_progress(ProgressStage.REQUIREMENTS, progress,
                                         {"task": f"req_task_{i}", "completed": i, "total": 5})
        time.sleep(0.2)  # Simulate work

    print("\n2. Moving to architecture design...")
    progress_indicator.update_progress(ProgressStage.ARCHITECTURE, 0,
                                     {"phase": "design", "subtasks": 3})

    for i in range(1, 4):
        progress = i * 33
        progress_indicator.update_progress(ProgressStage.ARCHITECTURE, progress,
                                         {"task": f"arch_task_{i}", "completed": i, "total": 3})
        time.sleep(0.3)  # Simulate work

    print("\n3. Starting development phase...")
    progress_indicator.update_progress(ProgressStage.DEVELOPMENT, 0,
                                     {"features_planned": 10, "features_completed": 0})

    for i in range(1, 11):
        progress = i * 10
        progress_indicator.update_progress(ProgressStage.DEVELOPMENT, progress,
                                         {"feature": f"feature_{i}", "completed": i, "total": 10})
        time.sleep(0.1)  # Simulate work

    print("\n4. Recording performance statistics...")
    progress_indicator.record_performance_stat("lines_of_code", 1250, "LOC")
    progress_indicator.record_performance_stat("files_created", 23, "files")
    progress_indicator.record_performance_stat("test_coverage", 87.5, "%")

    print("\n5. Final progress summary:")
    progress_indicator.display_progress_summary()


if __name__ == "__main__":
    demo_progress_indicators()