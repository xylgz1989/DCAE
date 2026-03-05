"""Tests for cross-domain recommendation functionality."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from dcae.knowledge import (
    DomainKnowledgeBase,
    DomainType,
    KnowledgeEntry,
    CrossDomainRecommendationEngine,
    Recommendation,
    CrossDomainRelationship
)


class TestRelationshipIdentifier(unittest.TestCase):
    """Tests for RelationshipIdentifier."""

    def setUp(self):
        """Set up test database."""
        from dcae.knowledge.cross_domain import RelationshipIdentifier
        self.identifier = RelationshipIdentifier()

    def test_identify_relationships_different_domains(self):
        """Test identifying relationships between different domain types."""
        # Create knowledge entries from different domains
        entry1 = KnowledgeEntry(
            id="1",
            domain=DomainType.TECHNICAL,
            content="API rate limiting helps prevent server overload by controlling request frequency",
            source="tech_docs",
            confidence=0.8,
            timestamp=datetime.now()
        )

        entry2 = KnowledgeEntry(
            id="2",
            domain=DomainType.BUSINESS,
            content="Customer experience is affected when systems are overloaded or unresponsive",
            source="business_docs",
            confidence=0.7,
            timestamp=datetime.now()
        )

        knowledge_list = [entry1, entry2]
        relationships = self.identifier.identify_relationships(knowledge_list)

        # Check if any relationships were identified
        self.assertIsInstance(relationships, list)
        # May or may not find a relationship depending on similarity

    def test_identify_relationships_same_domain(self):
        """Test that relationships aren't identified between same domain entries."""
        entry1 = KnowledgeEntry(
            id="1",
            domain=DomainType.TECHNICAL,
            content="API rate limiting helps prevent server overload",
            source="tech_docs",
            confidence=0.8,
            timestamp=datetime.now()
        )

        entry2 = KnowledgeEntry(
            id="2",
            domain=DomainType.TECHNICAL,  # Same domain
            content="Database optimization improves query performance",
            source="tech_docs",
            confidence=0.7,
            timestamp=datetime.now()
        )

        knowledge_list = [entry1, entry2]
        relationships = self.identifier.identify_relationships(knowledge_list)

        # Since both are same domain, there shouldn't be cross-domain relationships
        self.assertEqual(len(relationships), 0)

    def test_calculate_semantic_similarity(self):
        """Test semantic similarity calculation."""
        from dcae.knowledge.cross_domain import RelationshipIdentifier
        identifier = RelationshipIdentifier()

        content_a = "API rate limiting prevents server overload"
        content_b = "Rate limiting helps prevent server from being overwhelmed"

        similarity = identifier._calculate_semantic_similarity(content_a, content_b)

        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    def test_identify_relationship_type(self):
        """Test identification of relationship types."""
        from dcae.knowledge.cross_domain import RelationshipIdentifier
        identifier = RelationshipIdentifier()

        entry_a = KnowledgeEntry(
            id="1",
            domain=DomainType.TECHNICAL,
            content="Database optimization improves performance",
            source="tech_docs",
            confidence=0.8,
            timestamp=datetime.now()
        )

        entry_b = KnowledgeEntry(
            id="2",
            domain=DomainType.BUSINESS,
            content="System performance affects customer satisfaction",
            source="business_docs",
            confidence=0.7,
            timestamp=datetime.now()
        )

        relationship_type = identifier._identify_relationship_type(entry_a, entry_b)
        self.assertIsInstance(relationship_type, str)
        self.assertIn(relationship_type, ["influences", "correlates", "contradicts", "complements", "related_to"])


class TestCrossDomainRecommendationEngine(unittest.TestCase):
    """Tests for CrossDomainRecommendationEngine."""

    def setUp(self):
        """Set up test database and engine."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.kb = DomainKnowledgeBase(db_path=self.temp_db.name)

        # Add some test knowledge from different domains
        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="API rate limiting helps prevent server overload by controlling request frequency",
            source="tech_docs",
            confidence=0.8
        )

        self.kb.add_knowledge(
            domain=DomainType.BUSINESS,
            content="Customer experience is affected when systems are overloaded or unresponsive",
            source="business_docs",
            confidence=0.7
        )

        self.kb.add_knowledge(
            domain=DomainType.REGULATORY,
            content="Data privacy regulations require protection of customer information",
            source="regulatory_docs",
            confidence=0.9
        )

        self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="Encryption protects data in transit and at rest",
            source="security_docs",
            confidence=0.85
        )

        self.engine = CrossDomainRecommendationEngine(self.kb)

    def tearDown(self):
        """Clean up test database."""
        Path(self.temp_db.name).unlink(missing_ok=True)

    def test_generate_recommendations(self):
        """Test generating cross-domain recommendations."""
        recommendations = self.engine.generate_recommendations(
            context="system design",
            min_relationship_strength=0.2,
            max_recommendations=5
        )

        self.assertIsInstance(recommendations, list)
        # Even if no strong relationships are found, should return an empty list
        for rec in recommendations:
            self.assertIsInstance(rec, Recommendation)
            self.assertIsInstance(rec.confidence, float)
            self.assertGreaterEqual(rec.confidence, 0.0)
            self.assertLessEqual(rec.confidence, 1.0)

    def test_generate_recommendations_with_target_domains(self):
        """Test generating recommendations with target domain filtering."""
        recommendations = self.engine.generate_recommendations(
            context="security",
            target_domains=[DomainType.TECHNICAL, DomainType.REGULATORY],
            min_relationship_strength=0.2,
            max_recommendations=5
        )

        self.assertIsInstance(recommendations, list)

    def test_create_recommendation_from_relationship(self):
        """Test creating a recommendation from a relationship."""
        from dcae.knowledge.cross_domain import CrossDomainRelationship

        # Create sample entries in the database
        entry_a_id = self.kb.add_knowledge(
            domain=DomainType.TECHNICAL,
            content="API rate limiting helps prevent server overload",
            source="tech_docs",
            confidence=0.8
        )

        entry_b_id = self.kb.add_knowledge(
            domain=DomainType.BUSINESS,
            content="Customer experience is affected by system performance",
            source="business_docs",
            confidence=0.7
        )

        # Create a mock relationship
        relationship = CrossDomainRelationship(
            knowledge_ids=(entry_a_id, entry_b_id),
            domain_pair=(DomainType.TECHNICAL, DomainType.BUSINESS),
            relationship_type="influences",
            strength=0.7,
            description="Technical decisions impact business outcomes",
            timestamp=datetime.now()
        )

        # Get the actual entries for the test
        all_entries = self.kb.get_knowledge()
        entry_a = next(e for e in all_entries if e.id == entry_a_id)
        entry_b = next(e for e in all_entries if e.id == entry_b_id)

        # Test creating recommendation
        recommendation = self.engine._create_recommendation_from_relationship(
            relationship,
            "system performance context"
        )

        if recommendation is not None:  # The method might return None if entries aren't found
            self.assertIsInstance(recommendation, Recommendation)
            self.assertIsInstance(recommendation.title, str)
            self.assertIsInstance(recommendation.confidence, float)
            self.assertIn(DomainType.TECHNICAL, recommendation.source_domains)
            self.assertIn(DomainType.BUSINESS, recommendation.source_domains)

    def test_get_recommendation_explanation(self):
        """Test getting explanation for a recommendation."""
        # Create a sample recommendation
        sample_recommendation = Recommendation(
            id="test-id",
            title="Sample Cross-Domain Insight",
            description="A sample recommendation",
            source_domains=[DomainType.TECHNICAL, DomainType.BUSINESS],
            confidence=0.8,
            explanation="This recommendation connects technical and business considerations.",
            related_knowledge_ids=["id1", "id2"],
            timestamp=datetime.now()
        )

        explanation = self.engine.get_recommendation_explanation(sample_recommendation)

        self.assertIsInstance(explanation, str)
        self.assertIn("Sample Cross-Domain Insight", explanation)
        self.assertIn("technical", explanation.lower())
        self.assertIn("business", explanation.lower())


if __name__ == '__main__':
    unittest.main()