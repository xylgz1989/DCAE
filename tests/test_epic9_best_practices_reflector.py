import unittest
from src.dcae.knowledge_fusion.best_practices_reflector import BestPracticesReflector, BestPracticeCategory, BestPractice, BestPracticeCheckResult
from src.dcae.knowledge_fusion.domain_knowledge_manager import DomainKnowledgeManager, DomainType


class TestEpic9BestPracticesReflector(unittest.TestCase):
    """Test cases for Best Practices Reflector (FR49)."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.domain_manager = DomainKnowledgeManager()
        self.reflector = BestPracticesReflector(self.domain_manager)

    def test_add_and_retrieve_best_practices(self):
        """Test adding and retrieving best practices."""
        # Get initial count of default practices
        initial_count = len(self.reflector.best_practices)
        self.assertEqual(initial_count, 4)  # Should be 4 default practices

        # Add a security best practice
        practice1 = BestPractice(
            id="bp_sec_001_custom",
            title="Custom Input Validation",
            description="Always validate inputs to prevent injection attacks",
            category=BestPracticeCategory.SECURITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Validate input length, type, and format",
                "Use allowlists instead of blocklists"
            ],
            examples=[
                "Validate email format with regex",
                "Check numeric inputs are within expected range"
            ],
            severity="high",
            applicable_patterns=["API", "form", "input"]
        )
        self.reflector.add_best_practice(practice1)

        # Add a code quality best practice
        practice2 = BestPractice(
            id="bp_cq_001_custom",
            title="Custom Function Length",
            description="Keep functions small and focused on a single responsibility",
            category=BestPracticeCategory.CODE_QUALITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Functions should fit on one screen",
                "Each function should do one thing well"
            ],
            examples=[
                "A function with more than 50 lines might need refactoring"
            ],
            severity="medium",
            applicable_patterns=["function", "method"]
        )
        self.reflector.add_best_practice(practice2)

        # Verify practices were added (including defaults)
        self.assertEqual(len(self.reflector.best_practices), initial_count + 2)  # 4 + 2 = 6
        self.assertIn("bp_sec_001_custom", self.reflector.best_practices)
        self.assertIn("bp_cq_001_custom", self.reflector.best_practices)

        # Retrieve by category
        security_practices = self.reflector.get_practices_by_category(BestPracticeCategory.SECURITY)
        code_quality_practices = self.reflector.get_practices_by_category(BestPracticeCategory.CODE_QUALITY)

        # Should have at least 1 in each category (including defaults and our additions)
        self.assertGreaterEqual(len(security_practices), 1)
        self.assertGreaterEqual(len(code_quality_practices), 1)

        # Check that our added practices are among the retrieved ones
        security_titles = [bp.title for bp in security_practices]
        code_quality_titles = [bp.title for bp in code_quality_practices]

        self.assertIn("Custom Input Validation", security_titles)
        self.assertIn("Custom Function Length", code_quality_titles)

    def test_get_practices_by_domain(self):
        """Test retrieving best practices by domain."""
        # Add practices for different domains
        finance_bp = BestPractice(
            id="bp_finance_001",
            title="Financial Calculations",
            description="Use decimal precision for financial calculations",
            category=BestPracticeCategory.CODE_QUALITY,
            domain=DomainType.FINANCE,
            implementation_guidelines=["Use decimal instead of float for money"],
            examples=["decimal.Decimal for currency calculations"],
            severity="high"
        )
        healthcare_bp = BestPractice(
            id="bp_healthcare_001",
            title="Patient Privacy",
            description="Ensure PHI is properly encrypted and access-controlled",
            category=BestPracticeCategory.SECURITY,
            domain=DomainType.HEALTHCARE,
            implementation_guidelines=["Encrypt at rest and in transit"],
            examples=["End-to-end encryption for patient records"],
            severity="critical"
        )
        ecommerce_bp = BestPractice(
            id="bp_ecommerce_001",
            title="Cart Persistence",
            description="Maintain shopping cart state reliably",
            category=BestPracticeCategory.PERFORMANCE,
            domain=DomainType.ECOMMERCE,
            implementation_guidelines=["Use distributed caching"],
            examples=["Redis for cart storage"],
            severity="medium"
        )

        self.reflector.add_best_practice(finance_bp)
        self.reflector.add_best_practice(healthcare_bp)
        self.reflector.add_best_practice(ecommerce_bp)

        # Retrieve by domain
        finance_practices = self.reflector.get_practices_by_domain(DomainType.FINANCE)
        healthcare_practices = self.reflector.get_practices_by_domain(DomainType.HEALTHCARE)
        ecommerce_practices = self.reflector.get_practices_by_domain(DomainType.ECOMMERCE)

        self.assertEqual(len(finance_practices), 1)
        self.assertEqual(len(healthcare_practices), 1)
        self.assertEqual(len(ecommerce_practices), 1)

        self.assertEqual(finance_practices[0].title, "Financial Calculations")
        self.assertEqual(healthcare_practices[0].title, "Patient Privacy")
        self.assertEqual(ecommerce_practices[0].title, "Cart Persistence")

    def test_reflect_best_practices_in_content(self):
        """Test reflecting best practices in content."""
        # Add some best practices
        security_bp = BestPractice(
            id="bp_security_input",
            title="Input Validation Required",
            description="Validate all user inputs",
            category=BestPracticeCategory.SECURITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=["Always validate inputs"],
            examples=["Validate before processing"],
            severity="high",
            applicable_patterns=["input", "request", "user"]
        )
        self.reflector.add_best_practice(security_bp)

        # Test content that doesn't follow the practice
        non_secure_content = """
def process_user_request(user_data):
    # Directly using user input without validation
    db.execute(f"SELECT * FROM users WHERE id = {user_data}")
    return result
        """

        # Check best practice compliance
        results = self.reflector.reflect_best_practices_in_content(
            non_secure_content,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.SECURITY]
        )

        # Should find issues with security practices
        self.assertGreaterEqual(len(results), 1)

        # Verify at least one check identified issues
        violated_practices = [r for r in results if not r.is_followed]
        self.assertGreaterEqual(len(violated_practices), 0)

    def test_check_practice_compliance_security(self):
        """Test compliance checking for security practices."""
        # Add a security practice
        security_bp = BestPractice(
            id="bp_security_check",
            title="Security Practice",
            description="Check for security issues",
            category=BestPracticeCategory.SECURITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=["Validate inputs", "Sanitize outputs"],
            examples=["Use parameterized queries"],
            severity="high"
        )
        self.reflector.add_best_practice(security_bp)

        # Content that may have security issues
        content_with_issues = """
def handle_user_input(input):
    # Potentially unsafe operation
    result = eval(input)  # Security issue
    return result
        """

        results = self.reflector.reflect_best_practices_in_content(
            content_with_issues,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.SECURITY]
        )

        # Verify that results are returned
        self.assertIsInstance(results, list)

    def test_integrate_best_practices(self):
        """Test integrating best practices into content."""
        # Add a testing best practice
        testing_bp = BestPractice(
            id="bp_testing_units",
            title="Unit Tests Required",
            description="Write unit tests for all functions",
            category=BestPracticeCategory.TESTING,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=["Test each function separately"],
            examples=["Use pytest for testing"],
            severity="medium"
        )
        self.reflector.add_best_practice(testing_bp)

        # Base content
        base_content = """
def add_numbers(a, b):
    return a + b
        """

        # Integrate best practices
        result = self.reflector.integrate_best_practices(
            base_content,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.TESTING]
        )

        # Verify the result structure
        self.assertIn('enhanced_content', result)
        self.assertIn('applied_practices', result)
        self.assertIn('suggestions', result)

        # The enhanced content should contain the original content plus additions
        self.assertIn('add_numbers', result['enhanced_content'])

    def test_check_code_quality_practices(self):
        """Test checking code quality best practices."""
        # Add a code quality practice
        cq_bp = BestPractice(
            id="bp_cq_functions",
            title="Small Functions",
            description="Keep functions small",
            category=BestPracticeCategory.CODE_QUALITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=["Small functions are easier to test"],
            examples=["Break large functions"],
            severity="medium"
        )
        self.reflector.add_best_practice(cq_bp)

        # Content with potential code quality issues
        content = """
def very_long_function_with_many_operations():
    # This function has many lines which could indicate a quality issue
    var1 = 1
    var2 = 2
    var3 = 3
    # Many more lines...
    var10 = 10
    var11 = 11
    var12 = 12
    # Even more lines...
    var20 = 20
    return var1 + var2 + var3 + var10 + var11 + var12 + var20
        """

        results = self.reflector.reflect_best_practices_in_content(
            content,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.CODE_QUALITY]
        )

        # Results should be returned without error
        self.assertIsInstance(results, list)

    def test_get_domain_best_practices_summary(self):
        """Test getting domain best practices summary."""
        # Add practices for a specific domain
        for i in range(3):
            bp = BestPractice(
                id=f"bp_sum_{i}",
                title=f"Summary Practice {i}",
                description=f"Description for practice {i}",
                category=BestPracticeCategory.SECURITY if i % 2 == 0 else BestPracticeCategory.CODE_QUALITY,
                domain=DomainType.FINANCE,
                implementation_guidelines=[f"Guideline {i}"],
                examples=[f"Example {i}"],
                severity="medium"
            )
            self.reflector.add_best_practice(bp)

        # Get summary
        summary = self.reflector.get_domain_best_practices_summary(DomainType.FINANCE)

        # Verify summary structure
        self.assertIn('domain', summary)
        self.assertIn('total_practices', summary)
        self.assertIn('practices_by_category', summary)
        self.assertIn('practice_titles', summary)

        self.assertEqual(summary['domain'], DomainType.FINANCE.value)
        self.assertEqual(summary['total_practices'], 3)
        self.assertEqual(len(summary['practice_titles']), 3)

    def test_export_import_best_practices(self):
        """Test exporting and importing best practices."""
        # Get initial count of default practices
        initial_count = len(self.reflector.best_practices)

        # Add some best practices
        bp1 = BestPractice(
            id="bp_exp_001",
            title="Export Test Practice 1",
            description="Testing export functionality",
            category=BestPracticeCategory.SECURITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=["Guideline 1", "Guideline 2"],
            examples=["Example 1"],
            severity="high",
            applicable_patterns=["test", "export"]
        )
        bp2 = BestPractice(
            id="bp_exp_002",
            title="Export Test Practice 2",
            description="Testing export functionality again",
            category=BestPracticeCategory.CODE_QUALITY,
            domain=DomainType.FINANCE,
            implementation_guidelines=["Guideline A"],
            examples=["Example A", "Example B"],
            severity="medium",
            applicable_patterns=["quality", "code"]
        )

        self.reflector.add_best_practice(bp1)
        self.reflector.add_best_practice(bp2)

        # Confirm we have initial + our 2 practices
        self.assertEqual(len(self.reflector.best_practices), initial_count + 2)

        # Export best practices
        export_json = self.reflector.export_best_practices()
        self.assertIsNotNone(export_json)
        self.assertIn("Export Test Practice 1", export_json)
        self.assertIn("Export Test Practice 2", export_json)

        # Create a new reflector and import
        new_reflector = BestPracticesReflector(self.domain_manager)
        # New reflector should have the same initial default practices
        self.assertEqual(len(new_reflector.best_practices), initial_count)

        import_success = new_reflector.import_best_practices(export_json)

        # After import, it should have initial + our 2 imported practices
        self.assertTrue(import_success)
        self.assertEqual(len(new_reflector.best_practices), initial_count + 2)
        self.assertIn("bp_exp_001", new_reflector.best_practices)
        self.assertIn("bp_exp_002", new_reflector.best_practices)

        # Verify content integrity
        imported_bp1 = new_reflector.best_practices["bp_exp_001"]
        self.assertEqual(imported_bp1.title, "Export Test Practice 1")
        self.assertEqual(imported_bp1.category, BestPracticeCategory.SECURITY)
        self.assertEqual(imported_bp1.domain, DomainType.TECHNOLOGY)
        self.assertIn("Guideline 1", imported_bp1.implementation_guidelines)


if __name__ == '__main__':
    unittest.main()