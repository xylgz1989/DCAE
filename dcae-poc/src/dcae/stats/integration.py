"""Integration module for connecting statistics collection to DCAE operations."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from pathlib import Path

from ..core import DCAEOrchestrator
from .collector import StatisticsCollector
from .dashboard import PerformanceDashboard
from .storage import StatisticsStorage
from .models import OperationType


class DCAEStatsIntegration:
    """Integrates statistics collection into DCAE operations."""

    def __init__(self, orchestrator: DCAEOrchestrator, storage_path: str = "./storage"):
        """
        Initialize the statistics integration.

        Args:
            orchestrator: DCAEOrchestrator instance for DCAE operations
            storage_path: Path for storing statistics
        """
        self.orchestrator = orchestrator

        # Initialize statistics components
        self.stats_storage = StatisticsStorage()
        self.collector = StatisticsCollector(storage_path=storage_path)
        self.dashboard = PerformanceDashboard(storage_path=storage_path)

        # Initialize async components
        self._initialized = False

    async def initialize(self):
        """Initialize statistics components."""
        await self.stats_storage.initialize()
        self._initialized = True

    async def wrap_operation(
        self,
        operation_type: OperationType,
        operation_name: str,
        project_id: Optional[str] = None,
        operation_func=None,
        *args,
        **kwargs
    ):
        """
        Wrap an operation with statistics collection.

        Args:
            operation_type: Type of operation being tracked
            operation_name: Name/description of the operation
            project_id: ID of the associated project
            operation_func: The function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the operation function
        """
        if not self._initialized:
            await self.initialize()

        # Start tracking the operation
        operation_id = self.collector.start_operation(
            operation_type=operation_type,
            operation_name=operation_name,
            project_id=project_id,
            metadata=kwargs.get('metadata', {})
        )

        try:
            # Execute the operation
            result = await operation_func(*args, **kwargs) if asyncio.iscoroutinefunction(operation_func) else operation_func(*args, **kwargs)

            # Complete the operation successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                api_calls=kwargs.get('api_calls', 0),
                tokens_used=kwargs.get('tokens_used', 0)
            )

            return result

        except Exception as e:
            # Complete the operation with failure
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_project_creation(self, project_name: str, project_path: str):
        """
        Track project creation operation.

        Args:
            project_name: Name of the project being created
            project_path: Path where the project is being created
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.PROJECT_CREATION,
            operation_name=f"Create project: {project_name}",
            metadata={"project_path": project_path}
        )

        try:
            # Perform project creation through orchestrator
            # This would call the actual project creation method
            result = await self.orchestrator.execute_workflow(Path(project_path))  # Placeholder

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_code_generation(self, prompt: str, project_id: Optional[str] = None):
        """
        Track code generation operation.

        Args:
            prompt: The prompt for code generation
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.CODE_GENERATION,
            operation_name="Code generation",
            project_id=project_id,
            metadata={"prompt_length": len(prompt)}
        )

        try:
            # For now, we'll simulate a code generation operation
            # In a real scenario, this would call the actual code generation
            result = f"Simulated code generation for prompt: {prompt[:30]}..."

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_code_review(self, file_path: str, project_id: Optional[str] = None):
        """
        Track code review operation.

        Args:
            file_path: Path of the file being reviewed
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.CODE_REVIEW,
            operation_name=f"Code review: {file_path}",
            project_id=project_id,
            metadata={"file_path": file_path}
        )

        try:
            # For now, we'll simulate a code review operation
            # In a real scenario, this would call the actual code review
            result = f"Simulated code review for file: {file_path}"

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_debugging(self, error_msg: str, context: Optional[str] = None, project_id: Optional[str] = None):
        """
        Track debugging operation.

        Args:
            error_msg: Error message to debug
            context: Additional context (optional)
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.DEBUGGING,
            operation_name="Debug operation",
            project_id=project_id,
            metadata={
                "error_msg_length": len(error_msg),
                "has_context": context is not None
            }
        )

        try:
            # For now, we'll simulate a debugging operation
            # In a real scenario, this would call the actual debugging
            result = f"Simulated debugging for error: {error_msg[:30]}..."

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_requirement_generation(self, prompt: str, project_id: Optional[str] = None):
        """
        Track requirement generation operation.

        Args:
            prompt: The prompt for requirement generation
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.REQUIREMENT_GEN,
            operation_name="Requirement generation",
            project_id=project_id,
            metadata={"prompt_length": len(prompt)}
        )

        try:
            # For now, we'll simulate a requirement generation operation
            # In a real scenario, this would call the actual requirement generation
            result = f"Simulated requirement generation for prompt: {prompt[:30]}..."

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    def get_statistics_for_project(self, project_id: str, days: int = 7):
        """
        Get statistics for a specific project.

        Args:
            project_id: ID of the project
            days: Number of days to look back (default 7)

        Returns:
            Aggregate statistics for the project
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        return self.dashboard.get_project_statistics(project_id, start_date, end_date)

    def get_system_health(self):
        """
        Get overall system health based on statistics.

        Returns:
            Dictionary containing health metrics
        """
        return self.dashboard.get_health_status()

    async def shutdown(self):
        """Shutdown the statistics integration."""
        self.collector.shutdown()
        await self.stats_storage.close()


class DCAEStatsIntegration:
    """Integrates statistics collection into DCAE operations."""

    def __init__(self, core: DCACore, storage_manager: StorageManager):
        """
        Initialize the statistics integration.

        Args:
            core: DCACore instance for DCAE operations
            storage_manager: Storage manager for persisting statistics
        """
        self.core = core
        self.storage_manager = storage_manager

        # Initialize statistics components
        self.stats_storage = StatisticsStorage()
        self.collector = StatisticsCollector(enabled=True)
        self.dashboard = PerformanceDashboard(storage_manager)

        # Initialize async components
        self._initialized = False

    async def initialize(self):
        """Initialize statistics components."""
        await self.stats_storage.initialize()
        self._initialized = True

    async def wrap_operation(
        self,
        operation_type: OperationType,
        operation_name: str,
        project_id: Optional[str] = None,
        operation_func=None,
        *args,
        **kwargs
    ):
        """
        Wrap an operation with statistics collection.

        Args:
            operation_type: Type of operation being tracked
            operation_name: Name/description of the operation
            project_id: ID of the associated project
            operation_func: The function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the operation function
        """
        if not self._initialized:
            await self.initialize()

        # Start tracking the operation
        operation_id = self.collector.start_operation(
            operation_type=operation_type,
            operation_name=operation_name,
            project_id=project_id,
            metadata=kwargs.get('metadata', {})
        )

        try:
            # Execute the operation
            result = await operation_func(*args, **kwargs) if asyncio.iscoroutinefunction(operation_func) else operation_func(*args, **kwargs)

            # Complete the operation successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                api_calls=kwargs.get('api_calls', 0),
                tokens_used=kwargs.get('tokens_used', 0)
            )

            return result

        except Exception as e:
            # Complete the operation with failure
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_project_creation(self, project_name: str, project_path: str):
        """
        Track project creation operation.

        Args:
            project_name: Name of the project being created
            project_path: Path where the project is being created
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.PROJECT_CREATION,
            operation_name=f"Create project: {project_name}",
            metadata={"project_path": project_path}
        )

        try:
            # Perform project creation through core
            # This would call the actual project creation method
            result = await self.core.create_project(project_name, project_path)

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_code_generation(self, prompt: str, project_id: Optional[str] = None):
        """
        Track code generation operation.

        Args:
            prompt: The prompt for code generation
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.CODE_GENERATION,
            operation_name="Code generation",
            project_id=project_id,
            metadata={"prompt_length": len(prompt)}
        )

        try:
            # Perform code generation through core
            result = await self.core.generate_code(prompt)

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_code_review(self, file_path: str, project_id: Optional[str] = None):
        """
        Track code review operation.

        Args:
            file_path: Path of the file being reviewed
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.CODE_REVIEW,
            operation_name=f"Code review: {file_path}",
            project_id=project_id,
            metadata={"file_path": file_path}
        )

        try:
            # Perform code review through core
            result = await self.core.review_code(file_path)

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_debugging(self, error_msg: str, context: Optional[str] = None, project_id: Optional[str] = None):
        """
        Track debugging operation.

        Args:
            error_msg: Error message to debug
            context: Additional context (optional)
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.DEBUGGING,
            operation_name="Debug operation",
            project_id=project_id,
            metadata={
                "error_msg_length": len(error_msg),
                "has_context": context is not None
            }
        )

        try:
            # Perform debugging through core
            result = await self.core.debug_issue(error_msg, context)

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def track_requirement_generation(self, prompt: str, project_id: Optional[str] = None):
        """
        Track requirement generation operation.

        Args:
            prompt: The prompt for requirement generation
            project_id: ID of the project (optional)
        """
        operation_id = self.collector.start_operation(
            operation_type=OperationType.REQUIREMENT_GEN,
            operation_name="Requirement generation",
            project_id=project_id,
            metadata={"prompt_length": len(prompt)}
        )

        try:
            # Perform requirement generation through core
            result = await self.core.generate_requirement(prompt)

            # Complete successfully
            self.collector.complete_operation(
                operation_id=operation_id,
                success=True,
                metadata_updates={"result": "success"}
            )

            return result
        except Exception as e:
            self.collector.complete_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            raise e

    async def get_statistics_for_project(self, project_id: str, days: int = 7):
        """
        Get statistics for a specific project.

        Args:
            project_id: ID of the project
            days: Number of days to look back (default 7)

        Returns:
            Aggregate statistics for the project
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        return await self.dashboard.get_project_statistics(project_id, start_date, end_date)

    async def get_system_health(self):
        """
        Get overall system health based on statistics.

        Returns:
            Dictionary containing health metrics
        """
        return await self.dashboard.get_health_status()

    async def shutdown(self):
        """Shutdown the statistics integration."""
        self.collector.shutdown()
        await self.stats_storage.close()