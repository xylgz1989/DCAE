"""
Tests for the DCAE Epic #1: Project Setup & Management Module
"""

import os
import tempfile
import shutil
from pathlib import Path
import json
import yaml
from datetime import datetime
import pytest

from dcae.project_config import (
    ProjectConfigManager,
    GlobalSettingsManager,
    APIKeyManager,
    SettingsUpdater,
    LoggingErrorReporter,
    ProgressIndicator,
    configure_project_management_features,
    pause_project_workflow,
    resume_project_workflow,
    manage_multiple_projects
)
from dcae.advanced_project_mgmt import (
    BMADWorkflowController,
    ProjectPauseResumeManager,
    MultipleProjectManager,
    PerformanceStatisticsManager,
    start_bmad_workflow,
    pause_current_project,
    resume_current_project,
    is_project_paused,
    create_new_dcae_project,
    list_managed_projects,
    collect_performance_statistics
)
from dcae.config_management import DCAEConfig, ConfigurationManager, DisciplineLevel


def test_project_config_manager_initialization():
    """Test ProjectConfigManager initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure first
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        # Now test ProjectConfigManager
        config_mgr = ProjectConfigManager(project_path)

        assert config_mgr is not None
        assert config_mgr.project_path == project_path
        assert config_mgr.config_path.exists()


def test_project_configuration():
    """Test configuring project settings."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_mgr = ProjectConfigManager(project_path)

        # Test getting project info
        info = config_mgr.get_project_info()
        assert "name" in info
        assert "version" in info

        # Test configuring project settings
        settings = {
            "dcae.bmad_workflow.discipline_level": "strict",
            "dcae.bmad_workflow.consensus_enabled": True
        }

        success = config_mgr.configure_project_settings(settings)
        assert success is True

        # Verify settings were applied
        assert config_mgr.config.get("dcae.bmad_workflow.discipline_level") == "strict"
        assert config_mgr.config.get("dcae.bmad_workflow.consensus_enabled") is True


def test_discipline_level_management():
    """Test discipline level management."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_mgr = ProjectConfigManager(project_path)

        # Test updating discipline level
        success = config_mgr.update_discipline_level(DisciplineLevel.STRICT)
        assert success is True

        # Verify the change
        current_level = config_mgr.get_current_discipline_level()
        assert current_level == DisciplineLevel.STRICT


def test_project_state_management():
    """Test project state management."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_mgr = ProjectConfigManager(project_path)

        # Test saving project state
        success = config_mgr.save_project_state("business", completed=True)
        assert success is True

        # Test getting project state
        state = config_mgr.get_project_state()
        assert "stages" in state
        assert "business" in state["stages"]
        assert state["stages"]["business"]["completed"] is True


def test_global_settings_manager():
    """Test GlobalSettingsManager functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_path = project_path / ".dcae/config.yaml"
        global_mgr = GlobalSettingsManager(config_path)

        # Test configuring global settings
        settings = {
            "dcae.bmad_workflow.discipline_level": "balanced",
            "dcae.logging.level": "DEBUG"
        }

        success = global_mgr.configure_global_settings(settings)
        assert success is True

        # Verify settings
        settings_out = global_mgr.get_global_settings()
        assert settings_out["discipline_level"] == "balanced"
        assert settings_out["log_level"] == "DEBUG"


def test_api_key_manager():
    """Test APIKeyManager functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_path = project_path / ".dcae/config.yaml"
        api_mgr = APIKeyManager(config_path)

        # Test setting an API key
        success = api_mgr.set_api_key("openai", "test-api-key-123", enable=True)
        assert success is True

        # Verify the key was set
        status = api_mgr.get_api_key_status()
        assert "openai" in status
        assert status["openai"]["enabled"] is True
        assert status["openai"]["has_key"] is True

        # Test getting enabled providers
        enabled = api_mgr.get_enabled_providers()
        assert "openai" in enabled

        # Test removing an API key
        success = api_mgr.remove_api_key("openai")
        assert success is True


def test_settings_updater():
    """Test SettingsUpdater functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_path = project_path / ".dcae/config.yaml"
        updater = SettingsUpdater(config_path)

        # Test updating settings live
        settings = {
            "dcae.logging.level": "WARNING",
            "dcae.bmad_workflow.performance_stats.collection_interval_minutes": 10
        }

        success = updater.update_settings_live(settings)
        assert success is True


def test_logging_error_reporter():
    """Test LoggingErrorReporter functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_path = project_path / ".dcae/config.yaml"
        logger = LoggingErrorReporter(config_path)

        # Test configuring logging
        success = logger.configure_logging(level="INFO", file_output=True, console_output=True)
        assert success is True

        # Test logging an event
        logger.log_event("INFO", "Test log message", "test")

        # Test reporting an error
        logger.report_error("Test error message", "test_error", "test_component", "test_context")


def test_progress_indicator():
    """Test ProgressIndicator functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_path = project_path / ".dcae/config.yaml"
        progress = ProgressIndicator(config_path)

        # Test updating progress
        progress.update_progress("business", 50, {"step": "requirements_gathering"})

        # Test recording performance stat
        progress.record_performance_stat("execution_time", 5.25, "seconds", datetime.now())

        # Test getting current indicators
        indicators = progress.get_current_indicators()
        assert "workflow_progress" in indicators
        assert "performance_stats" in indicators


def test_configure_project_management_features():
    """Test the configure_project_management_features function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        # Change to the project directory temporarily
        original_cwd = os.getcwd()
        os.chdir(project_path)

        try:
            managers = configure_project_management_features()

            # Verify all managers are returned
            assert "project_config" in managers
            assert "global_settings" in managers
            assert "api_manager" in managers
            assert "settings_updater" in managers
            assert "logger" in managers
            assert "progress" in managers

            # Test that an API key can be set using the returned manager
            api_manager = managers["api_manager"]
            success = api_manager.set_api_key("openai", "test-key", enable=True)
            assert success is True
        finally:
            os.chdir(original_cwd)


def test_bmad_workflow_controller_initialization():
    """Test BMADWorkflowController initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        controller = BMADWorkflowController(project_path)

        assert controller is not None
        assert controller.project_path == project_path


def test_project_pause_resume_manager():
    """Test ProjectPauseResumeManager functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        pause_mgr = ProjectPauseResumeManager(project_path)

        # Initially, no workflow should be paused
        assert pause_mgr.is_workflow_paused() is False
        assert pause_mgr.get_pause_info() is None

        # Test pausing workflow
        success = pause_mgr.pause_workflow("test_pause_reason")
        assert success is True
        assert pause_mgr.is_workflow_paused() is True

        # Get pause info
        pause_info = pause_mgr.get_pause_info()
        assert pause_info is not None
        assert "current_stage" in pause_info
        assert "reason" in pause_info
        assert pause_info["reason"] == "test_pause_reason"
        assert "timestamp" in pause_info
        assert "workflow_state" in pause_info

        # Test getting pause duration
        duration = pause_mgr.get_pause_duration()
        assert duration is not None
        assert isinstance(duration, (int, float))

        # Test resuming workflow
        success = pause_mgr.resume_workflow()
        assert success is True
        assert pause_mgr.is_workflow_paused() is False

        # After resume, pause info should be gone
        assert pause_mgr.get_pause_info() is None


def test_project_pause_resume_manager_with_validation():
    """Test ProjectPauseResumeManager functionality with data validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        pause_mgr = ProjectPauseResumeManager(project_path)

        # Test pausing with additional data
        additional_data = {"test_key": "test_value", "nested": {"inner": "value"}}
        success = pause_mgr.pause_workflow("validation_test", additional_data)
        assert success is True
        assert pause_mgr.is_workflow_paused() is True

        # Verify pause info contains additional data
        pause_info = pause_mgr.get_pause_info()
        assert pause_info is not None
        assert "additional_data" in pause_info
        assert pause_info["additional_data"]["test_key"] == "test_value"
        assert pause_info["additional_data"]["nested"]["inner"] == "value"


def test_project_pause_resume_manager_edge_cases():
    """Test ProjectPauseResumeManager edge cases and error handling."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        pause_mgr = ProjectPauseResumeManager(project_path)

        # Test resuming when no pause file exists
        success = pause_mgr.resume_workflow()
        assert success is False

        # Test pause and resume cycle
        success = pause_mgr.pause_workflow()
        assert success is True

        # Test attempting to pause again (should still work)
        success = pause_mgr.pause_workflow("second_pause")
        assert success is True

        # Resume successfully
        success = pause_mgr.resume_workflow()
        assert success is True


def test_project_pause_resume_manager_corrupted_data():
    """Test ProjectPauseResumeManager with corrupted pause data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        pause_mgr = ProjectPauseResumeManager(project_path)

        # Create a corrupted pause file
        pause_mgr.pause_file.parent.mkdir(parents=True, exist_ok=True)
        with open(pause_mgr.pause_file, 'w', encoding='utf-8') as f:
            f.write("{invalid json")

        # Should handle corrupted data gracefully
        assert pause_mgr.is_workflow_paused() is False
        assert pause_mgr.get_pause_info() is None

        # Clean up the corrupted file
        if pause_mgr.pause_file.exists():
            pause_mgr.pause_file.unlink()


def test_project_pause_resume_convenience_functions():
    """Test the convenience functions for pause/resume."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        # Change to the project directory temporarily
        original_cwd = os.getcwd()
        os.chdir(project_path)

        try:
            # Test pause convenience function
            success = pause_current_project("convenience_test")
            assert success is True

            # Check if project is paused using convenience function
            assert is_project_paused() is True

            # Resume using convenience function
            success = resume_current_project()
            assert success is True

            # Check if project is no longer paused
            assert is_project_paused() is False
        finally:
            os.chdir(original_cwd)


def test_multiple_project_manager_enhanced():
    """Test MultipleProjectManager enhanced functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        projects_root = Path(temp_dir) / "projects"

        mgr = MultipleProjectManager(projects_root)

        # Test creating a new project with unique ID
        success = mgr.create_new_project("test_project_enhanced")
        assert success is True

        # Test listing projects with enhanced details
        projects = mgr.get_managed_projects()
        assert len(projects) >= 1
        project_names = [p["name"] for p in projects]
        assert "test_project_enhanced" in project_names

        # Check that enhanced project details are present
        for project in projects:
            if project["name"] == "test_project_enhanced":
                assert "workflow_progress" in project
                assert "workflow_status" in project
                assert "is_paused" in project
                break

        # Test project status functionality
        status = mgr.get_project_status("test_project_enhanced")
        assert status is not None
        assert status["name"] == "test_project_enhanced"
        assert "disk_usage" in status
        assert "file_count" in status

        # Test integration method
        integration_success = mgr.integrate_with_existing_systems()
        assert integration_success is True


def test_multiple_project_manager_comprehensive():
    """Test MultipleProjectManager comprehensive functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        projects_root = Path(temp_dir) / "projects"

        mgr = MultipleProjectManager(projects_root)

        # Test creating multiple projects
        success1 = mgr.create_new_project("comprehensive_test_1")
        success2 = mgr.create_new_project("comprehensive_test_2")
        assert success1 is True
        assert success2 is True

        # Verify unique project IDs
        projects = mgr.get_managed_projects()
        project_ids = [p.get("metadata", {}).get("project_id") for p in projects if p["name"].startswith("comprehensive_test")]
        assert len(set(project_ids)) == 2  # Ensure unique IDs
        assert all(pid is not None for pid in project_ids)

        # Test switch functionality
        # Find one of the created projects
        test_project = next(p for p in projects if p["name"] == "comprehensive_test_1")
        original_dir = os.getcwd()
        try:
            success = mgr.switch_to_project(test_project["path"])
            assert success is True
        finally:
            os.chdir(original_dir)

        # Test project removal with enhanced safety
        # First try with wrong confirmation to ensure safety works
        import io
        import sys
        from unittest.mock import patch

        # Test removal with incorrect confirmation
        with patch('builtins.input', return_value='WRONG_CONFIRMATION'):
            success = mgr.remove_project("comprehensive_test_2", confirm=True)
            assert success is False  # Should fail with wrong confirmation

        # Verify project still exists
        projects_after_wrong = mgr.get_managed_projects()
        project_names_after_wrong = [p["name"] for p in projects_after_wrong]
        assert "comprehensive_test_2" in project_names_after_wrong

        # Now test with correct confirmation
        correct_confirm = f'DELETE COMPREHENSIVE_TEST_2'
        with patch('builtins.input', return_value=correct_confirm):
            success = mgr.remove_project("comprehensive_test_2", confirm=True)
            assert success is True

        # Verify project was removed
        projects_after = mgr.get_managed_projects()
        project_names_after = [p["name"] for p in projects_after]
        assert "comprehensive_test_2" not in project_names_after


def test_performance_statistics_manager():
    """Test PerformanceStatisticsManager functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        stats_mgr = PerformanceStatisticsManager(project_path)

        # Test recording a metric
        stats_mgr.record_metric("execution_time", 3.14, "seconds",
                               {"stage": "test", "operation": "calculation"})

        # Test getting statistics
        stats = stats_mgr.get_statistics()
        assert "metrics" in stats
        assert "execution_times" in stats["metrics"]

        # Test getting summary
        summary = stats_mgr.get_summary()
        assert "total_executions" in summary


def test_collect_performance_statistics():
    """Test the collect_performance_statistics function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        # Change to the project directory temporarily
        original_cwd = os.getcwd()
        os.chdir(project_path)

        try:
            summary = collect_performance_statistics()

            # Verify that summary contains expected keys
            assert "total_executions" in summary
            assert "last_updated" in summary
        finally:
            os.chdir(original_cwd)


def test_config_file_structure():
    """Test that the configuration file has the expected structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        config_path = project_path / ".dcae/config.yaml"

        # Load the config and verify structure
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Verify expected top-level sections exist
        assert "project" in config
        assert "dcae" in config

        # Verify expected subsections
        assert "bmad_workflow" in config["dcae"]
        assert "llm_providers" in config["dcae"]
        assert "logging" in config["dcae"]

        # Verify expected llm providers
        providers = config["dcae"]["llm_providers"]
        expected_providers = ["openai", "anthropic", "qwen", "glm"]
        for provider in expected_providers:
            assert provider in providers
            assert "enabled" in providers[provider]
            assert "api_key" in providers[provider]


def test_state_file_structure():
    """Test that the state file has the expected structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Initialize DCAE project structure
        from dcae.init import initialize_dcae_project
        initialize_dcae_project(str(project_path))

        state_path = project_path / ".dcae/state.json"

        # Load the state and verify structure
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # Verify expected structure
        assert "current_stage" in state
        assert "stages" in state
        assert "business" in state["stages"]
        assert "architecture" in state["stages"]
        assert "development" in state["stages"]
        assert "quality_assurance" in state["stages"]

        for stage in state["stages"]:
            assert "completed" in state["stages"][stage]
            assert "timestamp" in state["stages"][stage]


if __name__ == "__main__":
    # Run tests
    test_project_config_manager_initialization()
    test_project_configuration()
    test_discipline_level_management()
    test_project_state_management()
    test_global_settings_manager()
    test_api_key_manager()
    test_settings_updater()
    test_logging_error_reporter()
    test_progress_indicator()
    test_configure_project_management_features()
    test_bmad_workflow_controller_initialization()
    test_project_pause_resume_manager()
    test_multiple_project_manager_enhanced()
    test_multiple_project_manager_comprehensive()
    test_performance_statistics_manager()
    test_collect_performance_statistics()
    test_config_file_structure()
    test_state_file_structure()
    print("All Epic #1: Project Setup & Management tests passed!")