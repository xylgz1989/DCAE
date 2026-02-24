import unittest
from src.dcae.knowledge_fusion.domain_knowledge_manager import DomainKnowledgeManager, DomainType, DomainKnowledgeEntry
from src.dcae.knowledge_fusion.knowledge_fuser import KnowledgeItem, KnowledgeSourceType


class TestEpic9DomainKnowledgeManager(unittest.TestCase):
    """Test cases for Domain Knowledge Manager (FR47)."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.domain_manager = DomainKnowledgeManager()

    def test_add_and_retrieve_domain_knowledge(self):
        """Test adding and retrieving domain-specific knowledge."""
        # Add knowledge to finance domain
        entry_id1 = self.domain_manager.add_domain_knowledge(
            domain=DomainType.FINANCE,
            content="Regulatory compliance requirements for financial applications",
            tags=["compliance", "regulation", "financial"],
            contributor="financial_expert"
        )

        # Add knowledge to healthcare domain
        entry_id2 = self.domain_manager.add_domain_knowledge(
            domain=DomainType.HEALTHCARE,
            content="HIPAA privacy considerations for health data",
            tags=["privacy", "hipaa", "healthcare"],
            contributor="medical_professional"
        )

        # Verify entries were created with correct IDs
        self.assertTrue(entry_id1.startswith("dk_"))
        self.assertTrue(entry_id2.startswith("dk_"))

        # Retrieve by ID
        entry1 = self.domain_manager.get_knowledge_by_id(entry_id1)
        entry2 = self.domain_manager.get_knowledge_by_id(entry_id2)

        self.assertIsNotNone(entry1)
        self.assertIsNotNone(entry2)
        self.assertEqual(entry1.domain, DomainType.FINANCE)
        self.assertEqual(entry2.domain, DomainType.HEALTHCARE)
        self.assertEqual(entry1.knowledge_item.content, "Regulatory compliance requirements for financial applications")
        self.assertEqual(entry2.knowledge_item.content, "HIPAA privacy considerations for health data")

    def test_get_knowledge_by_domain(self):
        """Test retrieving knowledge by domain."""
        # Add knowledge to different domains
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.ECOMMERCE,
            content="Shopping cart optimization techniques",
            tags=["cart", "optimization", "conversion"]
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.ECOMMERCE,
            content="Payment gateway security best practices",
            tags=["payment", "security", "gateway"]
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.EDUCATION,
            content="Student data privacy guidelines",
            tags=["privacy", "student", "education"]
        )

        # Retrieve knowledge by domain
        ecommerce_knowledge = self.domain_manager.get_knowledge_by_domain(DomainType.ECOMMERCE)
        education_knowledge = self.domain_manager.get_knowledge_by_domain(DomainType.EDUCATION)
        manufacturing_knowledge = self.domain_manager.get_knowledge_by_domain(DomainType.MANUFACTURING)

        # Verify counts
        self.assertEqual(len(ecommerce_knowledge), 2)
        self.assertEqual(len(education_knowledge), 1)
        self.assertEqual(len(manufacturing_knowledge), 0)

        # Verify domain filtering
        for entry in ecommerce_knowledge:
            self.assertEqual(entry.domain, DomainType.ECOMMERCE)

    def test_get_knowledge_by_tag(self):
        """Test retrieving knowledge by tag."""
        # Add knowledge with various tags
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.FINANCE,
            content="Banking security protocols",
            tags=["security", "banking", "protocol"]
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.HEALTHCARE,
            content="Medical device regulations",
            tags=["security", "medical", "regulation"]
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.TECHNOLOGY,
            content="Cloud infrastructure security",
            tags=["cloud", "security", "infrastructure"]
        )

        # Retrieve by tag
        security_knowledge = self.domain_manager.get_knowledge_by_tag("security")

        # Verify all entries with 'security' tag are retrieved
        self.assertEqual(len(security_knowledge), 3)
        for entry in security_knowledge:
            self.assertIn("security", entry.knowledge_item.tags)

    def test_search_knowledge(self):
        """Test searching for knowledge by query."""
        # Add knowledge with searchable content
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.FINANCE,
            content="Anti-money laundering compliance procedures",
            tags=["aml", "compliance", "financial"]
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.ECOMMERCE,
            content="Fraud detection in payment systems",
            tags=["fraud", "detection", "payment"]
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.ECOMMERCE,
            content="Customer authentication methods",
            tags=["authentication", "customer", "security"]
        )

        # Search for compliance-related knowledge
        compliance_results = self.domain_manager.search_knowledge("compliance")
        self.assertGreaterEqual(len(compliance_results), 1)
        self.assertTrue(any("compliance" in entry.knowledge_item.content.lower() for entry in compliance_results))

        # Search for fraud-related knowledge
        fraud_results = self.domain_manager.search_knowledge("fraud")
        self.assertGreaterEqual(len(fraud_results), 1)
        self.assertTrue(any("fraud" in entry.knowledge_item.content.lower() for entry in fraud_results))

    def test_update_knowledge_entry(self):
        """Test updating a domain knowledge entry."""
        # Add initial knowledge entry
        entry_id = self.domain_manager.add_domain_knowledge(
            domain=DomainType.TECHNOLOGY,
            content="Initial content about microservices",
            tags=["microservices", "initial"],
            metadata={"version": "1.0"}
        )

        # Retrieve the original entry
        original_entry = self.domain_manager.get_knowledge_by_id(entry_id)
        self.assertIsNotNone(original_entry)
        self.assertEqual(original_entry.knowledge_item.content, "Initial content about microservices")
        self.assertIn("microservices", original_entry.knowledge_item.tags)

        # Update the entry
        update_success = self.domain_manager.update_knowledge_entry(
            entry_id=entry_id,
            content="Updated content about modern microservices architecture",
            tags=["microservices", "architecture", "modern"],
            metadata={"version": "2.0", "updated": True}
        )

        # Verify update was successful
        self.assertTrue(update_success)

        # Retrieve the updated entry
        updated_entry = self.domain_manager.get_knowledge_by_id(entry_id)
        self.assertIsNotNone(updated_entry)
        self.assertEqual(updated_entry.knowledge_item.content, "Updated content about modern microservices architecture")
        self.assertEqual(updated_entry.knowledge_item.tags, ["microservices", "architecture", "modern"])
        self.assertEqual(updated_entry.knowledge_item.metadata, {"version": "2.0", "updated": True})

    def test_remove_knowledge_entry(self):
        """Test removing a domain knowledge entry."""
        # Add knowledge entry
        entry_id = self.domain_manager.add_domain_knowledge(
            domain=DomainType.MANUFACTURING,
            content="Quality control processes in manufacturing",
            tags=["quality", "control", "manufacturing"]
        )

        # Verify entry exists
        self.assertIsNotNone(self.domain_manager.get_knowledge_by_id(entry_id))

        # Remove the entry
        remove_success = self.domain_manager.remove_knowledge_entry(entry_id)

        # Verify removal was successful
        self.assertTrue(remove_success)
        self.assertIsNone(self.domain_manager.get_knowledge_by_id(entry_id))

        # Verify entry is not in domain index
        manufacturing_entries = self.domain_manager.get_knowledge_by_domain(DomainType.MANUFACTURING)
        self.assertEqual(len(manufacturing_entries), 0)

    def test_approve_disapprove_knowledge(self):
        """Test approving and disapproving knowledge entries."""
        # Add knowledge entry (by default, it's approved)
        entry_id = self.domain_manager.add_domain_knowledge(
            domain=DomainType.GOVERNMENT,
            content="Government procurement guidelines",
            approved=True
        )

        # Verify it's approved initially
        entry = self.domain_manager.get_knowledge_by_id(entry_id)
        self.assertIsNotNone(entry)
        self.assertTrue(entry.approved)

        # Get approved entries for the domain
        approved_entries = self.domain_manager.get_approved_knowledge_by_domain(DomainType.GOVERNMENT)
        self.assertEqual(len(approved_entries), 1)

        # Disapprove the entry
        approval_success = self.domain_manager.approve_knowledge_entry(entry_id, approve=False)
        self.assertTrue(approval_success)

        # Verify it's no longer approved
        entry_after_disapproval = self.domain_manager.get_knowledge_by_id(entry_id)
        self.assertIsNotNone(entry_after_disapproval)
        self.assertFalse(entry_after_disapproval.approved)

        # Verify it's not returned in approved results
        approved_entries_after = self.domain_manager.get_approved_knowledge_by_domain(DomainType.GOVERNMENT)
        self.assertEqual(len(approved_entries_after), 0)

        # Approve again
        reapproval_success = self.domain_manager.approve_knowledge_entry(entry_id, approve=True)
        self.assertTrue(reapproval_success)

        # Verify it's approved again
        approved_entries_reapproved = self.domain_manager.get_approved_knowledge_by_domain(DomainType.GOVERNMENT)
        self.assertEqual(len(approved_entries_reapproved), 1)

    def test_export_import_knowledge(self):
        """Test exporting and importing domain knowledge."""
        # Add knowledge entries
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.FINANCE,
            content="Financial risk assessment models",
            tags=["risk", "assessment", "finance"],
            contributor="risk_analyst",
            metadata={"industry": "banking", "region": "global"}
        )
        self.domain_manager.add_domain_knowledge(
            domain=DomainType.HEALTHCARE,
            content="Electronic health record security",
            tags=["ehr", "security", "privacy"],
            contributor="health_it_specialist",
            metadata={"compliance": "hipaa", "type": "security"}
        )

        # Export knowledge
        export_json = self.domain_manager.export_knowledge()
        self.assertIsNotNone(export_json)
        self.assertIn("Financial risk assessment models", export_json)
        self.assertIn("Electronic health record security", export_json)

        # Create a new domain manager and import
        new_domain_manager = DomainKnowledgeManager()
        import_success = new_domain_manager.import_knowledge(export_json)

        # Verify import was successful
        self.assertTrue(import_success)
        self.assertEqual(len(new_domain_manager.domain_knowledge), 2)

        # Verify content integrity
        finance_entries = new_domain_manager.get_knowledge_by_domain(DomainType.FINANCE)
        healthcare_entries = new_domain_manager.get_knowledge_by_domain(DomainType.HEALTHCARE)

        self.assertEqual(len(finance_entries), 1)
        self.assertEqual(len(healthcare_entries), 1)

        # Verify specific content
        self.assertEqual(finance_entries[0].knowledge_item.content, "Financial risk assessment models")
        self.assertEqual(healthcare_entries[0].knowledge_item.content, "Electronic health record security")
        self.assertIn("risk", finance_entries[0].knowledge_item.tags)
        self.assertIn("privacy", healthcare_entries[0].knowledge_item.tags)


if __name__ == '__main__':
    unittest.main()