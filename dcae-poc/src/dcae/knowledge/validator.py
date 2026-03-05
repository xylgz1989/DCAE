"""Validation module for domain-specific knowledge."""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from . import KnowledgeEntry, DomainType


class KnowledgeValidator:
    """Validates domain-specific knowledge for accuracy and relevance."""

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate_entry(self, entry: KnowledgeEntry) -> Tuple[bool, List[str]]:
        """Validate a single knowledge entry.

        Args:
            entry: The knowledge entry to validate

        Returns:
            Tuple of (is_valid, list_of_validation_errors)
        """
        errors = []

        # Validate basic properties
        if not entry.id:
            errors.append("Entry ID is required")

        if not entry.content or not entry.content.strip():
            errors.append("Content is required and cannot be empty")

        if len(entry.content.strip()) < 10:
            errors.append("Content too short (minimum 10 characters)")

        if len(entry.content) > 10000:
            errors.append("Content too long (maximum 10,000 characters)")

        if entry.confidence < 0.0 or entry.confidence > 1.0:
            errors.append("Confidence must be between 0.0 and 1.0")

        if not entry.source or not entry.source.strip():
            errors.append("Source is required")

        if not entry.timestamp:
            errors.append("Timestamp is required")

        # Domain-specific validations
        if entry.domain == DomainType.TECHNICAL:
            self._validate_technical_knowledge(entry, errors)
        elif entry.domain == DomainType.BUSINESS:
            self._validate_business_knowledge(entry, errors)
        elif entry.domain == DomainType.REGULATORY:
            self._validate_regulatory_knowledge(entry, errors)
        elif entry.domain == DomainType.DOMAIN_EXPERTISE:
            self._validate_expertise_knowledge(entry, errors)

        # Check for consistency in metadata
        if entry.metadata:
            self._validate_metadata(entry, errors)

        return len(errors) == 0, errors

    def _validate_technical_knowledge(self, entry: KnowledgeEntry, errors: List[str]):
        """Validate technical knowledge."""
        # For technical domain, just ensure it's substantive
        if len(entry.content) < 20:
            errors.append("Technical knowledge should be more detailed (minimum 20 characters)")

    def _validate_business_knowledge(self, entry: KnowledgeEntry, errors: List[str]):
        """Validate business knowledge."""
        # Business content should have some business terms
        business_indicators = [
            'revenue', 'profit', 'margin', 'customer', 'market', 'stakeholder',
            'ROI', 'KPI', 'metric', 'objective', 'strategy', 'process',
            'workflow', 'efficiency', 'cost', 'investment', 'opportunity'
        ]

        content_lower = entry.content.lower()
        if not any(indicator in content_lower for indicator in business_indicators):
            errors.append("Business knowledge should contain business terminology")

    def _validate_regulatory_knowledge(self, entry: KnowledgeEntry, errors: List[str]):
        """Validate regulatory knowledge."""
        # Regulatory content should have compliance terms
        regulatory_indicators = [
            'requirement', 'compliance', 'standard', 'regulation', 'policy',
            'procedure', 'must', 'shall', 'should', 'certification', 'audit',
            'control', 'governance', 'risk', 'approval', 'authorization'
        ]

        content_lower = entry.content.lower()
        if not any(indicator in content_lower for indicator in regulatory_indicators):
            errors.append("Regulatory knowledge should contain compliance-related terminology")

    def _validate_expertise_knowledge(self, entry: KnowledgeEntry, errors: List[str]):
        """Validate domain expertise knowledge."""
        # Expertise content should be substantial
        if len(entry.content) < 50:
            errors.append("Domain expertise knowledge should be more detailed (minimum 50 characters)")

    def _validate_metadata(self, entry: KnowledgeEntry, errors: List[str]):
        """Validate metadata."""
        if 'expiry_date' in entry.metadata:
            try:
                expiry = datetime.fromisoformat(str(entry.metadata['expiry_date']))
                if expiry < datetime.now():
                    errors.append("Knowledge entry has expired")
            except ValueError:
                errors.append("Invalid expiry date format in metadata")

        if 'last_verified' in entry.metadata:
            try:
                last_verified = datetime.fromisoformat(str(entry.metadata['last_verified']))
                # Check if verification is too old (arbitrary 1 year)
                if (datetime.now() - last_verified).days > 365:
                    errors.append("Knowledge entry not verified in over a year")
            except ValueError:
                errors.append("Invalid last_verified date format in metadata")

    def assess_accuracy(
        self,
        content: str,
        source_reputation: float = 0.5,
        cross_reference_sources: Optional[List[str]] = None
    ) -> float:
        """Assess the accuracy of knowledge content.

        Args:
            content: The knowledge content
            source_reputation: Reputation of the source (0.0 to 1.0)
            cross_reference_sources: Other sources to cross-reference

        Returns:
            Accuracy score (0.0 to 1.0)
        """
        # Simple heuristics for accuracy assessment
        score = source_reputation

        # Increase score for well-structured content
        if len(content) > 100:  # Longer content tends to be more detailed
            score += 0.1
        if '?' not in content:  # Factual statements rather than questions
            score += 0.1
        if 'example' in content.lower() or 'sample' in content.lower():  # Examples indicate good practice
            score += 0.1

        # Normalize score to 0-1 range
        score = min(max(score, 0.0), 1.0)

        return score

    def detect_outdated_information(self, entry: KnowledgeEntry) -> bool:
        """Detect if knowledge entry might be outdated.

        Args:
            entry: The knowledge entry to check

        Returns:
            True if potentially outdated
        """
        # Check if there's an expiry date that has passed
        if 'expiry_date' in entry.metadata:
            try:
                expiry = datetime.fromisoformat(str(entry.metadata['expiry_date']))
                if expiry < datetime.now():
                    return True
            except ValueError:
                pass  # Invalid date format

        # Check for temporal indicators that might suggest outdated info
        content_lower = entry.content.lower()
        temporal_indicators = [
            'as of', 'current as of', 'updated', 'latest version',
            'recently', 'currently', 'this year', 'this quarter'
        ]

        # If the entry mentions specific dates but no expiry is set, it might be outdated
        import re
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}/\d{2}/\d{2}',  # MM/DD/YY
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                # Found a date in the content - could be outdated
                return True

        return False

    def cross_validate(
        self,
        content: str,
        comparison_sources: List[str]
    ) -> Dict[str, Any]:
        """Cross-validate knowledge against other sources.

        Args:
            content: The knowledge content to validate
            comparison_sources: List of sources to compare against

        Returns:
            Validation results
        """
        results = {
            'match_score': 0.0,
            'conflicting_info': [],
            'supporting_evidence': [],
            'confidence_adjustment': 0.0
        }

        # Simple text similarity comparison
        import difflib

        total_similarity = 0.0
        match_count = 0

        for source in comparison_sources:
            similarity = difflib.SequenceMatcher(None, content.lower(), source.lower()).ratio()
            if similarity > 0.7:  # Significant match
                results['supporting_evidence'].append({
                    'source_content': source[:100] + "..." if len(source) > 100 else source,
                    'similarity': similarity
                })
                total_similarity += similarity
                match_count += 1
            elif similarity < 0.3:  # Potential conflict
                results['conflicting_info'].append({
                    'source_content': source[:100] + "..." if len(source) > 100 else source,
                    'similarity': similarity
                })

        if match_count > 0:
            results['match_score'] = total_similarity / match_count
            # Increase confidence if well-supported
            results['confidence_adjustment'] = min(results['match_score'] * 0.2, 0.3)
        else:
            # Decrease confidence if no supporting evidence
            results['confidence_adjustment'] = -0.2

        return results