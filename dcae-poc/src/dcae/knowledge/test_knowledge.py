"""Tests for domain-specific knowledge functionality."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from dcae.knowledge import DomainKnowledgeBase, DomainType, KnowledgeEntry, KnowledgeFusionEngine
from dcae.knowledge.input_handler import DomainKnowledgeInputHandler
from dcae.knowledge.validator import KnowledgeValidator


class TestDomainKnowledgeBase(unittest.TestCase):
    """Tests for DomainKnowledgeBase."""

    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.kb = DomainKnowledgeBase(db_path=self.temp_db.name)

    def tearDown(self):
        """Clean up test database."""
        Path(self.temp_db.name).unlink(missing_ok=True)

    def test_add_and_get_knowledge(self):
        """Test adding and retrieving knowledge."""
        entry_id = self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="Python is a programming language",
            source="test",
            confidence=0.9
        )

        entries = self.kb.get_knowledge()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].id, entry_id)
        self.assertEqual(entries[0].domain, DomainType.TECHNICAL)
        self.assertEqual(entries[0].content, "Python is a programming language")
        self.assertEqual(entries[0].confidence, 0.9)

    def test_filter_by_domain(self):
        """Test filtering knowledge by domain."""
        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="Python is a programming language",
            source="test"
        )
        self.kb.add_knowledge(
            domain=DomainType.BUSINESS,
            content="Revenue is income",
            source="test"
        )

        tech_entries = self.kb.get_knowledge(domain=DomainType.TECHNICAL)
        self.assertEqual(len(tech_entries), 1)
        self.assertEqual(tech_entries[0].content, "Python is a programming language")

        business_entries = self.kb.get_knowledge(domain=DomainType.BUSINESS)
        self.assertEqual(len(business_entries), 1)
        self.assertEqual(business_entries[0].content, "Revenue is income")

    def test_min_confidence_filter(self):
        """Test filtering by minimum confidence."""
        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="High confidence info",
            source="test",
            confidence=0.9
        )
        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="Low confidence info",
            source="test",
            confidence=0.3
        )

        high_conf_entries = self.kb.get_knowledge(min_confidence=0.5)
        self.assertEqual(len(high_conf_entries), 1)
        self.assertEqual(high_conf_entries[0].content, "High confidence info")

    def test_search_knowledge(self):
        """Test searching knowledge."""
        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="Python programming language",
            source="test"
        )
        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="Java programming language",
            source="test"
        )

        results = self.kb.search_knowledge("Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "Python programming language")

    def test_update_confidence(self):
        """Test updating knowledge confidence."""
        entry_id = self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="Some info",
            source="test",
            confidence=0.7
        )

        self.kb.update_knowledge_confidence(entry_id, 0.9)

        entries = self.kb.get_knowledge()
        self.assertEqual(entries[0].confidence, 0.9)


class TestDomainKnowledgeInputHandler(unittest.TestCase):
    """Tests for DomainKnowledgeInputHandler."""

    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.kb = DomainKnowledgeBase(db_path=self.temp_db.name)
        self.handler = DomainKnowledgeInputHandler(self.kb)

    def tearDown(self):
        """Clean up test database."""
        Path(self.temp_db.name).unlink(missing_ok=True)

    def test_manual_knowledge_addition(self):
        """Test adding knowledge manually."""
        entry_id = self.handler.add_manual_knowledge(
            domain=DomainType.TECHNICAL,
            content="Manual entry",
            source="test",
            confidence=0.8
        )

        entries = self.kb.get_knowledge()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].id, entry_id)
        self.assertEqual(entries[0].content, "Manual entry")

    def test_import_from_json(self):
        """Test importing knowledge from JSON."""
        json_content = [
            {"content": "JSON entry 1", "confidence": 0.8},
            {"content": "JSON entry 2", "confidence": 0.7, "source": "test_source"}
        ]

        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        import json
        json.dump(json_content, temp_file)
        temp_file.close()

        count = self.handler.import_from_file(temp_file.name, DomainType.TECHNICAL)
        self.assertEqual(count, 2)

        entries = self.kb.get_knowledge()
        self.assertEqual(len(entries), 2)

        Path(temp_file.name).unlink()

    def test_import_from_text(self):
        """Test importing knowledge from text."""
        text = """This is the first paragraph with important information.

This is the second paragraph with different information.

Short third paragraph."""

        count = self.handler.import_from_text(text, DomainType.TECHNICAL)
        # Should create at least 2 entries from the paragraphs
        self.assertGreaterEqual(count, 2)

        entries = self.kb.get_knowledge()
        self.assertGreaterEqual(len(entries), 2)

    def test_validate_knowledge_entry(self):
        """Test knowledge entry validation."""
        # Valid entry
        is_valid, error = self.handler.validate_knowledge_entry(
            "Valid content with sufficient length",
            DomainType.TECHNICAL
        )
        self.assertTrue(is_valid)

        # Invalid - too short
        is_valid, error = self.handler.validate_knowledge_entry(
            "Hi",
            DomainType.TECHNICAL
        )
        self.assertFalse(is_valid)


class TestKnowledgeValidator(unittest.TestCase):
    """Tests for KnowledgeValidator."""

    def setUp(self):
        """Set up validator."""
        self.validator = KnowledgeValidator()

    def test_validate_entry(self):
        """Test entry validation."""
        entry = KnowledgeEntry(
            id="test-id",
            domain=DomainType.TECHNICAL,
            content="Python is a programming language used for various applications.",
            source="test",
            confidence=0.8,
            timestamp=datetime.now()
        )

        is_valid, errors = self.validator.validate_entry(entry)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_entry(self):
        """Test validation of invalid entry."""
        entry = KnowledgeEntry(
            id="",
            domain=DomainType.TECHNICAL,
            content="",  # Empty content
            source="",
            confidence=1.5,  # Invalid confidence
            timestamp=datetime.now()
        )

        is_valid, errors = self.validator.validate_entry(entry)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_detect_outdated_information(self):
        """Test detection of outdated information."""
        entry = KnowledgeEntry(
            id="test-id",
            domain=DomainType.TECHNICAL,
            content="This was true as of 2020-01-01, but may be outdated now.",
            source="test",
            confidence=0.8,
            timestamp=datetime.now(),
            metadata={"expiry_date": "2020-01-01T00:00:00"}
        )

        is_outdated = self.validator.detect_outdated_information(entry)
        self.assertTrue(is_outdated)


class TestKnowledgeFusionEngine(unittest.TestCase):
    """Tests for KnowledgeFusionEngine."""

    def setUp(self):
        """Set up test database and engine."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.kb = DomainKnowledgeBase(db_path=self.temp_db.name)

        # Add some test knowledge
        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="The best practice for API design is to use REST principles",
            source="best_practices_guide",
            confidence=0.9
        )

        self.engine = KnowledgeFusionEngine(self.kb)

    def tearDown(self):
        """Clean up test database."""
        Path(self.temp_db.name).unlink(missing_ok=True)

    def test_get_relevant_knowledge(self):
        """Test getting relevant knowledge."""
        relevant = self.engine.get_relevant_knowledge(
            context="API design",
            domain=DomainType.TECHNICAL
        )

        self.assertEqual(len(relevant), 1)
        self.assertIn("API", relevant[0].content)

    def test_integrate_knowledge(self):
        """Test integrating knowledge into a prompt."""
        original_prompt = "How should I design my API?"
        augmented_prompt = self.engine.integrate_knowledge(
            prompt=original_prompt,
            context="API design",
            domain=DomainType.TECHNICAL
        )

        self.assertIn("API", augmented_prompt)
        self.assertIn("REST", augmented_prompt)
        self.assertIn(original_prompt, augmented_prompt)


if __name__ == '__main__':
    unittest.main()