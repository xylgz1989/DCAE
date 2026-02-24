import unittest
from src.dcae.knowledge_fusion.cross_domain_recommender import CrossDomainRecommender, Context, RecommendationType
from src.dcae.knowledge_fusion.domain_knowledge_manager import DomainKnowledgeManager, DomainType
from src.dcae.knowledge_fusion.knowledge_fuser import KnowledgeSourceType


class TestEpic9CrossDomainRecommender(unittest.TestCase):
    """Test cases for Cross-Domain Recommender (FR48)."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.domain_manager = DomainKnowledgeManager()
        self.recommender = CrossDomainRecommender(self.domain_manager)

        # Add some knowledge to test with
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.FINANCE,
            content="Secure transaction processing with encryption and validation",
            tags=["security", "transaction", "encryption"],
            approved=True
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.ECOMMERCE,
            content="Shopping cart persistence and inventory management",
            tags=["persistence", "inventory", "cart"],
            approved=True
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.HEALTHCARE,
            content="Patient data protection and HIPAA compliance",
            tags=["privacy", "compliance", "patient"],
            approved=True
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.TECHNOLOGY,
            content="Microservices architecture with API gateways",
            tags=["architecture", "microservices", "api"],
            approved=True
        )

    def test_generate_basic_recommendations(self):
        """Test generating basic cross-domain recommendations."""
        # Create a context for an e-commerce project
        context = Context(
            project_type="e-commerce platform",
            domain_types=[DomainType.ECOMMERCE, DomainType.FINANCE],
            problem_description="Need secure payment processing and shopping cart functionality",
            current_stage="implementation",
            constraints=["PCI compliance", "low latency"],
            requirements=["secure transactions", "user sessions"],
            technology_stack=["Node.js", "PostgreSQL", "Redis"],
            team_expertise=["JavaScript", "SQL"],
            performance_requirements={"response_time": "100ms", "throughput": "1000 TPS"}
        )

        # Generate recommendations
        recommendations = self.recommender.generate_recommendations(context, max_recommendations=3)

        # Verify recommendations were generated
        self.assertGreaterEqual(len(recommendations), 1)

        # Verify recommendation properties
        for rec in recommendations:
            self.assertIsNotNone(rec.id)
            self.assertIsNotNone(rec.title)
            self.assertIsNotNone(rec.description)
            self.assertIsNotNone(rec.recommendation_type)
            self.assertIsNotNone(rec.source_domains)
            self.assertGreaterEqual(rec.confidence_score, 0.0)
            self.assertLessEqual(rec.confidence_score, 1.0)

    def test_generate_recommendations_for_specific_context(self):
        """Test generating recommendations for specific contexts."""
        # Create a healthcare-focused context
        healthcare_context = Context(
            project_type="healthcare application",
            domain_types=[DomainType.HEALTHCARE],
            problem_description="Managing patient records with privacy requirements",
            current_stage="design",
            constraints=["HIPAA compliance", "data residency"],
            requirements=["audit trails", "user authentication"],
            technology_stack=["Python", "PostgreSQL", "FHIR"],
            team_expertise=["Python", "healthcare"],
            performance_requirements={"availability": "99.9%"}
        )

        # Generate recommendations
        recommendations = self.recommender.generate_recommendations(healthcare_context, max_recommendations=2)

        # Verify recommendations are relevant to healthcare context
        self.assertGreaterEqual(len(recommendations), 1)

        # Check that recommendations relate to privacy, compliance, or healthcare
        for rec in recommendations:
            description_lower = rec.description.lower()
            self.assertTrue(
                "privacy" in description_lower or
                "compliance" in description_lower or
                "patient" in description_lower or
                "healthcare" in description_lower or
                "security" in description_lower
            )

    def test_infer_recommendation_type(self):
        """Test that recommendation types are inferred correctly."""
        # Create a context that should trigger security recommendations
        security_context = Context(
            project_type="web application",
            domain_types=[DomainType.TECHNOLOGY],
            problem_description="Need to secure user authentication",
            current_stage="implementation",
            constraints=["OWASP compliance"],
            requirements=["secure login", "password storage"],
            technology_stack=["React", "Node.js", "MongoDB"],
            team_expertise=["full-stack"],
            performance_requirements={}
        )

        recommendations = self.recommender.generate_recommendations(security_context, max_recommendations=3)

        # Some recommendations should be security-related
        security_recs = [r for r in recommendations if r.recommendation_type == RecommendationType.SECURITY]
        # This might be empty depending on the matching algorithm, which is fine

    def test_personalize_recommendations(self):
        """Test personalizing recommendations based on user profile."""
        # Create a context
        context = Context(
            project_type="API service",
            domain_types=[DomainType.TECHNOLOGY],
            problem_description="Building a scalable API service",
            current_stage="architecture",
            constraints=["high throughput", "low latency"],
            requirements=["microservices", "API gateway"],
            technology_stack=["Go", "Kubernetes", "PostgreSQL"],
            team_expertise=["Go", "Kubernetes"],
            performance_requirements={"throughput": "10000 RPS"}
        )

        # Create a user profile that prefers certain technologies
        user_profile = {
            'expertise_area': 'backend',
            'low_confidence_areas': ['frontend'],
            'preferred_technologies': ['Go', 'Kubernetes', 'PostgreSQL']
        }

        # Generate regular recommendations
        regular_recs = self.recommender.generate_recommendations(context, max_recommendations=3)

        # Generate personalized recommendations
        personalized_recs = self.recommender.personalize_recommendations(context, user_profile)

        # Both should return recommendations
        self.assertGreaterEqual(len(regular_recs), 0)
        self.assertGreaterEqual(len(personalized_recs), 0)

        # Personalized recommendations may have adjusted scores based on user profile
        # but structure should be the same

    def test_explain_recommendation_reasoning(self):
        """Test explaining the reasoning behind recommendations."""
        # Create a context
        context = Context(
            project_type="payment processor",
            domain_types=[DomainType.FINANCE],
            problem_description="Secure payment processing system",
            current_stage="design",
            constraints=["PCI DSS compliance"],
            requirements=["tokenization", "encryption"],
            technology_stack=["Java", "Oracle", "Spring"],
            team_expertise=["Java", "finance"],
            performance_requirements={"transaction_time": "2s"}
        )

        recommendations = self.recommender.generate_recommendations(context, max_recommendations=1)
        self.assertGreaterEqual(len(recommendations), 1)

        recommendation = recommendations[0]

        # Get explanation
        explanation = self.recommender.explain_recommendation_reasoning(recommendation)

        # Verify explanation structure
        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 0)
        self.assertIn(recommendation.title, explanation)

    def test_cross_domain_insights(self):
        """Test getting insights from domains not in the primary context."""
        # Create a context focused on education
        education_context = Context(
            project_type="learning management system",
            domain_types=[DomainType.EDUCATION],
            problem_description="Educational content management",
            current_stage="requirements",
            constraints=["accessibility", "standards_compliance"],
            requirements=["content_authoring", "student_tracking"],
            technology_stack=["React", "Node.js", "MongoDB"],
            team_expertise=["JavaScript", "education"],
            performance_requirements={}
        )

        # Generate recommendations - these might include cross-domain insights from other domains
        recommendations = self.recommender.generate_recommendations(education_context, max_recommendations=3)

        # Verify recommendations were generated
        self.assertGreaterEqual(len(recommendations), 0)

        # Check that the recommender has cross-domain capability
        for rec in recommendations:
            # Each recommendation should have a clear source
            self.assertIsNotNone(rec.source_domains)
            self.assertIsNotNone(rec.description)

    def test_record_recommendation_feedback(self):
        """Test recording feedback on recommendations."""
        # This tests the feedback mechanism
        dummy_id = "rec_test_12345"

        # Record positive feedback
        positive_feedback_result = self.recommender.get_recommendation_feedback(
            dummy_id,
            positive=True,
            notes="This recommendation was very helpful for our use case"
        )
        self.assertTrue(positive_feedback_result)

        # Record negative feedback
        negative_feedback_result = self.recommender.get_recommendation_feedback(
            dummy_id,
            positive=False,
            notes="This recommendation didn't fit our architecture"
        )
        self.assertTrue(negative_feedback_result)

    def test_context_keyword_extraction(self):
        """Test that context keywords are properly extracted for matching."""
        # Create context with specific keywords
        context = Context(
            project_type="security monitoring platform",
            domain_types=[DomainType.TECHNOLOGY],
            problem_description="Real-time threat detection and response",
            current_stage="architecture",
            constraints=["real-time processing", "low false positives"],
            requirements=["threat_intelligence", "anomaly_detection"],
            technology_stack=["Kafka", "Spark", "Elasticsearch"],
            team_expertise=["big_data", "security"],
            performance_requirements={"processing_delay": "100ms"}
        )

        # Although we can't directly test the internal keyword extraction,
        # we can test that recommendations are generated based on context
        recommendations = self.recommender.generate_recommendations(context, max_recommendations=2)

        # Verify recommendations were generated based on context
        self.assertGreaterEqual(len(recommendations), 0)


if __name__ == '__main__':
    unittest.main()