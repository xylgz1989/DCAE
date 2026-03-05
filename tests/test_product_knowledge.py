"""
Test suite for the product knowledge integration.
Tests the core functionality of the product knowledge access system.
"""

import asyncio
from pathlib import Path
import tempfile
import os

from src.dcae.product_knowledge.interface import ProductKnowledgeInterface, ProductKnowledgeCacheInterface
from src.dcae.product_knowledge.access import ProductKnowledgeAccess, SimpleProductKnowledgeCache, Document


def test_product_knowledge_cache():
    """Test the product knowledge cache implementation."""
    cache = SimpleProductKnowledgeCache()

    # Test setting and getting a value
    async def test_operations():
        await cache.set("test_key", "test_value", ttl=300)
        result = await cache.get("test_key")
        assert result == "test_value"

        # Test cache invalidation
        await cache.invalidate("test_key")
        result = await cache.get("test_key")
        assert result is None

    asyncio.run(test_operations())


def test_product_knowledge_access():
    """Test the product knowledge access functionality with temporary files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test documents
        docs_dir = temp_path / "docs"
        docs_dir.mkdir()

        # Create a few test documents
        (docs_dir / "coding_standards.md").write_text("""
# Coding Standards

## Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants

## Documentation
- All public functions must have docstrings
- Use Google-style docstrings
        """)

        (docs_dir / "architecture_patterns.md").write_text("""
# Architecture Patterns

## MVC Pattern
The Model-View-Controller pattern separates concerns:
- Model: Handles data and business logic
- View: Manages UI presentation
- Controller: Coordinates between Model and View

## Repository Pattern
Provides an abstraction layer between domain and data mapping layers.
        """)

        (docs_dir / "deployment_guide.txt").write_text("""
Deployment Guide
==============

To deploy the application:

1. Set environment variables
2. Run database migrations
3. Start the server
        """)

        cache = SimpleProductKnowledgeCache()
        knowledge_access = ProductKnowledgeAccess(docs_dir, cache)

        # Build the index
        async def test_access():
            await knowledge_access._build_index()

            # Verify documents were loaded
            assert len(knowledge_access.documents) == 3

            # Test search functionality
            results = await knowledge_access.search("coding standards", max_results=5)
            assert len(results) >= 1
            assert any("Coding Standards" in result['title'] for result in results)

            # Test search for architecture patterns
            results = await knowledge_access.search("architecture patterns", max_results=5)
            assert len(results) >= 1
            assert any("Architecture Patterns" in result['title'] for result in results)

        asyncio.run(test_access())


def test_document_retrieval():
    """Test retrieving specific documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test documents
        docs_dir = temp_path / "docs"
        docs_dir.mkdir()

        (docs_dir / "test_doc.md").write_text("# Test Document\nThis is a test document.")

        cache = SimpleProductKnowledgeCache()
        knowledge_access = ProductKnowledgeAccess(docs_dir, cache)

        # Build the index and retrieve document
        async def test_retrieval():
            await knowledge_access._build_index()

            # Get the first document's ID
            if knowledge_access.documents:
                doc_id = knowledge_access.documents[0].id

                # Retrieve document by ID
                doc = await knowledge_access.get_document_by_id(doc_id)
                assert doc is not None
                assert doc['id'] == doc_id

        asyncio.run(test_retrieval())


def test_contextual_search():
    """Test contextual search functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test documents
        docs_dir = temp_path / "docs"
        docs_dir.mkdir()

        (docs_dir / "coding_standards.md").write_text("""
# Coding Standards

## Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants
        """)

        cache = SimpleProductKnowledgeCache()
        knowledge_access = ProductKnowledgeAccess(docs_dir, cache)

        # Build the index and test contextual search
        async def test_contextual():
            await knowledge_access._build_index()

            # Test contextual search for coding-related content
            results = await knowledge_access.get_relevant_documents("I need to understand coding conventions", max_results=5)
            assert len(results) >= 1
            # Should find the coding standards document
            titles = [result['title'] for result in results]
            assert any("Coding Standards" in title for title in titles)

        asyncio.run(test_contextual())


def test_similarity_calculation():
    """Test the similarity calculation function directly."""
    cache = SimpleProductKnowledgeCache()
    knowledge_access = ProductKnowledgeAccess(Path("."), cache)

    # Create a test document
    doc = Document(
        id="test",
        title="Python Coding Standards",
        content="This document describes Python coding standards and best practices for naming conventions.",
        source_path="./test.md",
        metadata={}
    )

    # Test similarity with related terms
    score1 = knowledge_access._calculate_similarity("python coding", doc)
    score2 = knowledge_access._calculate_similarity("java programming", doc)

    # The Python-related query should have higher similarity
    assert score1 > score2


if __name__ == "__main__":
    test_product_knowledge_cache()
    test_product_knowledge_access()
    test_document_retrieval()
    test_contextual_search()
    test_similarity_calculation()
    print("All tests passed!")