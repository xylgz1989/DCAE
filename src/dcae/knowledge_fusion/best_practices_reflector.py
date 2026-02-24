"""Module for reflecting domain-specific best practices in generated content."""
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from .knowledge_fuser import KnowledgeItem, KnowledgeSourceType
from .domain_knowledge_manager import DomainKnowledgeManager, DomainType
from .cross_domain_recommender import Recommendation, RecommendationType


class BestPracticeCategory(Enum):
    """Categories of best practices."""
    CODE_QUALITY = "code_quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    ERROR_HANDLING = "error_handling"


@dataclass
class BestPractice:
    """Represents a best practice."""
    id: str
    title: str
    description: str
    category: BestPracticeCategory
    domain: DomainType
    implementation_guidelines: List[str]
    examples: List[str]
    severity: str = "medium"  # low, medium, high
    applicable_patterns: List[str] = None

    def __post_init__(self):
        if self.applicable_patterns is None:
            self.applicable_patterns = []


@dataclass
class BestPracticeCheckResult:
    """Result of a best practice check."""
    practice_id: str
    practice_title: str
    category: BestPracticeCategory
    is_followed: bool
    violations: List[str]
    suggestions: List[str]
    confidence: float


class BestPracticesReflector:
    """Reflects domain-specific best practices in generated content."""

    def __init__(self, domain_manager: DomainKnowledgeManager):
        """
        Initialize the best practices reflector.

        Args:
            domain_manager: Domain knowledge manager to use for best practices
        """
        self.domain_manager = domain_manager
        self.best_practices: Dict[str, BestPractice] = {}
        self.category_indices: Dict[BestPracticeCategory, Set[str]] = {
            category: set() for category in BestPracticeCategory
        }
        self.domain_indices: Dict[DomainType, Set[str]] = {
            domain: set() for domain in DomainType
        }

        # Load default best practices
        self._load_default_best_practices()

    def _load_default_best_practices(self):
        """Load default best practices for common categories."""
        # Security best practices
        self.add_best_practice(BestPractice(
            id="bp_sec_001",
            title="Input Validation",
            description="Always validate inputs to prevent injection attacks",
            category=BestPracticeCategory.SECURITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Validate input length, type, and format",
                "Use allowlists instead of blocklists",
                "Sanitize inputs before processing"
            ],
            examples=[
                "Validate email format with regex",
                "Check numeric inputs are within expected range"
            ],
            severity="high",
            applicable_patterns=["API", "form", "input"]
        ))

        # Code quality best practices
        self.add_best_practice(BestPractice(
            id="bp_cq_001",
            title="Function Length",
            description="Keep functions small and focused on a single responsibility",
            category=BestPracticeCategory.CODE_QUALITY,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Functions should fit on one screen",
                "Each function should do one thing well",
                "Break down complex functions into smaller ones"
            ],
            examples=[
                "A function with more than 50 lines might need refactoring",
                "Separate data processing from display logic"
            ],
            severity="medium",
            applicable_patterns=["function", "method", "procedure"]
        ))

        # Testing best practices
        self.add_best_practice(BestPractice(
            id="bp_test_001",
            title="Test Coverage",
            description="Maintain high test coverage for critical functionality",
            category=BestPracticeCategory.TESTING,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Aim for 80%+ line coverage",
                "Focus on critical business logic",
                "Test edge cases and error conditions"
            ],
            examples=[
                "Test boundary values",
                "Verify error handling paths"
            ],
            severity="medium",
            applicable_patterns=["test", "unit", "integration"]
        ))

        # Performance best practices
        self.add_best_practice(BestPractice(
            id="bp_perf_001",
            title="Efficient Algorithms",
            description="Choose algorithms with appropriate time and space complexity",
            category=BestPracticeCategory.PERFORMANCE,
            domain=DomainType.TECHNOLOGY,
            implementation_guidelines=[
                "Understand Big O notation for your algorithms",
                "Consider data size when selecting algorithms",
                "Cache expensive computations"
            ],
            examples=[
                "Use hash tables for O(1) lookups when appropriate",
                "Avoid nested loops when possible"
            ],
            severity="medium",
            applicable_patterns=["algorithm", "data", "performance"]
        ))

    def add_best_practice(self, practice: BestPractice) -> bool:
        """
        Add a best practice to the registry.

        Args:
            practice: Best practice to add

        Returns:
            True if addition was successful, False otherwise
        """
        self.best_practices[practice.id] = practice
        self.category_indices[practice.category].add(practice.id)
        self.domain_indices[practice.domain].add(practice.id)
        return True

    def get_practices_by_category(self, category: BestPracticeCategory) -> List[BestPractice]:
        """
        Get best practices by category.

        Args:
            category: Category to retrieve practices for

        Returns:
            List of best practices in the category
        """
        practice_ids = self.category_indices.get(category, set())
        return [
            self.best_practices[practice_id]
            for practice_id in practice_ids
            if practice_id in self.best_practices
        ]

    def get_practices_by_domain(self, domain: DomainType) -> List[BestPractice]:
        """
        Get best practices by domain.

        Args:
            domain: Domain to retrieve practices for

        Returns:
            List of best practices for the domain
        """
        practice_ids = self.domain_indices.get(domain, set())
        return [
            self.best_practices[practice_id]
            for practice_id in practice_ids
            if practice_id in self.best_practices
        ]

    def get_practice_by_id(self, practice_id: str) -> Optional[BestPractice]:
        """
        Get a specific best practice by ID.

        Args:
            practice_id: ID of the practice to retrieve

        Returns:
            Best practice or None if not found
        """
        return self.best_practices.get(practice_id)

    def reflect_best_practices_in_content(
        self,
        content: str,
        domain: DomainType,
        categories: List[BestPracticeCategory] = None
    ) -> List[BestPracticeCheckResult]:
        """
        Reflect best practices in generated content by checking compliance.

        Args:
            content: Content to analyze for best practice compliance
            domain: Domain context for the content
            categories: Specific categories to check (all if None)

        Returns:
            List of best practice check results
        """
        if categories is None:
            categories = list(BestPracticeCategory)

        # Get relevant practices for this domain and categories
        relevant_practices = []
        for category in categories:
            practices = self.get_practices_by_category(category)
            domain_practices = [p for p in practices if p.domain == domain or p.domain == DomainType.TECHNOLOGY]
            relevant_practices.extend(domain_practices)

        results = []
        for practice in relevant_practices:
            result = self._check_practice_compliance(practice, content)
            if result:
                results.append(result)

        return results

    def _check_practice_compliance(self, practice: BestPractice, content: str) -> Optional[BestPracticeCheckResult]:
        """Check if content complies with a specific best practice."""
        # Analyze content for compliance with the practice
        violations = []
        suggestions = []

        # Different checks based on practice category
        if practice.category == BestPracticeCategory.SECURITY:
            violations, suggestions = self._check_security_practices(practice, content)
        elif practice.category == BestPracticeCategory.CODE_QUALITY:
            violations, suggestions = self._check_code_quality_practices(practice, content)
        elif practice.category == BestPracticeCategory.TESTING:
            violations, suggestions = self._check_testing_practices(practice, content)
        elif practice.category == BestPracticeCategory.PERFORMANCE:
            violations, suggestions = self._check_performance_practices(practice, content)
        else:
            # For other categories, use generic pattern matching
            violations, suggestions = self._check_generic_practices(practice, content)

        is_followed = len(violations) == 0
        confidence = 0.8 if is_followed else 0.8 - (len(violations) * 0.1)
        confidence = max(0.1, confidence)  # Minimum confidence of 0.1

        return BestPracticeCheckResult(
            practice_id=practice.id,
            practice_title=practice.title,
            category=practice.category,
            is_followed=is_followed,
            violations=violations,
            suggestions=suggestions,
            confidence=confidence
        )

    def _check_security_practices(self, practice: BestPractice, content: str) -> Tuple[List[str], List[str]]:
        """Check security best practices."""
        violations = []
        suggestions = []

        # Check for input validation
        if "input" in content.lower() and "validate" not in content.lower():
            violations.append("Input validation not found in content that handles user input")
            suggestions.append("Add validation for input data")

        # Check for sanitization
        if "sanitize" not in content.lower() and "escape" not in content.lower():
            # Only flag if there are input/output operations
            input_patterns = [r'request\.', r'input\(', r'argv\[' , r'raw_input\(']
            for pattern in input_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append("Input sanitization not found")
                    suggestions.append("Consider sanitizing user inputs to prevent injection attacks")
                    break

        return violations, suggestions

    def _check_code_quality_practices(self, practice: BestPractice, content: str) -> Tuple[List[str], List[str]]:
        """Check code quality best practices."""
        violations = []
        suggestions = []

        # Check function length (simple heuristic)
        # Count function definitions and estimate line count
        function_matches = re.finditer(r'(def |function |func |fn )\w+\s*\(', content)
        for match in function_matches:
            # Find the corresponding closing bracket/colon for the function
            func_start = match.end()
            # This is a simplified approach - in reality would need proper parsing
            func_block_start = content.find(":", func_start)
            if func_block_start != -1:
                # Count lines until next function definition or end of significant indentation
                remaining_content = content[func_block_start+1:]
                lines = remaining_content.split('\n')

                # Count non-empty lines until we hit a line with the same or less indentation
                line_count = 0
                for line in lines:
                    if line.strip():  # non-empty line
                        line_count += 1
                    # Simplified: if we get more than 50 lines, flag it
                    if line_count > 50:
                        violations.append("Function appears to be longer than recommended 50 lines")
                        suggestions.append("Consider breaking this function into smaller, more focused functions")
                        break

        # Check for comments
        comment_ratio = len(re.findall(r'#|\*|//', content)) / len(content.split())
        if comment_ratio < 0.05:  # Less than 5% comments
            violations.append("Low comment density detected")
            suggestions.append("Consider adding more comments to explain complex logic")

        return violations, suggestions

    def _check_testing_practices(self, practice: BestPractice, content: str) -> Tuple[List[str], List[str]]:
        """Check testing best practices."""
        violations = []
        suggestions = []

        # Check for test-related keywords
        test_keywords = ['assert', 'test_', 'it(', 'describe(', 'unittest', 'pytest', 'mock', 'stub']
        has_tests = any(keyword in content.lower() for keyword in test_keywords)

        if not has_tests and 'test' in practice.title.lower():
            violations.append("No evidence of testing practices in the code")
            suggestions.append("Consider adding unit tests for the implemented functionality")

        return violations, suggestions

    def _check_performance_practices(self, practice: BestPractice, content: str) -> Tuple[List[str], List[str]]:
        """Check performance best practices."""
        violations = []
        suggestions = []

        # Check for inefficient patterns
        if content.lower().count('for') > 2 and content.lower().count('for') > content.lower().count('range'):
            # Potential nested loop pattern without optimization
            violations.append("Multiple for loops detected - potential performance bottleneck")
            suggestions.append("Consider algorithm optimization or caching strategies")

        return violations, suggestions

    def _check_generic_practices(self, practice: BestPractice, content: str) -> Tuple[List[str], List[str]]:
        """Generic best practice checker."""
        violations = []
        suggestions = []

        # Just return empty for now
        return violations, suggestions

    def integrate_best_practices(
        self,
        content: str,
        domain: DomainType,
        target_categories: List[BestPracticeCategory] = None
    ) -> Dict[str, Any]:
        """
        Integrate best practices directly into content generation.

        Args:
            content: Base content to enhance
            domain: Domain context
            target_categories: Categories to focus on (all if None)

        Returns:
            Dictionary with enhanced content and best practice information
        """
        if target_categories is None:
            target_categories = list(BestPracticeCategory)

        # Get relevant practices
        relevant_practices = []
        for category in target_categories:
            practices = self.get_practices_by_category(category)
            domain_practices = [p for p in practices if p.domain == domain or p.domain == DomainType.TECHNOLOGY]
            relevant_practices.extend(domain_practices)

        # Apply practices to content
        enhanced_content = content
        applied_practices = []

        for practice in relevant_practices:
            enhanced_content, applied = self._apply_practice_to_content(
                practice, enhanced_content
            )
            if applied:
                applied_practices.append(practice.id)

        return {
            'enhanced_content': enhanced_content,
            'applied_practices': applied_practices,
            'suggestions': [p.title for p in relevant_practices if p.id in applied_practices]
        }

    def _apply_practice_to_content(self, practice: BestPractice, content: str) -> Tuple[str, bool]:
        """Apply a best practice to content (add commentary, structure, etc.)."""
        # For now, we'll just append a comment about the best practice if it's relevant
        if practice.category == BestPracticeCategory.SECURITY and 'input' in content.lower():
            return content + f"\n# SECURITY NOTE: Remember to validate and sanitize inputs per best practice: {practice.title}", True
        elif practice.category == BestPracticeCategory.CODE_QUALITY and 'def ' in content:
            return content + f"\n# CODE QUALITY: Ensure this function follows the best practice: {practice.title}", True
        elif practice.category == BestPracticeCategory.TESTING and ('def ' in content or 'function' in content):
            return content + f"\n# TESTING: Consider writing unit tests for this function per best practice: {practice.title}", True

        return content, False

    def get_domain_best_practices_summary(self, domain: DomainType) -> Dict[str, Any]:
        """
        Get a summary of best practices for a domain.

        Args:
            domain: Domain to get summary for

        Returns:
            Dictionary with best practices summary
        """
        practices = self.get_practices_by_domain(domain)
        category_counts = {}

        for practice in practices:
            cat = practice.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            'domain': domain.value,
            'total_practices': len(practices),
            'practices_by_category': category_counts,
            'practice_titles': [p.title for p in practices]
        }

    def export_best_practices(self) -> str:
        """
        Export all best practices as JSON.

        Returns:
            JSON string containing all best practices
        """
        import json

        export_data = []
        for practice in self.best_practices.values():
            practice_dict = {
                'id': practice.id,
                'title': practice.title,
                'description': practice.description,
                'category': practice.category.value,
                'domain': practice.domain.value,
                'implementation_guidelines': practice.implementation_guidelines,
                'examples': practice.examples,
                'severity': practice.severity,
                'applicable_patterns': practice.applicable_patterns
            }
            export_data.append(practice_dict)

        return json.dumps(export_data, indent=2)

    def import_best_practices(self, json_str: str) -> bool:
        """
        Import best practices from JSON.

        Args:
            json_str: JSON string containing best practices data

        Returns:
            True if import was successful, False otherwise
        """
        import json
        try:
            data = json.loads(json_str)
            for practice_data in data:
                practice = BestPractice(
                    id=practice_data['id'],
                    title=practice_data['title'],
                    description=practice_data['description'],
                    category=BestPracticeCategory(practice_data['category']),
                    domain=DomainType(practice_data['domain']),
                    implementation_guidelines=practice_data['implementation_guidelines'],
                    examples=practice_data['examples'],
                    severity=practice_data.get('severity', 'medium'),
                    applicable_patterns=practice_data.get('applicable_patterns', [])
                )
                self.add_best_practice(practice)
            return True
        except (json.JSONDecodeError, ValueError):
            return False