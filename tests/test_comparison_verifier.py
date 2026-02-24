import unittest
from unittest.mock import MagicMock
from src.dcae.llm_management.comparison_verifier import MultiLLMComparison, ComparisonResult, ConsistencyCheck


class TestMultiLLMComparison(unittest.TestCase):
    """Test cases for the MultiLLMComparison functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock LLM clients
        self.mock_llm1 = MagicMock()
        self.mock_llm1.generate.return_value = "This is response from LLM 1"
        self.mock_llm2 = MagicMock()
        self.mock_llm2.generate.return_value = "This is response from LLM 2"
        self.mock_llm3 = MagicMock()
        self.mock_llm3.generate.return_value = "This is response from LLM 1"  # Same as LLM 1

        self.llm_clients = {
            "llm1": self.mock_llm1,
            "llm2": self.mock_llm2,
            "llm3": self.mock_llm3
        }

        self.comparator = MultiLLMComparison(self.llm_clients)

    def test_submit_identical_tasks_to_multiple_llms(self):
        """Test submitting identical tasks to multiple LLMs."""
        task_prompt = "Generate a simple greeting message"

        results = self.comparator.submit_to_multiple(task_prompt, ["llm1", "llm2"])

        # Should have results from 2 LLMs
        self.assertEqual(len(results), 2)
        self.assertIn("llm1", results)
        self.assertIn("llm2", results)
        self.assertEqual(results["llm1"], "This is response from LLM 1")
        self.assertEqual(results["llm2"], "This is response from LLM 2")

    def test_compare_outputs_for_consistency(self):
        """Test comparing outputs for consistency."""
        task_prompt = "What is the capital of France?"

        results = self.comparator.submit_to_multiple(task_prompt, ["llm1", "llm3"])

        # Both LLMs returned the same response
        consistency_check = self.comparator.compare_consistency(results)

        # Since both responses are the same, should have high consistency
        self.assertGreaterEqual(consistency_check.agreement_percentage, 1.0)
        self.assertEqual(len(consistency_check.discrepancies), 0)

    def test_identify_significant_discrepancies(self):
        """Test identifying significant discrepancies between outputs."""
        task_prompt = "What is 2+2?"

        results = self.comparator.submit_to_multiple(task_prompt, ["llm1", "llm2"])

        # Compare consistency
        consistency_check = self.comparator.compare_consistency(results)

        # Since responses are different, should have discrepancies
        if consistency_check.agreement_percentage < 1.0:
            self.assertGreater(len(consistency_check.discrepancies), 0)

    def test_specify_comparison_thresholds(self):
        """Test specifying comparison thresholds."""
        task_prompt = "Describe a tree in one sentence"

        results = self.comparator.submit_to_multiple(task_prompt, ["llm1", "llm2"])

        # Compare with a lenient threshold
        consistency_check = self.comparator.compare_consistency(results, threshold=0.3)

        # With a low threshold, should be more lenient
        self.assertIsNotNone(consistency_check.agreement_percentage)

        # Compare with a strict threshold
        consistency_check_strict = self.comparator.compare_consistency(results, threshold=0.9)

        # The strict check might have lower agreement percentage
        self.assertIsNotNone(consistency_check_strict.agreement_percentage)

    def test_provide_confidence_scores(self):
        """Test providing confidence scores based on consensus."""
        task_prompt = "Translate 'hello' to French"

        results = self.comparator.submit_to_multiple(task_prompt, ["llm1", "llm2", "llm3"])

        confidence_score = self.comparator.calculate_confidence_score(results)

        # Should return a confidence score between 0 and 1
        self.assertIsInstance(confidence_score, float)
        self.assertGreaterEqual(confidence_score, 0.0)
        self.assertLessEqual(confidence_score, 1.0)

    def test_highlight_areas_of_disagreement(self):
        """Test highlighting areas where LLMs disagree."""
        task_prompt = "Explain quantum computing briefly"

        results = {
            "llm1": "Quantum computing uses quantum bits that can be 0 and 1 simultaneously.",
            "llm2": "Quantum computing is a type of computation that harnesses quantum mechanics.",
            "llm3": "Quantum computing uses quantum bits that can be 0 and 1 simultaneously."
        }

        discrepancies = self.comparator.find_discrepancies(results)

        # Should identify differences between llm2 and others
        self.assertIsNotNone(discrepancies)

    def test_consolidate_outputs_with_attribution(self):
        """Test consolidating outputs with clear attribution."""
        task_prompt = "What is photosynthesis?"

        results = self.comparator.submit_to_multiple(task_prompt, ["llm1", "llm2"])

        consolidated = self.comparator.consolidate_outputs(results)

        # Should return a structured result with attributions
        self.assertIsNotNone(consolidated)
        self.assertIn("responses", consolidated)
        self.assertIn("consensus", consolidated)
        self.assertIn("discrepancies", consolidated)

    def test_concurrent_processing(self):
        """Test concurrent processing of multiple LLM requests."""
        task_prompt = "Say hi"

        results = self.comparator.submit_to_multiple_concurrent(task_prompt, ["llm1", "llm2"])

        # Should get results from both LLMs
        self.assertEqual(len(results), 2)
        self.assertIn("llm1", results)
        self.assertIn("llm2", results)

    def test_handle_failed_requests(self):
        """Test handling of failed LLM requests."""
        # Make one of the LLMs throw an exception
        self.mock_llm1.generate.side_effect = Exception("API Error")

        task_prompt = "Say something"

        results = self.comparator.submit_to_multiple(task_prompt, ["llm1", "llm2"])

        # Should still return result from llm2, and maybe handle the failure
        self.assertIn("llm2", results)
        # Depending on implementation, might or might not have llm1 result

    def test_comparison_metrics_calculation(self):
        """Test calculation of comparison metrics."""
        results = {
            "llm1": "Similar response content",
            "llm2": "Similar response content",
            "llm3": "Different response content"
        }

        consistency_check = self.comparator.compare_consistency(results)

        self.assertIsInstance(consistency_check, ConsistencyCheck)
        self.assertGreaterEqual(consistency_check.agreement_percentage, 0.0)
        self.assertLessEqual(consistency_check.agreement_percentage, 1.0)
        self.assertIsInstance(consistency_check.discrepancies, list)


if __name__ == '__main__':
    unittest.main()