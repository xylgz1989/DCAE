# Cross-Domain Recommendation System API Documentation

## Overview

The Cross-Domain Recommendation System enables the identification of relationships and generation of insights that span multiple knowledge domains. It analyzes knowledge from different domains (Technical, Business, Regulatory, etc.) to identify connections that might not be apparent when examining domains individually.

## Core Components

### 1. CrossDomainRecommendationEngine

The primary class responsible for generating cross-domain recommendations.

#### Initialization

```python
from dcae.knowledge import DomainKnowledgeBase
from dcae.knowledge.cross_domain import CrossDomainRecommendationEngine

# Initialize knowledge base
kb = DomainKnowledgeBase(db_path="./knowledge.db")

# Initialize recommendation engine
engine = CrossDomainRecommendationEngine(knowledge_base=kb)
```

#### Methods

##### `generate_recommendations(context="", target_domains=None, min_relationship_strength=0.4, max_recommendations=10, min_confidence=0.5)`

Generates cross-domain recommendations based on the provided context.

**Parameters:**
- `context` (str): Current development or analysis context for relevance filtering
- `target_domains` (List[DomainType], optional): Specific domains to focus on; if None, all domains are analyzed
- `min_relationship_strength` (float): Minimum strength threshold for relationships (0.0 to 1.0)
- `max_recommendations` (int): Maximum number of recommendations to return
- `min_confidence` (float): Minimum confidence threshold for knowledge entries (0.0 to 1.0)

**Returns:**
- `List[Recommendation]`: List of cross-domain recommendations ordered by confidence

**Example:**
```python
from dcae.knowledge import DomainType

recommendations = engine.generate_recommendations(
    context="system security implementation",
    target_domains=[DomainType.TECHNICAL, DomainType.REGULATORY],
    min_relationship_strength=0.3,
    max_recommendations=5,
    min_confidence=0.6
)

for rec in recommendations:
    print(f"Title: {rec.title}")
    print(f"Confidence: {rec.confidence:.2f}")
    print(f"Domains: {rec.source_domains}")
    print("---")
```

##### `get_recommendation_explanation(recommendation)`

Generates a detailed explanation for a specific recommendation.

**Parameters:**
- `recommendation` (Recommendation): The recommendation to explain

**Returns:**
- `str`: Detailed explanation of the recommendation

**Example:**
```python
explanation = engine.get_recommendation_explanation(recommendations[0])
print(explanation)
```

##### `get_comprehensive_explanation(recommendation, include_raw_relationships=True)`

Generates comprehensive technical details about a recommendation.

**Parameters:**
- `recommendation` (Recommendation): The recommendation to explain
- `include_raw_relationships` (bool): Whether to include raw relationship data

**Returns:**
- `Dict[str, Any]`: Dictionary containing comprehensive explanation details

**Example:**
```python
details = engine.get_comprehensive_explanation(recommendations[0])
print(details['confidence_details'])
print(details['related_knowledge'])
```

##### `analyze_multi_domain_patterns(domain_types, time_window_days=30)`

Analyzes patterns across multiple domains within a specific time window.

**Parameters:**
- `domain_types` (List[DomainType]): List of domain types to analyze
- `time_window_days` (int): Number of days to look back for pattern analysis

**Returns:**
- `Dict[str, Any]`: Dictionary containing pattern analysis results

**Example:**
```python
patterns = engine.analyze_multi_domain_patterns(
    domain_types=[DomainType.TECHNICAL, DomainType.BUSINESS],
    time_window_days=60
)
print(f"Total relationships: {patterns['total_relationships']}")
print(f"Average strength: {patterns['average_strength']:.2f}")
```

### 2. Recommendation Class

Represents a cross-domain recommendation with various attributes.

#### Attributes:
- `id` (str): Unique identifier for the recommendation
- `title` (str): Human-readable title of the recommendation
- `description` (str): Brief description of the recommendation
- `source_domains` (List[DomainType]): List of domains that contributed to the recommendation
- `confidence` (float): Overall confidence score (0.0 to 1.0)
- `explanation` (str): Explanation of why the recommendation was made
- `related_knowledge_ids` (List[str]): IDs of related knowledge entries
- `timestamp` (datetime): When the recommendation was created
- `confidence_breakdown` (Dict[str, float]): Breakdown of confidence components
- `metadata` (Dict[str, Any]): Additional metadata

### 3. ConfidenceScorer

Calculates and manages confidence scores for cross-domain insights.

#### Methods:
- `calculate_overall_confidence(knowledge_confidences, relationship_strength, source_diversity, recency_factor, consistency_factor)`
- `calculate_recency_factor(timestamp)`
- `calculate_consistency_factor(domain_confidences, relationship_type)`

### 4. RelationshipIdentifier

Identifies relationships between knowledge entries from different domains.

#### Methods:
- `identify_relationships(knowledge_entries)` - Identifies cross-domain relationships
- `_calculate_semantic_similarity(content_a, content_b)` - Calculates similarity between content strings
- `_identify_relationship_type(entry_a, entry_b)` - Identifies the type of relationship

## Usage Patterns

### 1. Basic Cross-Domain Analysis

```python
from dcae.knowledge import DomainKnowledgeBase, DomainType
from dcae.knowledge.cross_domain import CrossDomainRecommendationEngine

# Initialize system
kb = DomainKnowledgeBase()
engine = CrossDomainRecommendationEngine(kb)

# Add some knowledge
kb.add_knowledge(
    domain=DomainType.TECHNICAL,
    content="API rate limiting helps prevent server overload",
    source="security_docs",
    confidence=0.8
)

kb.add_knowledge(
    domain=DomainType.BUSINESS,
    content="System performance affects customer satisfaction",
    source="business_docs",
    confidence=0.75
)

# Generate recommendations
recommendations = engine.generate_recommendations(context="system performance")
```

### 2. Targeted Domain Analysis

```python
# Focus on specific domains only
tech_and_business_recs = engine.generate_recommendations(
    context="security implementation",
    target_domains=[DomainType.TECHNICAL, DomainType.BUSINESS],
    min_relationship_strength=0.5
)
```

### 3. Integration with Workflows

The system is designed to integrate seamlessly with existing workflow engines:

```python
# In a workflow step, generate insights before execution
cross_domain_insights = engine.generate_recommendations(
    context=f"{step.task} {step.context}",
    min_relationship_strength=0.4,
    max_recommendations=2
)

if cross_domain_insights:
    for insight in cross_domain_insights:
        print(f"Cross-domain insight: {insight.title}")

        # Optionally incorporate insights into the task
        if insight.confidence > 0.6:
            enhanced_task = f"{step.task}\n\nCross-domain insight: {insight.explanation[:200]}..."
```

### 4. Performance Optimization

The system includes several performance optimizations:

- **Caching**: Semantic similarities are cached to avoid redundant calculations
- **Entry Limiting**: Maximum number of entries to process can be configured
- **Context Filtering**: Relationships are filtered by relevance to context
- **Early Termination**: Processing stops when maximum recommendations are generated

## Best Practices

1. **Context Relevance**: Always provide context to filter relevant recommendations
2. **Confidence Thresholds**: Adjust `min_relationship_strength` and `min_confidence` based on your tolerance for uncertainty
3. **Domain Focus**: Use `target_domains` to focus analysis on relevant areas
4. **Performance Monitoring**: Monitor performance metrics if analyzing large knowledge bases
5. **Explanation Utilization**: Use explanation methods to understand why recommendations were made