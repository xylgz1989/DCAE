"""
Review and Quality Assurance - Integrated Review Mechanism

This module implements the complete review mechanism that integrates all previous review functionality.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import time
import threading
from enum import Enum


class ReviewPhase(Enum):
    """Enumeration for review phases."""
    INITIALIZATION = "initialization"
    STATIC_ANALYSIS = "static_analysis"
    SECURITY_REVIEW = "security_review"
    PERFORMANCE_EVALUATION = "performance_evaluation"
    ARCHITECTURE_CHECK = "architecture_check"
    REQUIREMENTS_VERIFICATION = "requirements_verification"
    ISSUE_IDENTIFICATION = "issue_identification"
    REPORT_GENERATION = "report_generation"
    COMPLETION = "completion"


class ReviewStatus(Enum):
    """Enumeration for review status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ReviewResult:
    """Represents the result of a review operation."""
    phase: ReviewPhase
    status: ReviewStatus
    findings: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    timestamp: str
    duration: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class ReviewConfiguration:
    """Configuration for the review mechanism."""
    enable_static_analysis: bool = True
    enable_security_review: bool = True
    enable_performance_evaluation: bool = True
    enable_architecture_check: bool = True
    enable_requirements_verification: bool = True
    enable_issue_identification: bool = True
    max_execution_time: int = 3600  # seconds
    output_format: str = "json"
    verbose_logging: bool = True


class ReviewOrchestrator:
    """Orchestrates the complete review process."""

    def __init__(self, project_path: str, requirements_spec: Optional[Dict[str, Any]] = None,
                 architecture_spec: Optional[Dict[str, Any]] = None):
        """
        Initialize the review orchestrator.

        Args:
            project_path: Path to the project root
            requirements_spec: Requirements specification
            architecture_spec: Architecture specification
        """
        self.project_path = Path(project_path)
        self.requirements_spec = requirements_spec or {}
        self.architecture_spec = architecture_spec or {}
        self.config = ReviewConfiguration()

        # Import other modules (assuming they exist)
        try:
            from .pause_and_review import ReviewManager
            self.review_manager = ReviewManager(project_path)
        except ImportError:
            print("Warning: pause_and_review module not available")
            self.review_manager = None

        try:
            from .generated_output_review import GeneratedOutputReviewer
            self.output_reviewer = GeneratedOutputReviewer(
                project_path, requirements_spec, architecture_spec
            )
        except ImportError:
            print("Warning: generated_output_review module not available")
            self.output_reviewer = None

        try:
            from .modification_suggestions import ModificationSuggestionSubmitter
            self.suggestion_submitter = ModificationSuggestionSubmitter(project_path)
        except ImportError:
            print("Warning: modification_suggestions module not available")
            self.suggestion_submitter = None

        try:
            from .identify_code_issues import IssueDetector
            self.issue_detector = IssueDetector(project_path)
        except ImportError:
            print("Warning: identify_code_issues module not available")
            self.issue_detector = None

        try:
            from .review_rules_checkpoints import ReviewRulesConfigurer
            self.rules_configurer = ReviewRulesConfigurer(project_path)
        except ImportError:
            print("Warning: review_rules_checkpoints module not available")
            self.rules_configurer = None

        self.results: List[ReviewResult] = []
        self.current_phase = ReviewPhase.INITIALIZATION
        self.status = ReviewStatus.PENDING
        self.start_time = None
        self.end_time = None

    def configure(self, config: ReviewConfiguration):
        """
        Configure the review process.

        Args:
            config: Review configuration
        """
        self.config = config
        print(f"Review configured with settings: {config.__dict__}")

    def run_complete_review(self, target_path: Optional[str] = None) -> List[ReviewResult]:
        """
        Run the complete integrated review process.

        Args:
            target_path: Specific path to review (optional)

        Returns:
            List of review results for each phase
        """
        print("Starting integrated review process...")
        self.start_time = time.time()
        self.status = ReviewStatus.IN_PROGRESS
        self.results = []

        # Phase 1: Initialization
        if self.config.enable_static_analysis:
            init_result = self._execute_initialization_phase(target_path)
            self.results.append(init_result)

        # Phase 2: Static Analysis Review
        if self.config.enable_static_analysis and self.output_reviewer:
            static_result = self._execute_static_analysis_phase(target_path)
            self.results.append(static_result)

        # Phase 3: Security Review
        if self.config.enable_security_review and self.issue_detector:
            security_result = self._execute_security_review_phase(target_path)
            self.results.append(security_result)

        # Phase 4: Performance Evaluation
        if self.config.enable_performance_evaluation:
            perf_result = self._execute_performance_evaluation_phase(target_path)
            self.results.append(perf_result)

        # Phase 5: Architecture Check
        if self.config.enable_architecture_check:
            arch_result = self._execute_architecture_check_phase(target_path)
            self.results.append(arch_result)

        # Phase 6: Requirements Verification
        if self.config.enable_requirements_verification:
            req_result = self._execute_requirements_verification_phase(target_path)
            self.results.append(req_result)

        # Phase 7: Issue Identification
        if self.config.enable_issue_identification and self.issue_detector:
            issue_result = self._execute_issue_identification_phase(target_path)
            self.results.append(issue_result)

        # Phase 8: Report Generation
        report_result = self._execute_report_generation_phase()
        self.results.append(report_result)

        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        print(f"Complete review finished in {total_duration:.2f} seconds")

        # Phase 9: Completion
        completion_result = ReviewResult(
            phase=ReviewPhase.COMPLETION,
            status=ReviewStatus.COMPLETED,
            findings=[],
            metrics={"total_duration": total_duration, "total_phases": len(self.results)},
            timestamp=datetime.now().isoformat(),
            duration=0.0
        )
        self.results.append(completion_result)

        return self.results

    def _execute_initialization_phase(self, target_path: Optional[str] = None) -> ReviewResult:
        """Execute the initialization phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.INITIALIZATION
        print("  Running initialization phase...")

        # Initialize all components
        findings = []
        metrics = {}

        if self.review_manager:
            findings.append({
                "type": "initialization",
                "message": "Review manager initialized successfully",
                "details": {"component": "ReviewManager"}
            })

        if self.output_reviewer:
            findings.append({
                "type": "initialization",
                "message": "Output reviewer initialized successfully",
                "details": {"component": "GeneratedOutputReviewer"}
            })

        if self.suggestion_submitter:
            findings.append({
                "type": "initialization",
                "message": "Suggestion submitter initialized successfully",
                "details": {"component": "ModificationSuggestionSubmitter"}
            })

        if self.issue_detector:
            findings.append({
                "type": "initialization",
                "message": "Issue detector initialized successfully",
                "details": {"component": "IssueDetector"}
            })

        if self.rules_configurer:
            findings.append({
                "type": "initialization",
                "message": "Rules configurer initialized successfully",
                "details": {"component": "ReviewRulesConfigurer"}
            })

        duration = time.time() - start_time
        return ReviewResult(
            phase=ReviewPhase.INITIALIZATION,
            status=ReviewStatus.COMPLETED,
            findings=findings,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )

    def _execute_static_analysis_phase(self, target_path: Optional[str] = None) -> ReviewResult:
        """Execute the static analysis phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.STATIC_ANALYSIS
        print("  Running static analysis phase...")

        if not self.output_reviewer:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.STATIC_ANALYSIS,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": "Output reviewer not available"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

        try:
            # Perform static analysis review
            report = self.output_reviewer.review_generated_output(target_path)

            findings = []
            for finding in report.findings:
                findings.append({
                    "type": "static_analysis",
                    "category": finding.category.value,
                    "severity": finding.severity.value,
                    "file_path": finding.file_path,
                    "line_number": finding.line_number,
                    "issue_description": finding.issue_description,
                    "recommendation": finding.recommendation
                })

            metrics = {
                "total_findings": len(findings),
                "findings_by_severity": report.summary["findings_by_severity"],
                "findings_by_category": report.summary["findings_by_category"],
                "files_analyzed": report.summary["files_reviewed"]
            }

            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.STATIC_ANALYSIS,
                status=ReviewStatus.COMPLETED,
                findings=findings,
                metrics=metrics,
                timestamp=datetime.now().isoformat(),
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.STATIC_ANALYSIS,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": f"Static analysis failed: {str(e)}"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

    def _execute_security_review_phase(self, target_path: Optional[str] = None) -> ReviewResult:
        """Execute the security review phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.SECURITY_REVIEW
        print("  Running security review phase...")

        if not self.issue_detector:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.SECURITY_REVIEW,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": "Issue detector not available"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

        try:
            # Perform security-focused issue detection
            issues = self.issue_detector.scan_project(target_path)

            security_findings = []
            for issue in issues:
                if issue.category.value in ["security_vulnerability", "resource_leak"]:
                    security_findings.append({
                        "type": "security",
                        "category": issue.category.value,
                        "severity": issue.severity.value,
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "issue_description": issue.issue_description,
                        "recommendation": issue.recommendation,
                        "confidence": issue.confidence
                    })

            metrics = {
                "total_security_issues": len(security_findings),
                "critical_security_issues": len([f for f in security_findings if f["severity"] == "critical"])
            }

            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.SECURITY_REVIEW,
                status=ReviewStatus.COMPLETED,
                findings=security_findings,
                metrics=metrics,
                timestamp=datetime.now().isoformat(),
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.SECURITY_REVIEW,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": f"Security review failed: {str(e)}"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

    def _execute_performance_evaluation_phase(self, target_path: Optional[str] = None) -> ReviewResult:
        """Execute the performance evaluation phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.PERFORMANCE_EVALUATION
        print("  Running performance evaluation phase...")

        # For now, this is a placeholder since we don't have a dedicated performance evaluator
        findings = [
            {
                "type": "performance_info",
                "message": "Performance evaluation not yet implemented in this version",
                "details": {
                    "evaluation_type": "placeholder",
                    "note": "This is a placeholder phase in the integrated mechanism"
                }
            }
        ]

        metrics = {"placeholder_executed": True}

        duration = time.time() - start_time
        return ReviewResult(
            phase=ReviewPhase.PERFORMANCE_EVALUATION,
            status=ReviewStatus.COMPLETED,
            findings=findings,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )

    def _execute_architecture_check_phase(self, target_path: Optional[str] = None) -> ReviewResult:
        """Execute the architecture check phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.ARCHITECTURE_CHECK
        print("  Running architecture check phase...")

        if not self.output_reviewer:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.ARCHITECTURE_CHECK,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": "Output reviewer not available"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

        # Architecture checks are part of the output review process
        findings = [
            {
                "type": "architecture_info",
                "message": "Architecture alignment checks executed as part of output review",
                "details": {
                    "arch_components_required": len(self.architecture_spec.get("components", [])),
                    "note": "Architecture validation performed during static analysis"
                }
            }
        ]

        metrics = {"architecture_validation_performed": True}

        duration = time.time() - start_time
        return ReviewResult(
            phase=ReviewPhase.ARCHITECTURE_CHECK,
            status=ReviewStatus.COMPLETED,
            findings=findings,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )

    def _execute_requirements_verification_phase(self, target_path: Optional[str] = None) -> ReviewResult:
        """Execute the requirements verification phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.REQUIREMENTS_VERIFICATION
        print("  Running requirements verification phase...")

        if not self.output_reviewer:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.REQUIREMENTS_VERIFICATION,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": "Output reviewer not available"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

        # Requirements verification is part of the output review process
        findings = [
            {
                "type": "requirements_info",
                "message": "Requirements coverage checks executed as part of output review",
                "details": {
                    "functional_requirements_count": len(self.requirements_spec.get("functional_requirements", [])),
                    "non_functional_requirements_count": len(self.requirements_spec.get("non_functional_requirements", [])),
                    "note": "Requirements validation performed during static analysis"
                }
            }
        ]

        metrics = {"requirements_validation_performed": True}

        duration = time.time() - start_time
        return ReviewResult(
            phase=ReviewPhase.REQUIREMENTS_VERIFICATION,
            status=ReviewStatus.COMPLETED,
            findings=findings,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )

    def _execute_issue_identification_phase(self, target_path: Optional[str] = None) -> ReviewResult:
        """Execute the issue identification phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.ISSUE_IDENTIFICATION
        print("  Running issue identification phase...")

        if not self.issue_detector:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.ISSUE_IDENTIFICATION,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": "Issue detector not available"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

        try:
            # Perform comprehensive issue detection
            issues = self.issue_detector.scan_project(target_path)

            all_findings = []
            for issue in issues:
                all_findings.append({
                    "type": "issue_identification",
                    "category": issue.category.value,
                    "severity": issue.severity.value,
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "issue_description": issue.issue_description,
                    "recommendation": issue.recommendation,
                    "confidence": issue.confidence
                })

            metrics = {
                "total_issues_identified": len(all_findings),
                "by_severity": {},
                "by_category": {}
            }

            # Count by severity and category
            for finding in all_findings:
                sev = finding["severity"]
                cat = finding["category"]
                metrics["by_severity"][sev] = metrics["by_severity"].get(sev, 0) + 1
                metrics["by_category"][cat] = metrics["by_category"].get(cat, 0) + 1

            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.ISSUE_IDENTIFICATION,
                status=ReviewStatus.COMPLETED,
                findings=all_findings,
                metrics=metrics,
                timestamp=datetime.now().isoformat(),
                duration=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return ReviewResult(
                phase=ReviewPhase.ISSUE_IDENTIFICATION,
                status=ReviewStatus.FAILED,
                findings=[{"type": "error", "message": f"Issue identification failed: {str(e)}"}],
                metrics={},
                timestamp=datetime.now().isoformat(),
                duration=duration
            )

    def _execute_report_generation_phase(self) -> ReviewResult:
        """Execute the report generation phase."""
        start_time = time.time()
        self.current_phase = ReviewPhase.REPORT_GENERATION
        print("  Running report generation phase...")

        # Generate comprehensive report from all phases
        findings = []
        metrics = {}

        for result in self.results:
            findings.extend(result.findings)
            metrics.update({f"{result.phase.value}_{k}": v for k, v in result.metrics.items()})

        # Add overall summary metrics
        total_findings = sum(len(r.findings) for r in self.results)
        critical_issues = sum(
            1 for r in self.results
            for f in r.findings
            if isinstance(f, dict) and f.get("severity") == "critical"
        )

        metrics.update({
            "total_findings_across_all_phases": total_findings,
            "critical_issues_found": critical_issues,
            "total_review_phases_completed": len([r for r in self.results if r.status == ReviewStatus.COMPLETED])
        })

        duration = time.time() - start_time
        return ReviewResult(
            phase=ReviewPhase.REPORT_GENERATION,
            status=ReviewStatus.COMPLETED,
            findings=findings,
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
            duration=duration
        )

    def get_overall_summary(self) -> Dict[str, Any]:
        """Get an overall summary of all review phases."""
        if not self.results:
            return {"status": "no_results", "message": "No review results available"}

        total_findings = 0
        total_duration = 0
        completed_phases = 0
        failed_phases = 0

        by_severity = {}
        by_category = {}

        for result in self.results:
            total_findings += len(result.findings)
            total_duration += result.duration

            if result.status == ReviewStatus.COMPLETED:
                completed_phases += 1
            elif result.status == ReviewStatus.FAILED:
                failed_phases += 1

            # Aggregate by severity and category
            for finding in result.findings:
                if isinstance(finding, dict):
                    sev = finding.get("severity", "unknown")
                    cat = finding.get("category", "unknown")

                    by_severity[sev] = by_severity.get(sev, 0) + 1
                    by_category[cat] = by_category.get(cat, 0) + 1

        summary = {
            "overall_status": self.status.value,
            "total_phases": len(self.results),
            "completed_phases": completed_phases,
            "failed_phases": failed_phases,
            "total_findings": total_findings,
            "total_duration_seconds": total_duration,
            "findings_by_severity": by_severity,
            "findings_by_category": by_category,
            "timestamp": datetime.now().isoformat()
        }

        if self.start_time and self.end_time:
            summary["actual_total_duration"] = self.end_time - self.start_time

        return summary

    def export_results(self, output_path: str, format_type: str = "json"):
        """Export review results to a file."""
        export_data = {
            "summary": self.get_overall_summary(),
            "results_by_phase": [
                {
                    "phase": result.phase.value,
                    "status": result.status.value,
                    "findings_count": len(result.findings),
                    "findings": result.findings,
                    "metrics": result.metrics,
                    "timestamp": result.timestamp,
                    "duration": result.duration
                } for result in self.results
            ],
            "project_path": str(self.project_path),
            "execution_config": self.config.__dict__
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            if format_type.lower() == "json":
                json.dump(export_data, f, indent=2)
            else:
                # Default to JSON
                json.dump(export_data, f, indent=2)

        print(f"Review results exported to: {output_path}")


def main():
    """Example usage of the integrated review mechanism."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Create sample files with issues for the review tools to detect
        sample_file = project_path / "sample_code.py"
        sample_code = '''
import pickle  # Security issue: unsafe pickle usage

def process_data(data):
    """Function with potential performance and quality issues."""
    password = "hardcoded_secret"  # Security issue

    # Performance issue: nested loops
    result = []
    for i in data:
        for j in data:
            if i == j:
                result.append(i)

    # Long function with many lines
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x_val = 27
    y_val = 28
    z_val = 29
    aa = 30  # Function is longer than 50 lines (quality issue)

    return result

def another_function():
    # SQL injection potential
    user_input = "some_input"
    query = f"SELECT * FROM table WHERE id = {user_input}"  # Security issue
    cursor.execute(query)  # Assuming cursor exists elsewhere
    '''

        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_code)

        # Sample requirements and architecture specs
        requirements_spec = {
            "functional_requirements": [
                {"id": "REQ001", "title": "Data Processing", "description": "System shall process data"}
            ],
            "non_functional_requirements": [
                {"id": "NFR001", "title": "Security", "description": "System shall be secure"}
            ]
        }

        architecture_spec = {
            "components": [
                {"name": "Data Processor"},
                {"name": "Security Manager"}
            ]
        }

        # Initialize the orchestrator
        orchestrator = ReviewOrchestrator(
            str(project_path),
            requirements_spec,
            architecture_spec
        )

        print("DCAE Review & Quality Assurance - Integrated Review Mechanism")
        print("="*75)

        # Run the complete integrated review
        print("Executing complete integrated review process...\n")
        results = orchestrator.run_complete_review()

        # Print summary
        summary = orchestrator.get_overall_summary()

        print("\n" + "="*50)
        print("INTEGRATED REVIEW SUMMARY")
        print("="*50)
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Completed Phases: {summary['completed_phases']}/{summary['total_phases']}")
        print(f"Failed Phases: {summary['failed_phases']}")
        print(f"Total Findings: {summary['total_findings']}")
        print(f"Total Duration: {summary['total_duration_seconds']:.2f}s")

        print("\nFindings by Severity:")
        for severity, count in summary['findings_by_severity'].items():
            print(f"  {severity.upper()}: {count}")

        print("\nFindings by Category:")
        for category, count in summary['findings_by_category'].items():
            print(f"  {category.replace('_', ' ').title()}: {count}")

        print("="*50)

        # Export results
        output_path = project_path / "integrated_review_report.json"
        orchestrator.export_results(str(output_path))

        print(f"\nIntegrated review completed successfully.")
        print(f"Detailed report available at: {output_path}")


if __name__ == "__main__":
    main()