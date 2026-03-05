"""
Review Correlation Engine Module

This module implements the correlation engine that identifies relationships between
findings from different review modules in the DCAE framework.
"""
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
from collections import defaultdict
import hashlib


class CorrelationType(Enum):
    """Types of correlations between review findings."""
    SAME_FILE = "same_file"
    SAME_ISSUE_TYPE = "same_issue_type"
    SAME_CODE_PATTERN = "same_code_pattern"
    SAME_SEVERITY = "same_severity"
    ROOT_CAUSE_LINK = "root_cause_link"
    IMPACT_CHAIN = "impact_chain"


@dataclass
class Finding:
    """Represents a finding from any review module."""
    id: str
    module: str  # Which review module generated this finding
    category: str
    severity: str
    file_path: str
    line_number: int
    issue_description: str
    recommendation: str
    code_snippet: str
    additional_metadata: Optional[Dict[str, Any]] = None

    def get_signature(self) -> str:
        """Generate a signature for this finding based on its properties."""
        # Create a signature based on key identifying properties
        sig_str = f"{self.category}|{self.issue_description}|{self.file_path}|{self.line_number}"
        return hashlib.md5(sig_str.encode()).hexdigest()


@dataclass
class Correlation:
    """Represents a correlation between two or more findings."""
    correlation_id: str
    correlation_type: CorrelationType
    finding_ids: List[str]
    strength: float  # 0.0 to 1.0
    description: str
    supporting_evidence: List[str]


class ReviewCorrelationEngine:
    """Engine that correlates findings from different review modules."""

    def __init__(self):
        self.findings: List[Finding] = []
        self.correlations: List[Correlation] = []
        self.pattern_matchers = {
            "hardcoded_credentials": [
                r"(password|secret|token|key|credential|auth|login|pass|pwd|api_key|client_secret)\s*[=:]\s*['\"].*['\"]",
                r"(os\.environ\.get\(['\"]\w*password\w*['\"],?\s*['\"].*['\"]?\))"
            ],
            "sql_injection": [
                r"(cursor\.execute|execute\(|conn\.execute|db\.query).*\+",
                r"(f\".*\{.*\}.*\")",
                r"(\+.*\+)"
            ],
            "nested_loops": [
                r"(for\s+\w+\s+in\s+.*)[\s\n\r]*.*for\s+\w+\s+in\s+",
                r"(while\s+.*)[\s\n\r]*.*for\s+\w+\s+in\s+"
            ]
        }

    def add_finding(self, finding: Finding) -> None:
        """Add a finding from any review module."""
        self.findings.append(finding)

    def add_findings(self, findings: List[Finding]) -> None:
        """Add multiple findings from any review module."""
        self.findings.extend(findings)

    def calculate_correlation_strength(self, finding1: Finding, finding2: Finding) -> Tuple[CorrelationType, float, str]:
        """
        Calculate the correlation strength between two findings.

        Returns:
            Tuple of (correlation_type, strength, description)
        """
        correlations = []

        # Check for same file correlation
        if finding1.file_path == finding2.file_path:
            # Higher correlation if they're on the same or nearby lines
            line_diff = abs(finding1.line_number - finding2.line_number)
            strength = max(0.5, 1.0 - (line_diff * 0.1))  # Higher correlation for nearby lines
            desc = f"Both findings in same file: {finding1.file_path}"
            correlations.append((CorrelationType.SAME_FILE, strength, desc))

        # Check for same issue type (based on category)
        if finding1.category == finding2.category:
            strength = 0.8
            desc = f"Both findings related to {finding1.category}"
            correlations.append((CorrelationType.SAME_ISSUE_TYPE, strength, desc))

        # Check for similar issue descriptions (fuzzy matching)
        if self._is_similar_text(finding1.issue_description, finding2.issue_description):
            strength = 0.7
            desc = f"Similar issue descriptions: '{finding1.issue_description[:30]}...' and '{finding2.issue_description[:30]}...'"
            correlations.append((CorrelationType.SAME_ISSUE_TYPE, strength, desc))

        # Check for same severity
        if finding1.severity == finding2.severity:
            strength = 0.6
            desc = f"Both findings have {finding1.severity} severity"
            correlations.append((CorrelationType.SAME_SEVERITY, strength, desc))

        # Check for pattern correlation
        for pattern_type, patterns in self.pattern_matchers.items():
            pattern1_match = self._matches_any_pattern(finding1.issue_description, patterns) or \
                             self._matches_any_pattern(finding1.code_snippet, patterns)
            pattern2_match = self._matches_any_pattern(finding2.issue_description, patterns) or \
                             self._matches_any_pattern(finding2.code_snippet, patterns)

            if pattern1_match and pattern2_match:
                strength = 0.9
                desc = f"Both findings match {pattern_type} pattern"
                correlations.append((CorrelationType.SAME_CODE_PATTERN, strength, desc))

        # Return the strongest correlation
        if correlations:
            return max(correlations, key=lambda x: x[1])

        return CorrelationType.SAME_FILE, 0.0, "No significant correlation found"

    def _is_similar_text(self, text1: str, text2: str, threshold: float = 0.6) -> bool:
        """Check if two texts are similar using a simple similarity algorithm."""
        # Simple word overlap method
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return False

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        jaccard_similarity = len(intersection) / len(union)
        return jaccard_similarity >= threshold

    def _matches_any_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns."""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def find_correlations(self) -> List[Correlation]:
        """Find all correlations between the stored findings."""
        self.correlations = []

        if len(self.findings) < 2:
            return []

        # Compare every pair of findings
        for i in range(len(self.findings)):
            for j in range(i + 1, len(self.findings)):
                finding1 = self.findings[i]
                finding2 = self.findings[j]

                corr_type, strength, desc = self.calculate_correlation_strength(finding1, finding2)

                # Only include correlations above a threshold
                if strength > 0.3:
                    correlation = Correlation(
                        correlation_id=f"corr_{finding1.id}_{finding2.id}",
                        correlation_type=corr_type,
                        finding_ids=[finding1.id, finding2.id],
                        strength=strength,
                        description=desc,
                        supporting_evidence=[
                            f"Finding 1: {finding1.issue_description}",
                            f"Finding 2: {finding2.issue_description}"
                        ]
                    )
                    self.correlations.append(correlation)

        # Sort by strength (highest first)
        self.correlations.sort(key=lambda x: x.strength, reverse=True)

        return self.correlations

    def get_grouped_correlations(self) -> Dict[str, List[Correlation]]:
        """Group correlations by type."""
        grouped = defaultdict(list)
        for correlation in self.correlations:
            grouped[correlation.correlation_type.value].append(correlation)
        return dict(grouped)

    def get_high_correlation_groups(self, threshold: float = 0.7) -> List[List[Finding]]:
        """
        Group findings that have high correlation between them.

        Returns:
            List of groups, where each group is a list of correlated findings
        """
        high_corr_correlations = [c for c in self.correlations if c.strength >= threshold]

        # Find connected components in the correlation graph
        groups = []
        visited = set()

        for correlation in high_corr_correlations:
            # Find the findings involved in this correlation
            current_group = []
            for finding_id in correlation.finding_ids:
                if finding_id not in visited:
                    finding = next((f for f in self.findings if f.id == finding_id), None)
                    if finding:
                        current_group.append(finding)
                        visited.add(finding_id)

            if current_group:
                # Check if this group overlaps with an existing group
                merged = False
                for i, existing_group in enumerate(groups):
                    if any(f.id in [ef.id for ef in existing_group] for f in current_group):
                        # Merge groups
                        for f in current_group:
                            if f not in existing_group:
                                existing_group.append(f)
                        merged = True
                        break

                if not merged:
                    groups.append(current_group)

        # Add any remaining findings as individual groups
        for finding in self.findings:
            if finding.id not in visited:
                groups.append([finding])

        return groups

    def deduplicate_findings(self) -> List[Finding]:
        """
        Remove duplicate findings based on correlation analysis.

        Returns:
            List of deduplicated findings with merged information where appropriate
        """
        # Group highly correlated findings
        correlated_groups = self.get_high_correlation_groups(threshold=0.8)

        deduplicated = []

        for group in correlated_groups:
            if len(group) == 1:
                # Single finding, just add it
                deduplicated.append(group[0])
            else:
                # Multiple correlated findings, merge them
                representative = self._merge_findings(group)
                deduplicated.append(representative)

        return deduplicated

    def _merge_findings(self, findings: List[Finding]) -> Finding:
        """Merge a group of correlated findings into a single finding."""
        # Use the first finding as a base
        base = findings[0]

        # Collect all unique recommendations and evidence
        all_recommendations = [f.recommendation for f in findings if f.recommendation]
        all_snippets = [f.code_snippet for f in findings if f.code_snippet]

        # Create a merged recommendation
        merged_recommendation = "; ".join(list(set(all_recommendations)))

        # Create a merged code snippet (if they're from the same location)
        merged_snippet = "; ".join(list(set(all_snippets)))[:500]  # Limit length

        # Create a composite ID
        merged_id = "_".join([f.id for f in findings])[:100]

        # Determine the most severe severity among the group
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        most_severe = max([f.severity for f in findings],
                         key=lambda s: severity_order.get(s, 0))

        return Finding(
            id=merged_id,
            module=f"Merged({','.join(list(set([f.module for f in findings]))[:3])})",  # Limit module names
            category=base.category,  # Keep base category
            severity=most_severe,  # Use the most severe
            file_path=base.file_path,
            line_number=min([f.line_number for f in findings]),  # Use earliest line
            issue_description=f"Merged findings: {base.issue_description}",
            recommendation=merged_recommendation or base.recommendation,
            code_snippet=merged_snippet or base.code_snippet,
            additional_metadata={
                "merged_from": [f.id for f in findings],
                "original_modules": list(set([f.module for f in findings])),
                "merge_count": len(findings)
            }
        )

    def get_correlation_report(self) -> Dict[str, Any]:
        """Generate a report of correlations found."""
        total_findings = len(self.findings)
        total_correlations = len(self.correlations)
        high_correlations = len([c for c in self.correlations if c.strength >= 0.7])
        deduplicated_findings = len(self.deduplicate_findings())

        grouped_correlations = self.get_grouped_correlations()

        report = {
            "summary": {
                "total_findings": total_findings,
                "total_correlations": total_correlations,
                "high_correlations": high_correlations,  # Correlations with strength >= 0.7
                "deduplicated_findings": deduplicated_findings,
                "potential_duplicates_removed": total_findings - deduplicated_findings
            },
            "by_type": {
                corr_type: len(cors) for corr_type, cors in grouped_correlations.items()
            },
            "top_correlations": [
                {
                    "type": corr.correlation_type.value,
                    "strength": corr.strength,
                    "description": corr.description,
                    "finding_ids": corr.finding_ids
                }
                for corr in self.correlations[:10]  # Top 10 correlations
            ]
        }

        return report


def main():
    """Example usage of the correlation engine."""
    # Create a correlation engine
    engine = ReviewCorrelationEngine()

    # Add some sample findings
    finding1 = Finding(
        id="gen_sec_001",
        module="generated_output_review",
        category="security",
        severity="high",
        file_path="src/app.py",
        line_number=15,
        issue_description="Hardcoded credential found in code",
        recommendation="Move credentials to environment variables",
        code_snippet='password = "secret123"'
    )

    finding2 = Finding(
        id="rules_sec_001",
        module="rules_engine_review",
        category="security",
        severity="critical",
        file_path="src/app.py",
        line_number=15,
        issue_description="Detected hardcoded password assignment",
        recommendation="Use secure configuration management",
        code_snippet='password = "secret123"'
    )

    finding3 = Finding(
        id="gen_perform_001",
        module="generated_output_review",
        category="performance",
        severity="medium",
        file_path="src/utils.py",
        line_number=42,
        issue_description="Nested loops detected causing O(n^2) complexity",
        recommendation="Consider algorithm optimization",
        code_snippet="for i in data:\n    for j in data:"
    )

    finding4 = Finding(
        id="gen_quality_001",
        module="generated_output_review",
        category="code_quality",
        severity="low",
        file_path="src/app.py",
        line_number=20,
        issue_description="TODO comment found in code",
        recommendation="Address the TODO before finalizing the code",
        code_snippet="# TODO: Refactor this function"
    )

    # Add findings to the engine
    engine.add_findings([finding1, finding2, finding3, finding4])

    print("DCAE Review & Quality Assurance - Correlation Engine")
    print("="*60)

    # Find correlations
    correlations = engine.find_correlations()

    print(f"Found {len(correlations)} correlations between findings")

    # Show correlation report
    report = engine.get_correlation_report()
    print(f"\nCorrelation Summary:")
    print(f"  Total Findings: {report['summary']['total_findings']}")
    print(f"  Total Correlations: {report['summary']['total_correlations']}")
    print(f"  High Correlations (>0.7): {report['summary']['high_correlations']}")
    print(f"  Deduplicated Findings: {report['summary']['deduplicated_findings']}")
    print(f"  Potential Duplicates Removed: {report['summary']['potential_duplicates_removed']}")

    print(f"\nCorrelations by Type:")
    for corr_type, count in report['by_type'].items():
        print(f"  {corr_type}: {count}")

    print(f"\nTop Correlations:")
    for corr in report['top_correlations'][:3]:  # Show top 3
        print(f"  {corr['type']}: Strength {corr['strength']:.2f}")
        print(f"    Description: {corr['description']}")
        print(f"    Findings: {', '.join(corr['finding_ids'])}")

    # Show deduplicated findings
    deduplicated = engine.deduplicate_findings()
    print(f"\nAfter deduplication: {len(deduplicated)} findings remain from {len(engine.findings)} originals")

    print("\nCorrelation engine demonstration completed!")


if __name__ == "__main__":
    main()