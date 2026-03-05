"""
CLI Integration for Product Knowledge

This module extends the existing DCAE CLI with commands for accessing
product knowledge during development.
"""

import typer
from pathlib import Path
from typing import Optional
import asyncio
import json

from ..product_knowledge.access import ProductKnowledgeAccess, SimpleProductKnowledgeCache

app = typer.Typer()

@app.command("search-knowledge")
def search_knowledge(
    query: str = typer.Argument(..., help="The search query for product knowledge"),
    max_results: int = typer.Option(5, "--max-results", "-n", help="Maximum number of results to return"),
    knowledge_base: Optional[Path] = typer.Option(None, "--knowledge-base", "-kb", help="Path to knowledge base directory")
):
    """
    Search for relevant product knowledge in the documentation.
    """
    from ..config import DCAEConfig

    # Load configuration
    config = DCAEConfig.load()

    # Determine knowledge base path
    kb_path = knowledge_base or Path(config.project_knowledge_path or "./docs")

    # Create product knowledge access instance
    cache = SimpleProductKnowledgeCache()
    knowledge_access = ProductKnowledgeAccess(kb_path, cache)

    # Perform search
    async def run_search():
        results = await knowledge_access.search(query, max_results)
        return results

    results = asyncio.run(run_search())

    # Print results
    if results:
        typer.echo(f"\nFound {len(results)} relevant documents:\n")
        for i, result in enumerate(results, 1):
            typer.echo(f"{i}. {result['title']}")
            typer.echo(f"   Source: {result['source_path']}")
            typer.echo(f"   Relevance: {result['score']:.2f}")
            typer.echo(f"   Preview: {result['content_preview']}\n")
    else:
        typer.echo("No relevant documents found.")


@app.command("knowledge-info")
def knowledge_info(
    knowledge_base: Optional[Path] = typer.Option(None, "--knowledge-base", "-kb", help="Path to knowledge base directory")
):
    """
    Show information about the product knowledge base.
    """
    from ..config import DCAEConfig

    # Load configuration
    config = DCAEConfig.load()

    # Determine knowledge base path
    kb_path = knowledge_base or Path(config.project_knowledge_path or "./docs")

    if not kb_path.exists():
        typer.echo(f"Knowledge base path does not exist: {kb_path}")
        raise typer.Exit(code=1)

    # Count documents
    md_files = list(kb_path.rglob("*.md"))
    txt_files = list(kb_path.rglob("*.txt"))
    rst_files = list(kb_path.rglob("*.rst"))

    total_docs = len(md_files) + len(txt_files) + len(rst_files)

    typer.echo(f"Product Knowledge Base Information:")
    typer.echo(f"  Path: {kb_path.absolute()}")
    typer.echo(f"  Total documents: {total_docs}")
    typer.echo(f"  Markdown files: {len(md_files)}")
    typer.echo(f"  Text files: {len(txt_files)}")
    typer.echo(f"  ReStructuredText files: {len(rst_files)}")


@app.command("get-document")
def get_document(
    doc_id: str = typer.Argument(..., help="The ID of the document to retrieve"),
    knowledge_base: Optional[Path] = typer.Option(None, "--knowledge-base", "-kb", help="Path to knowledge base directory")
):
    """
    Retrieve a specific document by its ID.
    """
    from ..config import DCAEConfig

    # Load configuration
    config = DCAEConfig.load()

    # Determine knowledge base path
    kb_path = knowledge_base or Path(config.project_knowledge_path or "./docs")

    # Create product knowledge access instance
    cache = SimpleProductKnowledgeCache()
    knowledge_access = ProductKnowledgeAccess(kb_path, cache)

    # Get document
    async def run_get():
        doc = await knowledge_access.get_document_by_id(doc_id)
        return doc

    doc = asyncio.run(run_get())

    if doc:
        typer.echo(f"Title: {doc['title']}")
        typer.echo(f"Source: {doc['source_path']}")
        typer.echo(f"Content:\n{doc['content']}")
    else:
        typer.echo(f"No document found with ID: {doc_id}")


@app.command("suggest-knowledge")
def suggest_knowledge(
    context: str = typer.Argument(..., help="Development context to find relevant knowledge for"),
    max_results: int = typer.Option(3, "--max-results", "-n", help="Maximum number of suggestions"),
    knowledge_base: Optional[Path] = typer.Option(None, "--knowledge-base", "-kb", help="Path to knowledge base directory")
):
    """
    Get suggestions for relevant product knowledge based on development context.
    """
    from ..config import DCAEConfig

    # Load configuration
    config = DCAEConfig.load()

    # Determine knowledge base path
    kb_path = knowledge_base or Path(config.project_knowledge_path or "./docs")

    # Create product knowledge access instance
    cache = SimpleProductKnowledgeCache()
    knowledge_access = ProductKnowledgeAccess(kb_path, cache)

    # Get relevant documents
    async def run_suggest():
        results = await knowledge_access.get_relevant_documents(context, max_results)
        return results

    results = asyncio.run(run_suggest())

    # Print suggestions
    if results:
        typer.echo(f"\nBased on your context '{context}', here are relevant documents:\n")
        for i, result in enumerate(results, 1):
            typer.echo(f"{i}. {result['title']}")
            typer.echo(f"   Source: {result['source_path']}")
            typer.echo(f"   Relevance: {result['score']:.2f}")
    else:
        typer.echo("No relevant documents found for the given context.")