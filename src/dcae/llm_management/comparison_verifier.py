"""Module for comparing and verifying outputs across multiple LLMs."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Set
import difflib
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class ComparisonResult:
    """Data class representing the result of a comparison between LLM outputs."""
    provider_name: str
    output: str
    confidence: float = 1.0  # Confidence in this output


@dataclass
class ConsistencyCheck:
    """Data class representing the result of consistency checking."""
    agreement_percentage: float
    discrepancies: List[Dict[str, Any]]
    common_elements: List[str]


class MultiLLMComparison:
    """Handles comparison and verification of outputs across multiple LLMs."""

    def __init__(self, llm_clients: Dict[str, Any]):
        """
        Initialize the MultiLLMComparison.

        Args:
            llm_clients: Dictionary mapping provider names to LLM client objects
        """
        self.llm_clients = llm_clients

    def submit_to_multiple(self, prompt: str, provider_names: List[str]) -> Dict[str, str]:
        """
        Submit identical tasks to multiple LLMs.

        Args:
            prompt: The prompt to send to LLMs
            provider_names: List of provider names to submit to

        Returns:
            Dictionary mapping provider names to their responses
        """
        results = {}

        for provider_name in provider_names:
            if provider_name in self.llm_clients:
                try:
                    # Call the LLM client's generation method
                    response = self.llm_clients[provider_name].generate(prompt)
                    results[provider_name] = response
                except Exception as e:
                    print(f"Error getting response from {provider_name}: {e}")
                    results[provider_name] = f"Error: {str(e)}"

        return results

    def submit_to_multiple_concurrent(self, prompt: str, provider_names: List[str]) -> Dict[str, str]:
        """
        Submit identical tasks to multiple LLMs concurrently.

        Args:
            prompt: The prompt to send to LLMs
            provider_names: List of provider names to submit to

        Returns:
            Dictionary mapping provider names to their responses
        """
        results = {}

        with ThreadPoolExecutor(max_workers=len(provider_names)) as executor:
            # Create futures for each provider
            futures = {
                executor.submit(self._generate_single, provider_name, prompt): provider_name
                for provider_name in provider_names if provider_name in self.llm_clients
            }

            # Collect results
            for future in as_completed(futures):
                provider_name = futures[future]
                try:
                    response = future.result()
                    results[provider_name] = response
                except Exception as e:
                    print(f"Error getting response from {provider_name}: {e}")
                    results[provider_name] = f"Error: {str(e)}"

        return results

    def _generate_single(self, provider_name: str, prompt: str) -> str:
        """Helper method to generate response from a single provider."""
        return self.llm_clients[provider_name].generate(prompt)

    def compare_consistency(self, results: Dict[str, str], threshold: float = 0.7) -> ConsistencyCheck:
        """
        Compare outputs for consistency and identify discrepancies.

        Args:
            results: Dictionary mapping provider names to their responses
            threshold: Similarity threshold for determining agreement

        Returns:
            ConsistencyCheck object containing comparison results
        """
        if len(results) < 2:
            return ConsistencyCheck(1.0, [], [])

        # Get all responses
        responses = list(results.values())
        provider_names = list(results.keys())

        # Compare all pairs of responses
        total_comparisons = 0
        agreements = 0
        discrepancies = []

        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                total_comparisons += 1
                similarity = self._calculate_similarity(responses[i], responses[j])

                if similarity >= threshold:
                    agreements += 1
                else:
                    discrepancies.append({
                        'providers': [provider_names[i], provider_names[j]],
                        'response_1': responses[i],
                        'response_2': responses[j],
                        'similarity': similarity,
                        'threshold': threshold
                    })

        # Calculate agreement percentage
        agreement_percentage = agreements / total_comparisons if total_comparisons > 0 else 1.0

        # Find common elements across responses
        common_elements = self._find_common_elements(responses)

        return ConsistencyCheck(agreement_percentage, discrepancies, common_elements)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        # Use SequenceMatcher to calculate similarity
        matcher = difflib.SequenceMatcher(None, text1.strip(), text2.strip())
        return matcher.ratio()

    def _find_common_elements(self, responses: List[str]) -> List[str]:
        """
        Find common elements across multiple responses.

        Args:
            responses: List of response texts

        Returns:
            List of common elements found across responses
        """
        if not responses:
            return []

        # Tokenize each response
        token_sets = [set(resp.lower().split()) for resp in responses]

        # Find intersection of all token sets
        if token_sets:
            common_tokens = set.intersection(*token_sets) if len(token_sets) > 1 else token_sets[0]
            return list(common_tokens)[:10]  # Return top 10 common tokens
        return []

    def find_discrepancies(self, results: Dict[str, str], threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find discrepancies between LLM outputs.

        Args:
            results: Dictionary mapping provider names to their responses
            threshold: Similarity threshold for determining agreement

        Returns:
            List of discrepancy reports
        """
        consistency_check = self.compare_consistency(results, threshold)
        return consistency_check.discrepancies

    def calculate_confidence_score(self, results: Dict[str, str], threshold: float = 0.7) -> float:
        """
        Calculate a confidence score based on LLM consensus.

        Args:
            results: Dictionary mapping provider names to their responses
            threshold: Similarity threshold for determining agreement

        Returns:
            Confidence score between 0 and 1
        """
        consistency_check = self.compare_consistency(results, threshold)
        return consistency_check.agreement_percentage

    def consolidate_outputs(self, results: Dict[str, str], threshold: float = 0.7) -> Dict[str, Any]:
        """
        Consolidate outputs from multiple LLMs with clear attribution.

        Args:
            results: Dictionary mapping provider names to their responses
            threshold: Similarity threshold for determining agreement

        Returns:
            Consolidated output with attribution information
        """
        consistency_check = self.compare_consistency(results, threshold)

        return {
            'responses': results,
            'consensus': consistency_check.common_elements,
            'discrepancies': consistency_check.discrepancies,
            'agreement_percentage': consistency_check.agreement_percentage,
            'summary': self._create_summary(results, consistency_check)
        }

    def _create_summary(self, results: Dict[str, str], consistency_check: ConsistencyCheck) -> str:
        """
        Create a summary of the comparison results.

        Args:
            results: Original results from LLMs
            consistency_check: Consistency check results

        Returns:
            Summary string
        """
        num_providers = len(results)
        num_agreements = int(consistency_check.agreement_percentage * (num_providers * (num_providers - 1) / 2))
        num_discrepancies = len(consistency_check.discrepancies)

        summary_parts = [
            f"Submitted to {num_providers} providers",
            f"Agreements found: {num_agreements}",
            f"Discrepancies identified: {num_discrepancies}"
        ]

        if consistency_check.common_elements:
            summary_parts.append(f"Common elements: {', '.join(consistency_check.common_elements[:5])}")

        return "; ".join(summary_parts)