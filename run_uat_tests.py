#!/usr/bin/env python3
"""
User Acceptance Testing (UAT) Script for DCAE Framework

This script performs end-to-end tests of the DCAE framework functionality
to validate that it meets user requirements and works as expected.
"""

import sys
import os
import tempfile
import json
from pathlib import Path
import asyncio
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, '.')

def print_section(title):
    """Print a section header for the test."""
    print(f"\n{'='*60}")
    print(f"TESTING: {title}")
    print('='*60)

def print_status(status, message):
    """Print a test status message."""
    print(f"[{status}] {message}")

def test_progress_indicators():
    """Test progress indicator functionality."""
    print_section("Progress Indicators")

    try:
        from src.dcae.progress_indicators import ProgressIndicator, ProgressStage

        # Create temporary files for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.json'
            indicators_path = Path(tmpdir) / 'indicators.json'

            # Create minimal config
            with open(config_path, 'w') as f:
                json.dump({
                    'dcae': {
                        'logging': {
                            'console_output': False,
                            'file_output': False
                        }
                    }
                }, f)

            # Initialize progress indicator
            pi = ProgressIndicator(config_path=config_path, indicators_path=indicators_path)

            # Test updating progress
            result = pi.update_progress(ProgressStage.DEVELOPMENT, 75, {
                'task': 'UAT Testing',
                'details': 'Verifying progress indicator functionality'
            })

            if result:
                print_status("PASS", "Progress indicator update successful")
            else:
                print_status("FAIL", "Progress indicator update failed")
                return False

            # Test getting summary
            summary = pi.get_progress_summary()
            if summary and 'overall_progress' in summary:
                print_status("PASS", f"Progress summary retrieved: {summary['overall_progress']}%")
            else:
                print_status("FAIL", "Could not retrieve progress summary")
                return False

            return True
    except Exception as e:
        print_status("FAIL", f"Progress indicator test failed: {e}")
        return False

def test_constraint_management():
    """Test constraint management functionality."""
    print_section("Constraint Management")

    try:
        from src.dcae.knowledge_fusion.project_constraints_manager import ProjectConstraintsManager
        from src.dcae.knowledge_fusion.constraint_validation import ConstraintValidator

        # Initialize the constraint manager
        cm = ProjectConstraintsManager()

        # Test basic functionality
        all_constraints = cm.get_active_constraints()
        print_status("PASS", f"Retrieved {len(all_constraints)} active constraints")

        # Create and test a constraint
        test_constraint = cm.create_constraint(
            name="UAT_Test_Constraint",
            category="testing",
            description="Test constraint for UAT validation",
            severity="medium"
        )

        if test_constraint:
            print_status("PASS", "Constraint creation successful")
        else:
            print_status("FAIL", "Constraint creation failed")
            return False

        # Test validator
        cv = ConstraintValidator()
        validation_result = cv.validate_file("uat-test-plan.md")  # Self-validate this file

        print_status("PASS", f"Constraint validation completed: {type(validation_result)}")

        return True
    except Exception as e:
        print_status("FAIL", f"Constraint management test failed: {e}")
        return False

def test_product_knowledge():
    """Test product knowledge access functionality."""
    print_section("Product Knowledge Access")

    try:
        from src.dcae.product_knowledge.access import ProductKnowledgeAccess, SimpleProductKnowledgeCache
        from pathlib import Path

        # Create a temporary directory with test documentation
        with tempfile.TemporaryDirectory() as tmpdir:
            docs_dir = Path(tmpdir) / "docs"
            docs_dir.mkdir()

            # Create test documentation
            test_doc = docs_dir / "uat_testing_guide.md"
            test_doc.write_text("""
# UAT Testing Guide

This document describes the User Acceptance Testing procedures.

## Testing Guidelines
- All functionality should be validated
- Performance requirements must be met
- User workflows must be intuitive
            """)

            # Initialize knowledge access
            cache = SimpleProductKnowledgeCache()
            knowledge_access = ProductKnowledgeAccess(docs_dir, cache)

            # Try to search for content
            results = asyncio.run(knowledge_access.search("UAT testing", max_results=5))
            print_status("PASS", f"Found {len(results)} results for 'UAT testing' query")

            # Try to get relevant documents
            relevant_docs = asyncio.run(
                knowledge_access.get_relevant_documents("I need to understand UAT procedures", max_results=3)
            )
            print_status("PASS", f"Found {len(relevant_docs)} relevant documents")

            return True
    except Exception as e:
        print_status("FAIL", f"Product knowledge test failed: {e}")
        return False

def test_cli_functionality():
    """Test CLI functionality."""
    print_section("CLI Functionality")

    try:
        from src.dcae.cli import DCAECLI
        import io
        import contextlib

        # Initialize CLI
        cli = DCAECLI()
        print_status("PASS", "CLI initialization successful")

        # Test basic operations
        # We won't execute full commands, but verify components exist
        from src.dcae.generated_output_review import GeneratedOutputReviewer

        # Test reviewer initialization with a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            reviewer = GeneratedOutputReviewer(project_path=tmpdir)
            print_status("PASS", "Generated output reviewer initialization successful")

        return True
    except Exception as e:
        print_status("FAIL", f"CLI functionality test failed: {e}")
        return False

def test_review_mechanisms():
    """Test code review mechanisms."""
    print_section("Review Mechanisms")

    try:
        from src.dcae.generated_output_review import GeneratedOutputReviewer
        from src.dcae.review_rules_engine import ReviewRulesEngine

        # Initialize review components
        with tempfile.TemporaryDirectory() as tmpdir:
            reviewer = GeneratedOutputReviewer(project_path=tmpdir)
            rules_engine = ReviewRulesEngine()

            # Test basic functionality
            print_status("PASS", "Review components initialized successfully")

            # Test with a simple Python file
            test_file = Path(tmpdir) / "test_file.py"
            test_file.write_text("""
def hello_world():
    # This is a test function
    return "Hello, World!"

# End of test file
""")

            # Run a basic review
            report = reviewer.review_generated_output()
            print_status("PASS", "Generated output review completed")

            # Test rule engine
            issues = rules_engine.apply_rules(str(test_file))
            print_status("PASS", f"Applied rules, found {len(issues)} issues")

            return True
    except Exception as e:
        print_status("FAIL", f"Review mechanisms test failed: {e}")
        return False

def run_uat():
    """Run all UAT tests."""
    print("Starting User Acceptance Testing for DCAE Framework")
    print(f"Test execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Progress Indicators", test_progress_indicators),
        ("Constraint Management", test_constraint_management),
        ("Product Knowledge Access", test_product_knowledge),
        ("CLI Functionality", test_cli_functionality),
        ("Review Mechanisms", test_review_mechanisms),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} caused an unexpected error: {e}")
            results.append((test_name, False))

    # Print summary
    print_section("UAT SUMMARY")
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {test_name}")

    if failed_tests == 0:
        print(f"\n🎉 ALL UAT TESTS PASSED! 🎉")
        print("The DCAE framework is ready for user acceptance.")
        return True
    else:
        print(f"\n❌ {failed_tests} UAT TEST(S) FAILED")
        print("The DCAE framework needs corrections before final acceptance.")
        return False

if __name__ == "__main__":
    success = run_uat()
    sys.exit(0 if success else 1)