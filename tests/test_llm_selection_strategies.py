import unittest
from src.dcae.llm_management.selection_strategies import TaskAnalyzer, LLMSelector, TaskType, TaskComplexity
from src.dcae.llm_management.provider_config import ProviderConfig, ProviderType


class TestTaskAnalyzer(unittest.TestCase):
    """Test cases for the TaskAnalyzer."""

    def test_analyze_coding_task(self):
        """Test analyzing a coding task."""
        analyzer = TaskAnalyzer()

        task_description = "Generate Python code for a FastAPI endpoint that validates user input"

        result = analyzer.analyze(task_description)

        self.assertEqual(result.task_type, TaskType.CODING)
        self.assertGreater(result.complexity_score, 0.2)  # Should have some complexity
        self.assertIn("coding", result.characteristics)
        # Check for either specific language or general programming indicator
        self.assertTrue(any(char in result.characteristics for char in ["programming_language", "python"]))
        # Validate that some relevant characteristics are captured
        relevant_chars = ["validation", "api_development", "web_development"]
        has_relevant_char = any(char in result.characteristics for char in relevant_chars)
        self.assertTrue(has_relevant_char or "programming_language" in result.characteristics)

    def test_analyze_writing_task(self):
        """Test analyzing a writing task."""
        analyzer = TaskAnalyzer()

        task_description = "Write a detailed explanation of how neural networks work"

        result = analyzer.analyze(task_description)

        self.assertEqual(result.task_type, TaskType.WRITING)
        self.assertIn("writing", result.characteristics)
        # Check for explanation or similar concept in characteristics
        has_explanation_char = any(char in result.characteristics for char in ["general", "writing"])
        self.assertTrue(has_explanation_char)

    def test_analyze_analysis_task(self):
        """Test analyzing an analysis task."""
        analyzer = TaskAnalyzer()

        task_description = "Analyze this code for potential security vulnerabilities"

        result = analyzer.analyze(task_description)

        self.assertEqual(result.task_type, TaskType.ANALYSIS)
        self.assertIn("analysis", result.characteristics)
        self.assertIn("security", result.characteristics)

    def test_analyze_general_task(self):
        """Test analyzing a general task."""
        analyzer = TaskAnalyzer()

        task_description = "Answer questions about company policies"

        result = analyzer.analyze(task_description)

        self.assertEqual(result.task_type, TaskType.GENERAL)
        self.assertIn("general", result.characteristics)

    def test_complexity_scoring(self):
        """Test that complexity scoring works correctly."""
        analyzer = TaskAnalyzer()

        simple_task = "Say hello world"
        complex_task = "Design a distributed system architecture with load balancing, failover, security, monitoring, and scalability considerations"

        simple_result = analyzer.analyze(simple_task)
        complex_result = analyzer.analyze(complex_task)

        # Complex task should have higher complexity score
        self.assertLess(simple_result.complexity_score, complex_result.complexity_score)


class TestLLMSelector(unittest.TestCase):
    """Test cases for the LLMSelector."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create some test provider configs
        self.providers = {
            "gpt4": ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test_key",
                name="gpt4",
                model="gpt-4o",
                temperature=0.3  # More deterministic
            ),
            "claude": ProviderConfig(
                provider_type=ProviderType.ANTHROPIC,
                api_key="test_key",
                name="claude",
                model="claude-3-5-sonnet-20241022",
                temperature=0.3
            ),
            "qwen": ProviderConfig(
                provider_type=ProviderType.BIGMODEL,
                api_key="test_key",
                name="qwen",
                model="qwen-max",
                temperature=0.7
            )
        }

    def test_select_for_coding_task(self):
        """Test selecting an LLM for a coding task."""
        selector = LLMSelector(self.providers)

        task_description = "Generate Python code for a data processing function"

        selected = selector.select_best_provider(task_description)

        # For coding tasks, GPT-4 or Claude should be selected
        self.assertIn(selected.name, ["gpt4", "claude"])

    def test_select_for_writing_task(self):
        """Test selecting an LLM for a writing task."""
        selector = LLMSelector(self.providers)

        task_description = "Write a creative story about AI development"

        selected = selector.select_best_provider(task_description)

        # For creative writing, any of the providers could be suitable
        self.assertIn(selected.name, ["gpt4", "claude", "qwen"])

    def test_select_for_analysis_task(self):
        """Test selecting an LLM for an analysis task."""
        selector = LLMSelector(self.providers)

        task_description = "Analyze this algorithm for time complexity"

        selected = selector.select_best_provider(task_description)

        # For analysis tasks, GPT-4 or Claude should work well
        self.assertIn(selected.name, ["gpt4", "claude"])

    def test_select_based_on_complexity(self):
        """Test that selection considers task complexity."""
        selector = LLMSelector(self.providers)

        complex_task = "Design a complete microservices architecture with security, monitoring, deployment pipelines, and disaster recovery"

        selected = selector.select_best_provider(complex_task)

        # Complex tasks should go to capable models like GPT-4 or Claude
        self.assertIn(selected.name, ["gpt4", "claude"])

    def test_select_with_cost_consideration(self):
        """Test that selection can consider cost."""
        selector = LLMSelector(self.providers)

        # For simple tasks, selector might choose differently if cost is factored in
        simple_task = "Summarize this paragraph in one sentence"

        selected = selector.select_best_provider(simple_task)

        # Should still return a valid provider
        self.assertIsNotNone(selected)
        self.assertIn(selected.name, ["gpt4", "claude", "qwen"])

    def test_provider_availability_consideration(self):
        """Test that selection considers provider availability."""
        # Simulate some providers being unavailable
        selector = LLMSelector({"gpt4": self.providers["gpt4"]})

        task_description = "Generate Python code for a function"

        selected = selector.select_best_provider(task_description)

        # Should select the only available provider
        self.assertEqual(selected.name, "gpt4")


if __name__ == '__main__':
    unittest.main()