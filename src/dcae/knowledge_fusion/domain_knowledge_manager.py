"""Module for managing domain-specific knowledge input and retrieval."""
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from datetime import datetime
from .knowledge_fuser import KnowledgeItem, KnowledgeSourceType


class DomainType(Enum):
    """Types of domains for knowledge organization."""
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    ECOMMERCE = "ecommerce"
    EDUCATION = "education"
    GOVERNMENT = "government"
    MANUFACTURING = "manufacturing"
    TECHNOLOGY = "technology"
    OTHER = "other"


@dataclass
class DomainKnowledgeEntry:
    """Represents a domain-specific knowledge entry."""
    id: str
    domain: DomainType
    knowledge_item: KnowledgeItem
    created_at: str
    updated_at: str
    version: str = "1.0"
    approved: bool = True
    contributor: str = "system"


class DomainKnowledgeManager:
    """Manages domain-specific knowledge for system reference."""

    def __init__(self):
        """Initialize the domain knowledge manager."""
        self.domain_knowledge: Dict[str, DomainKnowledgeEntry] = {}
        self.domain_indices: Dict[DomainType, Set[str]] = {
            domain: set() for domain in DomainType
        }
        self.tag_indices: Dict[str, Set[str]] = {}
        self.contributor_indices: Dict[str, Set[str]] = {}

    def add_domain_knowledge(
        self,
        domain: DomainType,
        content: str,
        tags: List[str] = None,
        contributor: str = "system",
        metadata: Dict[str, Any] = None,
        approved: bool = True
    ) -> str:
        """
        Add domain-specific knowledge to the system.

        Args:
            domain: Domain category for the knowledge
            content: Knowledge content
            tags: Tags associated with the knowledge
            contributor: Entity contributing the knowledge
            metadata: Additional metadata
            approved: Whether the knowledge is approved for use

        Returns:
            ID of the created knowledge entry
        """
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}

        # Generate unique ID based on content and domain
        content_hash = hashlib.sha256(f"{domain.value}:{content}".encode()).hexdigest()
        entry_id = f"dk_{content_hash[:12]}"

        # Create knowledge item
        knowledge_item = KnowledgeItem(
            id=entry_id,
            source_type=KnowledgeSourceType.DOMAIN,
            content=content,
            tags=tags,
            metadata=metadata
        )

        # Create domain entry
        current_time = datetime.now().isoformat()
        entry = DomainKnowledgeEntry(
            id=entry_id,
            domain=domain,
            knowledge_item=knowledge_item,
            created_at=current_time,
            updated_at=current_time,
            approved=approved,
            contributor=contributor
        )

        # Store the entry
        self.domain_knowledge[entry_id] = entry
        self.domain_indices[domain].add(entry_id)

        # Update tag indices
        for tag in tags:
            if tag not in self.tag_indices:
                self.tag_indices[tag] = set()
            self.tag_indices[tag].add(entry_id)

        # Update contributor indices
        if contributor not in self.contributor_indices:
            self.contributor_indices[contributor] = set()
        self.contributor_indices[contributor].add(entry_id)

        return entry_id

    def get_knowledge_by_domain(self, domain: DomainType) -> List[DomainKnowledgeEntry]:
        """
        Get all knowledge entries for a specific domain.

        Args:
            domain: Domain to retrieve knowledge for

        Returns:
            List of domain knowledge entries
        """
        entry_ids = self.domain_indices.get(domain, set())
        return [
            self.domain_knowledge[entry_id]
            for entry_id in entry_ids
            if entry_id in self.domain_knowledge
        ]

    def get_knowledge_by_tag(self, tag: str) -> List[DomainKnowledgeEntry]:
        """
        Get knowledge entries by tag.

        Args:
            tag: Tag to search for

        Returns:
            List of domain knowledge entries with the tag
        """
        entry_ids = self.tag_indices.get(tag, set())
        return [
            self.domain_knowledge[entry_id]
            for entry_id in entry_ids
            if entry_id in self.domain_knowledge
        ]

    def get_knowledge_by_contributor(self, contributor: str) -> List[DomainKnowledgeEntry]:
        """
        Get knowledge entries by contributor.

        Args:
            contributor: Contributor to search for

        Returns:
            List of domain knowledge entries by contributor
        """
        entry_ids = self.contributor_indices.get(contributor, set())
        return [
            self.domain_knowledge[entry_id]
            for entry_id in entry_ids
            if entry_id in self.domain_knowledge
        ]

    def get_knowledge_by_id(self, entry_id: str) -> Optional[DomainKnowledgeEntry]:
        """
        Get a specific knowledge entry by ID.

        Args:
            entry_id: ID of the knowledge entry to retrieve

        Returns:
            Domain knowledge entry or None if not found
        """
        return self.domain_knowledge.get(entry_id)

    def search_knowledge(self, query: str, domain: DomainType = None) -> List[DomainKnowledgeEntry]:
        """
        Search domain knowledge for a query.

        Args:
            query: Query to search for
            domain: Optional domain to limit search to

        Returns:
            List of relevant domain knowledge entries
        """
        query_lower = query.lower()
        matching_entries = []

        for entry in self.domain_knowledge.values():
            # Skip if domain is specified and doesn't match
            if domain is not None and entry.domain != domain:
                continue

            # Check if query matches content, tags, or metadata
            content_match = query_lower in entry.knowledge_item.content.lower()
            tag_match = any(query_lower in tag.lower() for tag in entry.knowledge_item.tags)
            metadata_match = any(
                query_lower in str(value).lower()
                for value in entry.knowledge_item.metadata.values()
            )

            if content_match or tag_match or metadata_match:
                matching_entries.append(entry)

        return matching_entries

    def update_knowledge_entry(
        self,
        entry_id: str,
        content: str = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        approved: bool = None
    ) -> bool:
        """
        Update an existing domain knowledge entry.

        Args:
            entry_id: ID of the entry to update
            content: New content (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)
            approved: New approval status (optional)

        Returns:
            True if update was successful, False otherwise
        """
        if entry_id not in self.domain_knowledge:
            return False

        entry = self.domain_knowledge[entry_id]
        updated = False

        # Update content
        if content is not None:
            entry.knowledge_item.content = content
            updated = True

        # Update tags
        if tags is not None:
            # Remove from old tag indices
            for old_tag in entry.knowledge_item.tags:
                if old_tag in self.tag_indices:
                    self.tag_indices[old_tag].discard(entry_id)

            # Update tags
            entry.knowledge_item.tags = tags

            # Add to new tag indices
            for tag in tags:
                if tag not in self.tag_indices:
                    self.tag_indices[tag] = set()
                self.tag_indices[tag].add(entry_id)
            updated = True

        # Update metadata
        if metadata is not None:
            entry.knowledge_item.metadata.update(metadata)
            updated = True

        # Update approval status
        if approved is not None:
            entry.approved = approved
            updated = True

        # Update timestamp
        if updated:
            entry.updated_at = datetime.now().isoformat()

        return updated

    def remove_knowledge_entry(self, entry_id: str) -> bool:
        """
        Remove a domain knowledge entry.

        Args:
            entry_id: ID of the entry to remove

        Returns:
            True if removal was successful, False otherwise
        """
        if entry_id not in self.domain_knowledge:
            return False

        entry = self.domain_knowledge[entry_id]

        # Remove from domain index
        self.domain_indices[entry.domain].discard(entry_id)

        # Remove from tag indices
        for tag in entry.knowledge_item.tags:
            if tag in self.tag_indices:
                self.tag_indices[tag].discard(entry_id)

        # Remove from contributor index
        contributor = entry.contributor
        if contributor in self.contributor_indices:
            self.contributor_indices[contributor].discard(entry_id)

        # Remove from main storage
        del self.domain_knowledge[entry_id]

        return True

    def approve_knowledge_entry(self, entry_id: str, approve: bool = True) -> bool:
        """
        Approve or disapprove a knowledge entry.

        Args:
            entry_id: ID of the entry to update
            approve: Whether to approve (True) or disapprove (False)

        Returns:
            True if update was successful, False otherwise
        """
        if entry_id not in self.domain_knowledge:
            return False

        self.domain_knowledge[entry_id].approved = approve
        self.domain_knowledge[entry_id].updated_at = datetime.now().isoformat()
        return True

    def get_approved_knowledge_by_domain(self, domain: DomainType) -> List[DomainKnowledgeEntry]:
        """
        Get only approved knowledge entries for a domain.

        Args:
            domain: Domain to retrieve knowledge for

        Returns:
            List of approved domain knowledge entries
        """
        return [
            entry for entry in self.get_knowledge_by_domain(domain)
            if entry.approved
        ]

    def get_all_domains(self) -> List[DomainType]:
        """Get list of all domains with knowledge entries."""
        return [
            domain for domain in DomainType
            if len(self.domain_indices[domain]) > 0
        ]

    def export_knowledge(self) -> str:
        """
        Export all domain knowledge as JSON.

        Returns:
            JSON string containing all domain knowledge
        """
        export_data = []
        for entry in self.domain_knowledge.values():
            entry_dict = {
                'id': entry.id,
                'domain': entry.domain.value,
                'knowledge_item': {
                    'id': entry.knowledge_item.id,
                    'source_type': entry.knowledge_item.source_type.value,
                    'content': entry.knowledge_item.content,
                    'relevance_score': entry.knowledge_item.relevance_score,
                    'tags': entry.knowledge_item.tags,
                    'metadata': entry.knowledge_item.metadata
                },
                'created_at': entry.created_at,
                'updated_at': entry.updated_at,
                'version': entry.version,
                'approved': entry.approved,
                'contributor': entry.contributor
            }
            export_data.append(entry_dict)

        return json.dumps(export_data, indent=2)

    def import_knowledge(self, json_str: str) -> bool:
        """
        Import domain knowledge from JSON.

        Args:
            json_str: JSON string containing domain knowledge data

        Returns:
            True if import was successful, False otherwise
        """
        try:
            data = json.loads(json_str)
            for entry_data in data:
                domain = DomainType(entry_data['domain'])

                knowledge_item_data = entry_data['knowledge_item']
                knowledge_item = KnowledgeItem(
                    id=knowledge_item_data['id'],
                    source_type=KnowledgeSourceType(knowledge_item_data['source_type']),
                    content=knowledge_item_data['content'],
                    relevance_score=knowledge_item_data.get('relevance_score', 1.0),
                    tags=knowledge_item_data.get('tags', []),
                    metadata=knowledge_item_data.get('metadata', {})
                )

                entry = DomainKnowledgeEntry(
                    id=entry_data['id'],
                    domain=domain,
                    knowledge_item=knowledge_item,
                    created_at=entry_data['created_at'],
                    updated_at=entry_data['updated_at'],
                    version=entry_data.get('version', '1.0'),
                    approved=entry_data.get('approved', True),
                    contributor=entry_data.get('contributor', 'system')
                )

                # Store entry
                self.domain_knowledge[entry.id] = entry
                self.domain_indices[domain].add(entry.id)

                # Update indices
                for tag in knowledge_item.tags:
                    if tag not in self.tag_indices:
                        self.tag_indices[tag] = set()
                    self.tag_indices[tag].add(entry.id)

                contributor = entry.contributor
                if contributor not in self.contributor_indices:
                    self.contributor_indices[contributor] = set()
                self.contributor_indices[contributor].add(entry.id)

            return True
        except (json.JSONDecodeError, ValueError):
            return False