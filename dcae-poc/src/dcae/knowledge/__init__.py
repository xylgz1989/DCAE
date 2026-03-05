"""Domain-specific knowledge management module."""

import json
import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


class DomainType(Enum):
    """Types of knowledge domains."""
    TECHNICAL = "technical"
    BUSINESS = "business"
    REGULATORY = "regulatory"
    DOMAIN_EXPERTISE = "domain_expertise"
    CUSTOM = "custom"


@dataclass
class KnowledgeEntry:
    """Represents a single piece of domain-specific knowledge."""
    id: str
    domain: DomainType
    content: str
    source: str
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['domain'] = self.domain.value
        result['timestamp'] = self.timestamp.isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntry':
        """Create from dictionary."""
        data['domain'] = DomainType(data['domain'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class DomainKnowledgeBase:
    """Manages domain-specific knowledge storage and retrieval."""

    def __init__(self, db_path: str = "./dcae-knowledge.db"):
        """Initialize the knowledge base.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create knowledge entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_domain_timestamp
            ON knowledge_entries (domain, timestamp)
        """)

        conn.commit()
        conn.close()

    def add_knowledge(
        self,
        domain: DomainType,
        content: str,
        source: str = "unknown",
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add domain-specific knowledge to the base.

        Args:
            domain: The domain type
            content: The knowledge content
            source: Source of the knowledge
            confidence: Confidence level (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            ID of the added knowledge entry
        """
        import uuid
        entry_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        entry = KnowledgeEntry(
            id=entry_id,
            domain=domain,
            content=content,
            source=source,
            confidence=confidence,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        cursor.execute("""
            INSERT INTO knowledge_entries
            (id, domain, content, source, confidence, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.domain.value,
            entry.content,
            entry.source,
            entry.confidence,
            entry.timestamp.isoformat(),
            json.dumps(entry.metadata)
        ))

        conn.commit()
        conn.close()

        return entry_id

    def get_knowledge(
        self,
        domain: Optional[DomainType] = None,
        min_confidence: float = 0.0,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[KnowledgeEntry]:
        """Retrieve knowledge entries.

        Args:
            domain: Filter by domain type
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of knowledge entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM knowledge_entries WHERE confidence >= ?"
        params = [min_confidence]

        if domain:
            query += " AND domain = ?"
            params.append(domain.value)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        entries = []
        for row in rows:
            entry = KnowledgeEntry(
                id=row[0],
                domain=DomainType(row[1]),
                content=row[2],
                source=row[3],
                confidence=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                metadata=json.loads(row[6]) if row[6] else {}
            )
            entries.append(entry)

        conn.close()
        return entries

    def search_knowledge(
        self,
        query: str,
        domain: Optional[DomainType] = None,
        min_confidence: float = 0.0
    ) -> List[KnowledgeEntry]:
        """Search for knowledge entries containing the query string.

        Args:
            query: Search query string
            domain: Filter by domain type
            min_confidence: Minimum confidence threshold

        Returns:
            List of matching knowledge entries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query_clause = "WHERE content LIKE ? AND confidence >= ?"
        params = [f"%{query}%", min_confidence]

        if domain:
            query_clause += " AND domain = ?"
            params.append(domain.value)

        query_sql = f"SELECT * FROM knowledge_entries {query_clause} ORDER BY confidence DESC, timestamp DESC"

        cursor.execute(query_sql, params)
        rows = cursor.fetchall()

        entries = []
        for row in rows:
            entry = KnowledgeEntry(
                id=row[0],
                domain=DomainType(row[1]),
                content=row[2],
                source=row[3],
                confidence=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                metadata=json.loads(row[6]) if row[6] else {}
            )
            entries.append(entry)

        conn.close()
        return entries

    def update_knowledge_confidence(self, entry_id: str, new_confidence: float):
        """Update the confidence score of a knowledge entry.

        Args:
            entry_id: ID of the knowledge entry
            new_confidence: New confidence score
        """
        if not 0.0 <= new_confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE knowledge_entries SET confidence = ? WHERE id = ?",
            (new_confidence, entry_id)
        )

        conn.commit()
        conn.close()

    def remove_knowledge(self, entry_id: str):
        """Remove a knowledge entry.

        Args:
            entry_id: ID of the knowledge entry to remove
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM knowledge_entries WHERE id = ?",
            (entry_id,)
        )

        conn.commit()
        conn.close()


class KnowledgeFusionEngine:
    """Integrates domain-specific knowledge into processing workflows."""

    def __init__(self, knowledge_base: DomainKnowledgeBase):
        """Initialize the fusion engine.

        Args:
            knowledge_base: The knowledge base to use
        """
        self.knowledge_base = knowledge_base

    def get_relevant_knowledge(
        self,
        context: str,
        domain: DomainType,
        max_entries: int = 5,
        min_confidence: float = 0.5
    ) -> List[KnowledgeEntry]:
        """Get relevant knowledge for the given context and domain.

        Args:
            context: Processing context
            domain: Domain type
            max_entries: Maximum number of entries to return
            min_confidence: Minimum confidence threshold

        Returns:
            Relevant knowledge entries
        """
        # First try semantic search based on context
        search_results = self.knowledge_base.search_knowledge(
            query=context,
            domain=domain,
            min_confidence=min_confidence
        )

        # Limit results
        return search_results[:max_entries]

    def integrate_knowledge(
        self,
        prompt: str,
        context: str,
        domain: DomainType,
        min_confidence: float = 0.5
    ) -> str:
        """Integrate relevant domain knowledge into the prompt.

        Args:
            prompt: Original prompt
            context: Context for relevance matching
            domain: Domain type
            min_confidence: Minimum confidence threshold

        Returns:
            Augmented prompt with relevant knowledge
        """
        relevant_knowledge = self.get_relevant_knowledge(
            context=context,
            domain=domain,
            min_confidence=min_confidence
        )

        if not relevant_knowledge:
            return prompt

        # Build knowledge context
        knowledge_context = "Domain-specific knowledge that may be relevant:\n\n"
        for i, entry in enumerate(relevant_knowledge, 1):
            knowledge_context += f"{i}. {entry.content}\n"
            knowledge_context += f"   (Source: {entry.source}, Confidence: {entry.confidence:.2f})\n\n"

        # Prepend knowledge context to the original prompt
        return f"{knowledge_context}{prompt}"


# Export public classes
__all__ = [
    'DomainKnowledgeBase',
    'DomainType',
    'KnowledgeEntry',
    'KnowledgeFusionEngine',
    'CrossDomainRecommendationEngine',
    'Recommendation',
    'CrossDomainRelationship'
]

# Import cross-domain components
from .cross_domain import (
    CrossDomainRecommendationEngine,
    Recommendation,
    CrossDomainRelationship
)