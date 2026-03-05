"""
Implementation of product knowledge access functionality.

This module implements the interfaces defined in interface.py and provides
actual functionality for accessing and searching product knowledge.
"""

import asyncio
import json
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import re

try:
    import aiofiles
except ImportError:
    aiofiles = None

from .interface import ProductKnowledgeInterface, ProductKnowledgeCacheInterface


@dataclass
class Document:
    """Represents a document in the product knowledge system."""

    id: str
    title: str
    content: str
    source_path: str
    metadata: Dict[str, Any]


class SimpleProductKnowledgeCache(ProductKnowledgeCacheInterface):
    """
    Simple in-memory cache implementation for product knowledge.
    """

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, tuple] = {}
        self._access_order: List[str] = []  # For LRU eviction
        self._max_size = max_size

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value by key."""
        if key in self._cache:
            # Update access order for LRU
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            value, expiry = self._cache[key]
            if expiry is not None and asyncio.get_event_loop().time() > expiry:
                del self._cache[key]
                self._access_order.remove(key)
                return None
            return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        # Calculate expiry time if TTL is provided
        expiry = None
        if ttl is not None:
            expiry = asyncio.get_event_loop().time() + ttl

        # Add to cache
        self._cache[key] = (value, expiry)

        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        # Evict oldest entries if cache is full
        while len(self._cache) > self._max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]

    async def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry."""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)


class ProductKnowledgeAccess(ProductKnowledgeInterface):
    """
    Implementation of product knowledge access functionality.
    """

    def __init__(self, knowledge_base_path: Path, cache: Optional[ProductKnowledgeCacheInterface] = None):
        """
        Initialize the product knowledge access system.

        Args:
            knowledge_base_path: Path to the product knowledge base (typically docs/)
            cache: Optional cache implementation
        """
        self.knowledge_base_path = knowledge_base_path
        self.cache = cache or SimpleProductKnowledgeCache()
        self.documents: List[Document] = []
        self._index_built = False

    async def _ensure_index(self) -> None:
        """Ensure the document index is built."""
        if not self._index_built:
            await self._build_index()
            self._index_built = True

    async def _build_index(self) -> None:
        """Build an index of all documents in the knowledge base."""
        if not self.knowledge_base_path.exists():
            return

        docs = []
        for file_path in self.knowledge_base_path.rglob('*'):
            if file_path.suffix.lower() in ['.md', '.txt', '.rst']:
                try:
                    content = await self._read_file(file_path)
                    if content.strip():  # Only add non-empty documents
                        doc_id = self._generate_doc_id(str(file_path))
                        title = self._extract_title(content, file_path.name)
                        doc = Document(
                            id=doc_id,
                            title=title,
                            content=content,
                            source_path=str(file_path),
                            metadata={
                                'size': len(content),
                                'extension': file_path.suffix,
                                'created_at': file_path.stat().st_ctime
                            }
                        )
                        docs.append(doc)
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {str(e)}")

        self.documents = docs

    async def _read_file(self, file_path: Path) -> str:
        """Read a file asynchronously."""
        if aiofiles:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        else:
            # Fallback to synchronous reading
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

    def _generate_doc_id(self, file_path: str) -> str:
        """Generate a unique ID for a document."""
        return hashlib.md5(file_path.encode()).hexdigest()

    def _extract_title(self, content: str, fallback: str) -> str:
        """Extract title from content (first heading or filename)."""
        # Look for first markdown heading
        lines = content.split('\n')
        for line in lines[:10]:  # Only check first 10 lines
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('## '):
                return line[3:].strip()

        # Fallback to filename without extension
        return Path(fallback).stem.replace('_', ' ').replace('-', ' ').title()

    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant product knowledge based on a query.
        """
        await self._ensure_index()

        # Create cache key
        cache_key = f"search_{hashlib.md5((query + str(max_results)).encode()).hexdigest()}"

        # Try to get from cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Perform search
        query_lower = query.lower()
        results = []

        for doc in self.documents:
            score = self._calculate_similarity(query_lower, doc)
            if score > 0.1:  # Only include results with meaningful similarity
                results.append({
                    'id': doc.id,
                    'title': doc.title,
                    'source_path': doc.source_path,
                    'score': score,
                    'content_preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content
                })

        # Sort by score and take top results
        results.sort(key=lambda x: x['score'], reverse=True)
        final_results = results[:max_results]

        # Cache the result for 5 minutes
        await self.cache.set(cache_key, final_results, ttl=300)

        return final_results

    def _calculate_similarity(self, query: str, doc: Document) -> float:
        """
        Calculate similarity between query and document using simple keyword matching.
        """
        doc_content_lower = doc.content.lower()
        query_words = query.split()

        if not query_words:
            return 0.0

        matches = 0
        total_query_terms = 0

        for word in query_words:
            word = word.strip()
            if len(word) < 2:  # Skip very short words
                continue

            total_query_terms += 1
            # Count occurrences of word in content and title
            content_matches = len(re.findall(r'\b' + re.escape(word) + r'\b', doc_content_lower))
            title_matches = len(re.findall(r'\b' + re.escape(word) + r'\b', doc.title.lower()))
            matches += content_matches + (title_matches * 2)  # Title matches worth more

        if total_query_terms == 0:
            return 0.0

        # Normalize by document length to avoid favoring longer documents
        length_factor = min(len(doc.content) / 1000, 1.0) + 0.1  # Ensure some weight
        score = (matches / total_query_terms) / length_factor

        # Also boost documents where query appears in title
        if query in doc.title.lower():
            score *= 2.0

        return min(score, 1.0)  # Cap at 1.0

    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID.
        """
        await self._ensure_index()

        cache_key = f"doc_{doc_id}"
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        for doc in self.documents:
            if doc.id == doc_id:
                result = {
                    'id': doc.id,
                    'title': doc.title,
                    'content': doc.content,
                    'source_path': doc.source_path,
                    'metadata': doc.metadata
                }

                # Cache for 10 minutes
                await self.cache.set(cache_key, result, ttl=600)
                return result

        return None

    async def get_relevant_documents(self, context: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get documents relevant to the current development context.
        """
        await self._ensure_index()

        # Use context as search query
        return await self.search(context, max_results)