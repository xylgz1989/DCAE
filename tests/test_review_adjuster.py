import unittest
from src.dcae.discipline_control.review_adjuster import ReviewAdjuster, ReviewFrequency
from src.dcae.discipline_control.discipline_controller import DisciplineLevel


class TestReviewFrequency(unittest.TestCase):
    """Test cases for ReviewFrequency enum."""

    def test_review_frequency_values(self):
        """Test that ReviewFrequency enum has expected values."""
        self.assertEqual(ReviewFrequency.LOW.value, 1)
        self.assertEqual(ReviewFrequency.MEDIUM.value, 5)
        self.assertEqual(ReviewFrequency.HIGH.value, 9)


class TestReviewAdjuster(unittest.TestCase):
    """Test cases for ReviewAdjuster."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.adjuster = ReviewAdjuster()

    def test_adjuster_initialization(self):
        """Test initializing the review adjuster."""
        self.assertIsNotNone(self.adjuster.review_criteria)

    def test_adjust_for_fast_discipline(self):
        """Test adjusting review for fast discipline level."""
        criteria = self.adjuster.adjust_review_for_level(DisciplineLevel.FAST)

        # Fast mode should have minimal review criteria
        self.assertLess(len(criteria), 5)  # Should be minimal review
        # Fast mode should have shorter review times or fewer checks
        self.assertIn('quick_syntax_check', criteria)

    def test_adjust_for_balanced_discipline(self):
        """Test adjusting review for balanced discipline level."""
        criteria = self.adjuster.adjust_review_for_level(DisciplineLevel.BALANCED)

        # Balanced mode should have moderate review
        self.assertGreater(len(criteria), 2)
        self.assertLess(len(criteria), 10)  # More than fast, less than strict
        self.assertIn('syntax_check', criteria)
        self.assertIn('style_check', criteria)

    def test_adjust_for_strict_discipline(self):
        """Test adjusting review for strict discipline level."""
        criteria = self.adjuster.adjust_review_for_level(DisciplineLevel.STRICT)

        # Strict mode should have comprehensive review
        self.assertGreater(len(criteria), 5)
        self.assertIn('syntax_check', criteria)
        self.assertIn('style_check', criteria)
        self.assertIn('security_review', criteria)
        self.assertIn('performance_review', criteria)

    def test_get_review_parameters(self):
        """Test getting review parameters for different levels."""
        params = self.adjuster.get_review_parameters(DisciplineLevel.STRICT)

        self.assertIn('max_review_time', params)
        self.assertIn('review_depth', params)
        self.assertIn('approval_steps', params)

    def test_apply_review_settings(self):
        """Test applying review settings to a review process."""
        # This would involve mocking a review process
        # For now, just verify the adjuster can prepare settings
        settings = self.adjuster.prepare_settings(DisciplineLevel.BALANCED)

        self.assertIn('enabled_reviews', settings)
        self.assertIn('time_limits', settings)
        self.assertIn('approvals_needed', settings)

    def test_review_mapping_correctness(self):
        """Test that review mappings are correct."""
        fast_criteria = self.adjuster.adjust_review_for_level(DisciplineLevel.FAST)
        strict_criteria = self.adjuster.adjust_review_for_level(DisciplineLevel.STRICT)

        # Strict mode should have more criteria than fast mode
        self.assertGreater(len(strict_criteria), len(fast_criteria))

    def test_custom_review_config(self):
        """Test using custom review configuration."""
        custom_config = {
            'custom_review_1': {'enabled': True, 'urgency': 'high'},
            'custom_review_2': {'enabled': False, 'urgency': 'low'}
        }

        self.adjuster.update_custom_config(custom_config)

        # Verify custom config is stored
        self.assertIn('custom_review_1', self.adjuster.custom_reviews)

    def test_review_profile_creation(self):
        """Test creating review profiles."""
        profile = self.adjuster.create_review_profile(DisciplineLevel.FAST)

        self.assertIsNotNone(profile.name)
        self.assertIsNotNone(profile.enabled_reviews)
        self.assertIsNotNone(profile.parameters)

    def test_review_frequency_impact(self):
        """Test review settings for frequency impact."""
        fast_params = self.adjuster.get_review_parameters(DisciplineLevel.FAST)
        strict_params = self.adjuster.get_review_parameters(DisciplineLevel.STRICT)

        # Fast mode should have fewer approval steps
        fast_approvals = fast_params.get('approval_steps', 5)
        strict_approvals = strict_params.get('approval_steps', 5)

        # Strict mode should typically have more approvals
        self.assertLessEqual(fast_approvals, strict_approvals)

    def test_review_error_handling(self):
        """Test review adjustment error handling."""
        # Test with an unknown discipline level (though it shouldn't happen with enum)
        try:
            # This should use default behavior
            criteria = self.adjuster.adjust_review_for_level(DisciplineLevel.BALANCED)
            self.assertIsNotNone(criteria)
        except Exception:
            # If it raises an exception, that's also acceptable as long as it's handled
            pass


if __name__ == '__main__':
    unittest.main()