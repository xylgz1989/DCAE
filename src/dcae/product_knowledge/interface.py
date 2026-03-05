"""
Product Knowledge Access Module

This module provides interfaces and implementations for accessing
product knowledge from the documentation system during development.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncio
from pathlib import Path


class ProductKnowledgeInterface(ABC):
    """
    Abstract interface for accessing product knowledge.
    Defines the contract for product knowledge systems.
    """

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant product knowledge based on a query.

        Args:
            query: The search query string
            max_results: Maximum number of results to return

        Returns:
            List of relevant knowledge entries with metadata
        """
        pass

    @abstractmethod
    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID.

        Args:
            doc_id: Unique identifier for the document

        Returns:
            Document content and metadata, or None if not found
        """
        pass

    @abstractmethod
    async def get_relevant_documents(self, context: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get documents relevant to the current development context.

        Args:
            context: Current development context or code snippet
            max_results: Maximum number of results to return

        Returns:
            List of relevant documents
        """
        pass


class ProductKnowledgeCacheInterface(ABC):
    """
    Abstract interface for caching product knowledge.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get cached value by key.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        pass

    @abstractmethod
    async def invalidate(self, key: str) -> None:
        """
        Invalidate a specific cache entry.

        Args:
            key: Cache key to invalidate
        """
        pass