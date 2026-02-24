import os
import tempfile
import unittest
from pathlib import Path
import shutil

from src.dcae.review_rules_checkpoints import (
    ReviewRulesManager,
    ReviewRulesConfigurer,
    ReviewRule,
    Checkpoint,
    RuleSeverity,
    RuleCategory,
    CheckpointTrigger
)


class TestReviewRulesManager(unittest.TestCase):
    """Test cases for the review rules manager."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rules_manager_initialization(self):
        """Test initializing the review rules manager."""
        manager = ReviewRulesManager(self.project_path)

        # Should have default rules loaded
        self.assertGreater(len(manager.rules), 0)
        self.assertGreater(len(manager.checkpoints), 0)

        # Verify directory structure
        config_dir = os.path.join(self.project_path, ".dcae", "review-config")
        self.assertTrue(os.path.exists(config_dir))

    def test_default_rules_loaded(self):
        """Test that default rules are loaded."""
        manager = ReviewRulesManager(self.project_path)

        # Check for specific default rules
        rule_ids = [rule.id for rule in manager.rules]

        # Check for some default rules
        expected_default_rules = [
            "qm_complexity_threshold",
            "qm_function_length",
            "sec_hardcoded_credentials",
            "sec_sql_injection",
            "perf_nested_loops"
        ]

        for expected_rule in expected_default_rules:
            self.assertIn(expected_rule, rule_ids)

    def test_add_rule(self):
        """Test adding a new rule."""
        manager = ReviewRulesManager(self.project_path)

        # Add a new rule
        new_rule = ReviewRule(
            id="test_new_rule",
            name="Test New Rule",
            category=RuleCategory.STANDARDS,
            severity=RuleSeverity.MEDIUM,
            enabled=True,
            condition="line_length > 120",
            threshold=120.0,
            scope="*.py",
            description="Checks for long lines",
            recommendation="Keep lines under 120 characters"
        )

        success = manager.add_rule(new_rule)

        self.assertTrue(success)
        self.assertEqual(len(manager.rules), len(manager._load_defaults.__code__.co_consts) + 1)  # Original rules + new one

        # Find the new rule
        new_rule_found = None
        for rule in manager.rules:
            if rule.id == "test_new_rule":
                new_rule_found = rule
                break

        self.assertIsNotNone(new_rule_found)
        self.assertEqual(new_rule_found.name, "Test New Rule")

    def test_remove_rule(self):
        """Test removing a rule."""
        manager = ReviewRulesManager(self.project_path)

        # Add a rule first
        rule_to_remove = ReviewRule(
            id="rule_to_remove",
            name="Rule to Remove",
            category=RuleCategory.STANDARDS,
            severity=RuleSeverity.MEDIUM,
            enabled=True,
            condition="test_condition",
            description="Test rule for removal"
        )

        manager.add_rule(rule_to_remove)

        # Verify it was added
        self.assertIn("rule_to_remove", [r.id for r in manager.rules])

        # Remove the rule
        success = manager.remove_rule("rule_to_remove")

        self.assertTrue(success)
        self.assertNotIn("rule_to_remove", [r.id for r in manager.rules])

    def test_update_rule_status(self):
        """Test updating a rule's enabled status."""
        manager = ReviewRulesManager(self.project_path)

        # Add a rule first
        rule_to_toggle = ReviewRule(
            id="rule_to_toggle",
            name="Rule to Toggle",
            category=RuleCategory.STANDARDS,
            severity=RuleSeverity.MEDIUM,
            enabled=True,
            condition="test_condition",
            description="Test rule for toggling"
        )

        manager.add_rule(rule_to_toggle)

        # Initially should be enabled
        rule = manager.get_active_rules()
        self.assertIn("rule_to_toggle", [r.id for r in rule])

        # Disable it
        success = manager.update_rule_status("rule_to_toggle", False)

        self.assertTrue(success)

        # Now it shouldn't be in active rules
        active_rules = manager.get_active_rules()
        self.assertNotIn("rule_to_toggle", [r.id for r in active_rules])

    def test_get_active_rules(self):
        """Test getting active rules."""
        manager = ReviewRulesManager(self.project_path)

        # Add a disabled rule
        disabled_rule = ReviewRule(
            id="disabled_rule",
            name="Disabled Rule",
            category=RuleCategory.STANDARDS,
            severity=RuleSeverity.MEDIUM,
            enabled=False,
            condition="test_condition",
            description="Test disabled rule"
        )

        manager.add_rule(disabled_rule)

        active_rules = manager.get_active_rules()

        # Disabled rule should not be in active rules
        self.assertNotIn("disabled_rule", [r.id for r in active_rules])

        # Default rules should still be active
        self.assertGreater(len(active_rules), 0)

    def test_get_active_rules_by_category(self):
        """Test getting active rules by category."""
        manager = ReviewRulesManager(self.project_path)

        # Get security rules
        security_rules = manager.get_active_rules(RuleCategory.SECURITY)

        # Should have security rules
        self.assertGreater(len(security_rules), 0)
        for rule in security_rules:
            self.assertEqual(rule.category, RuleCategory.SECURITY)

    def test_evaluate_rule(self):
        """Test evaluating a rule."""
        manager = ReviewRulesManager(self.project_path)

        # Create a simple rule
        rule = ReviewRule(
            id="test_rule_numeric",
            name="Test Numeric Rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=RuleSeverity.MEDIUM,
            enabled=True,
            condition="test_metric > 10",
            description="Test rule"
        )

        # Test context that satisfies the condition
        context_true = {"test_metric": 15}
        result_true = manager.evaluate_rule(rule, context_true)
        self.assertTrue(result_true)

        # Test context that doesn't satisfy the condition
        context_false = {"test_metric": 5}
        result_false = manager.evaluate_rule(rule, context_false)
        self.assertFalse(result_false)

    def test_evaluate_builtin_conditions(self):
        """Test evaluating builtin conditions."""
        manager = ReviewRulesManager(self.project_path)

        # Test hardcoded credentials condition
        rule = ReviewRule(
            id="test_hardcoded_rule",
            name="Test Hardcoded Rule",
            category=RuleCategory.SECURITY,
            severity=RuleSeverity.CRITICAL,
            enabled=True,
            condition="has_hardcoded_credentials",
            description="Test hardcoded rule"
        )

        context_with_creds = {"has_hardcoded_credentials": True}
        result_true = manager.evaluate_rule(rule, context_with_creds)
        self.assertTrue(result_true)

        context_without_creds = {"has_hardcoded_credentials": False}
        result_false = manager.evaluate_rule(rule, context_without_creds)
        self.assertFalse(result_false)


class TestReviewRulesConfigurer(unittest.TestCase):
    """Test cases for the review rules configurer."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_path, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_configurer_initialization(self):
        """Test initializing the rules configurer."""
        configurer = ReviewRulesConfigurer(self.project_path)

        self.assertIsNotNone(configurer.manager)

    def test_create_custom_rule(self):
        """Test creating a custom rule via configurer."""
        configurer = ReviewRulesConfigurer(self.project_path)

        success = configurer.create_custom_rule(
            rule_id="custom_test_rule",
            name="Custom Test Rule",
            category=RuleCategory.STANDARDS,
            severity=RuleSeverity.LOW,
            condition="line_length > 80",
            threshold=80.0,
            scope="*.py",
            description="Checks for long lines",
            recommendation="Shorten long lines"
        )

        self.assertTrue(success)

        # Verify rule exists in manager
        rule_exists = any(rule.id == "custom_test_rule" for rule in configurer.manager.rules)
        self.assertTrue(rule_exists)

    def test_create_custom_checkpoint(self):
        """Test creating a custom checkpoint via configurer."""
        configurer = ReviewRulesConfigurer(self.project_path)

        success = configurer.create_custom_checkpoint(
            checkpoint_id="custom_test_checkpoint",
            name="Custom Test Checkpoint",
            trigger=CheckpointTrigger.EVENT_BASED,
            rule_ids=["qm_function_length"],
            target_scope="staged_files",
            blocking=True,
            description="Custom checkpoint for testing",
            conditions={"before": "git_commit"}
        )

        self.assertTrue(success)

        # Verify checkpoint exists in manager
        checkpoint_exists = any(cp.id == "custom_test_checkpoint" for cp in configurer.manager.checkpoints)
        self.assertTrue(checkpoint_exists)

    def test_toggle_rule(self):
        """Test toggling a rule via configurer."""
        configurer = ReviewRulesConfigurer(self.project_path)

        # Add a rule first
        configurer.create_custom_rule(
            rule_id="toggle_test_rule",
            name="Toggle Test Rule",
            category=RuleCategory.STANDARDS,
            severity=RuleSeverity.LOW,
            condition="test_condition",
            description="Test rule for toggling"
        )

        # Initially should be active
        initial_active = configurer.manager.get_active_rules()
        self.assertIn("toggle_test_rule", [r.id for r in initial_active])

        # Disable it
        success = configurer.toggle_rule("toggle_test_rule", False)
        self.assertTrue(success)

        # Should not be active anymore
        after_disable = configurer.manager.get_active_rules()
        self.assertNotIn("toggle_test_rule", [r.id for r in after_disable])

        # Enable it again
        success = configurer.toggle_rule("toggle_test_rule", True)
        self.assertTrue(success)

        # Should be active again
        after_enable = configurer.manager.get_active_rules()
        self.assertIn("toggle_test_rule", [r.id for r in after_enable])

    def test_get_rules_summary(self):
        """Test getting rules summary."""
        configurer = ReviewRulesConfigurer(self.project_path)

        summary = configurer.get_rules_summary()

        self.assertIn("total_rules", summary)
        self.assertIn("active_rules", summary)
        self.assertIn("inactive_rules", summary)
        self.assertIn("by_category", summary)
        self.assertIn("by_severity", summary)
        self.assertGreaterEqual(summary["total_rules"], 0)

    def test_get_checkpoints_summary(self):
        """Test getting checkpoints summary."""
        configurer = ReviewRulesConfigurer(self.project_path)

        summary = configurer.get_checkpoints_summary()

        self.assertIn("total_checkpoints", summary)
        self.assertIn("by_trigger", summary)
        self.assertGreaterEqual(summary["total_checkpoints"], 0)

    def test_apply_checkpoint(self):
        """Test applying a checkpoint."""
        configurer = ReviewRulesConfigurer(self.project_path)

        # Create a custom rule and checkpoint
        configurer.create_custom_rule(
            rule_id="apply_test_rule",
            name="Apply Test Rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=RuleSeverity.MEDIUM,
            condition="cyclomatic_complexity > 5",
            threshold=5.0,
            description="Test rule for application"
        )

        configurer.create_custom_checkpoint(
            checkpoint_id="apply_test_checkpoint",
            name="Apply Test Checkpoint",
            trigger=CheckpointTrigger.EVENT_BASED,
            rule_ids=["apply_test_rule", "qm_function_length"],
            description="Checkpoint for testing application"
        )

        # Apply with context that triggers the rule
        context = {
            "cyclomatic_complexity": 8,
            "function_length": 60
        }

        result = configurer.apply_checkpoint("apply_test_checkpoint", context)

        self.assertEqual(result["checkpoint_id"], "apply_test_checkpoint")
        self.assertFalse(result["passed"])  # Should fail because complexity > 5
        self.assertGreater(len(result["violations"]), 0)


class TestReviewRulesComponents(unittest.TestCase):
    """Test cases for individual review rules components."""

    def test_review_rule_creation(self):
        """Test creating a review rule."""
        rule = ReviewRule(
            id="test_rule",
            name="Test Rule",
            category=RuleCategory.SECURITY,
            severity=RuleSeverity.HIGH,
            enabled=True,
            condition="test_condition",
            threshold=10.0,
            scope="*.py",
            description="Test rule description",
            recommendation="Test recommendation"
        )

        self.assertEqual(rule.id, "test_rule")
        self.assertEqual(rule.name, "Test Rule")
        self.assertEqual(rule.category, RuleCategory.SECURITY)
        self.assertEqual(rule.severity, RuleSeverity.HIGH)
        self.assertTrue(rule.enabled)
        self.assertEqual(rule.condition, "test_condition")
        self.assertEqual(rule.threshold, 10.0)
        self.assertEqual(rule.scope, "*.py")
        self.assertEqual(rule.description, "Test rule description")
        self.assertEqual(rule.recommendation, "Test recommendation")

    def test_checkpoint_creation(self):
        """Test creating a checkpoint."""
        checkpoint = Checkpoint(
            id="test_checkpoint",
            name="Test Checkpoint",
            trigger=CheckpointTrigger.EVENT_BASED,
            rules=["rule1", "rule2"],
            target_scope="all_files",
            blocking=True,
            description="Test checkpoint description",
            conditions={"after": "generation"}
        )

        self.assertEqual(checkpoint.id, "test_checkpoint")
        self.assertEqual(checkpoint.name, "Test Checkpoint")
        self.assertEqual(checkpoint.trigger, CheckpointTrigger.EVENT_BASED)
        self.assertEqual(checkpoint.rules, ["rule1", "rule2"])
        self.assertEqual(checkpoint.target_scope, "all_files")
        self.assertTrue(checkpoint.blocking)
        self.assertEqual(checkpoint.description, "Test checkpoint description")
        self.assertEqual(checkpoint.conditions, {"after": "generation"})


if __name__ == '__main__':
    unittest.main()