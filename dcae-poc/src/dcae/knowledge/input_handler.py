"""Input handler for domain-specific knowledge."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from . import DomainKnowledgeBase, DomainType, KnowledgeEntry


class DomainKnowledgeInputHandler:
    """Handles input of domain-specific knowledge from various sources."""

    def __init__(self, knowledge_base: DomainKnowledgeBase):
        """Initialize the input handler.

        Args:
            knowledge_base: The knowledge base to store knowledge in
        """
        self.knowledge_base = knowledge_base

    def add_manual_knowledge(
        self,
        domain: DomainType,
        content: str,
        source: str = "manual_input",
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add knowledge manually.

        Args:
            domain: The domain type
            content: The knowledge content
            source: Source of the knowledge
            confidence: Confidence level (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            ID of the added knowledge entry
        """
        return self.knowledge_base.add_knowledge(
            domain=domain,
            content=content,
            source=source,
            confidence=confidence,
            metadata=metadata
        )

    def import_from_file(
        self,
        file_path: Union[str, Path],
        domain: DomainType,
        source: Optional[str] = None,
        confidence: float = 0.7
    ) -> int:
        """Import knowledge from a structured file.

        Supported formats: JSON, YAML (if available)

        Args:
            file_path: Path to the knowledge file
            domain: The domain type
            source: Source identifier (defaults to filename)
            confidence: Default confidence level

        Returns:
            Number of entries imported
        """
        import yaml

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {file_path}")

        # Determine source if not provided
        if source is None:
            source = f"file:{file_path.name}"

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.json']:
                data = json.load(f)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                # Assume plain text - treat as single knowledge entry
                content = f.read()
                self.knowledge_base.add_knowledge(
                    domain=domain,
                    content=content,
                    source=source,
                    confidence=confidence
                )
                return 1

        # Process structured data
        count = 0

        if isinstance(data, list):
            # Multiple entries as a list
            for entry in data:
                if isinstance(entry, dict):
                    content = entry.get('content', '')
                    entry_source = entry.get('source', source)
                    entry_confidence = entry.get('confidence', confidence)
                    entry_metadata = entry.get('metadata', {})

                    if content:
                        self.knowledge_base.add_knowledge(
                            domain=domain,
                            content=content,
                            source=entry_source,
                            confidence=entry_confidence,
                            metadata=entry_metadata
                        )
                        count += 1
        elif isinstance(data, dict):
            # Single entry or entries by key
            if 'content' in data:
                # Single entry
                content = data.get('content', '')
                entry_source = data.get('source', source)
                entry_confidence = data.get('confidence', confidence)
                entry_metadata = data.get('metadata', {})

                if content:
                    self.knowledge_base.add_knowledge(
                        domain=domain,
                        content=content,
                        source=entry_source,
                        confidence=entry_confidence,
                        metadata=entry_metadata
                    )
                    count += 1
            else:
                # Multiple entries by key
                for key, entry in data.items():
                    if isinstance(entry, dict) and 'content' in entry:
                        content = entry['content']
                        entry_source = entry.get('source', f"{source}:{key}")
                        entry_confidence = entry.get('confidence', confidence)
                        entry_metadata = entry.get('metadata', {})

                        if content:
                            self.knowledge_base.add_knowledge(
                                domain=domain,
                                content=content,
                                source=entry_source,
                                confidence=entry_confidence,
                                metadata=entry_metadata
                            )
                            count += 1

        return count

    def import_from_text(
        self,
        text: str,
        domain: DomainType,
        source: str = "text_import",
        confidence: float = 0.6
    ) -> int:
        """Import knowledge from raw text by splitting into logical chunks.

        Args:
            text: Raw text to split into knowledge chunks
            domain: The domain type
            source: Source identifier
            confidence: Default confidence level

        Returns:
            Number of entries imported
        """
        # Simple heuristic: split by paragraphs or sentences
        # This could be enhanced with NLP techniques for better chunking

        # Split text into logical segments (paragraphs or sentence groups)
        segments = []

        # First, try to split by paragraphs
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If paragraph is too long, try to split by sentences
            if len(para) > 500:  # Rough threshold
                sentences = para.split('. ')
                current_segment = ""

                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue

                    if len(current_segment + sent) < 500:
                        current_segment += sent + ". "
                    else:
                        if current_segment:
                            segments.append(current_segment.strip())
                        current_segment = sent + ". "

                if current_segment:
                    segments.append(current_segment.strip())
            else:
                segments.append(para)

        # Add each segment as a knowledge entry
        count = 0
        for segment in segments:
            if segment.strip():
                self.knowledge_base.add_knowledge(
                    domain=domain,
                    content=segment,
                    source=source,
                    confidence=confidence
                )
                count += 1

        return count

    def validate_knowledge_entry(
        self,
        content: str,
        domain: DomainType,
        expected_patterns: Optional[list] = None
    ) -> tuple[bool, str]:
        """Validate a knowledge entry before adding.

        Args:
            content: The knowledge content to validate
            domain: The domain type
            expected_patterns: List of regex patterns to check for

        Returns:
            Tuple of (is_valid, error_message)
        """
        import re

        # Basic checks
        if not content or not content.strip():
            return False, "Content cannot be empty"

        if len(content.strip()) < 10:
            return False, "Content too short (< 10 characters)"

        if len(content) > 10000:  # Arbitrary large limit
            return False, "Content too long (> 10,000 characters)"

        # Domain-specific validation
        if domain == DomainType.REGULATORY:
            # Regulatory knowledge should probably contain legal terms
            regulatory_terms = ['requirement', 'must', 'shall', 'should', 'compliance', 'standard', 'policy', 'procedure']
            if not any(term.lower() in content.lower() for term in regulatory_terms):
                return False, "Regulatory content should contain compliance-related terms"

        # Check against expected patterns if provided
        if expected_patterns:
            for pattern in expected_patterns:
                if not re.search(pattern, content, re.IGNORECASE):
                    return False, f"Missing expected pattern: {pattern}"

        return True, "Valid"