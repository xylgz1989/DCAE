"""Knowledge Fusion & Cross-Domain Intelligence module for the DCAE framework."""
from .knowledge_fuser import KnowledgeFuser, KnowledgeSourceType
from .domain_knowledge_manager import DomainKnowledgeManager
from .cross_domain_recommender import CrossDomainRecommender
from .best_practices_reflector import BestPracticesReflector
from .project_learning_system import ProjectLearningSystem

__all__ = [
    # Knowledge Fuser
    'KnowledgeFuser',
    'KnowledgeSourceType',

    # Domain Knowledge Manager
    'DomainKnowledgeManager',

    # Cross-Domain Recommender
    'CrossDomainRecommender',

    # Best Practices Reflector
    'BestPracticesReflector',

    # Project Learning System
    'ProjectLearningSystem'
]