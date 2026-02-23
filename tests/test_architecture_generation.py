"""
Tests for the DCAE Architecture Generation Module
"""

import os
import tempfile
from pathlib import Path
import json
import yaml

from dcae.architecture.generator import (
    ArchitectureGenerator,
    generate_architecture_from_requirements,
    select_starter_template,
    apply_architecture_patterns,
    create_layered_architecture,
    create_microservices_architecture,
    create_monolithic_architecture
)


def test_architecture_generator_initialization():
    """Test that ArchitectureGenerator initializes correctly."""
    generator = ArchitectureGenerator()

    assert generator is not None
    assert hasattr(generator, 'generate_from_requirements')
    assert hasattr(generator, 'apply_patterns')


def test_generate_architecture_from_requirements():
    """Test generating architecture from requirements."""
    requirements = {
        "project_name": "Test E-commerce",
        "functional_requirements": [
            {"id": "FR001", "description": "User authentication", "priority": "high"},
            {"id": "FR002", "description": "Product catalog", "priority": "high"},
            {"id": "FR003", "description": "Shopping cart", "priority": "medium"}
        ],
        "non_functional_requirements": [
            {"id": "NFR001", "description": "Handle 1000 concurrent users", "category": "performance"},
            {"id": "NFR002", "description": "99.9% availability", "category": "availability"}
        ]
    }

    # Generate architecture based on requirements
    architecture = generate_architecture_from_requirements(requirements)

    # Verify the structure of the generated architecture
    assert "project_name" in architecture
    assert architecture["project_name"] == "Test E-commerce"
    assert "layers" in architecture
    assert "components" in architecture
    assert "technology_stack" in architecture
    assert len(architecture["components"]) > 0


def test_select_starter_template():
    """Test selecting appropriate starter template based on requirements."""
    # Test with performance-focused requirements
    perf_reqs = {
        "non_functional_requirements": [
            {"category": "performance", "description": "High throughput required"},
            {"category": "scalability", "description": "Must scale horizontally"}
        ]
    }

    template = select_starter_template(perf_reqs)
    # Depending on implementation, this might return 'microservices' or similar
    # for performance/scalability focused requirements

    # Test with simple requirements
    simple_reqs = {
        "functional_requirements": [
            {"description": "Simple CRUD operations"}
        ],
        "non_functional_requirements": [
            {"category": "maintainability", "description": "Easy to maintain"}
        ]
    }

    simple_template = select_starter_template(simple_reqs)
    # This might return 'monolithic' or 'minimal' for simple requirements


def test_create_layered_architecture():
    """Test creating a layered architecture."""
    layers_needed = ['presentation', 'business', 'data']
    tech_stack = {'language': 'python', 'framework': 'fastapi'}

    layered_arch = create_layered_architecture(layers_needed, tech_stack)

    assert 'layers' in layered_arch
    assert len(layered_arch['layers']) == 3  # presentation, business, data
    assert 'technology_stack' in layered_arch
    assert layered_arch['technology_stack']['language'] == 'python'


def test_create_microservices_architecture():
    """Test creating a microservices architecture."""
    services_needed = [
        {'name': 'auth-service', 'responsibility': 'authentication'},
        {'name': 'catalog-service', 'responsibility': 'product catalog'},
        {'name': 'order-service', 'responsibility': 'order processing'}
    ]
    tech_stack = {'language': 'python', 'communication': 'rest'}

    micro_arch = create_microservices_architecture(services_needed, tech_stack)

    assert 'services' in micro_arch
    assert len(micro_arch['services']) == 3
    assert 'communication_pattern' in micro_arch
    assert micro_arch['communication_pattern'] == 'rest'


def test_create_monolithic_architecture():
    """Test creating a monolithic architecture."""
    requirements = {
        "functional_requirements": [
            {"id": "FR001", "description": "Simple user management", "priority": "high"}
        ]
    }

    tech_stack = {'language': 'python', 'framework': 'flask'}

    mono_arch = create_monolithic_architecture(requirements, tech_stack)

    assert 'architecture_style' in mono_arch
    assert mono_arch['architecture_style'] == 'monolithic'
    assert 'modules' in mono_arch
    assert 'technology_stack' in mono_arch


def test_apply_architecture_patterns():
    """Test applying architecture patterns to generated architecture."""
    base_arch = {
        "project_name": "Pattern Test",
        "components": [
            {"id": "service1", "type": "service", "needs_di": True},
            {"id": "repo1", "type": "repository", "needs_abstraction": True}
        ]
    }

    # Apply patterns like dependency injection, repository pattern, etc.
    patterned_arch = apply_architecture_patterns(base_arch)

    # After applying patterns, components should have additional configuration
    # indicating how patterns should be implemented
    assert "components" in patterned_arch
    # The specific changes depend on how patterns are applied in the implementation


def test_architecture_generator_class_methods():
    """Test the ArchitectureGenerator class methods directly."""
    generator = ArchitectureGenerator()

    # Test with a sample requirements document
    sample_requirements = {
        "project_name": "Sample Project",
        "description": "A sample project for testing",
        "functional_requirements": [
            {"id": "FR_SAMPLE_1", "description": "Should be able to store user data", "priority": "high"}
        ],
        "non_functional_requirements": [
            {"id": "NFR_SAMPLE_1", "description": "Should be secure", "category": "security"}
        ]
    }

    # Generate architecture
    generated_arch = generator.generate_from_requirements(sample_requirements)

    assert generated_arch is not None
    assert generated_arch["project_name"] == "Sample Project"
    assert "components" in generated_arch
    assert "patterns_applied" in generated_arch  # Assuming patterns are tracked


def test_complex_architecture_generation():
    """Test generating architecture for a complex project with mixed requirements."""
    complex_requirements = {
        "project_name": "Complex E-commerce Platform",
        "description": "A comprehensive e-commerce platform with multiple features",
        "functional_requirements": [
            {"id": "FR_AUTH", "description": "User registration and authentication", "priority": "critical"},
            {"id": "FR_PRODUCT", "description": "Product catalog management", "priority": "critical"},
            {"id": "FR_CART", "description": "Shopping cart functionality", "priority": "high"},
            {"id": "FR_PAYMENT", "description": "Secure payment processing", "priority": "critical"},
            {"id": "FR_ANALYTICS", "description": "Sales analytics dashboard", "priority": "medium"}
        ],
        "non_functional_requirements": [
            {"id": "NFR_PERF", "description": "Handle 5000 concurrent users", "category": "performance"},
            {"id": "NFR_SEC", "description": "PCI DSS compliance for payments", "category": "security"},
            {"id": "NFR_AVAIL", "description": "99.99% uptime", "category": "availability"},
            {"id": "NFR_SCALE", "description": "Auto-scale based on demand", "category": "scalability"}
        ]
    }

    # Generate architecture for complex requirements
    complex_arch = generate_architecture_from_requirements(complex_requirements)

    # Complex projects should result in more sophisticated architectures
    assert "project_name" in complex_arch
    assert complex_arch["project_name"] == "Complex E-commerce Platform"
    assert len(complex_arch["components"]) >= 5  # At least one per major FR
    assert "technology_stack" in complex_arch
    assert "security_considerations" in complex_arch  # NFRs should influence architecture
    assert "scaling_strategy" in complex_arch  # Scaling NFRs should be reflected


def test_error_handling_in_generation():
    """Test error handling when generating architecture with invalid requirements."""
    # Test with minimal requirements
    minimal_reqs = {}

    try:
        arch = generate_architecture_from_requirements(minimal_reqs)
        # If it doesn't throw an error, it should return a minimal architecture
        assert arch is not None
    except ValueError:
        # Expected if the function validates input strictly
        pass
    except Exception as e:
        # Other exceptions should be unexpected
        raise AssertionError(f"Unexpected exception: {e}")

    # Test with None requirements
    try:
        arch = generate_architecture_from_requirements(None)
        # Should either return a default architecture or raise ValueError
    except ValueError:
        # Expected behavior
        pass
    except Exception as e:
        # Other exceptions should be unexpected
        raise AssertionError(f"Unexpected exception: {e}")


if __name__ == "__main__":
    # Run tests
    test_architecture_generator_initialization()
    test_generate_architecture_from_requirements()
    test_select_starter_template()
    test_create_layered_architecture()
    test_create_microservices_architecture()
    test_create_monolithic_architecture()
    test_apply_architecture_patterns()
    test_architecture_generator_class_methods()
    test_complex_architecture_generation()
    test_error_handling_in_generation()
    print("All architecture generation tests passed!")