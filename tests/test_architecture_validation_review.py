"""
Tests for the DCAE Architecture Validation and Review Module
"""

import os
import tempfile
from pathlib import Path
import json
import yaml

from dcae.architecture.validator import (
    ArchitectureValidator,
    validate_architecture_consistency,
    validate_rationality,
    validate_technology_alignment,
    validate_scalability,
    validate_security_aspects,
    check_architecture_patterns
)
from dcae.architecture.reviewer import (
    ArchitectureReviewer,
    review_architecture_design,
    suggest_improvements,
    assess_quality_attributes,
    check_consistency_rules
)


def test_architecture_validator_initialization():
    """Test that ArchitectureValidator initializes correctly."""
    validator = ArchitectureValidator()

    assert validator is not None
    assert hasattr(validator, 'validate')
    assert hasattr(validator, 'check_patterns')
    assert hasattr(validator, 'validate_consistency')


def test_validate_architecture_consistency():
    """Test validating architecture consistency."""
    consistent_arch = {
        "project_name": "Consistent Project",
        "components": [
            {"id": "api", "dependencies": ["auth-service"]},
            {"id": "auth-service", "dependencies": []},  # No circular dependency
            {"id": "db", "dependencies": []}
        ],
        "technology_stack": {
            "backend": "python",
            "frontend": "react",
            "database": "postgresql"
        }
    }

    is_consistent, issues = validate_architecture_consistency(consistent_arch)
    assert is_consistent is True
    assert len(issues) == 0


def test_validate_architecture_with_issues():
    """Test validating architecture with known issues."""
    inconsistent_arch = {
        "project_name": "Inconsistent Project",
        "components": [
            {"id": "comp_a", "dependencies": ["comp_b"]},
            {"id": "comp_b", "dependencies": ["comp_c"]},
            {"id": "comp_c", "dependencies": ["comp_a"]}  # Circular dependency
        ],
        "technology_stack": {
            "backend": "python",
            "frontend": "react",
            # Missing database specification
        }
    }

    is_consistent, issues = validate_architecture_consistency(inconsistent_arch)
    assert is_consistent is False
    assert len(issues) > 0
    # Should detect circular dependency
    assert any("circular" in issue.lower() for issue in issues)


def test_validate_rationality():
    """Test validating the rationality of architecture decisions."""
    rational_arch = {
        "project_name": "Rational Project",
        "technology_stack": {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql",
            "message_queue": "redis"
        },
        "scalability_requirements": "moderate",
        "team_expertise": ["python", "postgresql"]
    }

    is_rational, issues = validate_rationality(rational_arch)
    assert is_rational is True
    assert len(issues) == 0


def test_validate_irrational_architecture():
    """Test validating an architecture with questionable decisions."""
    irrational_arch = {
        "project_name": "Irrational Project",
        "technology_stack": {
            "language": "assembly",  # Unnecessarily low-level for typical apps
            "framework": "none",
            "database": "flat_files"  # Not scalable
        },
        "scalability_requirements": "high",  # High scalability but poor tech choices
        "team_expertise": ["javascript", "python"]  # Team doesn't know assembly
    }

    is_rational, issues = validate_rationality(irrational_arch)
    assert is_rational is False
    assert len(issues) > 0


def test_validate_technology_alignment():
    """Test validating alignment between technology choices and requirements."""
    aligned_arch = {
        "project_name": "Aligned Project",
        "requirements": {
            "real_time_updates": True,
            "data_analytics": True,
            "security_critical": True
        },
        "technology_stack": {
            "backend": "nodejs",  # Good for real-time
            "database": "mongodb",  # Good for analytics
            "security_framework": "oauth2"
        }
    }

    is_aligned, issues = validate_technology_alignment(aligned_arch)
    assert is_aligned is True
    assert len(issues) == 0


def test_validate_scalability():
    """Test validating scalability aspects of architecture."""
    scalable_arch = {
        "project_name": "Scalable Project",
        "components": [
            {"id": "stateless_api", "stateful": False},  # Good for scaling
            {"id": "load_balancer", "purpose": "distribution"}
        ],
        "deployment_model": "containerized",
        "horizontal_scaling_supported": True
    }

    is_scalable, issues = validate_scalability(scalable_arch)
    assert is_scalable is True
    assert len(issues) == 0


def test_validate_security_aspects():
    """Test validating security aspects of architecture."""
    secure_arch = {
        "project_name": "Secure Project",
        "security_features": [
            "authentication",
            "authorization",
            "encryption_at_rest",
            "encryption_in_transit",
            "audit_logging"
        ],
        "components": [
            {"id": "auth_service", "implements": ["authentication", "authorization"]},
            {"id": "firewall", "implements": ["network_security"]}
        ]
    }

    is_secure, issues = validate_security_aspects(secure_arch)
    assert is_secure is True
    assert len(issues) == 0


def test_check_architecture_patterns():
    """Test checking that proper architecture patterns are followed."""
    patterned_arch = {
        "project_name": "Patterned Project",
        "layers": {
            "presentation": {"type": "mvc"},
            "business": {"type": "service_layer"},
            "data": {"type": "repository_pattern"}
        },
        "components": [
            {"id": "controller", "pattern": "mvc_controller"},
            {"id": "service", "pattern": "service_layer"},
            {"id": "repository", "pattern": "repository"}
        ]
    }

    patterns_followed, issues = check_architecture_patterns(patterned_arch)
    assert patterns_followed is True
    assert len(issues) == 0


def test_architecture_reviewer_initialization():
    """Test that ArchitectureReviewer initializes correctly."""
    reviewer = ArchitectureReviewer()

    assert reviewer is not None
    assert hasattr(reviewer, 'review')
    assert hasattr(reviewer, 'suggest_improvements')
    assert hasattr(reviewer, 'assess_quality_attributes')


def test_review_architecture_design():
    """Test reviewing architecture design."""
    arch_to_review = {
        "project_name": "Review Project",
        "components": [
            {"id": "api_gateway", "type": "gateway", "responsible_for": "routing"},
            {"id": "auth_service", "type": "service", "responsible_for": "authentication"}
        ],
        "technology_stack": {
            "language": "python",
            "framework": "fastapi",
            "database": "postgresql"
        }
    }

    review_result = review_architecture_design(arch_to_review)

    assert "overall_score" in review_result
    assert "strengths" in review_result
    assert "weaknesses" in review_result
    assert "recommendations" in review_result

    # Scores should be in reasonable range (e.g., 0-100)
    assert 0 <= review_result["overall_score"] <= 100


def test_suggest_improvements():
    """Test suggesting improvements to architecture."""
    arch_with_weaknesses = {
        "project_name": "Improvement Candidate",
        "components": [
            {"id": "monolith", "type": "monolithic", "responsible_for": "everything"}
        ],
        "technology_stack": {
            "language": "python",
            "framework": "flask"
        },
        "scalability_requirements": "high"
    }

    improvements = suggest_improvements(arch_with_weaknesses)

    assert isinstance(improvements, list)
    assert len(improvements) > 0
    # For high scalability requirements with monolithic architecture,
    # we should suggest moving to microservices
    improvement_str = " ".join(improvements).lower()
    assert "microservice" in improvement_str or "decompose" in improvement_str


def test_assess_quality_attributes():
    """Test assessing quality attributes of architecture."""
    arch_to_assess = {
        "project_name": "Quality Assessment",
        "components": [
            {"id": "api", "stateful": False, "dependencies": []},
            {"id": "cache", "purpose": "performance"},
            {"id": "logger", "purpose": "monitoring"}
        ],
        "technology_stack": {
            "language": "go",  # Generally good performance
            "framework": "gin"
        }
    }

    quality_scores = assess_quality_attributes(arch_to_assess)

    assert "performance" in quality_scores
    assert "scalability" in quality_scores
    assert "maintainability" in quality_scores
    assert "security" in quality_scores

    # All scores should be in reasonable range
    for attr, score in quality_scores.items():
        assert 0 <= score <= 100


def test_check_consistency_rules():
    """Test checking consistency rules in architecture."""
    arch_with_consistency = {
        "project_name": "Consistent Architecture",
        "naming_convention": "snake_case",
        "components": [
            {"id": "user_service", "name": "user_service", "style": "snake_case"},
            {"id": "order_processor", "name": "order_processor", "style": "snake_case"}
        ],
        "api_conventions": {
            "endpoint_style": "snake_case",
            "response_format": "json"
        }
    }

    rules_compliant, issues = check_consistency_rules(arch_with_consistency)

    assert rules_compliant is True
    assert len(issues) == 0


def test_validation_edge_cases():
    """Test validation with edge cases."""
    # Empty architecture
    empty_arch = {}

    try:
        is_consistent, issues = validate_architecture_consistency(empty_arch)
        # Should return False with issues for empty architecture
        assert is_consistent is False
    except Exception:
        # Or might raise an exception, which is also valid behavior
        pass

    # Architecture with only metadata
    minimal_arch = {
        "project_name": "Minimal",
        "description": "Minimal architecture"
    }

    is_consistent, issues = validate_architecture_consistency(minimal_arch)
    # Should identify missing components as an issue
    assert is_consistent is False or len(issues) > 0


def test_reviewer_comprehensive_review():
    """Test comprehensive review functionality of ArchitectureReviewer."""
    reviewer = ArchitectureReviewer()

    detailed_arch = {
        "project_name": "Comprehensive Review",
        "description": "A detailed architecture for review",
        "requirements_aligment": {
            "functional": ["FR001", "FR002"],
            "non_functional": ["NFR001", "NFR002"]
        },
        "components": [
            {"id": "api", "type": "rest_api", "interfaces": ["http"], "dependencies": []},
            {"id": "db", "type": "database", "interfaces": ["sql"], "dependencies": []}
        ],
        "technology_stack": {
            "backend": "python",
            "frontend": "react",
            "database": "postgresql",
            "message_queue": "rabbitmq"
        },
        "deployment": {
            "environment": "cloud",
            "containers": True,
            "orchestration": "kubernetes"
        },
        "security": {
            "authentication": "oauth2",
            "encryption": "aes256",
            "logging": "detailed"
        }
    }

    # Perform comprehensive review
    review_report = reviewer.review(detailed_arch)

    # Verify that the review report has expected sections
    assert "executive_summary" in review_report
    assert "detailed_analysis" in review_report
    assert "recommendations" in review_report
    assert "risk_assessment" in review_report
    assert "quality_attribute_scores" in review_report

    # The scores should be numeric
    for attr, score in review_report["quality_attribute_scores"].items():
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100


if __name__ == "__main__":
    # Run tests
    test_architecture_validator_initialization()
    test_validate_architecture_consistency()
    test_validate_architecture_with_issues()
    test_validate_rationality()
    test_validate_irrational_architecture()
    test_validate_technology_alignment()
    test_validate_scalability()
    test_validate_security_aspects()
    test_check_architecture_patterns()
    test_architecture_reviewer_initialization()
    test_review_architecture_design()
    test_suggest_improvements()
    test_assess_quality_attributes()
    test_check_consistency_rules()
    test_validation_edge_cases()
    test_reviewer_comprehensive_review()
    print("All architecture validation and review tests passed!")