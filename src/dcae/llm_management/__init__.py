"""LLM Management module for the DCAE framework."""
from .provider_config import ProviderConfig, ProviderType
from .provider_manager import LLMProviderManager
from .selection_strategies import TaskAnalyzer, LLMSelector, TaskType, TaskComplexity, TaskAnalysis
from .manual_selector import ManualLLMSelector
from .comparison_verifier import MultiLLMComparison, ComparisonResult, ConsistencyCheck
from .usage_tracker import UsageTracker, UsageRecord, UsageStatistics

__all__ = [
    # Provider Configuration
    'ProviderConfig',
    'ProviderType',

    # Provider Management
    'LLMProviderManager',

    # Selection Strategies
    'TaskAnalyzer',
    'LLMSelector',
    'TaskType',
    'TaskComplexity',
    'TaskAnalysis',

    # Manual Selection
    'ManualLLMSelector',

    # Comparison and Verification
    'MultiLLMComparison',
    'ComparisonResult',
    'ConsistencyCheck',

    # Usage Tracking
    'UsageTracker',
    'UsageRecord',
    'UsageStatistics'
]