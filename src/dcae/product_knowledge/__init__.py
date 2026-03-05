"""
Product Knowledge Module for DCAE

This module provides access to product knowledge during development,
integrating documentation and best practices into the development workflow.
"""

from .interface import ProductKnowledgeInterface, ProductKnowledgeCacheInterface
from .access import ProductKnowledgeAccess, SimpleProductKnowledgeCache

__all__ = [
    'ProductKnowledgeInterface',
    'ProductKnowledgeCacheInterface',
    'ProductKnowledgeAccess',
    'SimpleProductKnowledgeCache'
]