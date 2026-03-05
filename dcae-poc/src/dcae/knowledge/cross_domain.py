"""Cross-domain recommendation system for identifying relationships across different knowledge domains."""

import asyncio
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import difflib
import re

from . import KnowledgeEntry, DomainType, DomainKnowledgeBase, KnowledgeFusionEngine


@dataclass
class Recommendation:
    """Represents a cross-domain recommendation."""
    id: str
    title: str
    description: str
    source_domains: List[DomainType]
    confidence: float  # 0.0 to 1.0
    explanation: str
    related_knowledge_ids: List[str]
    timestamp: datetime
    confidence_breakdown: Dict[str, float] = None  # Breakdown of confidence components
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.confidence_breakdown is None:
            self.confidence_breakdown = {}


@dataclass
class CrossDomainRelationship:
    """Represents a relationship between knowledge entries from different domains."""
    knowledge_ids: Tuple[str, str]  # IDs of related knowledge entries
    domain_pair: Tuple[DomainType, DomainType]
    relationship_type: str  # e.g., "influences", "correlates", "contradicts", "complements"
    strength: float  # 0.0 to 1.0
    description: str
    timestamp: datetime


class RelationshipIdentifier:
    """Identifies relationships between knowledge entries from different domains."""

    def __init__(self):
        """Initialize the relationship identifier."""
        pass

    def identify_relationships(
        self,
        knowledge_entries: List[KnowledgeEntry]
    ) -> List[CrossDomainRelationship]:
        """Identify potential relationships between knowledge entries from different domains.

        Args:
            knowledge_entries: List of knowledge entries to analyze

        Returns:
            List of identified cross-domain relationships
        """
        relationships = []
        domain_groups = defaultdict(list)

        # Group entries by domain
        for entry in knowledge_entries:
            domain_groups[entry.domain].append(entry)

        # Compare entries across different domains
        domain_list = list(domain_groups.keys())

        for i in range(len(domain_list)):
            for j in range(i + 1, len(domain_list)):
                domain_a = domain_list[i]
                domain_b = domain_list[j]

                entries_a = domain_groups[domain_a]
                entries_b = domain_groups[domain_b]

                # Find relationships between entries of different domains
                for entry_a in entries_a:
                    for entry_b in entries_b:
                        relationship = self._analyze_relationship(entry_a, entry_b)
                        if relationship:
                            relationships.append(relationship)

        return relationships

    def _analyze_relationship(
        self,
        entry_a: KnowledgeEntry,
        entry_b: KnowledgeEntry
    ) -> Optional[CrossDomainRelationship]:
        """Analyze potential relationship between two knowledge entries from different domains.

        Args:
            entry_a: First knowledge entry
            entry_b: Second knowledge entry

        Returns:
            Identified relationship or None if no significant relationship found
        """
        if entry_a.domain == entry_b.domain:
            return None  # Only analyze cross-domain relationships

        # Calculate semantic similarity between entries
        similarity = self._calculate_semantic_similarity(entry_a.content, entry_b.content)

        # Skip if similarity is too low
        if similarity < 0.3:
            return None

        # Identify relationship type based on content analysis
        relationship_type = self._identify_relationship_type(entry_a, entry_b)
        description = self._generate_relationship_description(entry_a, entry_b, relationship_type)

        return CrossDomainRelationship(
            knowledge_ids=(entry_a.id, entry_b.id),
            domain_pair=(entry_a.domain, entry_b.domain),
            relationship_type=relationship_type,
            strength=similarity,
            description=description,
            timestamp=datetime.now()
        )

    def _calculate_semantic_similarity(self, content_a: str, content_b: str) -> float:
        """Calculate semantic similarity between two content strings.

        Args:
            content_a: First content string
            content_b: Second content string

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use difflib for basic similarity calculation
        similarity = difflib.SequenceMatcher(None, content_a.lower(), content_b.lower()).ratio()

        # Enhance with keyword overlap
        keywords_a = set(re.findall(r'\b\w+\b', content_a.lower()))
        keywords_b = set(re.findall(r'\b\w+\b', content_b.lower()))

        if keywords_a and keywords_b:
            keyword_overlap = len(keywords_a.intersection(keywords_b)) / len(keywords_a.union(keywords_b))
            # Combine structural and keyword similarity
            combined_similarity = (similarity + keyword_overlap) / 2
            return min(combined_similarity, 1.0)

        return similarity

    def _identify_relationship_type(
        self,
        entry_a: KnowledgeEntry,
        entry_b: KnowledgeEntry
    ) -> str:
        """Identify the type of relationship between two entries.

        Args:
            entry_a: First knowledge entry
            entry_b: Second knowledge entry

        Returns:
            Relationship type as a string
        """
        content_a = entry_a.content.lower()
        content_b = entry_b.content.lower()

        # Look for specific patterns that indicate relationship types
        influences_indicators = [
            'depends on', 'relies on', 'affected by', 'impacts', 'affects',
            'requires', 'necessitates', 'driven by', 'motivated by'
        ]

        correlates_indicators = [
            'related to', 'connected to', 'associated with', 'tied to',
            'corresponds to', 'matches', 'aligns with', 'consistent with'
        ]

        contradicts_indicators = [
            'conflicts with', 'opposes', 'contradicts', 'opposite to',
            'against', 'disagrees with', 'incompatible with'
        ]

        complements_indicators = [
            'supports', 'enhances', 'supplements', 'adds to',
            'works with', 'goes with', 'completes', 'strengthens'
        ]

        all_content = content_a + " " + content_b

        # Check for influence relationships
        for indicator in influences_indicators:
            if indicator in all_content:
                return "influences"

        # Check for correlation relationships
        for indicator in correlates_indicators:
            if indicator in all_content:
                return "correlates"

        # Check for contradiction relationships
        for indicator in contradicts_indicators:
            if indicator in all_content:
                return "contradicts"

        # Check for complementary relationships
        for indicator in complements_indicators:
            if indicator in all_content:
                return "complements"

        # Default to generic relationship if none of the above apply
        return "related_to"

    def _generate_relationship_description(
        self,
        entry_a: KnowledgeEntry,
        entry_b: KnowledgeEntry,
        relationship_type: str
    ) -> str:
        """Generate a human-readable description of the relationship.

        Args:
            entry_a: First knowledge entry
            entry_b: Second knowledge entry
            relationship_type: Type of relationship identified

        Returns:
            Descriptive text explaining the relationship
        """
        domain_a_name = entry_a.domain.value.title()
        domain_b_name = entry_b.domain.value.title()

        if relationship_type == "influences":
            return f"The {domain_a_name} knowledge influences the {domain_b_name} knowledge based on semantic similarities."
        elif relationship_type == "correlates":
            return f"The {domain_a_name} and {domain_b_name} knowledge are correlated with each other."
        elif relationship_type == "contradicts":
            return f"There appears to be a contradiction between {domain_a_name} and {domain_b_name} knowledge."
        elif relationship_type == "complements":
            return f"The {domain_a_name} and {domain_b_name} knowledge complement each other."
        else:
            return f"The {domain_a_name} and {domain_b_name} knowledge are related to each other."


class CrossDomainRecommendationEngine:
    """Generates recommendations by analyzing relationships across different knowledge domains."""

    def __init__(self, knowledge_base: DomainKnowledgeBase):
        """Initialize the recommendation engine.

        Args:
            knowledge_base: The knowledge base to use for analysis
        """
        self.knowledge_base = knowledge_base
        self.relationship_identifier = RelationshipIdentifier()
        self.knowledge_fusion_engine = KnowledgeFusionEngine(knowledge_base)

    def generate_recommendations(
        self,
        context: str = "",
        target_domains: Optional[List[DomainType]] = None,
        min_relationship_strength: float = 0.4,
        max_recommendations: int = 10,
        min_confidence: float = 0.5
    ) -> List[Recommendation]:
        """Generate cross-domain recommendations based on current context.

        Args:
            context: Current development or analysis context
            target_domains: Specific domains to focus on (None for all)
            min_relationship_strength: Minimum strength for relationships to consider
            max_recommendations: Maximum number of recommendations to return
            min_confidence: Minimum confidence of knowledge entries to consider

        Returns:
            List of generated recommendations
        """
        import uuid

        # Get relevant knowledge entries across all domains
        all_knowledge = self.knowledge_base.get_knowledge(min_confidence=min_confidence, limit=None)

        # Filter by target domains if specified
        if target_domains:
            filtered_knowledge = [
                entry for entry in all_knowledge
                if entry.domain in target_domains
            ]
        else:
            filtered_knowledge = all_knowledge

        # Identify relationships between entries
        relationships = self.relationship_identifier.identify_relationships(filtered_knowledge)

        # Filter relationships by minimum strength
        strong_relationships = [
            rel for rel in relationships
            if rel.strength >= min_relationship_strength
        ]

        # Apply context relevance if context is provided
        if context:
            strong_relationships = self._filter_by_context_relevance(strong_relationships, context)

        recommendations = []

        # Generate recommendations from strong relationships
        for relationship in strong_relationships:
            # Create a recommendation based on the relationship
            recommendation = self._create_recommendation_from_relationship(
                relationship, context
            )

            if recommendation:
                recommendations.append(recommendation)

                # Stop if we've reached the maximum number of recommendations
                if len(recommendations) >= max_recommendations:
                    break

        # Sort recommendations by confidence
        recommendations.sort(key=lambda r: r.confidence, reverse=True)

        return recommendations[:max_recommendations]

    def _filter_by_context_relevance(
        self,
        relationships: List[CrossDomainRelationship],
        context: str
    ) -> List[CrossDomainRelationship]:
        """Filter relationships based on relevance to the given context.

        Args:
            relationships: List of relationships to filter
            context: Context to match against

        Returns:
            Filtered list of relationships
        """
        relevant_relationships = []
        context_lower = context.lower()

        for relationship in relationships:
            # Get the related knowledge entries
            entry_a = self.knowledge_base.get_knowledge(
                min_confidence=0.0
            )
            entry_a = next((e for e in entry_a if e.id == relationship.knowledge_ids[0]), None)

            entry_b = self.knowledge_base.get_knowledge(
                min_confidence=0.0
            )
            entry_b = next((e for e in entry_b if e.id == relationship.knowledge_ids[1]), None)

            if not entry_a or not entry_b:
                continue

            # Check if either entry is related to context
            entry_a_relevant = context_lower in entry_a.content.lower()
            entry_b_relevant = context_lower in entry_b.content.lower()

            # Also check for semantic similarity to context
            content_a_similarity = difflib.SequenceMatcher(None, context_lower, entry_a.content.lower()).ratio()
            content_b_similarity = difflib.SequenceMatcher(None, context_lower, entry_b.content.lower()).ratio()

            is_relevant = (
                entry_a_relevant or
                entry_b_relevant or
                content_a_similarity > 0.2 or
                content_b_similarity > 0.2
            )

            if is_relevant:
                relevant_relationships.append(relationship)

        return relevant_relationships

    def _create_recommendation_from_relationship(
        self,
        relationship: CrossDomainRelationship,
        context: str = ""
    ) -> Optional[Recommendation]:
        """Create a recommendation from a cross-domain relationship.

        Args:
            relationship: The identified relationship
            context: Current context to tailor the recommendation

        Returns:
            Generated recommendation or None if not suitable
        """
        import uuid

        # Get the related knowledge entries
        all_entries = self.knowledge_base.get_knowledge(min_confidence=0.0)
        entry_a = next((e for e in all_entries if e.id == relationship.knowledge_ids[0]), None)
        entry_b = next((e for e in all_entries if e.id == relationship.knowledge_ids[1]), None)

        if not entry_a or not entry_b:
            return None

        # Generate a title for the recommendation
        title = f"Cross-Domain Insight: {entry_a.domain.value.title()} and {entry_b.domain.value.title()}"

        # Generate a description based on the relationship
        description = f"""
        Based on analysis of knowledge from {entry_a.domain.value} and {entry_b.domain.value} domains,
        a significant relationship was identified ({relationship.relationship_type}) between these knowledge areas.

        {entry_a.domain.value.title()} knowledge: {entry_a.content[:100]}...
        {entry_b.domain.value.title()} knowledge: {entry_b.content[:100]}...
        """

        # Generate explanation for the recommendation
        explanation = f"""
        This recommendation highlights a connection between {entry_a.domain.value} and {entry_b.domain.value} domains.
        The relationship was identified based on semantic similarities and content analysis.
        This insight may be valuable when making decisions that span multiple knowledge areas.

        Relationship: {relationship.description}
        """

        # Calculate confidence based on relationship strength and knowledge confidence
        avg_confidence = (entry_a.confidence + entry_b.confidence + relationship.strength) / 3
        final_confidence = min(avg_confidence, 1.0)

        return Recommendation(
            id=str(uuid.uuid4()),
            title=title.strip(),
            description=description.strip(),
            source_domains=[entry_a.domain, entry_b.domain],
            confidence=final_confidence,
            explanation=explanation.strip(),
            related_knowledge_ids=list(relationship.knowledge_ids),
            timestamp=datetime.now()
        )

    def get_recommendation_explanation(
        self,
        recommendation: Recommendation
    ) -> str:
        """Generate a detailed explanation for why a recommendation was made.

        Args:
            recommendation: The recommendation to explain

        Returns:
            Detailed explanation of the recommendation
        """
        # Get the related knowledge entries for more detailed explanation
        all_entries = self.knowledge_base.get_knowledge(min_confidence=0.0)

        # Find the knowledge entries associated with this recommendation
        related_entries = [
            entry for entry in all_entries
            if entry.id in recommendation.related_knowledge_ids
        ]

        # Build detailed explanation
        explanation = f"""
Cross-Domain Recommendation Explanation
=======================================
Title: {recommendation.title}

DOMAIN INTERACTIONS:
This recommendation spans the following domains: {[domain.value.title() for domain in recommendation.source_domains]}

The system identified meaningful connections between knowledge from different specialized areas,
allowing for insights that wouldn't be possible when examining domains in isolation.
"""
        # Add specific information about each related knowledge entry
        for i, entry in enumerate(related_entries, 1):
            explanation += f"""

RELATED KNOWLEDGE ENTRY #{i}:
- Domain: {entry.domain.value.title()}
- Content: {entry.content[:200]}{'...' if len(entry.content) > 200 else ''}
- Source: {entry.source}
- Entry Confidence: {entry.confidence:.2f}
- Last Updated: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""

        explanation += f"""

REASONING BEHIND RECOMMENDATION:
{recommendation.explanation}

WHY CROSS-DOMAIN INTELLIGENCE MATTERS:
Cross-domain analysis allows for identification of patterns and relationships that span
different areas of expertise (technical, business, regulatory, etc.). This holistic view
can reveal opportunities or risks that would be missed when analyzing domains independently.

RECOMMENDED ACTION:
Consider this insight when making decisions that affect multiple aspects of your project,
as it represents knowledge from interconnected domains that could impact various areas.
"""

        return explanation.strip()

    def get_comprehensive_explanation(
        self,
        recommendation: Recommendation,
        include_raw_relationships: bool = True
    ) -> Dict[str, Any]:
        """Generate a comprehensive explanation including technical details.

        Args:
            recommendation: The recommendation to explain
            include_raw_relationships: Whether to include raw relationship data

        Returns:
            Dictionary containing comprehensive explanation details
        """
        all_entries = self.knowledge_base.get_knowledge(min_confidence=0.0)
        related_entries = [
            entry for entry in all_entries
            if entry.id in recommendation.related_knowledge_ids
        ]

        # Analyze the relationships that led to this recommendation
        relationships = self.relationship_identifier.identify_relationships(related_entries)
        relevant_relationships = [
            r for r in relationships
            if set(r.knowledge_ids) == set(recommendation.related_knowledge_ids)
        ]

        result = {
            'recommendation_id': recommendation.id,
            'title': recommendation.title,
            'summary': recommendation.description,
            'confidence_details': {
                'overall': recommendation.confidence,
            },
            'domain_interactions': [domain.value for domain in recommendation.source_domains],
            'related_knowledge': [
                {
                    'id': entry.id,
                    'domain': entry.domain.value,
                    'content_preview': entry.content[:200] + ('...' if len(entry.content) > 200 else ''),
                    'source': entry.source,
                    'confidence': entry.confidence,
                    'timestamp': entry.timestamp.isoformat()
                }
                for entry in related_entries
            ],
            'reasoning': recommendation.explanation,
            'recommendation': 'Consider this cross-domain insight when making decisions affecting multiple knowledge areas.'
        }

        if include_raw_relationships and relevant_relationships:
            result['identified_relationships'] = [
                {
                    'knowledge_ids': list(rel.knowledge_ids),
                    'domains': [rel.domain_pair[0].value, rel.domain_pair[1].value],
                    'type': rel.relationship_type,
                    'strength': rel.strength,
                    'description': rel.description,
                    'timestamp': rel.timestamp.isoformat()
                }
                for rel in relevant_relationships
            ]

        return result

    def analyze_multi_domain_patterns(
        self,
        domain_types: List[DomainType],
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze patterns across multiple domains within a specific time window.

        Args:
            domain_types: List of domain types to analyze
            time_window_days: Number of days to look back for pattern analysis

        Returns:
            Dictionary containing pattern analysis results
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=time_window_days)

        # Get knowledge from specified domains
        all_knowledge = self.knowledge_base.get_knowledge(min_confidence=0.5)
        domain_knowledge = [
            entry for entry in all_knowledge
            if entry.domain in domain_types and entry.timestamp >= cutoff_date
        ]

        # Identify relationships among the selected domain knowledge
        relationships = self.relationship_identifier.identify_relationships(domain_knowledge)

        # Analyze patterns in the relationships
        pattern_analysis = {
            'total_relationships': len(relationships),
            'domain_pairs': defaultdict(int),
            'relationship_types': defaultdict(int),
            'average_strength': sum(rel.strength for rel in relationships) / len(relationships) if relationships else 0.0,
            'time_window': time_window_days,
            'analyzed_domains': [dt.value for dt in domain_types]
        }

        for rel in relationships:
            pair = tuple(sorted([rel.domain_pair[0].value, rel.domain_pair[1].value]))
            pattern_analysis['domain_pairs'][pair] += 1
            pattern_analysis['relationship_types'][rel.relationship_type] += 1

        return dict(pattern_analysis)