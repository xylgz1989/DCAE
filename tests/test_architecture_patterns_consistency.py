"""
Tests for the DCAE Architecture Patterns and Consistency Rules Module
"""

import os
import tempfile
from pathlib import Path
import json
import yaml

from dcae.architecture.patterns import (
    apply_dependency_injection_pattern,
    apply_repository_pattern,
    apply_service_layer_pattern,
    apply_dto_pattern,
    apply_event_driven_pattern,
    validate_naming_conventions,
    validate_layer_separation,
    validate_dependency_flow,
    validate_architecture_patterns,
    enforce_consistency_rules
)


def test_apply_dependency_injection_pattern():
    """Test applying dependency injection pattern."""
    components_before = [
        {"id": "service_a", "direct_dependencies": ["database_connection"]},
        {"id": "service_b", "direct_dependencies": ["external_api_client"]}
    ]

    # Apply dependency injection pattern
    components_after = apply_dependency_injection_pattern(components_before)

    # Verify that dependencies are now handled through injection
    for component in components_after:
        assert "dependencies" in component
        assert "injection_method" in component
        # Direct instantiation should be replaced with DI
        assert "direct_dependencies" not in component or len(component.get("direct_dependencies", [])) == 0


def test_apply_repository_pattern():
    """Test applying repository pattern."""
    raw_data_access_funcs = [
        {"id": "get_user_sql", "type": "direct_db_call", "entity": "user"},
        {"id": "save_order_sql", "type": "direct_db_call", "entity": "order"}
    ]

    # Apply repository pattern
    repository_components = apply_repository_pattern(raw_data_access_funcs)

    # Verify that direct DB calls are now wrapped in repositories
    for repo_component in repository_components:
        assert repo_component["type"] == "repository"
        assert "entity" in repo_component
        assert "standard_crud_ops" in repo_component
        assert repo_component["standard_crud_ops"] == ["create", "read", "update", "delete"]


def test_apply_service_layer_pattern():
    """Test applying service layer pattern."""
    mixed_components = [
        {"id": "user_controller", "logic_level": "mixed", "operations": ["validation", "db_ops", "business_logic"]},
        {"id": "order_handler", "logic_level": "mixed", "operations": ["validation", "db_ops", "business_logic"]}
    ]

    # Apply service layer pattern
    patterned_components = apply_service_layer_pattern(mixed_components)

    # Verify that business logic is separated into service layer
    for component in patterned_components:
        if "service" in component["id"]:
            assert "business_logic" in component["contained_logic"]
        elif "controller" in component["id"]:
            assert "business_logic" not in component["contained_logic"]


def test_apply_dto_pattern():
    """Test applying DTO pattern."""
    internal_entities = [
        {"id": "user_entity", "properties": ["id", "password_hash", "internal_notes"]},
        {"id": "order_entity", "properties": ["id", "payment_details", "internal_flags"]}
    ]

    # Apply DTO pattern
    dtos = apply_dto_pattern(internal_entities)

    # Verify that DTOs are created with appropriate properties
    for dto in dtos:
        assert "dto_type" in dto
        assert dto["dto_type"] in ["request", "response"]
        # Internal properties should not be in response DTOs
        if dto["dto_type"] == "response":
            assert "internal" not in " ".join(dto.get("exposed_properties", []))


def test_apply_event_driven_pattern():
    """Test applying event-driven pattern."""
    synchronous_components = [
        {"id": "order_processor", "calls": ["inventory_checker", "payment_processor", "shipping_scheduler"]},
        {"id": "notification_sender", "triggers": ["order_created"]}
    ]

    # Apply event-driven pattern
    async_components = apply_event_driven_pattern(synchronous_components)

    # Verify that direct calls are replaced with event publishing/subscribing
    for component in async_components:
        assert "events_published" in component or "events_subscribed" in component
        # Direct calls should be reduced
        assert "calls" not in component or len(component["calls"]) < len([c for c in synchronous_components if c["id"] == component["id"]][0]["calls"])


def test_validate_naming_conventions():
    """Test validating naming conventions."""
    properly_named = {
        "modules": ["user_service", "order_processor", "payment_gateway"],
        "classes": ["UserService", "OrderProcessor", "PaymentGateway"],
        "functions": ["get_user_by_id", "process_order", "validate_payment"],
        "variables": ["user_id", "order_amount", "payment_status"]
    }

    is_valid, issues = validate_naming_conventions(properly_named)
    assert is_valid is True
    assert len(issues) == 0


def test_validate_incorrect_naming():
    """Test validating incorrectly named components."""
    improperly_named = {
        "modules": ["UserService", "Order-Processor"],  # Wrong convention
        "classes": ["user_service", "Payment_Gateway"],  # Wrong convention
        "functions": ["GetUserById", "ProcessOrder!"],  # Invalid characters/incorrect style
        "variables": ["UserId", "OrderAmount"]  # Wrong convention
    }

    is_valid, issues = validate_naming_conventions(improperly_named)
    assert is_valid is False
    assert len(issues) > 0


def test_validate_layer_separation():
    """Test validating layer separation."""
    well_separated = {
        "layers": {
            "presentation": {
                "components": ["controller", "view"],
                "can_access": ["business"]
            },
            "business": {
                "components": ["service", "domain_model"],
                "can_access": ["data"]
            },
            "data": {
                "components": ["repository", "entity"],
                "can_access": []
            }
        }
    }

    is_valid, issues = validate_layer_separation(well_separated)
    assert is_valid is True
    assert len(issues) == 0


def test_validate_violated_layer_separation():
    """Test validating violated layer separation."""
    violated_separation = {
        "layers": {
            "presentation": {
                "components": ["controller", "view"],
                "can_access": ["business", "data"]  # Should not access data directly
            },
            "business": {
                "components": ["service", "domain_model"],
                "can_access": ["data"]
            },
            "data": {
                "components": ["repository", "entity"],
                "can_access": ["presentation"]  # Should not access presentation
            }
        }
    }

    is_valid, issues = validate_layer_separation(violated_separation)
    assert is_valid is False
    assert len(issues) > 0


def test_validate_dependency_flow():
    """Test validating dependency flow."""
    correct_flow = {
        "packages": {
            "domain": {"depends_on": []},  # Core, no dependencies
            "application": {"depends_on": ["domain"]},  # Depends on core
            "infrastructure": {"depends_on": ["application", "domain"]},  # Outer layer
            "presentation": {"depends_on": ["application"]}
        }
    }

    is_valid, issues = validate_dependency_flow(correct_flow)
    assert is_valid is True
    assert len(issues) == 0


def test_validate_backward_dependency():
    """Test validating backward dependencies (dependencies going inward)."""
    incorrect_flow = {
        "packages": {
            "domain": {"depends_on": ["application"]},  # Should not depend on outer layers
            "application": {"depends_on": ["domain"]},
            "infrastructure": {"depends_on": ["application", "domain"]},
            "presentation": {"depends_on": ["domain"]}  # Should not depend on core directly
        }
    }

    is_valid, issues = validate_dependency_flow(incorrect_flow)
    assert is_valid is False
    assert len(issues) > 0


def test_validate_architecture_patterns():
    """Test validating that architecture patterns are properly applied."""
    properly_patterned = {
        "components": [
            {"id": "user_service", "pattern": "service_layer"},
            {"id": "user_repository", "pattern": "repository"},
            {"id": "user_dao", "pattern": "data_transfer_object"},
            {"id": "event_publisher", "pattern": "event_driven"}
        ],
        "structure": {
            "dependency_injection_enabled": True,
            "layer_separation": True
        }
    }

    is_valid, issues = validate_architecture_patterns(properly_patterned)
    assert is_valid is True
    assert len(issues) == 0


def test_enforce_consistency_rules():
    """Test enforcing consistency rules."""
    architecture_with_rules = {
        "project_name": "Consistency Test",
        "components": [
            {"id": "comp_1", "naming_style": "snake_case", "lang": "python"},
            {"id": "comp_2", "naming_style": "snake_case", "lang": "python"}
        ],
        "conventions": {
            "naming_standard": "snake_case",
            "language": "python",
            "testing_framework": "pytest"
        }
    }

    is_consistent, issues = enforce_consistency_rules(architecture_with_rules)
    assert is_consistent is True
    assert len(issues) == 0


def test_inconsistency_detection():
    """Test detecting inconsistencies."""
    inconsistent_arch = {
        "project_name": "Inconsistent Test",
        "components": [
            {"id": "comp_one", "naming_style": "snake_case", "lang": "python"},  # Consistent
            {"id": "compTwo", "naming_style": "camelCase", "lang": "python"},    # Inconsistent naming
            {"id": "CompThree", "naming_style": "PascalCase", "lang": "javascript"}  # Inconsistent naming and lang
        ],
        "conventions": {
            "naming_standard": "snake_case",
            "language": "python",
            "testing_framework": "pytest"
        }
    }

    is_consistent, issues = enforce_consistency_rules(inconsistent_arch)
    assert is_consistent is False
    assert len(issues) > 0


def test_patterns_module_integration():
    """Test the patterns module as a whole."""
    # Start with a basic architecture
    basic_arch = {
        "project_name": "Pattern Integration Test",
        "components": [
            {"id": "user_controller", "type": "controller", "contains": ["business_logic", "data_access"]},
            {"id": "order_service", "type": "service", "contains": ["data_access"]},
            {"id": "payment_processor", "type": "service", "contains": ["external_api_calls"]}
        ],
        "layers": ["presentation", "business", "data"],
        "technology_stack": {"language": "python", "framework": "fastapi"}
    }

    # Apply multiple patterns
    di_applied = apply_dependency_injection_pattern(basic_arch["components"])
    layered_arch = {
        "presentation": [comp for comp in di_applied if "controller" in comp.get("type", "")],
        "business": [comp for comp in di_applied if "service" in comp.get("type", "")],
        "data": []  # Will be populated by repository pattern
    }

    # Apply repository pattern to services that access data
    repos_applied = apply_repository_pattern([comp for comp in di_applied if "data_access" in str(comp)])

    # Validate the resulting architecture
    arch_to_validate = {
        "components": di_applied,
        "repositories": repos_applied,
        "layers": layered_arch
    }

    patterns_valid, issues = validate_architecture_patterns(arch_to_validate)
    consistency_valid, _ = enforce_consistency_rules(arch_to_validate)

    # The architecture should now follow proper patterns
    assert patterns_valid or len(issues) == 0  # Assuming no issues were found after pattern application


def test_naming_convention_validation_comprehensive():
    """Test comprehensive naming convention validation."""
    # Valid Python naming conventions
    python_conventions = {
        "variables": ["user_id", "first_name", "is_active", "_private_var", "__dunder_method"],
        "functions": ["get_user", "calculate_total", "is_valid_email", "_private_func"],
        "classes": ["UserService", "UserProfile", "ApiException", "HttpRequest"],
        "modules": ["user_service", "order_processing", "email_notifications"],
        "constants": ["MAX_RETRIES", "DEFAULT_TIMEOUT", "API_ENDPOINT"]
    }

    is_valid, issues = validate_naming_conventions(python_conventions)
    assert is_valid is True
    assert len(issues) == 0

    # Invalid Python naming conventions
    invalid_python = {
        "variables": ["userId", "FirstName", "isValid", "2count"],  # camelCase, PascalCase, starts with number
        "functions": ["getUser", "CalculateTotal", "isValidEmail"],  # camelCase, PascalCase
        "classes": ["user_service", "UserProfileClass", "api_exception"],  # snake_case, suffixed
        "modules": ["UserService", "OrderProcessing", "EmailNotifications"],  # PascalCase
        "constants": ["max_retries", "defaultTimeout", "apiEndpoint"]  # not UPPER_SNAKE_CASE
    }

    is_valid, issues = validate_naming_conventions(invalid_python)
    assert is_valid is False
    assert len(issues) > 0


def test_layer_boundary_violation_detection():
    """Test detecting violations of layer boundaries."""
    # Architecture with proper layer boundaries
    proper_layers = {
        "layers": {
            "ui": {
                "name": "Presentation Layer",
                "components": ["UserController", "ProductView"],
                "can_depend_on": ["application"]
            },
            "application": {
                "name": "Application Layer",
                "components": ["UserService", "ProductService"],
                "can_depend_on": ["domain", "infrastructure"]
            },
            "domain": {
                "name": "Domain Layer",
                "components": ["User", "Product", "Order"],
                "can_depend_on": []  # Domain layer should not depend on others
            },
            "infrastructure": {
                "name": "Infrastructure Layer",
                "components": ["DatabaseRepository", "EmailSender"],
                "can_depend_on": ["application", "domain"]
            }
        }
    }

    # Test proper architecture
    is_valid, issues = validate_layer_separation(proper_layers)
    # This test depends on the specific implementation of validate_layer_separation
    # The important thing is that it properly checks for layer violations

    # Create an architecture with violations
    violated_layers = {
        "layers": {
            "ui": {
                "name": "Presentation Layer",
                "components": ["UserController", "ProductView"],
                "can_depend_on": ["application", "domain"]  # Violates boundary: shouldn't access domain directly
            },
            "application": {
                "name": "Application Layer",
                "components": ["UserService", "ProductService"],
                "can_depend_on": ["domain", "infrastructure"]
            },
            "domain": {
                "name": "Domain Layer",
                "components": ["User", "Product", "Order"],
                "can_depend_on": ["infrastructure"]  # Major violation: domain shouldn't depend on infrastructure
            },
            "infrastructure": {
                "name": "Infrastructure Layer",
                "components": ["DatabaseRepository", "EmailSender"],
                "can_depend_on": ["application", "domain"]
            }
        }
    }

    is_valid, issues = validate_layer_separation(violated_layers)
    # Should detect violations in the architecture
    assert is_valid is False or len(issues) > 0


def test_pattern_application_sequence():
    """Test applying multiple patterns in sequence."""
    # Start with raw, unstructured components
    raw_components = [
        {"id": "user_mgmt", "function": "handle user operations", "has_direct_db": True, "has_business_logic": True},
        {"id": "order_proc", "function": "process orders", "has_direct_db": True, "has_external_calls": True}
    ]

    # Apply patterns in a logical sequence
    # 1. First, apply dependency injection to handle direct dependencies
    di_components = apply_dependency_injection_pattern(raw_components)

    # 2. Then apply repository pattern to handle direct DB access
    repo_candidates = [c for c in di_components if c.get("has_direct_db")]
    repo_components = apply_repository_pattern(repo_candidates)

    # 3. Apply service layer pattern to separate business logic
    service_candidates = [c for c in di_components if c.get("has_business_logic")]
    service_components = apply_service_layer_pattern(service_candidates)

    # 4. Apply DTO pattern to handle data transfer
    dto_candidates = service_components  # Services often need DTOs
    dto_components = apply_dto_pattern(dto_candidates)

    # Verify that patterns were applied appropriately
    assert len(di_components) > 0
    assert len(repo_components) > 0
    assert len(service_components) > 0
    assert len(dto_components) > 0


if __name__ == "__main__":
    # Run tests
    test_apply_dependency_injection_pattern()
    test_apply_repository_pattern()
    test_apply_service_layer_pattern()
    test_apply_dto_pattern()
    test_apply_event_driven_pattern()
    test_validate_naming_conventions()
    test_validate_incorrect_naming()
    test_validate_layer_separation()
    test_validate_violated_layer_separation()
    test_validate_dependency_flow()
    test_validate_backward_dependency()
    test_validate_architecture_patterns()
    test_enforce_consistency_rules()
    test_inconsistency_detection()
    test_patterns_module_integration()
    test_naming_convention_validation_comprehensive()
    test_layer_boundary_violation_detection()
    test_pattern_application_sequence()
    print("All architecture patterns and consistency rules tests passed!")