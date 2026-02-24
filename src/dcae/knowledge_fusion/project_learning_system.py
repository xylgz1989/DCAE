"""Module for learning and remembering project-specific constraints and preferences."""
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import hashlib
from .knowledge_fuser import KnowledgeItem, KnowledgeSourceType


class ConstraintType(Enum):
    """Types of project constraints."""
    TECHNICAL = "technical"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    RESOURCE = "resource"
    TIMELINE = "timeline"
    COMPATIBILITY = "compatibility"


class PreferenceCategory(Enum):
    """Categories of project preferences."""
    CODING_STYLE = "coding_style"
    LIBRARY_CHOICE = "library_choice"
    ARCHITECTURE_PATTERN = "architecture_pattern"
    DEPLOYMENT_STRATEGY = "deployment_strategy"
    TESTING_APPROACH = "testing_approach"
    DOCUMENTATION_STYLE = "documentation_style"
    COMMUNICATION_PROTOCOL = "communication_protocol"


@dataclass
class ProjectConstraint:
    """Represents a project-specific constraint."""
    id: str
    type: ConstraintType
    description: str
    priority: int  # 1-5 scale, 5 being highest priority
    impact_level: str  # low, medium, high, critical
    justification: str
    created_at: str
    last_modified: str
    active: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProjectPreference:
    """Represents a project-specific preference."""
    id: str
    category: PreferenceCategory
    preference_value: str
    priority: int  # 1-5 scale
    justification: str
    created_at: str
    last_modified: str
    active: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LearningInsight:
    """Represents an insight learned from the project."""
    id: str
    insight_type: str  # constraint, preference, pattern, lesson
    description: str
    context: str
    timestamp: str
    importance: int  # 1-5 scale
    applicable_projects: List[str]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProjectLearningSystem:
    """Learns and remembers project-specific constraints and preferences."""

    def __init__(self):
        """Initialize the project learning system."""
        self.constraints: Dict[str, ProjectConstraint] = {}
        self.preferences: Dict[str, ProjectPreference] = {}
        self.learning_insights: Dict[str, LearningInsight] = {}
        self.constraint_indices: Dict[ConstraintType, Set[str]] = {
            ct: set() for ct in ConstraintType
        }
        self.preference_indices: Dict[PreferenceCategory, Set[str]] = {
            pc: set() for pc in PreferenceCategory
        }
        self.project_context: Dict[str, Any] = {}
        self.project_history: List[Dict[str, Any]] = []

    def register_constraint(
        self,
        constraint_type: ConstraintType,
        description: str,
        priority: int = 3,
        impact_level: str = "medium",
        justification: str = "",
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Register a project-specific constraint.

        Args:
            constraint_type: Type of constraint
            description: Description of the constraint
            priority: Priority level (1-5)
            impact_level: Impact level (low, medium, high, critical)
            justification: Reason for the constraint
            metadata: Additional metadata

        Returns:
            ID of the registered constraint
        """
        if metadata is None:
            metadata = {}

        # Generate unique ID based on content
        content_hash = hashlib.sha256(
            f"{constraint_type.value}:{description}:{justification}".encode()
        ).hexdigest()
        constraint_id = f"cnstr_{content_hash[:12]}"

        current_time = datetime.now().isoformat()

        constraint = ProjectConstraint(
            id=constraint_id,
            type=constraint_type,
            description=description,
            priority=min(max(priority, 1), 5),  # Clamp between 1-5
            impact_level=impact_level,
            justification=justification,
            created_at=current_time,
            last_modified=current_time,
            metadata=metadata
        )

        self.constraints[constraint_id] = constraint
        self.constraint_indices[constraint_type].add(constraint_id)

        # Log this activity
        self._log_activity("register_constraint", constraint_id)

        return constraint_id

    def register_preference(
        self,
        category: PreferenceCategory,
        preference_value: str,
        priority: int = 3,
        justification: str = "",
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Register a project-specific preference.

        Args:
            category: Category of preference
            preference_value: Value of the preference
            priority: Priority level (1-5)
            justification: Reason for the preference
            metadata: Additional metadata

        Returns:
            ID of the registered preference
        """
        if metadata is None:
            metadata = {}

        # Generate unique ID based on content
        content_hash = hashlib.sha256(
            f"{category.value}:{preference_value}:{justification}".encode()
        ).hexdigest()
        preference_id = f"pref_{content_hash[:12]}"

        current_time = datetime.now().isoformat()

        preference = ProjectPreference(
            id=preference_id,
            category=category,
            preference_value=preference_value,
            priority=min(max(priority, 1), 5),  # Clamp between 1-5
            justification=justification,
            created_at=current_time,
            last_modified=current_time,
            metadata=metadata
        )

        self.preferences[preference_id] = preference
        self.preference_indices[category].add(preference_id)

        # Log this activity
        self._log_activity("register_preference", preference_id)

        return preference_id

    def get_constraints_by_type(self, constraint_type: ConstraintType) -> List[ProjectConstraint]:
        """
        Get all constraints of a specific type.

        Args:
            constraint_type: Type of constraints to retrieve

        Returns:
            List of constraints of the specified type
        """
        constraint_ids = self.constraint_indices.get(constraint_type, set())
        return [
            self.constraints[cid]
            for cid in constraint_ids
            if cid in self.constraints
        ]

    def get_preferences_by_category(self, category: PreferenceCategory) -> List[ProjectPreference]:
        """
        Get all preferences of a specific category.

        Args:
            category: Category of preferences to retrieve

        Returns:
            List of preferences of the specified category
        """
        preference_ids = self.preference_indices.get(category, set())
        return [
            self.preferences[pid]
            for pid in preference_ids
            if pid in self.preferences
        ]

    def get_active_constraints(self) -> List[ProjectConstraint]:
        """Get all active constraints."""
        return [c for c in self.constraints.values() if c.active]

    def get_active_preferences(self) -> List[ProjectPreference]:
        """Get all active preferences."""
        return [p for p in self.preferences.values() if p.active]

    def update_constraint(
        self,
        constraint_id: str,
        description: str = None,
        priority: int = None,
        impact_level: str = None,
        justification: str = None,
        active: bool = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Update an existing constraint.

        Args:
            constraint_id: ID of constraint to update
            description: New description (optional)
            priority: New priority (optional)
            impact_level: New impact level (optional)
            justification: New justification (optional)
            active: New active status (optional)
            metadata: New metadata to merge (optional)

        Returns:
            True if update was successful, False otherwise
        """
        if constraint_id not in self.constraints:
            return False

        constraint = self.constraints[constraint_id]
        updated = False

        if description is not None:
            constraint.description = description
            updated = True
        if priority is not None:
            constraint.priority = min(max(priority, 1), 5)
            updated = True
        if impact_level is not None:
            constraint.impact_level = impact_level
            updated = True
        if justification is not None:
            constraint.justification = justification
            updated = True
        if active is not None:
            constraint.active = active
            updated = True
        if metadata is not None:
            constraint.metadata.update(metadata)
            updated = True

        if updated:
            constraint.last_modified = datetime.now().isoformat()

        # Log this activity
        self._log_activity("update_constraint", constraint_id)

        return updated

    def update_preference(
        self,
        preference_id: str,
        preference_value: str = None,
        priority: int = None,
        justification: str = None,
        active: bool = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Update an existing preference.

        Args:
            preference_id: ID of preference to update
            preference_value: New preference value (optional)
            priority: New priority (optional)
            justification: New justification (optional)
            active: New active status (optional)
            metadata: New metadata to merge (optional)

        Returns:
            True if update was successful, False otherwise
        """
        if preference_id not in self.preferences:
            return False

        preference = self.preferences[preference_id]
        updated = False

        if preference_value is not None:
            preference.preference_value = preference_value
            updated = True
        if priority is not None:
            preference.priority = min(max(priority, 1), 5)
            updated = True
        if justification is not None:
            preference.justification = justification
            updated = True
        if active is not None:
            preference.active = active
            updated = True
        if metadata is not None:
            preference.metadata.update(metadata)
            updated = True

        if updated:
            preference.last_modified = datetime.now().isoformat()

        # Log this activity
        self._log_activity("update_preference", preference_id)

        return updated

    def remove_constraint(self, constraint_id: str) -> bool:
        """
        Remove a constraint (soft delete by marking inactive).

        Args:
            constraint_id: ID of constraint to remove

        Returns:
            True if removal was successful, False otherwise
        """
        if constraint_id not in self.constraints:
            return False

        self.constraints[constraint_id].active = False
        self.constraints[constraint_id].last_modified = datetime.now().isoformat()

        # Log this activity
        self._log_activity("remove_constraint", constraint_id)

        return True

    def remove_preference(self, preference_id: str) -> bool:
        """
        Remove a preference (soft delete by marking inactive).

        Args:
            preference_id: ID of preference to remove

        Returns:
            True if removal was successful, False otherwise
        """
        if preference_id not in self.preferences:
            return False

        self.preferences[preference_id].active = False
        self.preferences[preference_id].last_modified = datetime.now().isoformat()

        # Log this activity
        self._log_activity("remove_preference", preference_id)

        return True

    def learn_from_project_event(self, event_type: str, context: str, details: Dict[str, Any]) -> str:
        """
        Learn from a project event and create an insight.

        Args:
            event_type: Type of event (e.g., "decision", "issue", "solution")
            context: Context of the event
            details: Details about the event

        Returns:
            ID of the created learning insight
        """
        insight_id = f"insight_{hashlib.sha256(f'{event_type}:{context}'.encode()).hexdigest()[:12]}"
        timestamp = datetime.now().isoformat()

        # Determine importance based on event type
        importance_map = {
            "critical_issue": 5,
            "major_decision": 4,
            "important_lesson": 4,
            "minor_issue": 2,
            "small_optimization": 2,
            "common_pattern": 3
        }
        importance = importance_map.get(event_type, 3)

        insight = LearningInsight(
            id=insight_id,
            insight_type=event_type,
            description=details.get("description", f"Learned from {event_type} event"),
            context=context,
            timestamp=timestamp,
            importance=importance,
            applicable_projects=details.get("applicable_projects", [])
        )

        self.learning_insights[insight_id] = insight

        # Log this activity
        self._log_activity("learn_from_event", insight_id)

        return insight_id

    def get_learning_insights(self, min_importance: int = 1) -> List[LearningInsight]:
        """
        Get learning insights with minimum importance level.

        Args:
            min_importance: Minimum importance level (1-5)

        Returns:
            List of learning insights with specified importance or higher
        """
        return [
            insight for insight in self.learning_insights.values()
            if insight.importance >= min_importance
        ]

    def get_applicable_knowledge_items(self) -> List[KnowledgeItem]:
        """
        Convert constraints and preferences to knowledge items for broader use.

        Returns:
            List of knowledge items representing project constraints and preferences
        """
        knowledge_items = []

        # Convert active constraints to knowledge items
        for constraint in self.get_active_constraints():
            item = KnowledgeItem(
                id=f"k_{constraint.id}",
                source_type=KnowledgeSourceType.DEVELOPMENT,
                content=f"CONSTRAINT: {constraint.description} - Priority: {constraint.priority}, Impact: {constraint.impact_level}",
                relevance_score=constraint.priority / 5.0,
                tags=[constraint.type.value, "constraint", "project-specific"],
                metadata=constraint.metadata
            )
            knowledge_items.append(item)

        # Convert active preferences to knowledge items
        for preference in self.get_active_preferences():
            item = KnowledgeItem(
                id=f"k_{preference.id}",
                source_type=KnowledgeSourceType.DEVELOPMENT,
                content=f"PREFERENCE: {preference.category.value} - {preference.preference_value} - Priority: {preference.priority}",
                relevance_score=preference.priority / 5.0,
                tags=[preference.category.value, "preference", "project-specific"],
                metadata=preference.metadata
            )
            knowledge_items.append(item)

        return knowledge_items

    def set_project_context(self, context: Dict[str, Any]) -> None:
        """
        Set the current project context.

        Args:
            context: Project context information
        """
        self.project_context.update(context)

        # Log this activity
        self._log_activity("set_project_context", context.get("project_id", "unknown"))

    def get_project_context(self) -> Dict[str, Any]:
        """
        Get the current project context.

        Returns:
            Current project context
        """
        return self.project_context.copy()

    def _log_activity(self, activity_type: str, target_id: str) -> None:
        """
        Log an activity for historical tracking.

        Args:
            activity_type: Type of activity
            target_id: ID of the target object
        """
        activity = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_type,
            "target_id": target_id,
            "context": self.project_context.copy()
        }
        self.project_history.append(activity)

    def get_project_history(self) -> List[Dict[str, Any]]:
        """
        Get the project history.

        Returns:
            List of historical activities
        """
        return self.project_history.copy()

    def export_project_memory(self) -> str:
        """
        Export all project-specific constraints, preferences, and insights as JSON.

        Returns:
            JSON string containing project memory
        """
        export_data = {
            "constraints": [],
            "preferences": [],
            "learning_insights": [],
            "project_context": self.project_context,
            "project_history": self.project_history
        }

        for constraint in self.constraints.values():
            export_data["constraints"].append({
                "id": constraint.id,
                "type": constraint.type.value,
                "description": constraint.description,
                "priority": constraint.priority,
                "impact_level": constraint.impact_level,
                "justification": constraint.justification,
                "created_at": constraint.created_at,
                "last_modified": constraint.last_modified,
                "active": constraint.active,
                "metadata": constraint.metadata
            })

        for preference in self.preferences.values():
            export_data["preferences"].append({
                "id": preference.id,
                "category": preference.category.value,
                "preference_value": preference.preference_value,
                "priority": preference.priority,
                "justification": preference.justification,
                "created_at": preference.created_at,
                "last_modified": preference.last_modified,
                "active": preference.active,
                "metadata": preference.metadata
            })

        for insight in self.learning_insights.values():
            export_data["learning_insights"].append({
                "id": insight.id,
                "insight_type": insight.insight_type,
                "description": insight.description,
                "context": insight.context,
                "timestamp": insight.timestamp,
                "importance": insight.importance,
                "applicable_projects": insight.applicable_projects,
                "metadata": insight.metadata
            })

        return json.dumps(export_data, indent=2)

    def import_project_memory(self, json_str: str) -> bool:
        """
        Import project-specific constraints, preferences, and insights from JSON.

        Args:
            json_str: JSON string containing project memory data

        Returns:
            True if import was successful, False otherwise
        """
        try:
            data = json.loads(json_str)

            # Import constraints
            for constraint_data in data.get("constraints", []):
                constraint = ProjectConstraint(
                    id=constraint_data["id"],
                    type=ConstraintType(constraint_data["type"]),
                    description=constraint_data["description"],
                    priority=constraint_data["priority"],
                    impact_level=constraint_data["impact_level"],
                    justification=constraint_data["justification"],
                    created_at=constraint_data["created_at"],
                    last_modified=constraint_data["last_modified"],
                    active=constraint_data.get("active", True),
                    metadata=constraint_data.get("metadata", {})
                )
                self.constraints[constraint.id] = constraint
                self.constraint_indices[constraint.type].add(constraint.id)

            # Import preferences
            for preference_data in data.get("preferences", []):
                preference = ProjectPreference(
                    id=preference_data["id"],
                    category=PreferenceCategory(preference_data["category"]),
                    preference_value=preference_data["preference_value"],
                    priority=preference_data["priority"],
                    justification=preference_data["justification"],
                    created_at=preference_data["created_at"],
                    last_modified=preference_data["last_modified"],
                    active=preference_data.get("active", True),
                    metadata=preference_data.get("metadata", {})
                )
                self.preferences[preference.id] = preference
                self.preference_indices[preference.category].add(preference.id)

            # Import learning insights
            for insight_data in data.get("learning_insights", []):
                insight = LearningInsight(
                    id=insight_data["id"],
                    insight_type=insight_data["insight_type"],
                    description=insight_data["description"],
                    context=insight_data["context"],
                    timestamp=insight_data["timestamp"],
                    importance=insight_data["importance"],
                    applicable_projects=insight_data["applicable_projects"],
                    metadata=insight_data.get("metadata", {})
                )
                self.learning_insights[insight.id] = insight

            # Restore project context and history
            self.project_context = data.get("project_context", {})
            self.project_history = data.get("project_history", [])

            return True
        except (json.JSONDecodeError, ValueError):
            return False

    def get_adaptive_guidance(self) -> Dict[str, Any]:
        """
        Get adaptive guidance based on accumulated project knowledge.

        Returns:
            Dictionary with adaptive guidance recommendations
        """
        guidance = {
            "critical_constraints": [],
            "high_priority_preferences": [],
            "key_lessons_learned": [],
            "recommended_approaches": []
        }

        # Identify critical constraints
        critical_constraints = [
            c for c in self.get_active_constraints()
            if c.impact_level == "critical" or c.priority >= 4
        ]
        guidance["critical_constraints"] = [
            {"id": c.id, "description": c.description, "type": c.type.value}
            for c in critical_constraints
        ]

        # Identify high priority preferences
        high_priority_prefs = [
            p for p in self.get_active_preferences()
            if p.priority >= 4
        ]
        guidance["high_priority_preferences"] = [
            {"id": p.id, "category": p.category.value, "value": p.preference_value}
            for p in high_priority_prefs
        ]

        # Get key lessons learned (high importance insights)
        key_lessons = [
            i for i in self.get_learning_insights(min_importance=4)
        ]
        guidance["key_lessons_learned"] = [
            {"id": i.id, "description": i.description, "type": i.insight_type}
            for i in key_lessons
        ]

        # Generate recommended approaches based on knowledge
        if critical_constraints:
            guidance["recommended_approaches"].append(
                "Prioritize solutions that address critical constraints first"
            )
        if high_priority_prefs:
            guidance["recommended_approaches"].append(
                "Adhere to project-specific preferences and conventions"
            )
        if key_lessons:
            guidance["recommended_approaches"].append(
                "Apply lessons learned from similar situations in this project"
            )

        return guidance