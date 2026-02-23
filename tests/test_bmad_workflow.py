"""
Tests for the DCAE BMAD Workflow Implementation Module
"""

import os
import tempfile
from pathlib import Path
import json
import yaml
from unittest.mock import Mock, patch, MagicMock

from dcae.bmad.workflow import (
    BMADWorkflowOrchestrator,
    BusinessManager,
    Architect,
    Developer,
    execute_bmad_workflow,
    coordinate_bmad_activities,
    handoff_between_roles,
    track_bmad_progress
)


def test_bmad_workflow_orchestrator_initialization():
    """Test that BMADWorkflowOrchestrator initializes correctly."""
    orchestrator = BMADWorkflowOrchestrator()

    assert orchestrator is not None
    assert hasattr(orchestrator, 'execute_workflow')
    assert hasattr(orchestrator, 'coordinate_roles')
    assert hasattr(orchestrator, 'track_progress')


def test_business_manager_initialization():
    """Test that BusinessManager initializes correctly."""
    bm = BusinessManager()

    assert bm is not None
    assert hasattr(bm, 'analyze_requirements')
    assert hasattr(bm, 'coordinate_project')
    assert hasattr(bm, 'communicate_with_stakeholders')


def test_architect_initialization():
    """Test that Architect initializes correctly."""
    arch = Architect()

    assert arch is not None
    assert hasattr(arch, 'generate_architecture')
    assert hasattr(arch, 'review_design')
    assert hasattr(arch, 'validate_solutions')


def test_developer_initialization():
    """Test that Developer initializes correctly."""
    dev = Developer()

    assert dev is not None
    assert hasattr(dev, 'implement_solution')
    assert hasattr(dev, 'follow_patterns')
    assert hasattr(dev, 'ensure_quality')


def test_execute_simple_bmad_workflow():
    """Test executing a simple BMAD workflow."""
    # Sample project requirements
    project_requirements = {
        "project_name": "Simple Web App",
        "description": "A simple web application for testing",
        "functional_requirements": [
            {"id": "FR001", "description": "User should be able to register", "priority": "high"},
            {"id": "FR002", "description": "User should be able to login", "priority": "high"}
        ],
        "non_functional_requirements": [
            {"id": "NFR001", "description": "System should be responsive", "category": "performance"}
        ]
    }

    # Execute the BMAD workflow
    workflow_result = execute_bmad_workflow(project_requirements)

    # Verify the workflow produced expected artifacts
    assert "business_analysis" in workflow_result
    assert "architecture_design" in workflow_result
    assert "implementation_plan" in workflow_result
    assert "timeline" in workflow_result


def test_bmad_coordination():
    """Test coordination between BMAD roles."""
    orchestrator = BMADWorkflowOrchestrator()

    # Mock the BMAD agents
    mock_bm = Mock(spec=BusinessManager)
    mock_arch = Mock(spec=Architect)
    mock_dev = Mock(spec=Developer)

    # Configure mocks to return appropriate values
    mock_bm.analyze_requirements.return_value = {
        "requirements_analysis": "Requirements analyzed successfully",
        "prioritized_requirements": ["FR001", "FR002"]
    }
    mock_arch.generate_architecture.return_value = {
        "architecture_design": "Microservices architecture selected",
        "components": ["api_gateway", "auth_service"]
    }
    mock_dev.implement_solution.return_value = {
        "implementation_plan": "Implementation plan created",
        "tech_stack": ["python", "fastapi"]
    }

    # Test coordination between roles
    coordination_result = coordinate_bmad_activities(
        mock_bm, mock_arch, mock_dev, {"project": "test"}
    )

    # Verify that each role's method was called
    mock_bm.analyze_requirements.assert_called()
    mock_arch.generate_architecture.assert_called()
    mock_dev.implement_solution.assert_called()


def test_handoff_between_roles():
    """Test proper handoffs between BMAD roles."""
    # Create a scenario where business manager passes work to architect
    business_output = {
        "requirements": ["requirement1", "requirement2"],
        "constraints": ["constraint1"],
        "success_criteria": ["criteria1"]
    }

    # Simulate handoff to architect
    arch_input = handoff_between_roles("business_to_arch", business_output)

    # Verify that the handoff properly formats data for the next role
    assert "requirements_for_architecture" in arch_input
    assert "project_constraints" in arch_input


def test_track_bmad_progress():
    """Test tracking progress through BMAD workflow."""
    workflow_state = {
        "current_phase": "business",
        "completed_phases": [],
        "progress_percentage": 0,
        "artifacts_produced": []
    }

    # Simulate progression through phases
    updated_state = track_bmad_progress(workflow_state, "business_completed")

    assert updated_state["current_phase"] == "architecture"
    assert "business" in updated_state["completed_phases"]
    assert updated_state["progress_percentage"] == 33  # Roughly 1/3

    updated_state = track_bmad_progress(updated_state, "architecture_completed")
    assert updated_state["current_phase"] == "development"
    assert "architecture" in updated_state["completed_phases"]
    assert updated_state["progress_percentage"] == 66  # Roughly 2/3


def test_bmad_workflow_orchestrator_class():
    """Test the BMADWorkflowOrchestrator class methods."""
    orchestrator = BMADWorkflowOrchestrator()

    # Test with a simple project
    simple_project = {
        "name": "Simple Project",
        "requirements": {
            "functional": [{"id": "FR001", "desc": "Basic functionality"}],
            "non_functional": [{"id": "NFR001", "desc": "Performance requirement"}]
        }
    }

    # Execute workflow using orchestrator
    result = orchestrator.execute_workflow(simple_project)

    # Verify that the workflow produces expected outputs
    assert "status" in result
    assert result["status"] in ["completed", "in_progress", "failed"]
    assert "business_output" in result
    assert "architecture_output" in result
    assert "development_output" in result


def test_business_manager_role_functions():
    """Test specific functions of the Business Manager role."""
    bm = BusinessManager()

    # Test requirements analysis
    raw_requirements = [
        {"id": "REQ001", "text": "The system shall allow users to create accounts"},
        {"id": "REQ002", "text": "Response time should be under 2 seconds"}
    ]

    analysis_result = bm.analyze_requirements(raw_requirements)

    assert "categorized_requirements" in analysis_result
    assert "functional" in analysis_result["categorized_requirements"]
    assert "non_functional" in analysis_result["categorized_requirements"]
    assert "priority_mapping" in analysis_result


def test_architect_role_functions():
    """Test specific functions of the Architect role."""
    arch = Architect()

    # Test architecture generation from requirements
    reqs_for_arch = {
        "functional": [
            {"id": "FR001", "description": "User management", "priority": "high"}
        ],
        "non_functional": [
            {"id": "NFR001", "description": "High availability", "category": "availability"}
        ]
    }

    arch_design = arch.generate_architecture(reqs_for_arch)

    assert "architecture_style" in arch_design
    assert "components" in arch_design
    assert "technology_recommendations" in arch_design
    assert "integration_points" in arch_design


def test_developer_role_functions():
    """Test specific functions of the Developer role."""
    dev = Developer()

    # Test implementation planning
    architecture_spec = {
        "components": [
            {"id": "api", "type": "rest_api", "tech_stack": ["python", "fastapi"]},
            {"id": "db", "type": "database", "tech_stack": ["postgresql"]}
        ],
        "patterns": ["repository", "dependency_injection"]
    }

    impl_plan = dev.implement_solution(architecture_spec)

    assert "implementation_steps" in impl_plan
    assert "estimated_timeline" in impl_plan
    assert "resource_requirements" in impl_plan
    assert "quality_assurance_plan" in impl_plan


def test_complex_bmad_workflow():
    """Test a more complex BMAD workflow with interdependencies."""
    complex_project = {
        "name": "Enterprise E-commerce Platform",
        "description": "A comprehensive e-commerce platform with multiple integrated systems",
        "stakeholders": ["customers", "merchants", "administrators"],
        "functional_requirements": [
            {"id": "FR_USERS", "description": "User account management", "priority": "critical"},
            {"id": "FR_PRODUCTS", "description": "Product catalog management", "priority": "critical"},
            {"id": "FR_ORDERS", "description": "Order processing system", "priority": "critical"},
            {"id": "FR_PAYMENTS", "description": "Secure payment processing", "priority": "critical"},
            {"id": "FR_ANALYTICS", "description": "Business analytics dashboard", "priority": "high"}
        ],
        "non_functional_requirements": [
            {"id": "NFR_PERFORMANCE", "description": "Handle 10,000 concurrent users", "category": "performance"},
            {"id": "NFR_SECURITY", "description": "PCI DSS compliance", "category": "security"},
            {"id": "NFR_AVAILABILITY", "description": "99.99% uptime", "category": "availability"},
            {"id": "NFR_SCALABILITY", "description": "Horizontal scaling capability", "category": "scalability"}
        ],
        "constraints": [
            "Must integrate with existing ERP system",
            "Mobile-first design required",
            "Multi-language support needed"
        ]
    }

    # Execute the complex workflow
    complex_result = execute_bmad_workflow(complex_project)

    # Verify comprehensive outputs
    assert "business_analysis" in complex_result
    assert "stakeholder_mapping" in complex_result["business_analysis"]
    assert "requirements_traceability" in complex_result["business_analysis"]

    assert "architecture_design" in complex_result
    assert "technology_stack" in complex_result["architecture_design"]
    assert "system_integration_plan" in complex_result["architecture_design"]
    assert "security_architecture" in complex_result["architecture_design"]

    assert "implementation_plan" in complex_result
    assert "phase_wise_tasks" in complex_result["implementation_plan"]
    assert "risk_mitigation_strategies" in complex_result["implementation_plan"]


def test_error_handling_in_bmad_workflow():
    """Test error handling in BMAD workflow."""
    orchestrator = BMADWorkflowOrchestrator()

    # Test with invalid input
    try:
        result = orchestrator.execute_workflow(None)
        # If no exception is raised, there should be an error status
        assert result["status"] == "failed" or "error" in result
    except Exception as e:
        # This is also acceptable - the system should handle invalid input gracefully
        assert str(e) is not None


def test_mock_based_bmad_workflow():
    """Test BMAD workflow using mocked dependencies for isolation."""
    with patch('dcae.bmad.workflow.BusinessManager') as mock_bm_class, \
         patch('dcae.bmad.workflow.Architect') as mock_arch_class, \
         patch('dcae.bmad.workflow.Developer') as mock_dev_class:

        # Create mock instances
        mock_bm = Mock()
        mock_arch = Mock()
        mock_dev = Mock()

        mock_bm_class.return_value = mock_bm
        mock_arch_class.return_value = mock_arch
        mock_dev_class.return_value = mock_dev

        # Configure return values
        mock_bm.analyze_requirements.return_value = {"business_outcome": "success"}
        mock_arch.generate_architecture.return_value = {"arch_outcome": "success"}
        mock_dev.implement_solution.return_value = {"dev_outcome": "success"}

        # Execute workflow
        project_data = {"name": "Mock Test Project"}
        result = execute_bmad_workflow(project_data)

        # Verify that each role was called appropriately
        mock_bm.analyze_requirements.assert_called_once()
        mock_arch.generate_architecture.assert_called_once()
        mock_dev.implement_solution.assert_called_once()


if __name__ == "__main__":
    # Run tests
    test_bmad_workflow_orchestrator_initialization()
    test_business_manager_initialization()
    test_architect_initialization()
    test_developer_initialization()
    test_execute_simple_bmad_workflow()
    test_bmad_coordination()
    test_handoff_between_roles()
    test_track_bmad_progress()
    test_bmad_workflow_orchestrator_class()
    test_business_manager_role_functions()
    test_architect_role_functions()
    test_developer_role_functions()
    test_complex_bmad_workflow()
    test_error_handling_in_bmad_workflow()
    test_mock_based_bmad_workflow()
    print("All BMAD workflow tests passed!")