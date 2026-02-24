import unittest
from src.dcae.knowledge_fusion.knowledge_fuser import KnowledgeFuser, KnowledgeItem, KnowledgeSourceType, FusedKnowledgeContext


class TestEpic9KnowledgeFusion(unittest.TestCase):
    """Test cases for Epic #9: Knowledge Fusion & Cross-Domain Intelligence."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.knowledge_fuser = KnowledgeFuser()

    def test_add_and_retrieve_knowledge_items(self):
        """Test adding and retrieving knowledge items."""
        # Add a knowledge item
        item1 = KnowledgeItem(
            id="test1",
            source_type=KnowledgeSourceType.DEVELOPMENT,
            content="Unit testing improves code quality"
        )
        self.knowledge_fuser.add_knowledge(item1)

        # Add another knowledge item
        item2 = KnowledgeItem(
            id="test2",
            source_type=KnowledgeSourceType.PRODUCT,
            content="User feedback is critical for product success"
        )
        self.knowledge_fuser.add_knowledge(item2)

        # Verify items were added
        self.assertEqual(len(self.knowledge_fuser.knowledge_store), 2)
        self.assertIn("test1", self.knowledge_fuser.knowledge_store)
        self.assertIn("test2", self.knowledge_fuser.knowledge_store)

    def test_get_knowledge_by_type(self):
        """Test retrieving knowledge by source type."""
        # Add knowledge items of different types
        dev_item = KnowledgeItem(
            id="dev1",
            source_type=KnowledgeSourceType.DEVELOPMENT,
            content="Agile development practices"
        )
        prod_item = KnowledgeItem(
            id="prod1",
            source_type=KnowledgeSourceType.PRODUCT,
            content="Product market fit strategies"
        )
        biz_item = KnowledgeItem(
            id="biz1",
            source_type=KnowledgeSourceType.BUSINESS,
            content="Business model innovation"
        )

        self.knowledge_fuser.add_knowledge(dev_item)
        self.knowledge_fuser.add_knowledge(prod_item)
        self.knowledge_fuser.add_knowledge(biz_item)

        # Retrieve by type
        dev_knowledge = self.knowledge_fuser.get_knowledge_by_type(KnowledgeSourceType.DEVELOPMENT)
        prod_knowledge = self.knowledge_fuser.get_knowledge_by_type(KnowledgeSourceType.PRODUCT)
        biz_knowledge = self.knowledge_fuser.get_knowledge_by_type(KnowledgeSourceType.BUSINESS)

        # Verify counts
        self.assertEqual(len(dev_knowledge), 1)
        self.assertEqual(len(prod_knowledge), 1)
        self.assertEqual(len(biz_knowledge), 1)

        # Verify content
        self.assertEqual(dev_knowledge[0].content, "Agile development practices")
        self.assertEqual(prod_knowledge[0].content, "Product market fit strategies")
        self.assertEqual(biz_knowledge[0].content, "Business model innovation")

    def test_get_knowledge_by_tags(self):
        """Test retrieving knowledge by tags."""
        # Add knowledge items with tags
        item1 = KnowledgeItem(
            id="item1",
            source_type=KnowledgeSourceType.TECHNICAL,
            content="Docker containerization",
            tags=["docker", "containers", "deployment"]
        )
        item2 = KnowledgeItem(
            id="item2",
            source_type=KnowledgeSourceType.TECHNICAL,
            content="Kubernetes orchestration",
            tags=["kubernetes", "orchestration", "containers"]
        )
        item3 = KnowledgeItem(
            id="item3",
            source_type=KnowledgeSourceType.BEST_PRACTICES,
            content="Code review processes",
            tags=["code-review", "quality", "collaboration"]
        )

        self.knowledge_fuser.add_knowledge(item1)
        self.knowledge_fuser.add_knowledge(item2)
        self.knowledge_fuser.add_knowledge(item3)

        # Retrieve by tag
        container_items = self.knowledge_fuser.get_knowledge_by_tags(["containers"])
        quality_items = self.knowledge_fuser.get_knowledge_by_tags(["quality"])

        # Verify results
        self.assertEqual(len(container_items), 2)  # item1 and item2
        self.assertEqual(len(quality_items), 1)   # item3

    def test_fuse_knowledge_basic(self):
        """Test basic knowledge fusion."""
        # Add various types of knowledge
        dev_item = KnowledgeItem(
            id="dev_api",
            source_type=KnowledgeSourceType.DEVELOPMENT,
            content="REST API best practices",
            tags=["api", "rest", "backend"]
        )
        prod_item = KnowledgeItem(
            id="prod_ui",
            source_type=KnowledgeSourceType.PRODUCT,
            content="User interface design principles",
            tags=["ui", "ux", "frontend"]
        )
        biz_item = KnowledgeItem(
            id="biz_scale",
            source_type=KnowledgeSourceType.BUSINESS,
            content="Scalability requirements for growth",
            tags=["scalability", "growth", "business"]
        )

        self.knowledge_fuser.add_knowledge(dev_item)
        self.knowledge_fuser.add_knowledge(prod_item)
        self.knowledge_fuser.add_knowledge(biz_item)

        # Define context requirements
        context_reqs = {
            'tags': ['api', 'ui', 'scalability'],
            'types': ['development', 'product', 'business']
        }

        # Perform knowledge fusion
        fused_context = self.knowledge_fuser.fuse_knowledge(context_reqs)

        # Verify the fusion results
        self.assertEqual(len(fused_context.development_knowledge), 1)
        self.assertEqual(len(fused_context.product_knowledge), 1)
        self.assertEqual(len(fused_context.business_context), 1)
        self.assertEqual(len(fused_context.technical_constraints), 0)
        self.assertEqual(len(fused_context.best_practices), 0)

        # Verify specific content
        self.assertEqual(fused_context.development_knowledge[0].content, "REST API best practices")
        self.assertEqual(fused_context.product_knowledge[0].content, "User interface design principles")
        self.assertEqual(fused_context.business_context[0].content, "Scalability requirements for growth")

    def test_get_relevant_knowledge(self):
        """Test retrieving relevant knowledge for a query."""
        # Add knowledge items
        item1 = KnowledgeItem(
            id="sec_auth",
            source_type=KnowledgeSourceType.BEST_PRACTICES,
            content="Security authentication mechanisms for web applications",
            tags=["security", "authentication", "web"]
        )
        item2 = KnowledgeItem(
            id="perf_db",
            source_type=KnowledgeSourceType.DEVELOPMENT,
            content="Database performance optimization techniques",
            tags=["performance", "database", "optimization"]
        )
        item3 = KnowledgeItem(
            id="ui_access",
            source_type=KnowledgeSourceType.PRODUCT,
            content="Accessibility guidelines for inclusive design",
            tags=["accessibility", "inclusive", "ui"]
        )

        self.knowledge_fuser.add_knowledge(item1)
        self.knowledge_fuser.add_knowledge(item2)
        self.knowledge_fuser.add_knowledge(item3)

        # Search for security-related knowledge
        security_results = self.knowledge_fuser.get_relevant_knowledge("security")
        self.assertGreaterEqual(len(security_results), 1)
        self.assertTrue(any("security" in result.content.lower() or "security" in result.tags for result in security_results))

        # Search for performance-related knowledge
        perf_results = self.knowledge_fuser.get_relevant_knowledge("performance")
        self.assertGreaterEqual(len(perf_results), 1)
        self.assertTrue(any("performance" in result.content.lower() or "performance" in result.tags for result in perf_results))

    def test_update_knowledge_item(self):
        """Test updating an existing knowledge item."""
        # Add initial knowledge item
        item = KnowledgeItem(
            id="update_test",
            source_type=KnowledgeSourceType.DEVELOPMENT,
            content="Initial content",
            tags=["old", "test"],
            relevance_score=0.5
        )
        self.knowledge_fuser.add_knowledge(item)

        # Update the knowledge item
        updates = {
            'content': 'Updated content about modern development practices',
            'relevance_score': 0.8,
            'tags': ['modern', 'development', 'practices']
        }
        result = self.knowledge_fuser.update_knowledge_item("update_test", updates)

        # Verify update was successful
        self.assertTrue(result)
        updated_item = self.knowledge_fuser.knowledge_store["update_test"]
        self.assertEqual(updated_item.content, 'Updated content about modern development practices')
        self.assertEqual(updated_item.relevance_score, 0.8)
        self.assertEqual(updated_item.tags, ['modern', 'development', 'practices'])

    def test_remove_knowledge_item(self):
        """Test removing a knowledge item."""
        # Add knowledge item
        item = KnowledgeItem(
            id="remove_test",
            source_type=KnowledgeSourceType.PRODUCT,
            content="Content to be removed"
        )
        self.knowledge_fuser.add_knowledge(item)

        # Verify it exists
        self.assertIn("remove_test", self.knowledge_fuser.knowledge_store)

        # Remove the item
        result = self.knowledge_fuser.remove_knowledge_item("remove_test")

        # Verify removal
        self.assertTrue(result)
        self.assertNotIn("remove_test", self.knowledge_fuser.knowledge_store)

    def test_export_import_knowledge(self):
        """Test exporting and importing knowledge."""
        # Add some knowledge items
        item1 = KnowledgeItem(
            id="exp1",
            source_type=KnowledgeSourceType.DEVELOPMENT,
            content="Export test content 1",
            tags=["export", "test"],
            relevance_score=0.7
        )
        item2 = KnowledgeItem(
            id="exp2",
            source_type=KnowledgeSourceType.BEST_PRACTICES,
            content="Export test content 2",
            tags=["export", "practice"],
            relevance_score=0.9
        )

        self.knowledge_fuser.add_knowledge(item1)
        self.knowledge_fuser.add_knowledge(item2)

        # Export knowledge
        export_json = self.knowledge_fuser.export_knowledge()
        self.assertIsNotNone(export_json)
        self.assertIn("exp1", export_json)
        self.assertIn("exp2", export_json)

        # Create a new knowledge fuser and import
        new_knowledge_fuser = KnowledgeFuser()
        import_success = new_knowledge_fuser.import_knowledge(export_json)

        # Verify import was successful
        self.assertTrue(import_success)
        self.assertEqual(len(new_knowledge_fuser.knowledge_store), 2)
        self.assertIn("exp1", new_knowledge_fuser.knowledge_store)
        self.assertIn("exp2", new_knowledge_fuser.knowledge_store)

        # Verify content integrity
        imported_item1 = new_knowledge_fuser.knowledge_store["exp1"]
        self.assertEqual(imported_item1.content, "Export test content 1")
        self.assertEqual(imported_item1.relevance_score, 0.7)
        self.assertEqual(imported_item1.tags, ["export", "test"])


if __name__ == '__main__':
    unittest.main()