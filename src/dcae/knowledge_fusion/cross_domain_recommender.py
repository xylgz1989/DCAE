"""Module for providing cross-domain recommendations based on context."""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import heapq
from .knowledge_fuser import KnowledgeItem, KnowledgeSourceType
from .domain_knowledge_manager import DomainKnowledgeManager, DomainType


class RecommendationType(Enum):
    """Types of recommendations."""
    TECHNIQUE = "technique"
    PATTERN = "pattern"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


@dataclass
class Recommendation:
    """Represents a cross-domain recommendation."""
    id: str
    title: str
    description: str
    recommendation_type: RecommendationType
    source_domains: List[DomainType]
    confidence_score: float
    knowledge_base: List[KnowledgeItem]
    implementation_notes: str = ""
    tradeoffs: List[str] = None
    alternatives: List[str] = None

    def __post_init__(self):
        if self.tradeoffs is None:
            self.tradeoffs = []
        if self.alternatives is None:
            self.alternatives = []


@dataclass
class Context:
    """Represents the current development context for recommendations."""
    project_type: str
    domain_types: List[DomainType]
    problem_description: str
    current_stage: str
    constraints: List[str]
    requirements: List[str]
    technology_stack: List[str]
    team_expertise: List[str]
    performance_requirements: Dict[str, Any]


class CrossDomainRecommender:
    """Provides cross-domain recommendations based on context."""

    def __init__(self, domain_manager: DomainKnowledgeManager):
        """
        Initialize the cross-domain recommender.

        Args:
            domain_manager: Domain knowledge manager to use for recommendations
        """
        self.domain_manager = domain_manager
        self.knowledge_cache: Dict[str, List[KnowledgeItem]] = {}
        self.recommendation_templates: Dict[RecommendationType, List[Dict[str, Any]]] = self._initialize_templates()

    def _initialize_templates(self) -> Dict[RecommendationType, List[Dict[str, Any]]]:
        """Initialize recommendation templates."""
        return {
            RecommendationType.TECHNIQUE: [
                {
                    "title": "Design Pattern Recommendation",
                    "description": "Based on cross-domain analysis, recommend proven patterns",
                    "confidence_multiplier": 1.0
                }
            ],
            RecommendationType.IMPLEMENTATION: [
                {
                    "title": "Implementation Strategy",
                    "description": "Cross-domain approach to implementation",
                    "confidence_multiplier": 1.0
                }
            ],
            RecommendationType.SECURITY: [
                {
                    "title": "Security Best Practice",
                    "description": "Security measures learned from multiple domains",
                    "confidence_multiplier": 1.2
                }
            ],
            RecommendationType.TESTING: [
                {
                    "title": "Testing Strategy",
                    "description": "Testing approaches from similar problems in other domains",
                    "confidence_multiplier": 1.1
                }
            ]
        }

    def generate_recommendations(self, context: Context, max_recommendations: int = 5) -> List[Recommendation]:
        """
        Generate cross-domain recommendations based on the provided context.

        Args:
            context: Current development context
            max_recommendations: Maximum number of recommendations to return

        Returns:
            List of cross-domain recommendations
        """
        recommendations = []

        # Get relevant knowledge from all domains in context
        for domain in context.domain_types:
            domain_knowledge = self.domain_manager.get_approved_knowledge_by_domain(domain)

            # For each piece of knowledge, evaluate its relevance to the context
            for entry in domain_knowledge:
                score = self._calculate_relevance_score(entry, context)
                if score > 0.5:  # Only consider high-relevance items
                    rec = self._create_recommendation_from_knowledge(entry, context, score)
                    if rec:
                        recommendations.append(rec)

        # Get cross-domain knowledge by searching for relevant concepts
        relevant_concepts = self._extract_relevant_concepts(context)
        for concept in relevant_concepts:
            cross_domain_items = self.domain_manager.search_knowledge(concept)
            for item in cross_domain_items:
                if item.domain not in context.domain_types:
                    score = self._calculate_cross_domain_relevance_score(item, context)
                    if score > 0.4:
                        rec = self._create_recommendation_from_cross_domain_knowledge(item, context, score)
                        if rec:
                            recommendations.append(rec)

        # Sort recommendations by confidence score and return top ones
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return recommendations[:max_recommendations]

    def _calculate_relevance_score(self, entry, context: Context) -> float:
        """Calculate how relevant an entry is to the current context."""
        score = 0.0

        # Check domain match
        if entry.domain in context.domain_types:
            score += 0.2

        # Check content relevance
        content_lower = entry.knowledge_item.content.lower()
        context_keywords = self._extract_context_keywords(context)

        for keyword in context_keywords:
            if keyword.lower() in content_lower:
                score += 0.1

        # Check tag relevance
        for tag in entry.knowledge_item.tags:
            if tag.lower() in context_keywords:
                score += 0.15

        # Check constraint match
        for constraint in context.constraints:
            if constraint.lower() in content_lower:
                score += 0.1

        # Normalize score
        return min(score, 1.0)

    def _calculate_cross_domain_relevance_score(self, entry, context: Context) -> float:
        """Calculate relevance for cross-domain items."""
        score = self._calculate_relevance_score(entry, context)

        # Add bonus for cross-domain relevance
        if entry.domain not in context.domain_types:
            score *= 1.3  # Boost cross-domain relevance

        return min(score, 1.0)

    def _extract_context_keywords(self, context: Context) -> List[str]:
        """Extract keywords from context for matching."""
        keywords = []

        # Add project type, requirements, constraints
        keywords.extend(context.project_type.split())
        keywords.extend(context.problem_description.split())
        keywords.extend(context.requirements)
        keywords.extend(context.constraints)
        keywords.extend(context.technology_stack)

        # Remove empty strings and convert to lower case
        keywords = [kw.lower().strip() for kw in keywords if kw.strip()]
        return keywords

    def _extract_relevant_concepts(self, context: Context) -> List[str]:
        """Extract concepts that might yield cross-domain insights."""
        concepts = []

        # Identify common concepts that appear across domains
        if "security" in context.problem_description.lower() or "secure" in context.problem_description.lower():
            concepts.append("security")
            concepts.append("authentication")
            concepts.append("authorization")
            concepts.append("encryption")

        if "performance" in context.problem_description.lower() or "fast" in context.problem_description.lower():
            concepts.append("performance")
            concepts.append("optimization")
            concepts.append("scalability")

        if "data" in context.problem_description.lower():
            concepts.append("data management")
            concepts.append("storage")
            concepts.append("processing")

        # Add technology stack items
        concepts.extend(context.technology_stack)

        # Add constraint-related concepts
        for constraint in context.constraints:
            if "memory" in constraint.lower():
                concepts.append("memory management")
                concepts.append("efficiency")
            elif "time" in constraint.lower():
                concepts.append("efficiency")
                concepts.append("performance")

        return list(set(concepts))  # Remove duplicates

    def _create_recommendation_from_knowledge(self, entry, context: Context, score: float) -> Optional[Recommendation]:
        """Create a recommendation from domain knowledge."""
        try:
            # Determine recommendation type based on tags or content
            rec_type = self._infer_recommendation_type(entry.knowledge_item)

            # Create recommendation
            rec_id = f"rec_{entry.id}"
            title = f"Recommendation from {entry.domain.value.title()} Domain"
            description = entry.knowledge_item.content[:200] + "..." if len(entry.knowledge_item.content) > 200 else entry.knowledge_item.content

            return Recommendation(
                id=rec_id,
                title=title,
                description=description,
                recommendation_type=rec_type,
                source_domains=[entry.domain],
                confidence_score=score,
                knowledge_base=[entry.knowledge_item]
            )
        except Exception:
            return None

    def _create_recommendation_from_cross_domain_knowledge(self, entry, context: Context, score: float) -> Optional[Recommendation]:
        """Create a recommendation from cross-domain knowledge."""
        try:
            # Determine recommendation type based on tags or content
            rec_type = self._infer_recommendation_type(entry.knowledge_item)

            # Create recommendation
            rec_id = f"cross_rec_{entry.id}"
            title = f"Cross-Domain Insight from {entry.domain.value.title()} Domain"
            description = f"Applying knowledge from {entry.domain.value.title()} domain: {entry.knowledge_item.content[:200]}..."

            return Recommendation(
                id=rec_id,
                title=title,
                description=description,
                recommendation_type=rec_type,
                source_domains=[entry.domain],
                confidence_score=score,
                knowledge_base=[entry.knowledge_item],
                implementation_notes=f"This recommendation draws from {entry.domain.value} domain expertise.",
                tradeoffs=["May require adaptation for current domain"],
                alternatives=[]
            )
        except Exception:
            return None

    def _infer_recommendation_type(self, knowledge_item: KnowledgeItem) -> RecommendationType:
        """Infer recommendation type from knowledge item."""
        content_lower = knowledge_item.content.lower()
        tags_lower = [tag.lower() for tag in knowledge_item.tags]

        # Check tags first
        if 'security' in tags_lower or 'auth' in tags_lower:
            return RecommendationType.SECURITY
        elif 'testing' in tags_lower or 'test' in tags_lower:
            return RecommendationType.TESTING
        elif 'pattern' in tags_lower:
            return RecommendationType.PATTERN
        elif 'architecture' in tags_lower:
            return RecommendationType.ARCHITECTURE

        # Check content
        if 'security' in content_lower or 'auth' in content_lower or 'encrypt' in content_lower:
            return RecommendationType.SECURITY
        elif 'test' in content_lower or 'unit' in content_lower:
            return RecommendationType.TESTING
        elif 'pattern' in content_lower or 'design' in content_lower:
            return RecommendationType.PATTERN
        elif 'architecture' in content_lower or 'structure' in content_lower:
            return RecommendationType.ARCHITECTURE
        elif 'implement' in content_lower:
            return RecommendationType.IMPLEMENTATION
        else:
            return RecommendationType.TECHNIQUE

    def get_recommendation_feedback(self, recommendation_id: str, positive: bool = True, notes: str = "") -> bool:
        """
        Record feedback on a recommendation to improve future suggestions.

        Args:
            recommendation_id: ID of the recommendation
            positive: Whether the feedback is positive or negative
            notes: Additional feedback notes

        Returns:
            True if feedback was recorded successfully
        """
        # In a real implementation, this would update a feedback system
        # For now, we'll just acknowledge the feedback
        print(f"Feedback recorded for recommendation {recommendation_id}: {'positive' if positive else 'negative'} - {notes}")
        return True

    def personalize_recommendations(self, context: Context, user_profile: Dict[str, Any]) -> List[Recommendation]:
        """
        Generate personalized recommendations based on user profile.

        Args:
            context: Current development context
            user_profile: User profile with preferences and expertise

        Returns:
            Personalized list of recommendations
        """
        recommendations = self.generate_recommendations(context)

        # Adjust scores based on user profile
        for rec in recommendations:
            # Boost recommendations that match user expertise
            if user_profile.get('expertise_area') in rec.title.lower():
                rec.confidence_score *= 1.1

            # Reduce recommendations for areas user indicated low confidence in
            low_confidence_areas = user_profile.get('low_confidence_areas', [])
            if any(area.lower() in rec.title.lower() for area in low_confidence_areas):
                rec.confidence_score *= 0.8

            # Boost recommendations for preferred technologies
            preferred_tech = user_profile.get('preferred_technologies', [])
            for tech in preferred_tech:
                if tech.lower() in rec.description.lower():
                    rec.confidence_score *= 1.1

        # Re-sort after adjustments
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        return recommendations

    def explain_recommendation_reasoning(self, recommendation: Recommendation) -> str:
        """
        Explain why a particular recommendation was made.

        Args:
            recommendation: Recommendation to explain

        Returns:
            Explanation of the reasoning behind the recommendation
        """
        explanation = f"The recommendation '{recommendation.title}' was made because:\n"
        explanation += f"1. It comes from the {recommendation.source_domains[0].value} domain, which has proven approaches to similar problems.\n"
        explanation += f"2. The confidence score of {recommendation.confidence_score:.2f} indicates strong relevance.\n"
        explanation += f"3. The technique/pattern has been successfully applied in contexts involving {', '.join(recommendation.knowledge_base[0].tags) if recommendation.knowledge_base else 'various areas'}.\n"

        if recommendation.tradeoffs:
            explanation += f"4. Consider these tradeoffs: {', '.join(recommendation.tradeoffs)}.\n"

        return explanation