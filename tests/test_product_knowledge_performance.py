"""
Performance tests for the product knowledge integration.
Tests the performance characteristics of the product knowledge access system.
"""

import asyncio
import time
from pathlib import Path
import tempfile

from src.dcae.product_knowledge.access import ProductKnowledgeAccess, SimpleProductKnowledgeCache


def test_performance():
    """Test the performance of the product knowledge system."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test documents
        docs_dir = temp_path / "docs"
        docs_dir.mkdir()

        # Create several test documents to test performance with multiple files
        for i in range(20):
            (docs_dir / f"doc_{i:02d}.md").write_text(f"""
# Document {i}

This is test document number {i} with some content to search through.
We want to make sure the search functionality performs well even with multiple documents.
Some key terms that might be searched for: performance, efficiency, search, document.

## Section A
Content for document {i} in section A

## Section B
More content for document {i} in section B

## Conclusion
Document {i} contains various terms that could be relevant to searches.
""")

        cache = SimpleProductKnowledgeCache()
        knowledge_access = ProductKnowledgeAccess(docs_dir, cache)

        # Measure index building time
        start_time = time.time()
        asyncio.run(knowledge_access._build_index())
        index_time = time.time() - start_time
        print(f"Index building time: {index_time:.4f} seconds for {len(knowledge_access.documents)} documents")

        # Measure search performance
        search_queries = [
            "performance efficiency",
            "search document",
            "section A content",
            "conclusion terms"
        ]

        total_search_time = 0
        search_count = 0

        for query in search_queries:
            start_time = time.time()
            results = asyncio.run(knowledge_access.search(query, max_results=5))
            search_time = time.time() - start_time
            total_search_time += search_time
            search_count += 1
            print(f"Search for '{query[:20]}...' took {search_time:.4f}s, found {len(results)} results")

        avg_search_time = total_search_time / search_count if search_count > 0 else 0
        print(f"Average search time: {avg_search_time:.4f} seconds")

        # Test cached vs uncached search performance
        query = "performance efficiency"

        # First search (uncached)
        start_time = time.time()
        results1 = asyncio.run(knowledge_access.search(query, max_results=5))
        first_search_time = time.time() - start_time

        # Second search (should be cached)
        start_time = time.time()
        results2 = asyncio.run(knowledge_access.search(query, max_results=5))
        cached_search_time = time.time() - start_time

        print(f"Uncached search time: {first_search_time:.4f}s")
        print(f"Cached search time: {cached_search_time:.4f}s")
        print(f"Speed improvement: {(first_search_time/cached_search_time):.2f}x faster when cached" if cached_search_time > 0 else "N/A")

        # Verify search results are consistent
        assert len(results1) == len(results2), "Cached and uncached results should have same length"

        # Overall performance check
        performance_ok = avg_search_time < 0.1  # Should search in under 100ms on average
        print(f"Performance check: {'PASS' if performance_ok else 'FAIL'} (avg search time < 100ms)")

        return performance_ok


if __name__ == "__main__":
    print("Running performance tests for product knowledge system...")
    success = test_performance()
    print(f"Performance tests: {'PASSED' if success else 'FAILED'}")