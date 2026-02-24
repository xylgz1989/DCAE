import unittest
from src.dcae.discipline_control.discipline_controller import DisciplineLevel, DisciplineController


class TestDisciplineLevel(unittest.TestCase):
    """Test cases for DisciplineLevel enum."""

    def test_discipline_level_values(self):
        """Test that DisciplineLevel enum has expected values."""
        self.assertEqual(DisciplineLevel.FAST.value, "fast")
        self.assertEqual(DisciplineLevel.BALANCED.value, "balanced")
        self.assertEqual(DisciplineLevel.STRICT.value, "strict")

    def test_discipline_level_names(self):
        """Test that DisciplineLevel enum has expected names."""
        self.assertTrue(hasattr(DisciplineLevel, 'FAST'))
        self.assertTrue(hasattr(DisciplineLevel, 'BALANCED'))
        self.assertTrue(hasattr(DisciplineLevel, 'STRICT'))


class TestDisciplineController(unittest.TestCase):
    """Test cases for DisciplineController."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.controller = DisciplineController()

    def test_controller_initialization(self):
        """Test initializing the discipline controller."""
        self.assertEqual(self.controller.current_level, DisciplineLevel.BALANCED)  # Default should be balanced
        self.assertIsNotNone(self.controller.settings)
        self.assertIsNotNone(self.controller.history)

    def test_set_discipline_level_fast(self):
        """Test setting discipline level to FAST."""
        result = self.controller.set_level(DisciplineLevel.FAST)

        self.assertTrue(result)
        self.assertEqual(self.controller.current_level, DisciplineLevel.FAST)

    def test_set_discipline_level_balanced(self):
        """Test setting discipline level to BALANCED."""
        result = self.controller.set_level(DisciplineLevel.BALANCED)

        self.assertTrue(result)
        self.assertEqual(self.controller.current_level, DisciplineLevel.BALANCED)

    def test_set_discipline_level_strict(self):
        """Test setting discipline level to STRICT."""
        result = self.controller.set_level(DisciplineLevel.STRICT)

        self.assertTrue(result)
        self.assertEqual(self.controller.current_level, DisciplineLevel.STRICT)

    def test_get_current_level(self):
        """Test getting the current discipline level."""
        self.controller.set_level(DisciplineLevel.STRICT)

        current_level = self.controller.get_current_level()

        self.assertEqual(current_level, DisciplineLevel.STRICT)

    def test_get_settings_for_level(self):
        """Test getting settings appropriate for a discipline level."""
        settings = self.controller.get_settings_for_level(DisciplineLevel.FAST)

        # Fast mode settings should be less strict
        self.assertLess(settings.get('validation_level', 10), 5)
        self.assertLess(settings.get('review_frequency', 10), 5)

    def test_history_tracking(self):
        """Test that discipline level changes are tracked in history."""
        initial_count = len(self.controller.history)

        self.controller.set_level(DisciplineLevel.FAST)
        self.controller.set_level(DisciplineLevel.STRICT)

        self.assertEqual(len(self.controller.history), initial_count + 2)

    def test_persistent_storage(self):
        """Test that discipline settings can be saved and loaded."""
        # Set a level and save
        self.controller.set_level(DisciplineLevel.STRICT)
        self.controller.save_settings("test_project")

        # Create new controller and load
        new_controller = DisciplineController()
        loaded = new_controller.load_settings("test_project")

        self.assertTrue(loaded)
        self.assertEqual(new_controller.current_level, DisciplineLevel.STRICT)

    def test_preview_changes(self):
        """Test previewing changes before applying them."""
        initial_level = self.controller.get_current_level()

        preview_settings = self.controller.preview_settings_for_level(DisciplineLevel.STRICT)

        # Preview shouldn't change the actual level
        self.assertEqual(self.controller.get_current_level(), initial_level)
        # But should return appropriate settings
        self.assertIsNotNone(preview_settings)
        self.assertGreater(preview_settings.get('validation_level', 0), 5)  # Strict mode should have higher validation


if __name__ == '__main__':
    unittest.main()