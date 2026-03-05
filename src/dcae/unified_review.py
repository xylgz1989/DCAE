"""
Unified Review Mechanism Module

This module provides the main entry point for the integrated review mechanism
that combines all quality assurance functionality in the DCAE framework.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime

from .review_orchestrator import ReviewMechanismOrchestrator
from .generated_output_review import GeneratedOutputReviewer
from .review_rules_checkpoints import ReviewRulesConfigurer
from .discipline_control.review_adjuster import ReviewAdjuster
from .review_rules_engine import ReviewRulesEngine


class UnifiedReviewInterface:
    """
    The main unified interface for all review functionality.

    This class provides a single entry point for all review operations,
    consistent APIs across different review types, integrated workflow
    management, and centralized configuration and reporting.
    """

    def __init__(self, project_path: str):
        """
        Initialize the unified review interface.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.orchestrator = ReviewMechanismOrchestrator()
        self.generated_reviewer = GeneratedOutputReviewer(project_path)
        self.rules_configurer = ReviewRulesConfigurer(project_path)
        self.review_adjuster = ReviewAdjuster()
        self.rules_engine = ReviewRulesEngine()

        # Create configuration directory if it doesn't exist
        self.config_dir = self.project_path / ".dcae" / "review-config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Default configuration
        self.default_config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the review mechanism."""
        return {
            "review_types": {
                "static_analysis": True,
                "security_scanning": True,
                "performance_analysis": True,
                "architecture_alignment": True,
                "requirements_coverage": True,
                "code_quality": True,
                "best_practices": True
            },
            "severity_threshold": "medium",  # Block on issues of this severity or higher
            "report_format": "detailed",  # Options: "brief", "detailed", "summary"
            "output_directory": str(self.project_path / "review_outputs"),
            "integrated_workflow": {
                "auto_trigger": ["commit", "pull_request"],
                "blocking_behavior": True,
                "integration_points": ["pre_commit", "ci_pipeline", "code_merge"]
            }
        }

    def run_comprehensive_review(
        self,
        target_path: Optional[str] = None,
        requirements_spec: Optional[Dict[str, Any]] = None,
        architecture_spec: Optional[Dict[str, Any]] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a comprehensive review combining all review functionality.

        Args:
            target_path: Specific path to review (optional, defaults to entire project)
            requirements_spec: Requirements specification for traceability
            architecture_spec: Architecture specification for alignment check
            custom_config: Custom configuration to override defaults

        Returns:
            Dictionary containing comprehensive review results
        """
        effective_config = self.default_config.copy()
        if custom_config:
            # Deep merge configuration
            self._deep_merge_config(effective_config, custom_config)

        # Prepare orchestrator configuration
        orchestrator_config = {
            "reviews": [
                {
                    "type": "generated_output_review",
                    "params": {
                        "project_path": str(self.project_path),
                        "requirements_spec": requirements_spec,
                        "architecture_spec": architecture_spec,
                        "target_path": target_path,
                        "config": effective_config.get("review_types", {})
                    },
                    "priority": 2
                },
                {
                    "type": "rules_engine_review",
                    "params": {
                        "review_context": {
                            "project_path": str(self.project_path),
                            "target_path": target_path
                        }
                    },
                    "priority": 1
                }
            ],
            "workflow_integration": effective_config.get("integrated_workflow", {})
        }

        # Run comprehensive review through orchestrator
        results = self.orchestrator.run_comprehensive_review(orchestrator_config)

        # Enhance results with additional information
        results["effective_config"] = effective_config
        results["review_timestamp"] = datetime.now().isoformat()
        results["project_path"] = str(self.project_path)
        results["target_path"] = target_path

        return results

    def _deep_merge_config(self, base: Dict, override: Dict) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_config(base[key], value)
            else:
                base[key] = value

    def run_specific_reviews(
        self,
        review_types: List[str],
        target_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run specific types of reviews.

        Args:
            review_types: List of review types to run
            target_path: Specific path to review
            config: Additional configuration options

        Returns:
            Dictionary containing results for specific review types
        """
        results = {}

        for review_type in review_types:
            if review_type == "generated_output":
                reviewer_config = config.get("generated_output", {}) if config else {}
                reviewer = GeneratedOutputReviewer(
                    project_path=str(self.project_path),
                    config=reviewer_config
                )
                report = reviewer.review_generated_output(target_path)
                results[review_type] = {
                    "report": report,
                    "summary": report.summary if report else {}
                }

            elif review_type == "rules_check":
                # Use the rules engine for this review
                context = {
                    "project_path": str(self.project_path),
                    "target_path": target_path
                }
                rule_results = self.rules_engine.evaluate_all_rules(context)
                results[review_type] = {
                    "violations": {k: v for k, v in rule_results.items() if v},
                    "compliance_rate": 1 - (sum(1 for v in rule_results.values() if v) / len(rule_results)) if rule_results else 1.0
                }

            elif review_type == "discipline_check":
                # Apply discipline-level review configuration
                from .discipline_control.discipline_level import DisciplineLevel
                discipline_level = config.get("discipline_level", DisciplineLevel.BALANCED) if config else DisciplineLevel.BALANCED
                settings = self.review_adjuster.prepare_settings(discipline_level)
                results[review_type] = settings

        return results

    def configure_review_rules(
        self,
        rule_updates: Dict[str, Any],
        checkpoint_updates: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Configure review rules and checkpoints.

        Args:
            rule_updates: Updates to review rules
            checkpoint_updates: Updates to checkpoints (optional)

        Returns:
            True if configuration was successful, False otherwise
        """
        success = True

        # Update rules
        for rule_id, rule_config in rule_updates.items():
            if "remove" in rule_config and rule_config["remove"]:
                success &= self.rules_configurer.manager.remove_rule(rule_id)
            else:
                # Assuming rule_config contains all necessary fields for ReviewRule
                from .review_rules_checkpoints import ReviewRule, RuleCategory, RuleSeverity
                try:
                    category = RuleCategory(rule_config.get("category", "quality_metrics"))
                    severity = RuleSeverity(rule_config.get("severity", "medium"))

                    rule = ReviewRule(
                        id=rule_config["id"],
                        name=rule_config["name"],
                        category=category,
                        severity=severity,
                        enabled=rule_config.get("enabled", True),
                        condition=rule_config["condition"],
                        threshold=rule_config.get("threshold"),
                        scope=rule_config.get("scope"),
                        description=rule_config.get("description"),
                        recommendation=rule_config.get("recommendation")
                    )

                    success &= self.rules_configurer.manager.add_rule(rule)
                except (KeyError, ValueError) as e:
                    print(f"Error creating rule {rule_id}: {e}")
                    success = False

        # Update checkpoints if provided
        if checkpoint_updates:
            for cp_id, cp_config in checkpoint_updates.items():
                if "remove" in cp_config and cp_config["remove"]:
                    success &= self.rules_configurer.manager.remove_checkpoint(cp_id)
                else:
                    # Assuming cp_config contains all necessary fields for Checkpoint
                    from .review_rules_checkpoints import Checkpoint, CheckpointTrigger
                    try:
                        trigger = CheckpointTrigger(cp_config.get("trigger", "event_based"))

                        checkpoint = Checkpoint(
                            id=cp_config["id"],
                            name=cp_config["name"],
                            trigger=trigger,
                            rules=cp_config["rules"],
                            target_scope=cp_config.get("target_scope"),
                            blocking=cp_config.get("blocking", True),
                            description=cp_config.get("description"),
                            conditions=cp_config.get("conditions")
                        )

                        success &= self.rules_configurer.manager.add_checkpoint(checkpoint)
                    except (KeyError, ValueError) as e:
                        print(f"Error creating checkpoint {cp_id}: {e}")
                        success = False

        return success

    def generate_unified_report(
        self,
        results: Dict[str, Any],
        output_format: str = "json",
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a unified report from review results.

        Args:
            results: Results from review operations
            output_format: Format for the report ("json", "text", "html")
            output_path: Path to save the report (optional)

        Returns:
            Path to the generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_output_path = str(self.project_path / f"review_report_{timestamp}.{output_format}")
        output_file = output_path or default_output_path

        if output_format == "json":
            # Prepare data for JSON export
            export_data = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "project_path": str(self.project_path),
                    "review_types_executed": results.get("effective_config", {}).get("review_types", {}).keys(),
                    "total_findings": len(results.get("findings", []))
                },
                "review_results": results,
                "summary": self._generate_summary_from_results(results)
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

        elif output_format == "text":
            # Generate text report
            report_text = self._generate_text_report(results)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)

        elif output_format == "html":
            # Generate HTML report
            report_html = self._generate_html_report(results)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_html)

        return output_file

    def _generate_summary_from_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary from review results."""
        summary = {
            "total_findings": 0,
            "findings_by_severity": {},
            "findings_by_category": {},
            "review_completion_status": "completed",  # In a real implementation, this could be more nuanced
            "overall_score": 0.0,
            "recommendations": []
        }

        # Extract findings if they exist in results
        findings = results.get("findings", [])
        summary["total_findings"] = len(findings)

        for finding in findings:
            # Assuming finding has severity and category attributes
            severity = getattr(finding, 'severity', None)
            category = getattr(finding, 'category', None)

            if severity:
                sev_val = severity.value if hasattr(severity, 'value') else str(severity)
                summary["findings_by_severity"][sev_val] = summary["findings_by_severity"].get(sev_val, 0) + 1

            if category:
                cat_val = category.value if hasattr(category, 'value') else str(category)
                summary["findings_by_category"][cat_val] = summary["findings_by_category"].get(cat_val, 0) + 1

        # Calculate overall score based on severity
        high_severity = summary["findings_by_severity"].get("high", 0) + summary["findings_by_severity"].get("critical", 0)
        medium_severity = summary["findings_by_severity"].get("medium", 0)
        low_severity = summary["findings_by_severity"].get("low", 0)

        # Score calculation: perfect score is 100, subtract points for issues
        score_reduction = (high_severity * 10) + (medium_severity * 5) + (low_severity * 1)
        summary["overall_score"] = max(0, 100 - score_reduction)

        return summary

    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """Generate a text-formatted report."""
        summary = self._generate_summary_from_results(results)

        report_lines = [
            "DCAE Unified Review Report",
            "=" * 50,
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project: {results.get('project_path', 'Unknown')}",
            f"Target: {results.get('target_path', 'Entire project')}",
            "",
            "SUMMARY",
            "-" * 15,
            f"Total Findings: {summary['total_findings']}",
            f"Overall Score: {summary['overall_score']}/100",
            "",
            "Findings by Severity:",
        ]

        for sev, count in summary["findings_by_severity"].items():
            report_lines.append(f"  {sev.title()}: {count}")

        report_lines.append("")
        report_lines.append("Findings by Category:")

        for cat, count in summary["findings_by_category"].items():
            report_lines.append(f"  {cat.replace('_', ' ').title()}: {count}")

        report_lines.append("")
        report_lines.append("=" * 50)

        return "\n".join(report_lines)

    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate an HTML-formatted report."""
        summary = self._generate_summary_from_results(results)

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DCAE Unified Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .summary-box {{ background-color: #e6f3ff; padding: 15px; margin: 10px 0; border-left: 4px solid #007acc; }}
        .severity-high {{ color: #d32f2f; }}
        .severity-medium {{ color: #ffa726; }}
        .severity-low {{ color: #558b2f; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DCAE Unified Review Report</h1>
        <p><strong>Generated at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Project:</strong> {results.get('project_path', 'Unknown')}</p>
        <p><strong>Target:</strong> {results.get('target_path', 'Entire project')}</p>
    </div>

    <div class="summary-box">
        <h2>Review Summary</h2>
        <p><strong>Total Findings:</strong> {summary['total_findings']}</p>
        <p><strong>Overall Score:</strong> <span class="{'severity-high' if summary['overall_score'] < 40 else 'severity-medium' if summary['overall_score'] < 70 else 'severity-low'}">{summary['overall_score']}/100</span></p>
    </div>

    <h3>Findings by Severity</h3>
    <table>
        <tr><th>Severity</th><th>Count</th></tr>
        {''.join([f'<tr><td>{sev.title()}</td><td>{count}</td></tr>' for sev, count in summary["findings_by_severity"].items()])}
    </table>

    <h3>Findings by Category</h3>
    <table>
        <tr><th>Category</th><th>Count</th></tr>
        {''.join([f'<tr><td>{cat.replace("_", " ").title()}</td><td>{count}</td></tr>' for cat, count in summary["findings_by_category"].items()])}
    </table>

    <footer>
        <hr>
        <p>Generated by DCAE Review Mechanism</p>
    </footer>
</body>
</html>
        """

        return html_content

    def integrate_with_workflow(self, workflow_type: str, config: Dict[str, Any]) -> bool:
        """
        Integrate the review mechanism with development workflows.

        Args:
            workflow_type: Type of workflow to integrate with ("ci_cd", "git_hooks", etc.)
            config: Configuration for the integration

        Returns:
            True if integration was successful, False otherwise
        """
        if workflow_type == "git_hooks":
            # Set up Git hooks for automatic reviews
            hooks_dir = self.project_path / ".git" / "hooks"
            if not hooks_dir.exists():
                print(f"Git repository not found at {self.project_path}. Cannot set up hooks.")
                return False

            # Create pre-commit hook
            pre_commit_hook = hooks_dir / "pre-commit"
            hook_content = f"""#!/bin/sh
# DCAE Pre-commit Review Hook
echo "Running DCAE review before commit..."
python -c "
from dcae.unified_review import UnifiedReviewInterface
import os
reviewer = UnifiedReviewInterface('{self.project_path}')
try:
    results = reviewer.run_comprehensive_review()
    print('Review completed. Findings:', len(results.get('findings', [])))
except Exception as e:
    print('Review failed:', str(e))
    exit(1)
"
"""

            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)

            # Make executable
            import stat
            pre_commit_hook.chmod(pre_commit_hook.stat().st_mode | stat.S_IEXEC)

            print(f"Git pre-commit hook created at {pre_commit_hook}")

        elif workflow_type == "ci_cd":
            # Generate CI/CD configuration
            ci_config = config.get("ci_template", "github_actions")  # Default to GitHub Actions

            if ci_config == "github_actions":
                workflow_dir = self.project_path / ".github" / "workflows"
                workflow_dir.mkdir(parents=True, exist_ok=True)

                workflow_content = f"""name: DCAE Code Review
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run DCAE Review
      run: |
        python -c "
from dcae.unified_review import UnifiedReviewInterface
reviewer = UnifiedReviewInterface('.')
results = reviewer.run_comprehensive_review()
findings = len(results.get('findings', []))
print(f'DCAE Review completed with {{findings}} findings')
if findings > 0:
    print('Review findings detected - check report for details')
"
"""

                workflow_file = workflow_dir / "dcae-review.yml"
                with open(workflow_file, 'w') as f:
                    f.write(workflow_content)

                print(f"GitHub Actions workflow created at {workflow_file}")

        return True

    def export_configuration(self, output_path: str) -> bool:
        """
        Export current review configuration.

        Args:
            output_path: Path to export configuration

        Returns:
            True if export was successful, False otherwise
        """
        config_data = {
            "version": "1.0",
            "export_date": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "default_config": self.default_config,
            "rules": [rule.__dict__ for rule in self.rules_configurer.manager.rules],
            "checkpoints": [cp.__dict__ for cp in self.rules_configurer.manager.checkpoints]
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting configuration: {e}")
            return False

    def import_configuration(self, input_path: str) -> bool:
        """
        Import review configuration from file.

        Args:
            input_path: Path to import configuration from

        Returns:
            True if import was successful, False otherwise
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Update default config
            if "default_config" in config_data:
                self.default_config = config_data["default_config"]

            # Import rules and checkpoints
            if "rules" in config_data:
                for rule_data in config_data["rules"]:
                    from .review_rules_checkpoints import ReviewRule, RuleCategory, RuleSeverity
                    try:
                        rule = ReviewRule(
                            id=rule_data["id"],
                            name=rule_data["name"],
                            category=RuleCategory(rule_data["category"]),
                            severity=RuleSeverity(rule_data["severity"]),
                            enabled=rule_data["enabled"],
                            condition=rule_data["condition"],
                            threshold=rule_data.get("threshold"),
                            scope=rule_data.get("scope"),
                            description=rule_data.get("description"),
                            recommendation=rule_data.get("recommendation")
                        )
                        self.rules_configurer.manager.add_rule(rule)
                    except Exception as e:
                        print(f"Error importing rule {rule_data.get('id', 'unknown')}: {e}")

            if "checkpoints" in config_data:
                for cp_data in config_data["checkpoints"]:
                    from .review_rules_checkpoints import Checkpoint, CheckpointTrigger
                    try:
                        checkpoint = Checkpoint(
                            id=cp_data["id"],
                            name=cp_data["name"],
                            trigger=CheckpointTrigger(cp_data["trigger"]),
                            rules=cp_data["rules"],
                            target_scope=cp_data.get("target_scope"),
                            blocking=cp_data.get("blocking", True),
                            description=cp_data.get("description"),
                            conditions=cp_data.get("conditions")
                        )
                        self.rules_configurer.manager.add_checkpoint(checkpoint)
                    except Exception as e:
                        print(f"Error importing checkpoint {cp_data.get('id', 'unknown')}: {e}")

            return True
        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False


def main():
    """Example usage of the unified review interface."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Create a sample file with some issues
        sample_file = project_path / "sample.py"
        sample_code = '''
def sample_function():
    """A sample function for review."""
    password = "hardcoded_password"  # Security issue
    result = []
    for i in range(10):
        for j in range(10):  # Nested loop - Performance issue
            result.append(i * j)
    return result
'''
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_code)

        print("DCAE Review & Quality Assurance - Unified Review Interface")
        print("="*70)

        # Initialize the unified review interface
        reviewer = UnifiedReviewInterface(str(project_path))

        # Run comprehensive review
        print("Running comprehensive review...")
        results = reviewer.run_comprehensive_review(
            target_path=str(project_path),
            custom_config={
                "review_types": {
                    "security_scanning": True,
                    "performance_analysis": True,
                    "code_quality": True
                },
                "severity_threshold": "medium"
            }
        )

        print(f"Review completed!")
        print(f"Total findings: {results['summary']['total_findings']}")
        print(f"Overall score: {results['summary']['overall_score']}/100")

        # Generate report
        report_path = reviewer.generate_unified_report(results, output_format="text")
        print(f"Text report generated: {report_path}")

        # Also generate HTML report
        html_report_path = reviewer.generate_unified_report(results, output_format="html")
        print(f"HTML report generated: {html_report_path}")

        # Demonstrate workflow integration (only CI/CD since git repo isn't initialized in temp dir)
        reviewer.integrate_with_workflow("ci_cd", {"ci_template": "github_actions"})

        print("\nUnified review interface demonstrated successfully!")


if __name__ == "__main__":
    main()