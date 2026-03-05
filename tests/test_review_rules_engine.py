import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import yaml

from src.review_rules_engine import (
    ReviewRulesEngine,
    ReviewRule,
    CheckpointDefinition,
    RuleCategory,
    SeverityLevel,
    CheckpointTrigger,
    QualityMetricsEvaluator,
    SecurityEvaluator,
    PerformanceEvaluator,
    ArchitectureEvaluator,
    StandardsEvaluator,
    RuleCondition,
    RuleAction
)


class TestReviewRulesEngine(unittest.TestCase):
    """Test cases for the ReviewRulesEngine class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.engine = ReviewRulesEngine()

    def test_add_rule_success(self):
        """Test that adding a valid rule works correctly."""
        rule = ReviewRule(
            id="test_rule",
            name="Test Rule",
            description="A test rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )

        result = self.engine.add_rule(rule)
        self.assertTrue(result)
        self.assertIn("test_rule", self.engine.rules)
        self.assertEqual(self.engine.rules["test_rule"].name, "Test Rule")

    def test_add_rule_validation_failure(self):
        """Test that adding an invalid rule returns False."""
        rule = ReviewRule(
            id="",  # Invalid - no ID
            name="Test Rule",
            description="A test rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )

        result = self.engine.add_rule(rule)
        self.assertFalse(result)

    def test_remove_rule(self):
        """Test removing a rule."""
        rule = ReviewRule(
            id="test_rule",
            name="Test Rule",
            description="A test rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )
        self.engine.add_rule(rule)

        # Verify rule was added
        self.assertIn("test_rule", self.engine.rules)

        # Remove the rule
        result = self.engine.remove_rule("test_rule")
        self.assertTrue(result)
        self.assertNotIn("test_rule", self.engine.rules)

    def test_get_rule(self):
        """Test getting a rule by ID."""
        rule = ReviewRule(
            id="test_rule",
            name="Test Rule",
            description="A test rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )
        self.engine.add_rule(rule)

        retrieved_rule = self.engine.get_rule("test_rule")
        self.assertIsNotNone(retrieved_rule)
        self.assertEqual(retrieved_rule.name, "Test Rule")

    def test_add_checkpoint_success(self):
        """Test that adding a valid checkpoint works correctly."""
        checkpoint = CheckpointDefinition(
            name="test_checkpoint",
            description="A test checkpoint",
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )

        result = self.engine.add_checkpoint(checkpoint)
        self.assertTrue(result)
        self.assertIn("test_checkpoint", self.engine.checkpoints)
        self.assertEqual(self.engine.checkpoints["test_checkpoint"].name, "test_checkpoint")

    def test_add_checkpoint_validation_failure(self):
        """Test that adding an invalid checkpoint returns False."""
        checkpoint = CheckpointDefinition(
            name="",  # Invalid - no name
            description="A test checkpoint",
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )

        result = self.engine.add_checkpoint(checkpoint)
        self.assertFalse(result)

    def test_remove_checkpoint(self):
        """Test removing a checkpoint."""
        checkpoint = CheckpointDefinition(
            name="test_checkpoint",
            description="A test checkpoint",
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )
        self.engine.add_checkpoint(checkpoint)

        # Verify checkpoint was added
        self.assertIn("test_checkpoint", self.engine.checkpoints)

        # Remove the checkpoint
        result = self.engine.remove_checkpoint("test_checkpoint")
        self.assertTrue(result)
        self.assertNotIn("test_checkpoint", self.engine.checkpoints)

    def test_get_checkpoint(self):
        """Test getting a checkpoint by name."""
        checkpoint = CheckpointDefinition(
            name="test_checkpoint",
            description="A test checkpoint",
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )
        self.engine.add_checkpoint(checkpoint)

        retrieved_checkpoint = self.engine.get_checkpoint("test_checkpoint")
        self.assertIsNotNone(retrieved_checkpoint)
        self.assertEqual(retrieved_checkpoint.name, "test_checkpoint")

    def test_evaluate_rule_disabled(self):
        """Test that disabled rules are not evaluated."""
        rule = ReviewRule(
            id="disabled_rule",
            name="Disabled Rule",
            description="A disabled rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM,
            enabled=False
        )
        self.engine.add_rule(rule)

        # Mock the evaluator to return True (which would indicate a violation)
        mock_evaluator = Mock()
        mock_evaluator.evaluate.return_value = True
        self.engine.evaluators[RuleCategory.QUALITY_METRICS] = mock_evaluator

        # Should return False because the rule is disabled
        result = self.engine.evaluate_rule("disabled_rule", {})
        self.assertFalse(result)
        # The evaluator should not have been called
        mock_evaluator.evaluate.assert_not_called()

    def test_execute_checkpoint_nonexistent(self):
        """Test executing a non-existent checkpoint raises an error."""
        with self.assertRaises(ValueError):
            self.engine.execute_checkpoint("nonexistent_checkpoint", {})

    def test_execute_all_checkpoints_empty(self):
        """Test executing all checkpoints when none are defined."""
        results = self.engine.execute_all_checkpoints({})
        self.assertEqual(results, {})

    def test_create_preset_engine(self):
        """Test creating an engine with preset configurations."""
        from src.review_rules_engine import create_preset_engine

        engine = create_preset_engine("standard")
        self.assertIsInstance(engine, ReviewRulesEngine)
        self.assertGreater(len(engine.rules), 0)

    def test_save_and_load_configuration(self):
        """Test saving and loading configuration."""
        # Add a rule and checkpoint to the engine
        rule = ReviewRule(
            id="config_test_rule",
            name="Config Test Rule",
            description="A rule for configuration testing",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )
        self.engine.add_rule(rule)

        checkpoint = CheckpointDefinition(
            name="config_test_checkpoint",
            description="A checkpoint for configuration testing",
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )
        self.engine.add_checkpoint(checkpoint)

        # Create a temporary file for the configuration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Save the configuration
        save_result = self.engine.save_configuration(temp_path)
        self.assertTrue(save_result)

        # Create a new engine and load the configuration
        new_engine = ReviewRulesEngine()
        load_result = new_engine.load_configuration(temp_path)
        self.assertTrue(load_result)

        # Check that the new engine has the same rules and checkpoints
        self.assertIn("config_test_rule", new_engine.rules)
        self.assertIn("config_test_checkpoint", new_engine.checkpoints)
        self.assertEqual(new_engine.rules["config_test_rule"].name, "Config Test Rule")
        self.assertEqual(new_engine.checkpoints["config_test_checkpoint"].name, "config_test_checkpoint")

        # Clean up
        temp_path.unlink()


class TestRuleEvaluators(unittest.TestCase):
    """Test cases for the rule evaluators."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.rule = ReviewRule(
            id="test_rule",
            name="Test Rule",
            description="A test rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )

    def test_quality_metrics_evaluator(self):
        """Test the QualityMetricsEvaluator."""
        evaluator = QualityMetricsEvaluator()
        result = evaluator.evaluate(self.rule, {})
        self.assertFalse(result)  # Placeholder returns False

    def test_security_evaluator(self):
        """Test the SecurityEvaluator."""
        evaluator = SecurityEvaluator()
        result = evaluator.evaluate(self.rule, {})
        self.assertFalse(result)  # Placeholder returns False

    def test_performance_evaluator(self):
        """Test the PerformanceEvaluator."""
        evaluator = PerformanceEvaluator()
        result = evaluator.evaluate(self.rule, {})
        self.assertFalse(result)  # Placeholder returns False

    def test_architecture_evaluator(self):
        """Test the ArchitectureEvaluator."""
        evaluator = ArchitectureEvaluator()
        result = evaluator.evaluate(self.rule, {})
        self.assertFalse(result)  # Placeholder returns False

    def test_standards_evaluator(self):
        """Test the StandardsEvaluator."""
        evaluator = StandardsEvaluator()
        result = evaluator.evaluate(self.rule, {})
        self.assertFalse(result)  # Placeholder returns False


class TestConfigurationValidator(unittest.TestCase):
    """Test cases for the ConfigurationValidator."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        from src.review_rules_engine import ConfigurationValidator
        self.validator = ConfigurationValidator()

    def test_validate_valid_rule(self):
        """Test validating a valid rule."""
        rule = ReviewRule(
            id="valid_rule",
            name="Valid Rule",
            description="A valid rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )
        errors = self.validator.validate_rule_config(rule)
        self.assertEqual(errors, [])

    def test_validate_invalid_rule_missing_id(self):
        """Test validating a rule with missing ID."""
        rule = ReviewRule(
            id="",  # Missing ID
            name="Invalid Rule",
            description="An invalid rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )
        errors = self.validator.validate_rule_config(rule)
        self.assertIn("Rule ID is required", errors)

    def test_validate_invalid_rule_missing_name(self):
        """Test validating a rule with missing name."""
        rule = ReviewRule(
            id="invalid_rule",
            name="",  # Missing name
            description="An invalid rule",
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )
        errors = self.validator.validate_rule_config(rule)
        self.assertIn("Rule name is required", errors)

    def test_validate_invalid_rule_missing_description(self):
        """Test validating a rule with missing description."""
        rule = ReviewRule(
            id="invalid_rule",
            name="Invalid Rule",
            description="",  # Missing description
            category=RuleCategory.QUALITY_METRICS,
            severity=SeverityLevel.MEDIUM
        )
        errors = self.validator.validate_rule_config(rule)
        self.assertIn("Rule description is required", errors)

    def test_validate_valid_checkpoint(self):
        """Test validating a valid checkpoint."""
        checkpoint = CheckpointDefinition(
            name="valid_checkpoint",
            description="A valid checkpoint",
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )
        errors = self.validator.validate_checkpoint_config(checkpoint)
        self.assertEqual(errors, [])

    def test_validate_invalid_checkpoint_missing_name(self):
        """Test validating a checkpoint with missing name."""
        checkpoint = CheckpointDefinition(
            name="",  # Missing name
            description="An invalid checkpoint",
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )
        errors = self.validator.validate_checkpoint_config(checkpoint)
        self.assertIn("Checkpoint name is required", errors)

    def test_validate_invalid_checkpoint_missing_description(self):
        """Test validating a checkpoint with missing description."""
        checkpoint = CheckpointDefinition(
            name="invalid_checkpoint",
            description="",  # Missing description
            activation_trigger=CheckpointTrigger.EVENT_BASED
        )
        errors = self.validator.validate_checkpoint_config(checkpoint)
        self.assertIn("Checkpoint description is required", errors)


if __name__ == '__main__':
    unittest.main()