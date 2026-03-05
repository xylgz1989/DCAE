"""Example usage of domain-specific knowledge functionality."""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import dcae modules
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from dcae.core import DCAEOrchestrator
from dcae.knowledge import DomainType
from dcae.knowledge.input_handler import DomainKnowledgeInputHandler


async def main():
    """Demonstrate domain-specific knowledge functionality."""

    print("=" * 60)
    print("DCAE Domain-Specific Knowledge Demo")
    print("=" * 60)

    # Initialize the orchestrator
    orchestrator = DCAEOrchestrator()
    await orchestrator.initialize()

    # Get access to the knowledge base
    kb = orchestrator.get_knowledge_base()
    handler = DomainKnowledgeInputHandler(kb)

    print("\n1. Adding domain-specific knowledge manually:")

    # Add technical knowledge
    tech_entry_id = handler.add_manual_knowledge(
        domain=DomainType.TECHNICAL,
        content="When designing APIs, use consistent naming conventions for endpoints. Prefer plural nouns (e.g., /users instead of /user).",
        source="api_best_practices_guide",
        confidence=0.9,
        metadata={"category": "api_design", "last_updated": "2026-03-02"}
    )
    print(f"   Added technical knowledge with ID: {tech_entry_id}")

    # Add business knowledge
    business_entry_id = handler.add_manual_knowledge(
        domain=DomainType.BUSINESS,
        content="Customer acquisition cost (CAC) should be less than 1/3 of customer lifetime value (LTV) for sustainable growth.",
        source="business_metrics_handbook",
        confidence=0.85,
        metadata={"industry": "SaaS", "reference": "growth_hacking_principles"}
    )
    print(f"   Added business knowledge with ID: {business_entry_id}")

    # Add regulatory knowledge
    regulatory_entry_id = handler.add_manual_knowledge(
        domain=DomainType.REGULATORY,
        content="GDPR requires explicit consent for processing personal data. Users must be informed about data collection and have the right to deletion.",
        source="gdpr_compliance_manual",
        confidence=0.95,
        metadata={"jurisdiction": "EU", "regulation": "GDPR", "article": "5-17"}
    )
    print(f"   Added regulatory knowledge with ID: {regulatory_entry_id}")

    print("\n2. Retrieving knowledge by domain:")

    # Get technical knowledge
    tech_knowledge = kb.get_knowledge(domain=DomainType.TECHNICAL)
    print(f"   Retrieved {len(tech_knowledge)} technical knowledge entries")
    for entry in tech_knowledge:
        print(f"     - {entry.content[:60]}...")

    # Get business knowledge
    business_knowledge = kb.get_knowledge(domain=DomainType.BUSINESS)
    print(f"   Retrieved {len(business_knowledge)} business knowledge entries")
    for entry in business_knowledge:
        print(f"     - {entry.content[:60]}...")

    print("\n3. Searching for specific knowledge:")

    # Search for API-related knowledge
    api_knowledge = kb.search_knowledge("API", domain=DomainType.TECHNICAL)
    print(f"   Found {len(api_knowledge)} API-related technical entries")
    for entry in api_knowledge:
        print(f"     - {entry.content}")
        print(f"       (Source: {entry.source}, Confidence: {entry.confidence})")

    print("\n4. Demonstrating knowledge fusion in a workflow:")

    # Create a sample workflow step that would benefit from domain knowledge
    sample_task = "Design an API endpoint for user management"
    sample_context = "We're building a user management system that needs to comply with GDPR regulations."

    print(f"   Original task: {sample_task}")
    print(f"   Context: {sample_context}")

    # Integrate knowledge
    fusion_engine = orchestrator.get_knowledge_fusion_engine()
    enhanced_task = fusion_engine.integrate_knowledge(
        prompt=sample_task,
        context=sample_context,
        domain=DomainType.TECHNICAL
    )

    print(f"   Enhanced task with domain knowledge:")
    print(f"     {enhanced_task[:200]}...")

    print("\n5. Importing knowledge from a file (demo):")

    # Create a temporary knowledge file
    demo_knowledge = [
        {
            "content": "Security best practices include using HTTPS, implementing proper authentication, and sanitizing user inputs.",
            "source": "security_guide",
            "confidence": 0.92,
            "metadata": {"category": "security", "level": "beginner"}
        },
        {
            "content": "Performance optimization techniques include caching, database indexing, and asynchronous processing.",
            "source": "perf_tuning_manual",
            "confidence": 0.88,
            "metadata": {"category": "performance", "level": "intermediate"}
        }
    ]

    import json
    temp_file = Path("temp_knowledge.json")
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(demo_knowledge, f, indent=2)

    # Import the knowledge
    imported_count = handler.import_from_file(
        temp_file,
        DomainType.TECHNICAL,
        source="demo_import"
    )
    print(f"   Imported {imported_count} knowledge entries from file")

    # Clean up
    temp_file.unlink()

    print("\n6. Showing all technical knowledge after import:")
    all_tech_knowledge = kb.get_knowledge(domain=DomainType.TECHNICAL)
    print(f"   Total technical knowledge entries: {len(all_tech_knowledge)}")
    for i, entry in enumerate(all_tech_knowledge, 1):
        print(f"     {i}. {entry.content[:50]}...")
        print(f"         Confidence: {entry.confidence}, Source: {entry.source}")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())