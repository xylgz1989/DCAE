import unittest
from src.dcae.discipline_control.methodology_enforcer import MethodologyEnforcer, TDDEnforcer, ProcessValidator
from src.dcae.discipline_control.discipline_controller import DisciplineLevel


class TestMethodologyEnforcer(unittest.TestCase):
    """Test cases for MethodologyEnforcer."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.enforcer = MethodologyEnforcer()

    def test_enforcer_initialization(self):
        """Test initializing the methodology enforcer."""
        self.assertIsNotNone(self.enforcer.active_enforcements)
        self.assertIsNotNone(self.enforcer.violations)

    def test_enforce_tdd_process(self):
        """Test enforcing TDD process."""
        tdd_enforcer = TDDEnforcer()

        # Mock a scenario where test is written before implementation
        test_written_first = tdd_enforcer.validate_tdd_sequence(["test_file.py", "implementation_file.py"])

        self.assertTrue(test_written_first)

        # Mock a scenario where implementation is written before test
        implementation_before_test = tdd_enforcer.validate_tdd_sequence(["implementation_file.py", "test_file.py"])

        self.assertFalse(implementation_before_test)

    def test_process_validation(self):
        """Test process validation functionality."""
        validator = ProcessValidator()

        # Validate a TDD process
        tdd_result = validator.validate_process('TDD', ['write_test', 'implement', 'refactor'])

        self.assertTrue(tdd_result)

        # Validate a process that doesn't follow TDD
        non_tdd_result = validator.validate_process('TDD', ['implement', 'write_test'])

        self.assertFalse(non_tdd_result)

    def test_enable_disable_processes(self):
        """Test enabling and disabling specific processes."""
        self.enforcer.enable_process('TDD')
        self.assertIn('TDD', self.enforcer.active_enforcements)

        self.enforcer.disable_process('TDD')
        self.assertNotIn('TDD', self.enforcer.active_enforcements)

    def test_check_compliance(self):
        """Test checking compliance with enforced processes."""
        self.enforcer.enable_process('TDD')

        # Simulate a compliant action
        is_compliant = self.enforcer.check_compliance('create_implementation', {'follows_tdd': True})

        self.assertTrue(is_compliant)

        # Simulate a non-compliant action
        is_not_compliant = self.enforcer.check_compliance('create_implementation', {'follows_tdd': False})

        self.assertFalse(is_not_compliant)

    def test_violation_tracking(self):
        """Test that violations are tracked properly."""
        initial_violations = len(self.enforcer.violations)

        self.enforcer.record_violation('TDD', 'Implemented code without writing test first')

        self.assertEqual(len(self.enforcer.violations), initial_violations + 1)

    def test_gating_mechanism(self):
        """Test that non-compliant operations are blocked."""
        self.enforcer.enable_process('TDD')

        # Should allow compliant operation
        allowed = self.enforcer.is_operation_allowed('create_implementation', {'follows_tdd': True})

        self.assertTrue(allowed)

        # Should block non-compliant operation
        blocked = self.enforcer.is_operation_allowed('create_implementation', {'follows_tdd': False})

        self.assertFalse(blocked)

    def test_methodology_config(self):
        """Test methodology configuration."""
        config = {
            'TDD': {'required': True, 'strictness': 'strict'},
            'CodeReview': {'required': True, 'strictness': 'balanced'}
        }

        self.enforcer.configure_methodologies(config)

        self.assertIn('TDD', self.enforcer.active_enforcements)
        self.assertIn('CodeReview', self.enforcer.active_enforcements)

    def test_composite_enforcement(self):
        """Test enforcing multiple methodologies simultaneously."""
        self.enforcer.enable_process('TDD')
        self.enforcer.enable_process('CodeReview')

        # Check compliance with both processes
        tdd_compliant = {'follows_tdd': True}
        review_compliant = {'has_review': True}

        overall_compliance = self.enforcer.check_compliance('complete_feature', {**tdd_compliant, **review_compliant})

        self.assertTrue(overall_compliance)

    def test_violation_reporting(self):
        """Test generating violation reports."""
        self.enforcer.record_violation('TDD', 'Bypassed test-first approach')
        self.enforcer.record_violation('CodeReview', 'Skipped peer review')

        report = self.enforcer.generate_violation_report()

        self.assertIn('violations', report)
        self.assertGreater(len(report['violations']), 0)

    def test_reset_violations(self):
        """Test resetting violation tracking."""
        self.enforcer.record_violation('TDD', 'Test violation')
        self.enforcer.reset_violations()

        self.assertEqual(len(self.enforcer.violations), 0)

    def test_enforcement_by_discipline_level(self):
        """Test that enforcement varies by discipline level."""
        tdd_enforcer = TDDEnforcer()

        # Get enforcement rules for different discipline levels
        fast_rules = tdd_enforcer.get_enforcement_rules(DisciplineLevel.FAST)
        strict_rules = tdd_enforcer.get_enforcement_rules(DisciplineLevel.STRICT)

        # Strict mode should have stricter enforcement than fast mode
        self.assertLessEqual(fast_rules.get('required_tests', 0), strict_rules.get('required_tests', 0))


class TestTDDEnforcer(unittest.TestCase):
    """Test cases for TDDEnforcer."""

    def test_tdd_validation_logic(self):
        """Test TDD validation logic."""
        enforcer = TDDEnforcer()

        # Test that TDD sequence is valid: test first, then implementation
        valid_sequence = enforcer.validate_tdd_sequence(['test.py', 'impl.py'])
        self.assertTrue(valid_sequence)

        # Test that non-TDD sequence is invalid: implementation first
        invalid_sequence = enforcer.validate_tdd_sequence(['impl.py', 'test.py'])
        self.assertFalse(invalid_sequence)

    def test_required_test_coverage(self):
        """Test required test coverage enforcement."""
        enforcer = TDDEnforcer()

        # Should pass with adequate test coverage
        passes = enforcer.validate_test_coverage({'lines': 100, 'covered': 90})
        self.assertTrue(passes)

        # Should fail with inadequate test coverage
        fails = enforcer.validate_test_coverage({'lines': 100, 'covered': 30})
        self.assertFalse(fails)

    def test_test_naming_conventions(self):
        """Test test naming convention enforcement."""
        enforcer = TDDEnforcer()

        # Valid test names
        valid_names = ['test_addition.py', 'user_auth_test.py', 'spec_calculator.js']
        for name in valid_names:
            self.assertTrue(enforcer.validate_test_filename(name), f"Failed for {name}")

        # Invalid test names
        invalid_names = ['impl.py', 'main.py', 'production_code.js']
        for name in invalid_names:
            self.assertFalse(enforcer.validate_test_filename(name), f"Passed incorrectly for {name}")


if __name__ == '__main__':
    unittest.main()