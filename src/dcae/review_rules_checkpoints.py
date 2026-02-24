"""
Review and Quality Assurance - Review Rules and Checkpoints Configuration Module

This module implements the functionality for configuring review rules and checkpoints
that determine when and how reviews occur in the development process.
"""

import os
import yaml
import json
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import re
import time
from datetime import datetime, timedelta


class RuleSeverity(Enum):
    """Enumeration for rule severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleCategory(Enum):
    """Enumeration for rule categories."""
    QUALITY_METRICS = "quality_metrics"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    STANDARDS = "standards"


class CheckpointTrigger(Enum):
    """Enumeration for checkpoint triggers."""
    MILESTONE_BASED = "milestone_based"
    EVENT_BASED = "event_based"
    SCHEDULE_BASED = "schedule_based"
    THRESHOLD_BASED = "threshold_based"


@dataclass
class ReviewRule:
    """Represents a review rule configuration."""
    id: str
    name: str
    category: RuleCategory
    severity: RuleSeverity
    enabled: bool
    condition: str  # Expression to evaluate
    threshold: Optional[float] = None
    scope: Optional[str] = None  # File pattern or scope
    description: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class Checkpoint:
    """Represents a review checkpoint configuration."""
    id: str
    name: str
    trigger: CheckpointTrigger
    rules: List[str]  # List of rule IDs to apply
    target_scope: Optional[str] = None  # Files/components to check
    blocking: bool = True  # Whether to block progress until review
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None  # Additional conditions


class ReviewRulesManager:
    """Manages the configuration and execution of review rules."""

    def __init__(self, project_path: str):
        """
        Initialize the review rules manager.

        Args:
            project_path: Path to the project root
        """
        self.project_path = Path(project_path)
        self.config_dir = self.project_path / ".dcae" / "review-config"
        self.rules_file = self.config_dir / "rules.yaml"
        self.checkpoints_file = self.config_dir / "checkpoints.yaml"

        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.rules: List[ReviewRule] = []
        self.checkpoints: List[Checkpoint] = []

        # Load default rules and checkpoints
        self._load_defaults()
        self._load_configuration()

    def _load_defaults(self):
        """Load default rules and checkpoints."""
        # Add default quality metrics rules
        self.rules.append(ReviewRule(
            id="qm_complexity_threshold",
            name="Complexity Threshold Check",
            category=RuleCategory.QUALITY_METRICS,
            severity=RuleSeverity.MEDIUM,
            enabled=True,
            condition="cyclomatic_complexity > 10",
            threshold=10.0,
            description="Checks if cyclomatic complexity exceeds threshold",
            recommendation="Refactor complex functions to reduce complexity"
        ))

        self.rules.append(ReviewRule(
            id="qm_function_length",
            name="Function Length Check",
            category=RuleCategory.QUALITY_METRICS,
            severity=RuleSeverity.LOW,
            enabled=True,
            condition="function_length > 50",
            threshold=50.0,
            description="Checks if functions exceed line limit",
            recommendation="Break down long functions into smaller units"
        ))

        # Add default security rules
        self.rules.append(ReviewRule(
            id="sec_hardcoded_credentials",
            name="Hardcoded Credentials Check",
            category=RuleCategory.SECURITY,
            severity=RuleSeverity.CRITICAL,
            enabled=True,
            condition="has_hardcoded_credentials",
            description="Detects hardcoded passwords, secrets, or tokens",
            recommendation="Move credentials to environment variables or secure configuration"
        ))

        self.rules.append(ReviewRule(
            id="sec_sql_injection",
            name="SQL Injection Check",
            category=RuleCategory.SECURITY,
            severity=RuleSeverity.CRITICAL,
            enabled=True,
            condition="has_sql_injection_potential",
            description="Detects potential SQL injection vulnerabilities",
            recommendation="Use parameterized queries instead of string concatenation"
        ))

        # Add default performance rules
        self.rules.append(ReviewRule(
            id="perf_nested_loops",
            name="Nested Loops Check",
            category=RuleCategory.PERFORMANCE,
            severity=RuleSeverity.MEDIUM,
            enabled=True,
            condition="has_nested_loops",
            description="Detects potentially inefficient nested loops",
            recommendation="Consider algorithm optimization or alternative data structures"
        ))

        # Add default checkpoints
        self.checkpoints.append(Checkpoint(
            id="post_generation_review",
            name="Post-Generation Review",
            trigger=CheckpointTrigger.EVENT_BASED,
            rules=["qm_complexity_threshold", "sec_hardcoded_credentials", "sec_sql_injection"],
            target_scope="generated_code",
            blocking=True,
            description="Review generated code for quality and security issues",
            conditions={"after": "code_generation"}
        ))

        self.checkpoints.append(Checkpoint(
            id="commit_review",
            name="Commit Review",
            trigger=CheckpointTrigger.EVENT_BASED,
            rules=["qm_function_length", "perf_nested_loops"],
            target_scope="changed_files",
            blocking=True,
            description="Review code before commit",
            conditions={"before": "git_commit"}
        ))

    def _load_configuration(self):
        """Load custom rules and checkpoints from configuration files."""
        # Load custom rules if file exists
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    rules_data = yaml.safe_load(f)

                if rules_data and 'rules' in rules_data:
                    for rule_data in rules_data['rules']:
                        rule = ReviewRule(
                            id=rule_data['id'],
                            name=rule_data['name'],
                            category=RuleCategory(rule_data['category']),
                            severity=RuleSeverity(rule_data['severity']),
                            enabled=rule_data.get('enabled', True),
                            condition=rule_data['condition'],
                            threshold=rule_data.get('threshold'),
                            scope=rule_data.get('scope'),
                            description=rule_data.get('description'),
                            recommendation=rule_data.get('recommendation')
                        )
                        self._update_or_add_rule(rule)
            except Exception as e:
                print(f"Warning: Could not load custom rules from {self.rules_file}: {e}")

        # Load custom checkpoints if file exists
        if self.checkpoints_file.exists():
            try:
                with open(self.checkpoints_file, 'r', encoding='utf-8') as f:
                    checkpoints_data = yaml.safe_load(f)

                if checkpoints_data and 'checkpoints' in checkpoints_data:
                    for cp_data in checkpoints_data['checkpoints']:
                        checkpoint = Checkpoint(
                            id=cp_data['id'],
                            name=cp_data['name'],
                            trigger=CheckpointTrigger(cp_data['trigger']),
                            rules=cp_data['rules'],
                            target_scope=cp_data.get('target_scope'),
                            blocking=cp_data.get('blocking', True),
                            description=cp_data.get('description'),
                            conditions=cp_data.get('conditions')
                        )
                        self._update_or_add_checkpoint(checkpoint)
            except Exception as e:
                print(f"Warning: Could not load custom checkpoints from {self.checkpoints_file}: {e}")

    def _update_or_add_rule(self, rule: ReviewRule):
        """Add or update a rule in the rules list."""
        for i, existing_rule in enumerate(self.rules):
            if existing_rule.id == rule.id:
                self.rules[i] = rule
                return
        self.rules.append(rule)

    def _update_or_add_checkpoint(self, checkpoint: Checkpoint):
        """Add or update a checkpoint in the checkpoints list."""
        for i, existing_cp in enumerate(self.checkpoints):
            if existing_cp.id == checkpoint.id:
                self.checkpoints[i] = checkpoint
                return
        self.checkpoints.append(checkpoint)

    def add_rule(self, rule: ReviewRule) -> bool:
        """
        Add a new review rule.

        Args:
            rule: The rule to add

        Returns:
            True if successfully added, False otherwise
        """
        if any(r.id == rule.id for r in self.rules):
            print(f"Rule with ID {rule.id} already exists")
            return False

        self.rules.append(rule)
        self._save_rules()
        print(f"Added rule: {rule.name} ({rule.id})")
        return True

    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a review rule.

        Args:
            rule_id: ID of the rule to remove

        Returns:
            True if successfully removed, False otherwise
        """
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                self._save_rules()
                print(f"Removed rule: {rule_id}")
                return True
        print(f"Rule {rule_id} not found")
        return False

    def add_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """
        Add a new checkpoint.

        Args:
            checkpoint: The checkpoint to add

        Returns:
            True if successfully added, False otherwise
        """
        if any(cp.id == checkpoint.id for cp in self.checkpoints):
            print(f"Checkpoint with ID {checkpoint.id} already exists")
            return False

        self.checkpoints.append(checkpoint)
        self._save_checkpoints()
        print(f"Added checkpoint: {checkpoint.name} ({checkpoint.id})")
        return True

    def remove_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Remove a checkpoint.

        Args:
            checkpoint_id: ID of the checkpoint to remove

        Returns:
            True if successfully removed, False otherwise
        """
        for i, checkpoint in enumerate(self.checkpoints):
            if checkpoint.id == checkpoint_id:
                del self.checkpoints[i]
                self._save_checkpoints()
                print(f"Removed checkpoint: {checkpoint_id}")
                return True
        print(f"Checkpoint {checkpoint_id} not found")
        return False

    def update_rule_status(self, rule_id: str, enabled: bool) -> bool:
        """
        Update the enabled status of a rule.

        Args:
            rule_id: ID of the rule to update
            enabled: New enabled status

        Returns:
            True if successfully updated, False otherwise
        """
        for rule in self.rules:
            if rule.id == rule_id:
                rule.enabled = enabled
                self._save_rules()
                status = "enabled" if enabled else "disabled"
                print(f"Rule {rule_id} is now {status}")
                return True
        print(f"Rule {rule_id} not found")
        return False

    def _save_rules(self):
        """Save rules to configuration file."""
        rules_data = {
            'rules': []
        }

        for rule in self.rules:
            rule_dict = {
                'id': rule.id,
                'name': rule.name,
                'category': rule.category.value,
                'severity': rule.severity.value,
                'enabled': rule.enabled,
                'condition': rule.condition
            }

            if rule.threshold is not None:
                rule_dict['threshold'] = rule.threshold
            if rule.scope:
                rule_dict['scope'] = rule.scope
            if rule.description:
                rule_dict['description'] = rule.description
            if rule.recommendation:
                rule_dict['recommendation'] = rule.recommendation

            rules_data['rules'].append(rule_dict)

        with open(self.rules_file, 'w', encoding='utf-8') as f:
            yaml.dump(rules_data, f, default_flow_style=False)

    def _save_checkpoints(self):
        """Save checkpoints to configuration file."""
        checkpoints_data = {
            'checkpoints': []
        }

        for checkpoint in self.checkpoints:
            cp_dict = {
                'id': checkpoint.id,
                'name': checkpoint.name,
                'trigger': checkpoint.trigger.value,
                'rules': checkpoint.rules,
                'blocking': checkpoint.blocking
            }

            if checkpoint.target_scope:
                cp_dict['target_scope'] = checkpoint.target_scope
            if checkpoint.description:
                cp_dict['description'] = checkpoint.description
            if checkpoint.conditions:
                cp_dict['conditions'] = checkpoint.conditions

            checkpoints_data['checkpoints'].append(cp_dict)

        with open(self.checkpoints_file, 'w', encoding='utf-8') as f:
            yaml.dump(checkpoints_data, f, default_flow_style=False)

    def get_active_rules(self, category: Optional[RuleCategory] = None) -> List[ReviewRule]:
        """Get active (enabled) rules, optionally filtered by category."""
        active_rules = [rule for rule in self.rules if rule.enabled]

        if category:
            active_rules = [rule for rule in active_rules if rule.category == category]

        return active_rules

    def get_checkpoints_by_trigger(self, trigger: CheckpointTrigger) -> List[Checkpoint]:
        """Get checkpoints by trigger type."""
        return [cp for cp in self.checkpoints if cp.trigger == trigger]

    def evaluate_rule(self, rule: ReviewRule, context: Dict[str, Any]) -> bool:
        """
        Evaluate a rule against a context.

        Args:
            rule: The rule to evaluate
            context: Context data to evaluate against

        Returns:
            True if rule condition is met, False otherwise
        """
        # For simplicity, we'll implement basic condition evaluation
        # In a full implementation, this would be more sophisticated

        if rule.condition == "cyclomatic_complexity > 10":
            return context.get('cyclomatic_complexity', 0) > 10
        elif rule.condition == "function_length > 50":
            return context.get('function_length', 0) > 50
        elif rule.condition == "has_hardcoded_credentials":
            return context.get('has_hardcoded_credentials', False)
        elif rule.condition == "has_sql_injection_potential":
            return context.get('has_sql_injection_potential', False)
        elif rule.condition == "has_nested_loops":
            return context.get('has_nested_loops', False)
        else:
            # Handle generic numeric comparison
            match = re.match(r'(\w+)\s*([<>!=]=?)\s*(\d+(?:\.\d+)?)', rule.condition)
            if match:
                field, op, value = match.groups()
                actual_value = context.get(field, 0)
                threshold = float(value)

                if op == '>':
                    return actual_value > threshold
                elif op == '>=':
                    return actual_value >= threshold
                elif op == '<':
                    return actual_value < threshold
                elif op == '<=':
                    return actual_value <= threshold
                elif op == '==':
                    return actual_value == threshold
                elif op == '!=':
                    return actual_value != threshold

        return False


class ReviewRulesConfigurer:
    """Interface for configuring review rules and checkpoints."""

    def __init__(self, project_path: str):
        """
        Initialize the rules configurer.

        Args:
            project_path: Path to the project root
        """
        self.manager = ReviewRulesManager(project_path)

    def create_custom_rule(self,
                          rule_id: str,
                          name: str,
                          category: RuleCategory,
                          severity: RuleSeverity,
                          condition: str,
                          threshold: Optional[float] = None,
                          scope: Optional[str] = None,
                          description: Optional[str] = None,
                          recommendation: Optional[str] = None) -> bool:
        """
        Create a custom review rule.

        Args:
            rule_id: Unique identifier for the rule
            name: Name of the rule
            category: Category of the rule
            severity: Severity level of the rule
            condition: Condition to evaluate
            threshold: Numeric threshold value
            scope: Scope of application
            description: Description of the rule
            recommendation: Recommendation when rule is triggered

        Returns:
            True if successfully created, False otherwise
        """
        rule = ReviewRule(
            id=rule_id,
            name=name,
            category=category,
            severity=severity,
            enabled=True,
            condition=condition,
            threshold=threshold,
            scope=scope,
            description=description,
            recommendation=recommendation
        )

        return self.manager.add_rule(rule)

    def create_custom_checkpoint(self,
                               checkpoint_id: str,
                               name: str,
                               trigger: CheckpointTrigger,
                               rule_ids: List[str],
                               target_scope: Optional[str] = None,
                               blocking: bool = True,
                               description: Optional[str] = None,
                               conditions: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a custom checkpoint.

        Args:
            checkpoint_id: Unique identifier for the checkpoint
            name: Name of the checkpoint
            trigger: Trigger type for the checkpoint
            rule_ids: List of rule IDs to apply at this checkpoint
            target_scope: Target scope for the checkpoint
            blocking: Whether the checkpoint blocks progress
            description: Description of the checkpoint
            conditions: Additional conditions for activation

        Returns:
            True if successfully created, False otherwise
        """
        checkpoint = Checkpoint(
            id=checkpoint_id,
            name=name,
            trigger=trigger,
            rules=rule_ids,
            target_scope=target_scope,
            blocking=blocking,
            description=description,
            conditions=conditions
        )

        return self.manager.add_checkpoint(checkpoint)

    def toggle_rule(self, rule_id: str, enabled: bool) -> bool:
        """
        Toggle a rule on or off.

        Args:
            rule_id: ID of the rule to toggle
            enabled: Whether to enable or disable

        Returns:
            True if successful, False otherwise
        """
        return self.manager.update_rule_status(rule_id, enabled)

    def get_rules_summary(self) -> Dict[str, Any]:
        """Get a summary of configured rules."""
        all_rules = self.manager.rules
        active_rules = self.manager.get_active_rules()

        summary = {
            "total_rules": len(all_rules),
            "active_rules": len(active_rules),
            "inactive_rules": len(all_rules) - len(active_rules),
            "by_category": {},
            "by_severity": {}
        }

        for rule in all_rules:
            # Count by category
            cat_val = rule.category.value
            summary["by_category"][cat_val] = summary["by_category"].get(cat_val, 0) + 1

            # Count by severity
            sev_val = rule.severity.value
            summary["by_severity"][sev_val] = summary["by_severity"].get(sev_val, 0) + 1

        return summary

    def get_checkpoints_summary(self) -> Dict[str, Any]:
        """Get a summary of configured checkpoints."""
        all_checkpoints = self.manager.checkpoints

        summary = {
            "total_checkpoints": len(all_checkpoints),
            "by_trigger": {}
        }

        for checkpoint in all_checkpoints:
            trigger_val = checkpoint.trigger.value
            summary["by_trigger"][trigger_val] = summary["by_trigger"].get(trigger_val, 0) + 1

        return summary

    def print_configuration_summary(self):
        """Print a summary of the current configuration."""
        print("\n" + "="*70)
        print("REVIEW RULES AND CHECKPOINTS CONFIGURATION")
        print("="*70)

        # Rules summary
        rules_summary = self.get_rules_summary()
        print(f"Total Rules: {rules_summary['total_rules']}")
        print(f"Active Rules: {rules_summary['active_rules']}")
        print(f"Inactive Rules: {rules_summary['inactive_rules']}")

        print("\nRules by Category:")
        for category, count in rules_summary["by_category"].items():
            print(f"  {category.replace('_', ' ').title()}: {count}")

        print("\nRules by Severity:")
        for severity, count in rules_summary["by_severity"].items():
            print(f"  {severity.replace('_', ' ').title()}: {count}")

        # Checkpoints summary
        cp_summary = self.get_checkpoints_summary()
        print(f"\nTotal Checkpoints: {cp_summary['total_checkpoints']}")

        print("\nCheckpoints by Trigger:")
        for trigger, count in cp_summary["by_trigger"].items():
            print(f"  {trigger.replace('_', ' ').title()}: {count}")

        print("="*70)

    def apply_checkpoint(self, checkpoint_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a checkpoint and evaluate its associated rules.

        Args:
            checkpoint_id: ID of the checkpoint to apply
            context: Context data to evaluate rules against

        Returns:
            Dictionary with evaluation results
        """
        checkpoint = None
        for cp in self.manager.checkpoints:
            if cp.id == checkpoint_id:
                checkpoint = cp
                break

        if not checkpoint:
            return {"error": f"Checkpoint {checkpoint_id} not found"}

        results = {
            "checkpoint_id": checkpoint_id,
            "checkpoint_name": checkpoint.name,
            "triggered_rules": [],
            "violations": [],
            "passed": True
        }

        for rule_id in checkpoint.rules:
            rule = None
            for r in self.manager.rules:
                if r.id == rule_id:
                    rule = r
                    break

            if rule and rule.enabled:
                results["triggered_rules"].append(rule.name)

                if self.manager.evaluate_rule(rule, context):
                    violation = {
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "severity": rule.severity.value,
                        "category": rule.category.value,
                        "description": rule.description,
                        "recommendation": rule.recommendation
                    }
                    results["violations"].append(violation)
                    results["passed"] = False

        return results


def main():
    """Example usage of the review rules and checkpoints configuration system."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Initialize the rules configurer
        configurer = ReviewRulesConfigurer(str(project_path))

        print("DCAE Review & Quality Assurance - Review Rules & Checkpoints Configuration")
        print("="*80)

        # Print initial configuration
        configurer.print_configuration_summary()

        # Create a custom rule
        print("\nCreating a custom rule...")
        custom_rule_created = configurer.create_custom_rule(
            rule_id="custom_long_line_check",
            name="Long Line Check",
            category=RuleCategory.STANDARDS,
            severity=RuleSeverity.LOW,
            condition="line_length > 120",
            threshold=120.0,
            scope="*.py",
            description="Checks if lines exceed 120 characters",
            recommendation="Keep lines under 120 characters for better readability"
        )

        print(f"Custom rule created: {custom_rule_created}")

        # Create a custom checkpoint
        print("\nCreating a custom checkpoint...")
        custom_checkpoint_created = configurer.create_custom_checkpoint(
            checkpoint_id="pre_commit_quality",
            name="Pre-Commit Quality Check",
            trigger=CheckpointTrigger.EVENT_BASED,
            rule_ids=["custom_long_line_check", "qm_function_length"],
            target_scope="staged_files",
            blocking=True,
            description="Check code quality before allowing commit",
            conditions={"before": "git_commit"}
        )

        print(f"Custom checkpoint created: {custom_checkpoint_created}")

        # Disable a rule
        print("\nDisabling the long line check rule...")
        configurer.toggle_rule("custom_long_line_check", False)

        # Print updated configuration
        print("\nUpdated configuration:")
        configurer.print_configuration_summary()

        # Apply a checkpoint with mock context data
        print("\nApplying 'post_generation_review' checkpoint...")
        mock_context = {
            "cyclomatic_complexity": 15,
            "function_length": 60,
            "has_hardcoded_credentials": False,
            "has_sql_injection_potential": True,
            "has_nested_loops": True
        }

        checkpoint_results = configurer.apply_checkpoint("post_generation_review", mock_context)
        print(f"Checkpoint: {checkpoint_results['checkpoint_name']}")
        print(f"Passed: {checkpoint_results['passed']}")
        print(f"Triggered Rules: {len(checkpoint_results['triggered_rules'])}")

        if checkpoint_results["violations"]:
            print(f"Violations Found: {len(checkpoint_results['violations'])}")
            for violation in checkpoint_results["violations"]:
                print(f"  - {violation['rule_name']} ({violation['severity']}): {violation['description']}")

        print(f"\nReview rules and checkpoints configuration system demonstrated successfully.")
        print(f"Configuration files saved in: {project_path}/.dcae/review-config/")


if __name__ == "__main__":
    main()