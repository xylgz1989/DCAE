"""
Review Orchestration Engine Module

This module implements the core orchestration engine for the review mechanism that integrates
all review functionality in the DCAE (Development Coding Agent Environment) framework.
"""
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import json

from .generated_output_review import GeneratedOutputReviewer, ReviewReport
from .review_rules_checkpoints import ReviewRulesConfigurer
from .discipline_control.review_adjuster import ReviewAdjuster
from .review_rules_engine import ReviewRulesEngine


class ReviewEventType(Enum):
    """Types of events in the review process."""
    SCHEDULER_START = "scheduler_start"
    SCHEDULER_END = "scheduler_end"
    COORDINATOR_START = "coordinator_start"
    COORDINATOR_END = "coordinator_end"
    REVIEWER_START = "reviewer_start"
    REVIEWER_END = "reviewer_end"
    CONTEXT_UPDATE = "context_update"
    RESULT_AGGREGATION = "result_aggregation"


@dataclass
class ReviewEvent:
    """Represents an event in the review process."""
    timestamp: float
    event_type: ReviewEventType
    details: Dict[str, Any]
    duration: Optional[float] = None


@dataclass
class ReviewResult:
    """Encapsulates a result from a review component."""
    component_name: str
    result_data: Any
    timestamp: float
    status: str  # "success", "failed", "partial", "skipped"
    metadata: Optional[Dict[str, Any]] = None


class ReviewContextManager:
    """Manages context across different review phases."""

    def __init__(self):
        self.context = {
            "review_session_id": f"review_{int(time.time())}",
            "start_time": time.time(),
            "review_history": [],
            "state": {},
            "results": {},
            "metadata": {},
            "progress": {}
        }
        self.lock = threading.Lock()

    def update_context(self, key: str, value: Any) -> None:
        """Update a specific key in the context."""
        with self.lock:
            self.context[key] = value

    def update_state(self, key: str, value: Any) -> None:
        """Update the state information."""
        with self.lock:
            self.context["state"][key] = value

    def update_result(self, component_name: str, result: ReviewResult) -> None:
        """Update the results with a new review result."""
        with self.lock:
            self.context["results"][component_name] = result

    def get_context(self) -> Dict[str, Any]:
        """Get the current context."""
        with self.lock:
            return self.context.copy()

    def add_event(self, event: ReviewEvent) -> None:
        """Add an event to the review history."""
        with self.lock:
            self.context["review_history"].append(event)

    def get_progress(self) -> Dict[str, Any]:
        """Get the current progress information."""
        with self.lock:
            return self.context["progress"].copy()

    def set_progress(self, key: str, value: Any) -> None:
        """Set a progress indicator."""
        with self.lock:
            self.context["progress"][key] = value


class ReviewScheduler:
    """Schedules different types of reviews."""

    def __init__(self, context_manager: ReviewContextManager):
        self.context_manager = context_manager
        self.scheduled_reviews = []
        self.executor = ThreadPoolExecutor(max_workers=4)

    def schedule_review(self, review_func: Callable, params: Dict[str, Any], priority: int = 1) -> str:
        """Schedule a review to be executed."""
        review_id = f"review_{len(self.scheduled_reviews)}_{int(time.time())}"

        scheduled_item = {
            "id": review_id,
            "function": review_func,
            "params": params,
            "priority": priority,
            "scheduled_at": time.time(),
            "status": "pending"
        }

        self.scheduled_reviews.append(scheduled_item)
        return review_id

    def execute_scheduled_reviews(self) -> List[ReviewResult]:
        """Execute all scheduled reviews."""
        results = []

        # Sort by priority (higher priority first)
        sorted_reviews = sorted(self.scheduled_reviews, key=lambda x: x["priority"], reverse=True)

        for review in sorted_reviews:
            review_id = review["id"]
            review_func = review["function"]
            params = review["params"]

            try:
                # Update status to running
                review["status"] = "running"

                # Execute the review
                start_time = time.time()
                result_data = review_func(**params)
                duration = time.time() - start_time

                # Create result object
                result = ReviewResult(
                    component_name=review_id,
                    result_data=result_data,
                    timestamp=time.time(),
                    status="success",
                    metadata={"duration": duration, "input_params": params}
                )

                results.append(result)

                # Update review status
                review["status"] = "completed"

            except Exception as e:
                result = ReviewResult(
                    component_name=review_id,
                    result_data=None,
                    timestamp=time.time(),
                    status="failed",
                    metadata={"error": str(e)}
                )
                results.append(result)
                review["status"] = "failed"

        # Add event to context
        event = ReviewEvent(
            timestamp=time.time(),
            event_type=ReviewEventType.SCHEDULER_END,
            details={"total_reviews": len(sorted_reviews), "results": [r.component_name for r in results]},
            duration=time.time() - self.context_manager.get_context()["start_time"]
        )
        self.context_manager.add_event(event)

        return results

    def clear_schedule(self) -> None:
        """Clear all scheduled reviews."""
        self.scheduled_reviews.clear()


class ReviewCoordinator:
    """Coordinates multiple review types and aggregates results."""

    def __init__(self, context_manager: ReviewContextManager, scheduler: ReviewScheduler):
        self.context_manager = context_manager
        self.scheduler = scheduler
        self.results_aggregator = {}

    def coordinate_reviews(self, reviews_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Coordinate the execution of multiple reviews based on configuration."""
        start_time = time.time()

        # Add event to context
        event = ReviewEvent(
            timestamp=start_time,
            event_type=ReviewEventType.COORDINATOR_START,
            details={"total_reviews_configured": len(reviews_config)},
        )
        self.context_manager.add_event(event)

        # Schedule all configured reviews
        for review_config in reviews_config:
            review_type = review_config["type"]
            params = review_config["params"]

            # Map review type to actual function
            if review_type == "generated_output_review":
                review_func = self._run_generated_output_review
            elif review_type == "rules_engine_review":
                review_func = self._run_rules_engine_review
            elif review_type == "discipline_review":
                review_func = self._run_discipline_review
            else:
                # Unknown review type, skip
                continue

            # Schedule the review
            self.scheduler.schedule_review(review_func, params, review_config.get("priority", 1))

        # Execute all scheduled reviews
        results = self.scheduler.execute_scheduled_reviews()

        # Aggregate results
        aggregated_results = self.aggregate_results(results)

        # Add completion event
        end_time = time.time()
        event = ReviewEvent(
            timestamp=end_time,
            event_type=ReviewEventType.COORDINATOR_END,
            details={
                "aggregated_results_count": len(aggregated_results),
                "duration": end_time - start_time
            },
            duration=end_time - start_time
        )
        self.context_manager.add_event(event)

        return aggregated_results

    def aggregate_results(self, results: List[ReviewResult]) -> Dict[str, Any]:
        """Aggregate results from different review components."""
        aggregated = {
            "summary": {},
            "findings": [],
            "metadata": {},
            "consolidated_report": None
        }

        # Group results by component type
        by_component = {}
        for result in results:
            component_name = result.component_name
            by_component[component_name] = result

            # Store the result in context
            self.context_manager.update_result(component_name, result)

        # Count statuses
        status_counts = {"success": 0, "failed": 0, "partial": 0, "skipped": 0}
        for result in results:
            status_counts[result.status] += 1

        aggregated["summary"] = {
            "total_reviews": len(results),
            "status_breakdown": status_counts,
            "timestamp": time.time()
        }

        # Combine findings if they're review reports
        all_findings = []
        for result in results:
            if result.status == "success" and hasattr(result.result_data, 'findings'):
                # Assume it's a ReviewReport-like object
                all_findings.extend(getattr(result.result_data, 'findings', []))

        aggregated["findings"] = all_findings

        # Store in aggregator
        self.results_aggregator = aggregated

        return aggregated

    def _run_generated_output_review(self, **kwargs) -> Any:
        """Execute generated output review."""
        # Add event to context
        event = ReviewEvent(
            timestamp=time.time(),
            event_type=ReviewEventType.REVIEWER_START,
            details={"review_type": "generated_output_review", "params": kwargs},
        )
        self.context_manager.add_event(event)

        try:
            reviewer = GeneratedOutputReviewer(
                project_path=kwargs.get("project_path", "."),
                requirements_spec=kwargs.get("requirements_spec"),
                architecture_spec=kwargs.get("architecture_spec"),
                config=kwargs.get("config")
            )

            target_path = kwargs.get("target_path")
            report = reviewer.review_generated_output(target_path)

            # Add completion event
            event = ReviewEvent(
                timestamp=time.time(),
                event_type=ReviewEventType.REVIEWER_END,
                details={
                    "review_type": "generated_output_review",
                    "findings_count": len(report.findings) if report and hasattr(report, 'findings') else 0
                },
            )
            self.context_manager.add_event(event)

            return report
        except Exception as e:
            # Add error event
            event = ReviewEvent(
                timestamp=time.time(),
                event_type=ReviewEventType.REVIEWER_END,
                details={
                    "review_type": "generated_output_review",
                    "error": str(e),
                    "status": "failed"
                },
            )
            self.context_manager.add_event(event)
            raise e

    def _run_rules_engine_review(self, **kwargs) -> Any:
        """Execute rules engine review."""
        event = ReviewEvent(
            timestamp=time.time(),
            event_type=ReviewEventType.REVIEWER_START,
            details={"review_type": "rules_engine_review", "params": kwargs},
        )
        self.context_manager.add_event(event)

        try:
            engine = kwargs.get("engine") or ReviewRulesEngine()
            context = kwargs.get("review_context", {})

            results = engine.evaluate_all_rules(context)

            # Add completion event
            event = ReviewEvent(
                timestamp=time.time(),
                event_type=ReviewEventType.REVIEWER_END,
                details={
                    "review_type": "rules_engine_review",
                    "violations_count": sum(1 for v in results.values() if v)
                },
            )
            self.context_manager.add_event(event)

            return results
        except Exception as e:
            # Add error event
            event = ReviewEvent(
                timestamp=time.time(),
                event_type=ReviewEventType.REVIEWER_END,
                details={
                    "review_type": "rules_engine_review",
                    "error": str(e),
                    "status": "failed"
                },
            )
            self.context_manager.add_event(event)
            raise e

    def _run_discipline_review(self, **kwargs) -> Any:
        """Execute discipline review."""
        event = ReviewEvent(
            timestamp=time.time(),
            event_type=ReviewEventType.REVIEWER_START,
            details={"review_type": "discipline_review", "params": kwargs},
        )
        self.context_manager.add_event(event)

        try:
            adjuster = kwargs.get("adjuster") or ReviewAdjuster()
            discipline_level = kwargs.get("discipline_level")

            if discipline_level:
                settings = adjuster.prepare_settings(discipline_level)
            else:
                from .discipline_control.discipline_level import DisciplineLevel
                settings = adjuster.prepare_settings(DisciplineLevel.BALANCED)

            # Add completion event
            event = ReviewEvent(
                timestamp=time.time(),
                event_type=ReviewEventType.REVIEWER_END,
                details={
                    "review_type": "discipline_review",
                    "settings_applied": len(settings) if settings else 0
                },
            )
            self.context_manager.add_event(event)

            return settings
        except Exception as e:
            # Add error event
            event = ReviewEvent(
                timestamp=time.time(),
                event_type=ReviewEventType.REVIEWER_END,
                details={
                    "review_type": "discipline_review",
                    "error": str(e),
                    "status": "failed"
                },
            )
            self.context_manager.add_event(event)
            raise e


class ReviewMechanismOrchestrator:
    """Main orchestrator for the unified review mechanism."""

    def __init__(self):
        self.context_manager = ReviewContextManager()
        self.scheduler = ReviewScheduler(self.context_manager)
        self.coordinator = ReviewCoordinator(self.context_manager, self.scheduler)
        self.event_handlers = []

    def register_event_handler(self, handler: Callable[[ReviewEvent], None]) -> None:
        """Register an event handler to process events."""
        self.event_handlers.append(handler)

    def run_comprehensive_review(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a comprehensive review based on the provided configuration.

        Args:
            config: Configuration specifying what reviews to run and how

        Returns:
            Dictionary containing aggregated review results
        """
        # Update context with configuration
        self.context_manager.update_context("current_config", config)

        # Add start event
        start_event = ReviewEvent(
            timestamp=time.time(),
            event_type=ReviewEventType.SCHEDULER_START,
            details={"config_keys": list(config.keys())},
        )
        self.context_manager.add_event(start_event)

        # Get reviews configuration
        reviews_config = config.get("reviews", [])

        # Coordinate the reviews
        aggregated_results = self.coordinator.coordinate_reviews(reviews_config)

        # Finalize results and create consolidated report
        final_results = self._finalize_results(aggregated_results, config)

        # Update context with final results
        self.context_manager.update_context("final_results", final_results)

        return final_results

    def _finalize_results(self, aggregated_results: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize aggregated results and create consolidated report."""
        # Create consolidated report
        consolidated_report = {
            "session_id": self.context_manager.get_context()["review_session_id"],
            "start_time": self.context_manager.get_context()["start_time"],
            "end_time": time.time(),
            "duration": time.time() - self.context_manager.get_context()["start_time"],
            "summary": aggregated_results["summary"],
            "findings": aggregated_results["findings"],
            "detailed_results": self.context_manager.get_context()["results"],
            "review_history": self.context_manager.get_context()["review_history"],
            "configuration_used": config
        }

        # Add to aggregated results
        aggregated_results["consolidated_report"] = consolidated_report

        # Update context with metadata
        self.context_manager.update_context("completed_at", time.time())

        return aggregated_results

    def export_results(self, results: Dict[str, Any], output_path: str) -> bool:
        """Export review results to a file."""
        try:
            # Prepare data for export (convert non-serializable objects)
            export_data = self._prepare_export_data(results)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Error exporting results to {output_path}: {e}")
            return False

    def _prepare_export_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare results data for export by handling non-serializable objects."""
        import copy
        export_data = copy.deepcopy(results)

        # Process consolidated report to make it JSON serializable
        if "consolidated_report" in export_data:
            report = export_data["consolidated_report"]

            # Convert Review objects to dictionaries if needed
            if "findings" in report and isinstance(report["findings"], list):
                serializable_findings = []
                for finding in report["findings"]:
                    if hasattr(finding, '__dict__'):
                        # Convert object to dictionary
                        finding_dict = finding.__dict__.copy()
                        serializable_findings.append(finding_dict)
                    else:
                        serializable_findings.append(finding)
                report["findings"] = serializable_findings

            # Process detailed results
            if "detailed_results" in report:
                for comp_name, result_obj in report["detailed_results"].items():
                    if isinstance(result_obj, ReviewResult) and hasattr(result_obj, '__dict__'):
                        report["detailed_results"][comp_name] = result_obj.__dict__.copy()

        return export_data


def main():
    """Example usage of the review mechanism orchestrator."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        # Sample files for testing
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

        # Initialize the orchestrator
        orchestrator = ReviewMechanismOrchestrator()

        print("DCAE Review Mechanism Implementation - Comprehensive Review")
        print("="*70)

        # Define review configuration
        review_config = {
            "reviews": [
                {
                    "type": "generated_output_review",
                    "params": {
                        "project_path": str(project_path),
                        "target_path": str(project_path)  # Review the entire project
                    },
                    "priority": 2
                },
                {
                    "type": "rules_engine_review",
                    "params": {
                        "review_context": {
                            "file_path": str(sample_file),
                            "has_hardcoded_credentials": True,
                            "has_nested_loops": True
                        }
                    },
                    "priority": 1
                }
            ],
            "workflow_integration": {
                "trigger_on": ["commit", "merge_request"],
                "blocking_threshold": "medium",
                "report_format": "detailed"
            }
        }

        print("Running comprehensive review...")
        results = orchestrator.run_comprehensive_review(review_config)

        print(f"Review completed!")
        print(f"Total findings: {len(results['findings'])}")
        print(f"Summary: {results['summary']}")

        # Export results
        output_path = project_path / "comprehensive_review_report.json"
        success = orchestrator.export_results(results, str(output_path))
        if success:
            print(f"Results exported to: {output_path}")

        print("Review mechanism orchestrator executed successfully!")


if __name__ == "__main__":
    main()