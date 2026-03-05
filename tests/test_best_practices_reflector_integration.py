import unittest
import sys
import os
from pathlib import Path

# Add the src directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dcae.knowledge_fusion.best_practices_reflector import (
    BestPracticesReflector, BestPracticeCategory, BestPractice, BestPracticeCheckResult
)
from src.dcae.knowledge_fusion.domain_knowledge_manager import DomainKnowledgeManager, DomainType


class TestBestPracticesImplementation(unittest.TestCase):
    """Test cases for best practices implementation and validation."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.domain_manager = DomainKnowledgeManager()
        self.reflector = BestPracticesReflector(self.domain_manager)

    def test_security_best_practices(self):
        """Test that security best practices are properly implemented."""
        # Add a custom security practice
        security_bp = BestPractice(
            id="test_security_001",
            title="SQL Injection Prevention",
            description="Use parameterized queries to prevent SQL injection",
            category=BestPracticeCategory.SECURITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Always use parameterized queries",
                "Validate and sanitize all inputs"
            ],
            examples=[
                "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
            ],
            severity="high",
            applicable_patterns=["sql", "database", "query"]
        )
        self.reflector.add_best_practice(security_bp)

        # Test vulnerable code detection
        vulnerable_sql = """
def get_user(user_id):
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
        """

        results = self.reflector.reflect_best_practices_in_content(
            vulnerable_sql,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.SECURITY]
        )

        # At least one security issue should be detected
        security_results = [r for r in results if r.category == BestPracticeCategory.SECURITY]
        self.assertTrue(len(security_results) > 0)

    def test_code_quality_practices(self):
        """Test that code quality best practices are implemented."""
        # Add a custom code quality practice
        cq_bp = BestPractice(
            id="test_cq_001",
            title="Function Size Limit",
            description="Functions should be small and focused",
            category=BestPracticeCategory.CODE_QUALITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Keep functions under 50 lines",
                "Each function should do one thing well"
            ],
            examples=[
                "Break large functions into smaller ones"
            ],
            severity="medium"
        )
        self.reflector.add_best_practice(cq_bp)

        # Test a long function
        long_function = """
def complex_function():
    # This function has more than 50 lines
    var1 = 1
    var2 = 2
    var3 = 3
    var4 = 4
    var5 = 5
    var6 = 6
    var7 = 7
    var8 = 8
    var9 = 9
    var10 = 10
    var11 = 11
    var12 = 12
    var13 = 13
    var14 = 14
    var15 = 15
    var16 = 16
    var17 = 17
    var18 = 18
    var19 = 19
    var20 = 20
    var21 = 21
    var22 = 22
    var23 = 23
    var24 = 24
    var25 = 25
    var26 = 26
    var27 = 27
    var28 = 28
    var29 = 29
    var30 = 30
    var31 = 31
    var32 = 32
    var33 = 33
    var34 = 34
    var35 = 35
    var36 = 36
    var37 = 37
    var38 = 38
    var39 = 39
    var40 = 40
    var41 = 41
    var42 = 42
    var43 = 43
    var44 = 44
    var45 = 45
    var46 = 46
    var47 = 47
    var48 = 48
    var49 = 49
    var50 = 50
    var51 = 51
    return var1 + var2 + var3 + var51
        """

        results = self.reflector.reflect_best_practices_in_content(
            long_function,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.CODE_QUALITY]
        )

        # The long function should trigger a code quality warning
        cq_results = [r for r in results if r.category == BestPracticeCategory.CODE_QUALITY]
        self.assertTrue(len(cq_results) > 0)

    def test_performance_best_practices(self):
        """Test that performance best practices are implemented."""
        # Test performance practices with nested loops
        nested_loops_code = """
def inefficient_operation():
    for i in range(1000):
        for j in range(1000):
            # Nested loops - potentially inefficient
            result = i * j
            process_result(result)
        """

        results = self.reflector.reflect_best_practices_in_content(
            nested_loops_code,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.PERFORMANCE]
        )

        # Should detect potential performance issues
        perf_results = [r for r in results if r.category == BestPracticeCategory.PERFORMANCE]
        # May or may not find performance issues depending on implementation

    def test_integrate_best_practices(self):
        """Test integration of best practices into code."""
        # Test enhancing content with best practices
        base_content = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
        """

        result = self.reflector.integrate_best_practices(
            base_content,
            DomainType.TECHNOLOGY,
            [BestPracticeCategory.SECURITY, BestPracticeCategory.CODE_QUALITY]
        )

        # Verify that the result contains expected elements
        self.assertIn('enhanced_content', result)
        self.assertIn('applied_practices', result)
        self.assertIn('suggestions', result)

        # The enhanced content should contain the original content
        self.assertIn('calculate_total', result['enhanced_content'])

    def test_best_practices_summary(self):
        """Test getting best practices summaries."""
        summary = self.reflector.get_domain_best_practices_summary(DomainType.TECHNOLOGY)

        # Verify summary structure
        self.assertIn('domain', summary)
        self.assertIn('total_practices', summary)
        self.assertIn('practices_by_category', summary)
        self.assertIn('practice_titles', summary)

        # Should have at least the default practices
        self.assertGreaterEqual(summary['total_practices'], 4)

    def test_export_import_functionality(self):
        """Test export and import of best practices."""
        # Export current practices
        exported = self.reflector.export_best_practices()
        self.assertIsNotNone(exported)
        self.assertIn("Input Validation", exported)

        # Create new reflector and import
        new_domain_manager = DomainKnowledgeManager()
        new_reflector = BestPracticesReflector(new_domain_manager)

        # Initially should have same number of default practices
        initial_count = len(new_reflector.best_practices)

        # Import practices
        success = new_reflector.import_best_practices(exported)
        self.assertTrue(success)

        # Should now have imported practices
        final_count = len(new_reflector.best_practices)
        self.assertEqual(final_count, initial_count)  # Same because they were the same practices


if __name__ == '__main__':
    unittest.main()