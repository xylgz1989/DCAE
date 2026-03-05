import unittest
import tempfile
from pathlib import Path
import yaml
from src.review_rules_engine import (
    ReviewRulesEngine,
    ReviewRule,
    CheckpointDefinition,
    RuleCategory,
    SeverityLevel,
    CheckpointTrigger
)


class TestReviewRulesEngineIntegration(unittest.TestCase):
    """Integration tests for the ReviewRulesEngine."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary configuration file for testing
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config_path = Path(self.temp_config.name)

        # Write a simple configuration to the temp file
        config_data = {
            'rules': [
                {
                    'id': 'integration_test_rule',
                    'name': 'Integration Test Rule',
                    'description': 'A rule for integration testing',
                    'category': 'quality_metrics',
                    'severity': 'medium',
                    'enabled': True
                }
            ],
            'checkpoints': [
                {
                    'name': 'integration_test_checkpoint',
                    'description': 'A checkpoint for integration testing',
                    'activation_trigger': 'event_based',
                    'associated_rules': ['integration_test_rule']
                }
            ]
        }

        yaml.dump(config_data, self.temp_config)
        self.temp_config.close()

        # Create engine with the temp configuration
        self.engine = ReviewRulesEngine(self.temp_config_path)

    def tearDown(self):
        """Clean up after each test method."""
        if self.temp_config_path.exists():
            self.temp_config_path.unlink()

    def test_engine_loads_configuration(self):
        """Test that the engine loads the configuration properly."""
        self.assertEqual(len(self.engine.rules), 1)
        self.assertEqual(len(self.engine.checkpoints), 1)

        # Check that the rule was loaded correctly
        rule = self.engine.rules.get('integration_test_rule')
        self.assertIsNotNone(rule)
        self.assertEqual(rule.name, 'Integration Test Rule')
        self.assertEqual(rule.category, RuleCategory.QUALITY_METRICS)

        # Check that the checkpoint was loaded correctly
        checkpoint = self.engine.checkpoints.get('integration_test_checkpoint')
        self.assertIsNotNone(checkpoint)
        self.assertEqual(checkpoint.name, 'integration_test_checkpoint')
        self.assertEqual(checkpoint.activation_trigger, CheckpointTrigger.EVENT_BASED)

    def test_rule_evaluation_integration(self):
        """Test that rule evaluation works in the integrated system."""
        # Add a rule to the engine
        rule = ReviewRule(
            id="eval_test_rule",
            name="Eval Test Rule",
            description="Rule for evaluation testing",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.LOW
        )
        self.engine.add_rule(rule)

        # Test evaluation with a mock context
        context = {
            "file_path": "test.py",
            "line_count": 100,
            "function_count": 5
        }

        # The rule should be disabled initially (placeholder implementation returns False)
        result = self.engine.evaluate_rule("eval_test_rule", context)
        self.assertFalse(result)

    def test_checkpoint_execution_integration(self):
        """Test that checkpoint execution works in the integrated system."""
        # Execute the loaded checkpoint
        context = {
            "file_path": "test.py",
            "change_type": "feature"
        }

        result = self.engine.execute_checkpoint("integration_test_checkpoint", context)

        # Check that the result has expected structure
        self.assertIn("checkpoint_name", result)
        self.assertIn("passed", result)
        self.assertIn("violations", result)
        self.assertIn("details", result)

        self.assertEqual(result["checkpoint_name"], "integration_test_checkpoint")
        # Since our placeholder evaluator returns False, the checkpoint should pass
        self.assertTrue(result["passed"])
        self.assertEqual(result["violations"], [])

    def test_save_and_reload_configuration(self):
        """Test saving the configuration and reloading it."""
        # Create a temporary file for saving
        temp_save_path = Path(tempfile.mktemp(suffix='.yaml'))

        # Add a new rule and checkpoint to the engine
        new_rule = ReviewRule(
            id="saved_test_rule",
            name="Saved Test Rule",
            description="Rule for save/load testing",
            category=RuleCategory.SECURITY,
            severity=SeverityLevel.HIGH
        )
        self.engine.add_rule(new_rule)

        new_checkpoint = CheckpointDefinition(
            name="saved_test_checkpoint",
            description="Checkpoint for save/load testing",
            activation_trigger=CheckpointTrigger.SCHEDULE_BASED
        )
        self.engine.add_checkpoint(new_checkpoint)

        # Save the configuration
        success = self.engine.save_configuration(temp_save_path)
        self.assertTrue(success)

        # Verify the file was created
        self.assertTrue(temp_save_path.exists())

        # Create a new engine and load the saved configuration
        new_engine = ReviewRulesEngine()
        load_success = new_engine.load_configuration(temp_save_path)
        self.assertTrue(load_success)

        # Verify that the new engine has the expected rules and checkpoints
        self.assertIn("integration_test_rule", new_engine.rules)
        self.assertIn("saved_test_rule", new_engine.rules)
        self.assertIn("integration_test_checkpoint", new_engine.checkpoints)
        self.assertIn("saved_test_checkpoint", new_engine.checkpoints)

        # Clean up
        if temp_save_path.exists():
            temp_save_path.unlink()

    def test_execute_all_checkpoints(self):
        """Test executing all checkpoints at once."""
        context = {
            "file_path": "test.py",
            "change_type": "refactor"
        }

        results = self.engine.execute_all_checkpoints(context)

        # Verify that we got results for our checkpoint
        self.assertIn("integration_test_checkpoint", results)

        # Verify structure of each result
        for checkpoint_name, result in results.items():
            self.assertIn("checkpoint_name", result)
            self.assertIn("passed", result)
            self.assertIn("violations", result)
            self.assertIn("details", result)

    def test_disabled_rule_not_evaluated(self):
        """Test that disabled rules are not evaluated even when associated with a checkpoint."""
        # Create a disabled rule
        disabled_rule = ReviewRule(
            id="disabled_test_rule",
            name="Disabled Test Rule",
            description="Disabled rule for testing",
            category=RuleCategory.PERFORMANCE,
            severity=SeverityLevel.HIGH,
            enabled=False
        )
        self.engine.add_rule(disabled_rule)

        # Create a checkpoint that includes the disabled rule
        disabled_checkpoint = CheckpointDefinition(
            name="disabled_test_checkpoint",
            description="Checkpoint with disabled rule",
            activation_trigger=CheckpointTrigger.EVENT_BASED,
            associated_rules=["disabled_test_rule", "integration_test_rule"]
        )
        self.engine.add_checkpoint(disabled_checkpoint)

        context = {
            "file_path": "test.py",
            "memory_usage": 100
        }

        # Execute the checkpoint
        result = self.engine.execute_checkpoint("disabled_test_checkpoint", context)

        # Since the disabled rule doesn't get evaluated, this should pass
        # (assuming the other rule also passes)
        self.assertIn("checkpoint_name", result)

        # The disabled rule should not appear in violations since it wasn't evaluated
        violating_rule_ids = [v['rule_id'] for v in result['violations']]
        self.assertNotIn("disabled_test_rule", violating_rule_ids)


class TestEndToEndScenario(unittest.TestCase):
    """End-to-end scenario test simulating real usage."""

    def setUp(self):
        """Set up the test engine with default rules."""
        self.engine = ReviewRulesEngine()

        # Add a few rules representing different categories
        quality_rule = ReviewRule(
            id="quality_complexity",
            name="Complexity Check",
            description="Check for excessive function complexity",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )

        security_rule = ReviewRule(
            id="security_hardcoded",
            name="Hardcoded Credentials Check",
            description="Check for hardcoded credentials",
            category=RuleCategory.SECURITY,
            severity=SeverityLevel.CRITICAL
        )

        standards_rule = ReviewRule(
            id="standards_naming",
            name="Naming Convention Check",
            description="Check for proper naming conventions",
            category=RuleCategory.STANDARDS,
            severity=SeverityLevel.LOW
        )

        for rule in [quality_rule, security_rule, standards_rule]:
            self.engine.add_rule(rule)

        # Add a checkpoint that includes these rules
        pre_commit_checkpoint = CheckpointDefinition(
            name="pre_commit",
            description="Pre-commit code review",
            activation_trigger=CheckpointTrigger.EVENT_BASED,
            associated_rules=["quality_complexity", "security_hardcoded", "standards_naming"],
            blocking=True
        )
        self.engine.add_checkpoint(pre_commit_checkpoint)

    def test_pre_commit_scenario(self):
        """Test a pre-commit scenario where code is reviewed before committing."""
        # Simulate code context (could include file contents, AST, etc.)
        code_context = {
            "file_path": "auth.py",
            "code_snippet": "password = 'secret123'",  # This might trigger security rule
            "function_names": ["login", "logout"],
            "variable_names": ["password", "user"],
            "line_count": 50,
            "complexity_score": 5
        }

        # Execute the pre-commit checkpoint
        result = self.engine.execute_checkpoint("pre_commit", code_context)

        # The checkpoint should execute and return results
        self.assertEqual(result["checkpoint_name"], "pre_commit")
        self.assertIsInstance(result["passed"], bool)
        self.assertIsInstance(result["violations"], list)
        self.assertIsInstance(result["details"], list)

        # The actual results would depend on the implementation of the evaluators
        # In this test, since our evaluators return False, we expect it to pass
        # But this could change depending on the actual implementation

        # Run evaluation of all rules to see how the system responds
        all_results = self.engine.evaluate_all_rules(code_context)
        self.assertEqual(len(all_results), 3)  # We have 3 rules


if __name__ == '__main__':
    unittest.main()