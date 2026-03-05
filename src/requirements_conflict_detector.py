"""
Conflict Detection Module for Requirements Analysis

This module implements algorithms to detect potential conflicts in requirements documentation
including inconsistencies, contradictions, ambiguities, and feasibility issues.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re


class IssueSeverity(Enum):
    """Severity levels for detected issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConflictType(Enum):
    """Types of conflicts that can be detected."""
    CONTRADICTION = "contradiction"
    INCONSISTENCY = "inconsistency"
    AMBIGUITY = "ambiguity"
    FEASIBILITY = "feasibility"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    DUPLICATE_REQUIREMENT = "duplicate_requirement"


@dataclass
class DetectedIssue:
    """Represents a detected conflict or issue in requirements."""
    id: str
    title: str
    description: str
    conflict_type: ConflictType
    severity: IssueSeverity
    affected_requirements: List[str]
    confidence_score: float  # 0.0 to 1.0
    suggested_resolution: str


@dataclass
class ConflictDetectionResult:
    """Result of the conflict detection process."""
    issues: List[DetectedIssue]
    summary: Dict[str, int]  # Count of issues by severity
    report_generated_at: str


class RequirementsConflictDetector:
    """Main class for detecting conflicts in requirements documentation."""

    def __init__(self):
        self.issues_found = []
        self.confidence_threshold = 0.6  # Minimum confidence to report an issue

    def detect_conflicts(self, requirements_text: str) -> ConflictDetectionResult:
        """
        Detect conflicts in requirements documentation.

        Args:
            requirements_text: The requirements documentation text to analyze

        Returns:
            ConflictDetectionResult containing detected issues
        """
        self.issues_found = []

        # Parse requirements from text
        requirements = self._parse_requirements(requirements_text)

        # Run various conflict detection algorithms
        self._detect_contradictions(requirements)
        self._detect_inconsistencies(requirements)
        self._detect_ambiguities(requirements)
        self._detect_feasibility_issues(requirements)
        self._detect_dependency_conflicts(requirements)
        self._detect_duplicate_requirements(requirements)

        # Prepare summary
        summary = self._generate_summary()

        from datetime import datetime
        result = ConflictDetectionResult(
            issues=self.issues_found,
            summary=summary,
            report_generated_at=datetime.now().isoformat()
        )

        return result

    def _parse_requirements(self, text: str) -> List[Dict[str, str]]:
        """
        Parse requirements from text document.

        Args:
            text: Raw requirements text

        Returns:
            List of requirement dictionaries
        """
        requirements = []

        # Look for common requirement formats:
        # - Lines starting with "REQ-" or "RQ-"
        # - Lines with "shall", "should", "must"
        # - Numbered lists with requirement-like statements

        lines = text.split('\n')

        # Regex patterns for different requirement formats
        patterns = [
            r'(REQ-\w+|\w+-\d+):\s*(.+)',  # REQ-001: requirement text
            r'([Rr]equirement\s+[\d.]+):\s*(.+)',  # Requirement 1.1: requirement text
        ]

        req_id_counter = 1

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('=='):
                continue

            # Check for requirement patterns with proper group handling
            found_match = False
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        # Make sure both groups exist
                        if match.lastindex and match.lastindex >= 2:
                            req_id = match.group(1).strip()
                            req_text = match.group(2).strip()

                            requirements.append({
                                'id': req_id,
                                'text': req_text,
                                'line_number': line_num
                            })
                            found_match = True
                            break
                        elif match.lastindex and match.lastindex >= 1:
                            # Only one group, treat as text with auto-generated ID
                            req_text = match.group(1).strip()
                            req_id = f'REQ-{req_id_counter:03d}'
                            req_id_counter += 1

                            requirements.append({
                                'id': req_id,
                                'text': req_text,
                                'line_number': line_num
                            })
                            found_match = True
                            break
                    except IndexError:
                        # Skip if group extraction fails
                        continue

            if not found_match:
                # Check for numbered lists (e.g., "1.2 Requirement text" or "1. Requirement text")
                numbered_pattern = r'^(\d+(?:\.\d+)*\.?)\s+(.+)$'
                numbered_match = re.search(numbered_pattern, line)
                if numbered_match:
                    req_id = f'REQ-{numbered_match.group(1).replace(".", "_").replace("_", "")}'
                    req_text = numbered_match.group(2).strip()

                    requirements.append({
                        'id': req_id,
                        'text': req_text,
                        'line_number': line_num
                    })
                    continue

                # If no specific pattern matched, check for imperative statements
                if any(word in line.lower() for word in ['shall', 'should', 'must', 'require', 'need']):
                    req_id = f'REQ-{req_id_counter:03d}'
                    requirements.append({
                        'id': req_id,
                        'text': line,
                        'line_number': line_num
                    })
                    req_id_counter += 1

        return requirements

    def _detect_contradictions(self, requirements: List[Dict[str, str]]) -> None:
        """Detect contradictory requirements."""
        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements[i+1:], i+1):
                contradiction, confidence = self._check_contradiction(req1['text'], req2['text'])

                if contradiction and confidence >= self.confidence_threshold:
                    issue = DetectedIssue(
                        id=f"CONTR-{i}-{j}",
                        title="Contradictory Requirements",
                        description=f"Requirement {req1['id']} contradicts requirement {req2['id']}: '{req1['text']}' vs '{req2['text']}'",
                        conflict_type=ConflictType.CONTRADICTION,
                        severity=IssueSeverity.HIGH,
                        affected_requirements=[req1['id'], req2['id']],
                        confidence_score=confidence,
                        suggested_resolution=f"Clarify which requirement takes precedence or revise to be compatible."
                    )
                    self.issues_found.append(issue)

    def _check_contradiction(self, text1: str, text2: str) -> Tuple[bool, float]:
        """
        Check if two requirements contradict each other.

        Args:
            text1, text2: Two requirement texts to compare

        Returns:
            Tuple of (is_contradictory, confidence_score)
        """
        # Convert to lowercase for comparison
        t1_lower = text1.lower()
        t2_lower = text2.lower()

        # Look for opposing constraints
        contradiction_indicators = [
            # Opposing quantities
            (r'must.*[><]\s*\d+', r'must.*[<>]\s*\d+'),  # Greater than vs Less than
            (r'should.*be.*at\s+least', r'should.*be.*at\s+most'),
            (r'must.*be.*greater', r'must.*be.*less'),

            # Opposing boolean states
            (r'must.*not', r'must.*'),
            (r'should.*not', r'should.*'),
            (r'prohibited', r'required'),
            (r'forbidden', r'required'),
        ]

        # Check for opposing terms in both directions
        for pattern1, pattern2 in contradiction_indicators:
            if re.search(pattern1, t1_lower) and re.search(pattern2, t2_lower):
                return True, 0.8
            if re.search(pattern2, t1_lower) and re.search(pattern1, t2_lower):
                return True, 0.8

        # Check for direct oppositions
        opposing_pairs = [
            ('required', 'forbidden'),
            ('mandatory', 'optional'),
            ('shall', 'shall not'),
            ('must', 'must not'),
            ('enable', 'disable'),
            ('allow', 'prevent'),
            ('support', 'exclude'),
        ]

        for term1, term2 in opposing_pairs:
            if (term1 in t1_lower and term2 in t2_lower) or \
               (term2 in t1_lower and term1 in t2_lower):
                return True, 0.9

        # Use keyword analysis to detect semantic contradictions
        # This is a simplified version - in a real implementation,
        # you'd want to use NLP techniques
        negative_keywords = ['not', 'never', 'prohibited', 'forbidden', 'without', 'except']
        positive_keywords = ['required', 'needed', 'essential', 'necessary', 'must', 'shall']

        t1_negatives = sum(1 for neg in negative_keywords if neg in t1_lower)
        t2_negatives = sum(1 for neg in negative_keywords if neg in t2_lower)

        t1_positives = sum(1 for pos in positive_keywords if pos in t1_lower)
        t2_positives = sum(1 for pos in positive_keywords if pos in t2_lower)

        # If one is highly negative and the other highly positive
        if (t1_negatives > 0 and t2_positives > 0) or \
           (t2_negatives > 0 and t1_positives > 0):
            return True, 0.7

        return False, 0.0

    def _detect_inconsistencies(self, requirements: List[Dict[str, str]]) -> None:
        """Detect inconsistent requirements."""
        # Group requirements by topic/functionality
        topic_groups = {}

        for req in requirements:
            # Extract potential topics from requirement text
            topics = self._extract_topics(req['text'])
            for topic in topics:
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(req)

        # Check each group for inconsistencies
        for topic, req_group in topic_groups.items():
            if len(req_group) < 2:
                continue  # Need at least 2 requirements to have inconsistency

            for i, req1 in enumerate(req_group):
                for j, req2 in enumerate(req_group[i+1:], i+1):
                    inconsistency, confidence = self._check_inconsistency(req1['text'], req2['text'])

                    if inconsistency and confidence >= self.confidence_threshold:
                        issue = DetectedIssue(
                            id=f"INCONS-{i}-{j}",
                            title="Inconsistent Requirements",
                            description=f"Inconsistent requirements in '{topic}' category: '{req1['text']}' vs '{req2['text']}'",
                            conflict_type=ConflictType.INCONSISTENCY,
                            severity=IssueSeverity.MEDIUM,
                            affected_requirements=[req1['id'], req2['id']],
                            confidence_score=confidence,
                            suggested_resolution=f"Standardize the approach or terminology used in these requirements."
                        )
                        self.issues_found.append(issue)

    def _extract_topics(self, text: str) -> List[str]:
        """Extract potential topics from requirement text."""
        # Common software development topics
        topics = []
        text_lower = text.lower()

        topic_keywords = {
            'authentication': ['login', 'auth', 'authenticate', 'password', 'access'],
            'performance': ['speed', 'fast', 'slow', 'response', 'time', 'delay', 'efficiency'],
            'security': ['secure', 'encrypt', 'protect', 'safe', 'vulnerability', 'privacy'],
            'ui_ux': ['interface', 'display', 'show', 'click', 'button', 'visual'],
            'data': ['store', 'save', 'retrieve', 'database', 'information', 'record'],
            'integration': ['connect', 'api', 'interface', 'communicate', 'exchange'],
            'logging': ['log', 'record', 'track', 'monitor', 'audit'],
            'error_handling': ['handle', 'error', 'exception', 'fail', 'retry'],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics or ['general']

    def _check_inconsistency(self, text1: str, text2: str) -> Tuple[bool, float]:
        """Check if two requirements are inconsistent."""
        # Look for different implementations of the same concept
        t1_lower = text1.lower()
        t2_lower = text2.lower()

        # Check if both refer to similar concepts but with different approaches
        concept_pairs = [
            ('store', 'save'),
            ('display', 'show'),
            ('send', 'transmit'),
            ('receive', 'accept'),
        ]

        inconsistency = False
        confidence = 0.0

        for concept1, concept2 in concept_pairs:
            if concept1 in t1_lower and concept2 in t2_lower:
                inconsistency = True
                confidence = 0.6
                break

        # Check for different technologies or methods
        tech_indicators = [
            (r'use.*mysql', r'use.*postgresql'),
            (r'based on.*xml', r'based on.*json'),
            (r'protocol.*http', r'protocol.*ftp'),
        ]

        for pattern1, pattern2 in tech_indicators:
            if re.search(pattern1, t1_lower) and re.search(pattern2, t2_lower):
                return True, 0.7
            if re.search(pattern2, t1_lower) and re.search(pattern1, t2_lower):
                return True, 0.7

        return inconsistency, confidence

    def _detect_ambiguities(self, requirements: List[Dict[str, str]]) -> None:
        """Detect ambiguous requirements."""
        for req in requirements:
            ambiguity, confidence = self._check_ambiguity(req['text'])

            if ambiguity and confidence >= self.confidence_threshold:
                issue = DetectedIssue(
                    id=f"AMBIG-{req['id']}",
                    title="Ambiguous Requirement",
                    description=f"Requirement {req['id']} contains ambiguous language: '{req['text']}'",
                    conflict_type=ConflictType.AMBIGUITY,
                    severity=IssueSeverity.MEDIUM,
                    affected_requirements=[req['id']],
                    confidence_score=confidence,
                    suggested_resolution="Clarify the requirement with specific, measurable, and unambiguous language."
                )
                self.issues_found.append(issue)

    def _check_ambiguity(self, text: str) -> Tuple[bool, float]:
        """Check if a requirement is ambiguous."""
        # Common ambiguous terms
        ambiguous_terms = [
            'etc.', 'etc', 'etcetera',  # Ambiguous quantity indicators
            'maybe', 'perhaps', 'possibly', 'might', 'could',  # Uncertainty
            'sometimes', 'occasionally', 'usually', 'generally',  # Frequency uncertainty
            'fast', 'quick', 'soon', 'recent', 'old', 'rapid',  # Relative measures
            'big', 'small', 'large', 'tiny', 'huge', 'little',  # Relative sizes
            'often', 'regularly', 'frequently', 'periodically',  # Frequency uncertainty
            'many', 'several', 'numerous', 'few', 'multiple', 'various',  # Quantity uncertainty
            'some', 'part of', 'most', 'majority', 'minority', 'portion',  # Partial indicators
            'best', 'good', 'excellent', 'top', 'prime', 'superior',  # Subjective qualities
            'adequate', 'sufficient', 'reasonable', 'appropriate', 'acceptable',  # Subjective measures
            'as needed', 'when possible', 'if convenient', 'as appropriate',  # Conditional
            'user friendly', 'easy', 'simple', 'intuitive', 'straightforward',  # Subjective properties
            'state of the art', 'modern', 'advanced', 'latest', 'cutting edge',  # Vague descriptors
            'standard', 'usual', 'typical', 'conventional', 'normal',  # Relative standards
        ]

        text_lower = text.lower()

        # Count ambiguous terms
        found_ambiguous_terms = []
        for term in ambiguous_terms:
            if term in text_lower:
                found_ambiguous_terms.append(term)

        if found_ambiguous_terms:
            # Confidence increases with number of ambiguous terms
            confidence = min(0.9, 0.4 + len(found_ambiguous_terms) * 0.15)
            return True, confidence

        # Check for vague quantifiers without specification
        vague_quantifier_patterns = [
            r'some\s+\w+',  # some users, some data
            r'many\s+\w+',  # many users, many records
            r'few\s+\w+',   # few users, few records
            r'most\s+\w+',  # most users, most data
            r'several\s+\w+',  # several users, several records
            r'numerous\s+\w+',  # numerous features
            r'a few\s+\w+',  # a few users
            r'multiple\s+\w+',  # multiple options
            r'various\s+\w+',  # various features
            r'different\s+\w+',  # different users
        ]

        for pattern in vague_quantifier_patterns:
            if re.search(pattern, text_lower):
                return True, 0.7

        # Check for undefined acronyms (simple heuristic)
        acronym_pattern = r'\b([A-Z]{2,4})\b'
        acronyms = re.findall(acronym_pattern, text)

        # Filter out common known acronyms
        common_acronyms = {'API', 'UI', 'UX', 'HTTP', 'HTTPS', 'JSON', 'XML', 'SQL', 'DB', 'CSV', 'PDF', 'HTML', 'CSS'}
        undefined_acronyms = [acronym for acronym in acronyms if acronym not in common_acronyms and len(acronym) > 1]

        if undefined_acronyms:
            return True, 0.6

        # Check for relative comparisons without reference points
        relative_comparison_patterns = [
            r'better.*than',  # Better than what?
            r'faster.*than',  # Faster than what?
            r'higher.*than',  # Higher than what?
            r'lower.*than',   # Lower than what?
            r'more.*than',    # More than what?
            r'less.*than',    # Less than what?
        ]

        for pattern in relative_comparison_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, 0.7

        return False, 0.0

    def _detect_feasibility_issues(self, requirements: List[Dict[str, str]]) -> None:
        """Detect potentially unfeasible requirements."""
        for req in requirements:
            feasibility_issue, confidence = self._check_feasibility(req['text'])

            if feasibility_issue and confidence >= self.confidence_threshold:
                issue = DetectedIssue(
                    id=f"FEAS-{req['id']}",
                    title="Feasibility Concern",
                    description=f"Requirement {req['id']} may be technically unfeasible: '{req['text']}'",
                    conflict_type=ConflictType.FEASIBILITY,
                    severity=IssueSeverity.HIGH,
                    affected_requirements=[req['id']],
                    confidence_score=confidence,
                    suggested_resolution="Investigate technical feasibility and consider alternatives or relaxation of requirements."
                )
                self.issues_found.append(issue)

    def _check_feasibility(self, text: str) -> Tuple[bool, float]:
        """Check if a requirement is potentially unfeasible."""
        text_lower = text.lower()

        # Look for physically impossible or extremely difficult requirements
        feasibility_indicators = [
            (r'immediate.*response', 0.8),  # Immediate response (violates physics)
            (r'infinite.*storage', 0.8),    # Infinite storage
            (r'zero.*latency', 0.8),        # Zero latency
            (r'100%.*uptime', 0.7),         # 100% uptime (impossible in practice)
            (r'instant.*transfer', 0.7),    # Instant transfer
            (r'unlimited.*requests', 0.7),  # Unlimited concurrent requests
        ]

        for pattern, confidence in feasibility_indicators:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, confidence

        # Look for contradictory performance requirements
        perf_conflicts = [
            r'(fast|quick|immediate).*\d+\s*(second|minute|hour)',  # Fast + specific time
            r'high.*throughput.*and.*minimal.*resource',            # High throughput + minimal resources
        ]

        for pattern in perf_conflicts:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, 0.6

        # Check for unrealistic security claims
        security_expressions = [
            r'completely.*secure',
            r'totally.*protected',
            r'100%.*safe',
        ]

        for pattern in security_expressions:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, 0.6

        return False, 0.0

    def _detect_dependency_conflicts(self, requirements: List[Dict[str, str]]) -> None:
        """Detect conflicts in requirement dependencies."""
        # This is a simplified version - real implementation would need
        # to parse dependency relationships more explicitly
        for req in requirements:
            # Look for dependency keywords that might indicate conflicts
            if 'depends on' in req['text'].lower() or 'requires' in req['text'].lower():
                # Check if there are other requirements that conflict with this dependency
                # For simplicity, we'll just flag requirements that seem to create circular dependencies
                # or incompatible technology stacks
                deps = self._extract_dependencies(req['text'])

                if len(deps) > 1:
                    # Check if any of the dependencies conflict with each other
                    for i, dep1 in enumerate(deps):
                        for j, dep2 in enumerate(deps[i+1:], i+1):
                            if self._dependencies_conflict(dep1, dep2):
                                issue = DetectedIssue(
                                    id=f"DEPCONF-{req['id']}-{i}-{j}",
                                    title="Dependency Conflict",
                                    description=f"Requirement {req['id']} has conflicting dependencies: {dep1} vs {dep2}",
                                    conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                                    severity=IssueSeverity.HIGH,
                                    affected_requirements=[req['id']],
                                    confidence_score=0.7,
                                    suggested_resolution=f"Resolve dependency conflict between {dep1} and {dep2}."
                                )
                                self.issues_found.append(issue)

    def _extract_dependencies(self, text: str) -> List[str]:
        """Extract dependencies from requirement text."""
        dependencies = []

        # Look for dependency patterns
        patterns = [
            r'depends\s+on\s+([^.!,;]*)',
            r'requires\s+([^.!,;]*)',
            r'uses\s+([^.!,;]*)',
            r'based\s+on\s+([^.!,;]*)',
        ]

        text_lower = text.lower()

        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Clean up the match and add to dependencies
                cleaned = match.strip().split()[0]  # Take first word as dependency indicator
                if cleaned and cleaned not in dependencies:
                    dependencies.append(cleaned)

        return dependencies

    def _dependencies_conflict(self, dep1: str, dep2: str) -> bool:
        """Check if two dependencies conflict with each other."""
        # Define known conflicting dependencies
        conflicts = {
            ('relational', 'nosql'),
            ('monolithic', 'microservice'),
            ('synchronous', 'asynchronous'),
            ('pull', 'push'),
        }

        # Check if the dependencies are in conflict
        for conflict_pair in conflicts:
            if dep1 in conflict_pair and dep2 in conflict_pair and dep1 != dep2:
                return True

        return False

    def _detect_duplicate_requirements(self, requirements: List[Dict[str, str]]) -> None:
        """Detect duplicate or very similar requirements."""
        seen_texts = {}

        for i, req in enumerate(requirements):
            # Normalize the text for comparison
            normalized_text = self._normalize_text(req['text'])

            # Check if we've seen a similar requirement
            for seen_text, seen_req_id in seen_texts.items():
                similarity = self._calculate_similarity(normalized_text, seen_text)

                if similarity > 0.8:  # 80% similarity threshold
                    issue = DetectedIssue(
                        id=f"DUP-{seen_req_id}-{req['id']}",
                        title="Duplicate Requirement",
                        description=f"Requirements {req['id']} and {seen_req_id} appear to be duplicates: '{req['text']}'",
                        conflict_type=ConflictType.DUPLICATE_REQUIREMENT,
                        severity=IssueSeverity.LOW,
                        affected_requirements=[req['id'], seen_req_id],
                        confidence_score=similarity,
                        suggested_resolution=f"Consider merging or clarifying the difference between these requirements."
                    )
                    self.issues_found.append(issue)

            seen_texts[normalized_text] = req['id']

    def _normalize_text(self, text: str) -> str:
        """Normalize text for similarity comparison."""
        import re

        # Convert to lowercase
        text = text.lower()

        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'may', 'might', 'must', 'can', 'could'
        }

        words = [word for word in re.findall(r'\w+', text) if word not in stop_words]
        return ' '.join(sorted(words))

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0

        # Simple Jaccard similarity
        set1 = set(text1.split())
        set2 = set(text2.split())

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 1.0

        return intersection / union

    def _generate_summary(self) -> Dict[str, int]:
        """Generate a summary of issues by severity."""
        summary = {
            IssueSeverity.CRITICAL.value: 0,
            IssueSeverity.HIGH.value: 0,
            IssueSeverity.MEDIUM.value: 0,
            IssueSeverity.LOW.value: 0
        }

        for issue in self.issues_found:
            summary[issue.severity.value] += 1

        return summary


def generate_conflict_report(result: ConflictDetectionResult) -> str:
    """
    Generate a human-readable report of detected conflicts.

    Args:
        result: ConflictDetectionResult object

    Returns:
        Formatted report string
    """
    report = []
    report.append("# Requirements Conflict Detection Report")
    report.append(f"Generated at: {result.report_generated_at}")
    report.append("")

    # Summary
    report.append("## Summary")
    report.append("| Severity | Count |")
    report.append("|----------|-------|")

    total_issues = 0
    for severity, count in result.summary.items():
        report.append(f"| {severity.title()} | {count} |")
        total_issues += count

    report.append(f"**Total Issues Found: {total_issues}**")
    report.append("")

    # Detailed issues
    report.append("## Detailed Issues")

    if not result.issues:
        report.append("*No conflicts detected.*")
    else:
        for i, issue in enumerate(result.issues, 1):
            report.append(f"### Issue {i}: {issue.title}")
            report.append(f"- **Type:** {issue.conflict_type.value.replace('_', ' ').title()}")
            report.append(f"- **Severity:** {issue.severity.value.upper()}")
            report.append(f"- **Affected Requirements:** {', '.join(issue.affected_requirements)}")
            report.append(f"- **Confidence:** {issue.confidence_score:.2f}")
            report.append(f"- **Description:** {issue.description}")
            report.append(f"- **Suggested Resolution:** {issue.suggested_resolution}")
            report.append("")

    return "\n".join(report)


# Example usage and testing
if __name__ == "__main__":
    # Example requirements with various conflicts
    sample_requirements = """
    # System Requirements Document

    1.0 Authentication Requirements
    1.1 The system shall authenticate users using username and password.
    1.2 The system shall require users to authenticate with biometric verification.
    1.3 User sessions shall expire after 30 minutes of inactivity.

    2.0 Performance Requirements
    2.1 The system shall respond to user requests within 2 seconds.
    2.2 The system must guarantee immediate response for all requests.
    2.3 Database queries should complete in under 5 seconds.

    3.0 Security Requirements
    3.1 The system must encrypt all user data using AES-256 encryption.
    3.2 User passwords shall be stored using bcrypt hashing.
    3.3 All data transmission must be protected with RSA encryption.

    4.0 Usability Requirements
    4.1 The system should be easy to use for users with minimal training.
    4.2 User interface must support advanced customization options.
    4.3 New users should find the system intuitive.

    5.0 Compatibility Requirements
    5.1 The system shall run on Windows operating systems.
    5.2 The system should be deployed on Linux servers.
    5.3 Mobile app required for iOS and Android platforms.

    6.0 Availability Requirements
    6.1 System availability shall be 100% uptime.
    6.2 Regular maintenance windows of 2 hours weekly are acceptable.
    6.3 Backup systems must be available during maintenance.

    7.0 Data Requirements
    7.1 The system shall store user preferences indefinitely.
    7.2 User data older than 5 years shall be purged annually.
    7.3 All user data must be preserved for compliance purposes.

    8.0 Additional Features
    8.1 The system should include reporting functionality.
    8.2 Reporting features required for all modules.
    """

    detector = RequirementsConflictDetector()
    result = detector.detect_conflicts(sample_requirements)

    report = generate_conflict_report(result)
    print(report)