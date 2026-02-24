"""Module for fusing development and product knowledge during code generation."""
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json


class KnowledgeSourceType(Enum):
    """Types of knowledge sources."""
    DEVELOPMENT = "development"
    PRODUCT = "product"
    BUSINESS = "business"
    TECHNICAL = "technical"
    DOMAIN = "domain"
    BEST_PRACTICES = "best_practices"


@dataclass
class KnowledgeItem:
    """Represents a piece of knowledge."""
    id: str
    source_type: KnowledgeSourceType
    content: str
    relevance_score: float = 1.0
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FusedKnowledgeContext:
    """Context containing fused knowledge for code generation."""
    development_knowledge: List[KnowledgeItem]
    product_knowledge: List[KnowledgeItem]
    business_context: List[KnowledgeItem]
    technical_constraints: List[KnowledgeItem]
    best_practices: List[KnowledgeItem]


class KnowledgeFuser:
    """Fuses development and product knowledge during code generation."""

    def __init__(self):
        """Initialize the knowledge fuser."""
        self.knowledge_store: Dict[str, KnowledgeItem] = {}
        self.fusion_rules: Dict[str, Any] = {}

    def add_knowledge(self, item: KnowledgeItem) -> str:
        """
        Add a knowledge item to the store.

        Args:
            item: Knowledge item to add

        Returns:
            ID of the added knowledge item
        """
        self.knowledge_store[item.id] = item
        return item.id

    def get_knowledge_by_type(self, source_type: KnowledgeSourceType) -> List[KnowledgeItem]:
        """
        Get knowledge items by source type.

        Args:
            source_type: Type of knowledge to retrieve

        Returns:
            List of knowledge items of the specified type
        """
        return [
            item for item in self.knowledge_store.values()
            if item.source_type == source_type
        ]

    def get_knowledge_by_tags(self, tags: List[str]) -> List[KnowledgeItem]:
        """
        Get knowledge items by tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of knowledge items matching the tags
        """
        matching_items = []
        for item in self.knowledge_store.values():
            if any(tag in item.tags for tag in tags):
                matching_items.append(item)
        return matching_items

    def fuse_knowledge(self, context_requirements: Dict[str, Any]) -> FusedKnowledgeContext:
        """
        Fuse development and product knowledge based on context requirements.

        Args:
            context_requirements: Requirements for the knowledge fusion

        Returns:
            Fused knowledge context containing relevant knowledge
        """
        # Extract requirements
        required_tags = context_requirements.get('tags', [])
        required_types = context_requirements.get('types', [t.value for t in KnowledgeSourceType])

        # Filter knowledge by requirements
        dev_knowledge = []
        product_knowledge = []
        business_knowledge = []
        tech_knowledge = []
        best_practice_knowledge = []

        for item in self.knowledge_store.values():
            if item.source_type.value in required_types:
                # If tags are specified, check if item matches any of them
                if not required_tags or any(tag in item.tags for tag in required_tags):
                    if item.source_type == KnowledgeSourceType.DEVELOPMENT:
                        dev_knowledge.append(item)
                    elif item.source_type == KnowledgeSourceType.PRODUCT:
                        product_knowledge.append(item)
                    elif item.source_type == KnowledgeSourceType.BUSINESS:
                        business_knowledge.append(item)
                    elif item.source_type == KnowledgeSourceType.TECHNICAL:
                        tech_knowledge.append(item)
                    elif item.source_type == KnowledgeSourceType.BEST_PRACTICES:
                        best_practice_knowledge.append(item)

        return FusedKnowledgeContext(
            development_knowledge=dev_knowledge,
            product_knowledge=product_knowledge,
            business_context=business_knowledge,
            technical_constraints=tech_knowledge,
            best_practices=best_practice_knowledge
        )

    def get_relevant_knowledge(self, query: str, max_results: int = 10) -> List[KnowledgeItem]:
        """
        Get knowledge items relevant to a query using simple text matching.

        Args:
            query: Query to match against knowledge items
            max_results: Maximum number of results to return

        Returns:
            List of relevant knowledge items
        """
        relevant_items = []
        query_lower = query.lower()

        for item in self.knowledge_store.values():
            # Match in content, tags, or metadata
            content_match = query_lower in item.content.lower()
            tag_match = any(query_lower in tag.lower() for tag in item.tags)
            metadata_match = any(
                query_lower in str(value).lower()
                for value in item.metadata.values()
            )

            if content_match or tag_match or metadata_match:
                relevant_items.append(item)

        # Sort by relevance score (descending) and return top results
        relevant_items.sort(key=lambda x: x.relevance_score, reverse=True)
        return relevant_items[:max_results]

    def update_knowledge_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing knowledge item.

        Args:
            item_id: ID of the knowledge item to update
            updates: Updates to apply to the knowledge item

        Returns:
            True if the update was successful, False otherwise
        """
        if item_id not in self.knowledge_store:
            return False

        item = self.knowledge_store[item_id]

        # Update allowed fields
        if 'content' in updates:
            item.content = updates['content']
        if 'relevance_score' in updates:
            item.relevance_score = updates['relevance_score']
        if 'tags' in updates:
            item.tags = updates['tags']
        if 'metadata' in updates:
            item.metadata.update(updates['metadata'])

        return True

    def remove_knowledge_item(self, item_id: str) -> bool:
        """
        Remove a knowledge item.

        Args:
            item_id: ID of the knowledge item to remove

        Returns:
            True if removal was successful, False otherwise
        """
        if item_id in self.knowledge_store:
            del self.knowledge_store[item_id]
            return True
        return False

    def export_knowledge(self) -> str:
        """
        Export all knowledge as JSON.

        Returns:
            JSON string containing all knowledge
        """
        export_data = []
        for item in self.knowledge_store.values():
            item_dict = {
                'id': item.id,
                'source_type': item.source_type.value,
                'content': item.content,
                'relevance_score': item.relevance_score,
                'tags': item.tags,
                'metadata': item.metadata
            }
            export_data.append(item_dict)

        return json.dumps(export_data, indent=2)

    def import_knowledge(self, json_str: str) -> bool:
        """
        Import knowledge from JSON.

        Args:
            json_str: JSON string containing knowledge data

        Returns:
            True if import was successful, False otherwise
        """
        try:
            data = json.loads(json_str)
            for item_data in data:
                source_type = KnowledgeSourceType(item_data['source_type'])
                item = KnowledgeItem(
                    id=item_data['id'],
                    source_type=source_type,
                    content=item_data['content'],
                    relevance_score=item_data.get('relevance_score', 1.0),
                    tags=item_data.get('tags', []),
                    metadata=item_data.get('metadata', {})
                )
                self.add_knowledge(item)
            return True
        except (json.JSONDecodeError, ValueError):
            return False