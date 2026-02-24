"""Module for intelligent LLM selection strategies."""
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import re


class TaskType(Enum):
    """Enum representing different types of tasks."""
    CODING = "coding"
    WRITING = "writing"
    ANALYSIS = "analysis"
    GENERAL = "general"
    CREATIVE = "creative"
    MATH = "math"


class TaskComplexity(Enum):
    """Enum representing different levels of task complexity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class TaskAnalysis:
    """Data class representing the analysis of a task."""
    task_type: TaskType
    complexity_score: float  # 0.0 to 1.0
    characteristics: List[str]
    estimated_tokens: int = 0


class TaskAnalyzer:
    """Analyzes tasks to determine their characteristics and requirements."""

    def analyze(self, task_description: str) -> TaskAnalysis:
        """
        Analyze a task description to determine its characteristics.

        Args:
            task_description: Description of the task to analyze

        Returns:
            TaskAnalysis object containing analysis results
        """
        # Normalize the description
        desc_lower = task_description.lower()

        # Determine task type
        task_type = self._determine_task_type(desc_lower)

        # Extract characteristics
        characteristics = self._extract_characteristics(desc_lower)

        # Calculate complexity score (0.0 to 1.0)
        complexity_score = self._calculate_complexity_score(task_description, characteristics)

        # Estimate token count
        estimated_tokens = self._estimate_token_count(task_description)

        return TaskAnalysis(
            task_type=task_type,
            complexity_score=complexity_score,
            characteristics=characteristics,
            estimated_tokens=estimated_tokens
        )

    def _determine_task_type(self, desc: str) -> TaskType:
        """Determine the type of task based on description."""
        # Look for coding indicators
        coding_keywords = [
            "code", "function", "program", "algorithm", "implementation",
            "python", "javascript", "java", "c++", "react", "api",
            "endpoint", "database", "class", "method", "variable",
            "library", "framework", "debug", "refactor", "optimize"
        ]

        # Look for writing indicators
        writing_keywords = [
            "write", "article", "blog", "essay", "story", "paragraph",
            "narrative", "explanation", "document", "text", "content",
            "draft", "compose", "create", "describe"
        ]

        # Look for analysis indicators
        analysis_keywords = [
            "analyze", "analyze", "review", "evaluate", "examine",
            "audit", "check", "assess", "inspect", "compare",
            "identify", "find", "security", "vulnerability", "complexity"
        ]

        # Look for creative indicators
        creative_keywords = [
            "creative", "imagine", "design", "innovative", "brainstorm",
            "fiction", "poem", "lyrics", "artistic", "inspire", "invent"
        ]

        # Look for math indicators
        math_keywords = [
            "calculate", "equation", "formula", "math", "compute",
            "derivative", "integral", "statistic", "probability",
            "algorithm", "optimization", "proof"
        ]

        # Count keyword matches
        coding_matches = sum(1 for keyword in coding_keywords if keyword in desc)
        writing_matches = sum(1 for keyword in writing_keywords if keyword in desc)
        analysis_matches = sum(1 for keyword in analysis_keywords if keyword in desc)
        creative_matches = sum(1 for keyword in creative_keywords if keyword in desc)
        math_matches = sum(1 for keyword in math_keywords if keyword in desc)

        # Determine type based on most matches
        max_matches = max(coding_matches, writing_matches, analysis_matches, creative_matches, math_matches)

        if max_matches == 0:
            return TaskType.GENERAL

        if coding_matches == max_matches:
            return TaskType.CODING
        elif writing_matches == max_matches:
            return TaskType.WRITING
        elif analysis_matches == max_matches:
            return TaskType.ANALYSIS
        elif creative_matches == max_matches:
            return TaskType.CREATIVE
        elif math_matches == max_matches:
            return TaskType.MATH

        return TaskType.GENERAL

    def _extract_characteristics(self, desc: str) -> List[str]:
        """Extract characteristics from the task description."""
        characteristics = []

        # Common characteristics to look for
        char_patterns = [
            (r"\bpython\b|\bjavascript\b|\bjava\b|\bgo\b|\brust\b|\bphp\b", "programming_language"),
            (r"\bweb\b|\bfrontend\b|\bbackend\b|\bfull[ -]?stack\b", "web_development"),
            (r"\bsecurity\b|\bvulnerabilit(y|ies)\b|\bsecure\b|\bhack\b", "security"),
            (r"\bdata\b|\banalysis\b|\banalytics\b|\bstatistics\b", "data_analysis"),
            (r"\balgorithm\b|\bcomplexity\b|\boptimiz(e|ation)\b", "algorithms"),
            (r"\btest\b|\btesting\b|\bunit[ -]?test\b|\bintegration[ -]?test\b", "testing"),
            (r"\bapi\b|\brest\b|\bgql\b|\bgraphql\b", "api_development"),
            (r"\bmobile\b|\bandroid\b|\bios\b|\bflutter\b|\breact[ -]?native\b", "mobile_development"),
            (r"\bml\b|\bai\b|\bmachine[ -]?learning\b|\bartificial[ -]?intelligence\b", "machine_learning"),
            (r"\bui\b|\bux\b|\binterface\b|\bdesign\b|\bfrontend\b", "ui_ux"),
            (r"\barchitect(ure|ural)\b", "architecture"),
            (r"\bscale\b|\bscalability\b|\bperformance\b|\boptimiz(e|ation)\b", "performance"),
            (r"\bcloud\b|\baws\b|\bazure\b|\bgcp\b|\bdocker\b|\bkubernetes\b", "cloud_native"),
        ]

        for pattern, characteristic in char_patterns:
            if re.search(pattern, desc, re.IGNORECASE):
                characteristics.append(characteristic)

        # Add general characteristics based on keywords
        if any(word in desc for word in ["analyze", "analyz", "review", "evaluate", "examine", "audit", "assess", "inspect", "compare", "identify"]):
            characteristics.append("analysis")

        if any(word in desc for word in ["write", "article", "blog", "essay", "story", "paragraph", "narrative", "explanation", "document", "text", "content", "draft", "compose", "create", "describe"]):
            characteristics.append("writing")

        if any(word in desc for word in ["code", "function", "program", "algorithm", "implementation", "python", "javascript", "java", "c++", "react", "api", "endpoint", "database", "class", "method", "variable", "library", "framework", "debug", "refactor", "optimize"]):
            characteristics.append("coding")

        if any(word in desc for word in ["creative", "imagine", "design", "innovative", "brainstorm", "fiction", "poem", "lyrics", "artistic", "inspire", "invent"]):
            characteristics.append("creative")

        if any(word in desc for word in ["calculate", "equation", "formula", "math", "compute", "derivative", "integral", "statistic", "probability", "algorithm", "optimization", "proof"]):
            characteristics.append("math")

        # Add complexity indicators
        if any(word in desc for word in ["simple", "easy", "basic"]):
            characteristics.append("simple")
        elif any(word in desc for word in ["complex", "advanced", "difficult"]):
            characteristics.append("complex")

        if any(word in desc for word in ["documentation", "doc", "readme"]):
            characteristics.append("documentation")

        if any(word in desc for word in ["bug", "fix", "error", "issue"]):
            characteristics.append("debugging")

        # Return at least 'general' if no other characteristics found
        return characteristics if characteristics else ["general"]

    def _calculate_complexity_score(self, task_description: str, characteristics: List[str]) -> float:
        """Calculate a complexity score from 0.0 to 1.0."""
        score = 0.2  # Start with a base score to ensure non-zero

        # Base on description length (normalized)
        word_count = len(task_description.split())
        length_factor = min(word_count / 20.0, 0.5)  # Longer tasks tend to be more complex, cap at 0.5
        score += length_factor

        # Adjust based on characteristics
        if "complex" in characteristics or "architecture" in characteristics:
            score += 0.3
        if "security" in characteristics:
            score += 0.25
        if "algorithms" in characteristics:
            score += 0.25
        if "machine_learning" in characteristics:
            score += 0.3
        if "cloud_native" in characteristics:
            score += 0.25
        if "analysis" in characteristics:
            score += 0.1  # Analysis tasks are generally of medium complexity
        if "coding" in characteristics:
            score += 0.15  # Programming tasks have inherent complexity

        # Cap at 1.0
        return min(score, 1.0)

    def _estimate_token_count(self, task_description: str) -> int:
        """Estimate the number of tokens in the task."""
        # Rough estimation: 1 token ~ 4 characters or 1.3 words
        word_count = len(task_description.split())
        return int(word_count * 1.3)  # Approximate token count


class LLMSelector:
    """Selects the most appropriate LLM for a given task."""

    def __init__(self, available_providers: Dict[str, 'ProviderConfig']):
        """
        Initialize the LLM selector.

        Args:
            available_providers: Dictionary of available provider configs
        """
        self.available_providers = available_providers
        self.task_analyzer = TaskAnalyzer()

    def select_best_provider(self, task_description: str) -> Optional['ProviderConfig']:
        """
        Select the best provider for a given task.

        Args:
            task_description: Description of the task to be performed

        Returns:
            The best ProviderConfig for the task, or None if no providers available
        """
        if not self.available_providers:
            return None

        # Analyze the task
        task_analysis = self.task_analyzer.analyze(task_description)

        # Score each available provider for this task
        scored_providers = []
        for provider_name, provider_config in self.available_providers.items():
            score = self._score_provider_for_task(provider_config, task_analysis)
            scored_providers.append((score, provider_config))

        # Sort by score (descending) and return the best
        scored_providers.sort(key=lambda x: x[0], reverse=True)

        return scored_providers[0][1] if scored_providers else None

    def _score_provider_for_task(self, provider_config: 'ProviderConfig', task_analysis: TaskAnalysis) -> float:
        """
        Score a provider for a specific task.

        Args:
            provider_config: The provider to score
            task_analysis: The analysis of the task

        Returns:
            A score from 0.0 to 1.0 indicating suitability
        """
        score = 0.0

        # Different providers have different strengths
        # These weights are configurable in a real implementation
        provider_strengths = {
            'gpt-4': {'coding': 0.9, 'analysis': 0.9, 'general': 0.8, 'writing': 0.8},
            'gpt-4o': {'coding': 0.95, 'analysis': 0.9, 'general': 0.9, 'writing': 0.85},
            'gpt-3.5-turbo': {'coding': 0.7, 'analysis': 0.7, 'general': 0.8, 'writing': 0.75},
            'claude-3-5-sonnet-20241022': {'coding': 0.9, 'analysis': 0.95, 'general': 0.9, 'writing': 0.9, 'creative': 0.85},
            'claude-3-opus': {'coding': 0.85, 'analysis': 0.95, 'general': 0.95, 'writing': 0.95, 'creative': 0.9},
            'qwen-max': {'coding': 0.8, 'analysis': 0.75, 'general': 0.8, 'writing': 0.75, 'chinese': 0.95},
            'qwen-plus': {'coding': 0.75, 'analysis': 0.7, 'general': 0.75, 'writing': 0.7},
            'gemini-1.5-pro': {'coding': 0.85, 'analysis': 0.85, 'general': 0.85, 'writing': 0.8},
        }

        # Get the provider's strength for this task type
        model_strengths = provider_strengths.get(provider_config.model, {})
        task_type_strength = model_strengths.get(task_analysis.task_type.value, 0.5)

        # Adjust for task complexity
        complexity_adjustment = 1.0
        if task_analysis.complexity_score > 0.7 and provider_config.model in ['gpt-4o', 'claude-3-5-sonnet-20241022', 'claude-3-opus']:
            complexity_adjustment = 1.1  # Complex tasks benefit from stronger models
        elif task_analysis.complexity_score < 0.3 and provider_config.model not in ['gpt-3.5-turbo']:
            complexity_adjustment = 0.9  # Simple tasks don't need the most expensive models

        # Consider cost factor (simplified)
        cost_multiplier = 1.0
        if provider_config.model in ['claude-3-opus']:
            cost_multiplier = 0.9  # Higher cost, slightly lower score unless best fit
        elif provider_config.model in ['gpt-3.5-turbo']:
            cost_multiplier = 1.05  # Lower cost, slight boost

        # Combine all factors
        score = task_type_strength * complexity_adjustment * cost_multiplier

        # Apply small penalty for very complex tasks if the model isn't known for handling them well
        if task_analysis.complexity_score > 0.8 and task_type_strength < 0.7:
            score *= 0.8

        return min(score, 1.0)  # Cap at 1.0