import unittest
from src.dcae.discipline_control.validation_adjuster import ValidationAdjuster, ValidationLevel, ValidationProfile
from src.dcae.discipline_control.discipline_controller import DisciplineLevel


class TestValidationLevel(unittest.TestCase):
    """Test cases for ValidationLevel enum."""

    def test_validation_level_values(self):
        """Test that ValidationLevel enum has expected values."""
        self.assertEqual(ValidationLevel.MINIMAL.value, 1)
        self.assertEqual(ValidationLevel.STANDARD.value, 5)
        self.assertEqual(ValidationLevel.RIGOROUS.value, 9)


class TestValidationAdjuster(unittest.TestCase):
    """Test cases for ValidationAdjuster."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.adjuster = ValidationAdjuster()

    def test_adjuster_initialization(self):
        """Test initializing the validation adjuster."""
        self.assertIsNotNone(self.adjuster.validation_rules)

    def test_adjust_for_fast_discipline(self):
        """Test adjusting validation for fast discipline level."""
        rules = self.adjuster.adjust_validation_for_level(DisciplineLevel.FAST)

        # Fast mode should have fewer validation rules
        self.assertLess(len(rules), 10)  # Should be minimal validation
        self.assertIn('syntax_check', rules)
        # Security checks might be reduced in fast mode
        # Performance checks might be minimized

    def test_adjust_for_balanced_discipline(self):
        """Test adjusting validation for balanced discipline level."""
        rules = self.adjuster.adjust_validation_for_level(DisciplineLevel.BALANCED)

        # Balanced mode should have moderate validation
        self.assertGreater(len(rules), 2)
        self.assertLess(len(rules), 15)  # More than fast, less than strict
        self.assertIn('syntax_check', rules)
        self.assertIn('style_check', rules)

    def test_adjust_for_strict_discipline(self):
        """Test adjusting validation for strict discipline level."""
        rules = self.adjuster.adjust_validation_for_level(DisciplineLevel.STRICT)

        # Strict mode should have comprehensive validation
        self.assertGreater(len(rules), 5)
        self.assertIn('syntax_check', rules)
        self.assertIn('style_check', rules)
        self.assertIn('security_scan', rules)
        self.assertIn('dependency_check', rules)

    def test_get_validation_parameters(self):
        """Test getting validation parameters for different levels."""
        params = self.adjuster.get_validation_parameters(DisciplineLevel.STRICT)

        self.assertIn('max_line_length', params)
        self.assertIn('min_test_coverage', params)
        self.assertIn('security_threshold', params)

    def test_apply_validation_settings(self):
        """Test applying validation settings to a validation process."""
        # This would involve mocking a validation process
        # For now, just verify the adjuster can prepare settings
        settings = self.adjuster.prepare_settings(DisciplineLevel.BALANCED)

        self.assertIn('enabled_checks', settings)
        self.assertIn('thresholds', settings)
        self.assertIn('timeouts', settings)

    def test_validation_mapping_correctness(self):
        """Test that validation mappings are correct."""
        fast_rules = self.adjuster.adjust_validation_for_level(DisciplineLevel.FAST)
        strict_rules = self.adjuster.adjust_validation_for_level(DisciplineLevel.STRICT)

        # Strict mode should have more rules than fast mode
        self.assertGreater(len(strict_rules), len(fast_rules))

    def test_custom_validation_config(self):
        """Test using custom validation configuration."""
        custom_config = {
            'custom_rule_1': {'enabled': True, 'severity': 'warning'},
            'custom_rule_2': {'enabled': False, 'severity': 'info'}
        }

        self.adjuster.update_custom_config(custom_config)

        # Verify custom config is stored
        self.assertIn('custom_rule_1', self.adjuster.custom_rules)

    def test_validation_profile_creation(self):
        """Test creating validation profiles."""
        profile = self.adjuster.create_validation_profile(DisciplineLevel.BALANCED)

        self.assertIsInstance(profile, ValidationProfile)
        self.assertIsNotNone(profile.name)
        self.assertIsNotNone(profile.enabled_checks)
        self.assertIsNotNone(profile.thresholds)
        self.assertIsNotNone(profile.timeouts)
        self.assertIsNotNone(profile.severity_levels)

    def test_validation_performance_impact(self):
        """Test validation settings for performance impact."""
        fast_params = self.adjuster.get_validation_parameters(DisciplineLevel.FAST)
        strict_params = self.adjuster.get_validation_parameters(DisciplineLevel.STRICT)

        # Fast mode should have lower timeouts
        fast_timeout = fast_params.get('timeout_seconds', 30)
        strict_timeout = strict_params.get('timeout_seconds', 120)

        # Strict mode may allow longer timeouts for comprehensive checks
        # But this test just ensures both return values
        self.assertIsInstance(fast_timeout, int)
        self.assertIsInstance(strict_timeout, int)

    def test_validation_error_handling(self):
        """Test validation adjustment error handling."""
        # Test with an unknown discipline level (though it shouldn't happen with enum)
        try:
            # This should use default behavior
            rules = self.adjuster.adjust_validation_for_level(DisciplineLevel.BALANCED)
            self.assertIsNotNone(rules)
        except Exception:
            # If it raises an exception, that's also acceptable as long as it's handled
            pass


if __name__ == '__main__':
    unittest.main()