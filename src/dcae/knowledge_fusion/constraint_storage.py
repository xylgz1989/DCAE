"""
Constraint Storage System

This module provides a comprehensive storage mechanism for project-specific constraints,
including both in-memory and persistent storage options.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from pathlib import Path
import json
import yaml
import sqlite3
from datetime import datetime
import threading
from abc import ABC, abstractmethod


class Constraint(BaseModel):
    """
    Represents a single project-specific constraint
    """
    id: str = Field(..., description="Unique identifier for the constraint")
    name: str = Field(..., description="Human-readable name of the constraint")
    category: str = Field(..., description="Category of the constraint (technical, architectural, budgetary, etc.)")
    description: str = Field(..., description="Detailed description of the constraint")
    severity: str = Field(default="medium", description="Severity level: low, medium, high, critical")
    active: bool = Field(default=True, description="Whether the constraint is currently active")
    source: str = Field(default="unknown", description="Source of the constraint information")
    created_at: datetime = Field(default_factory=datetime.now, description="When the constraint was first identified")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the constraint was last updated")
    related_files: List[str] = Field(default_factory=list, description="Files or components affected by this constraint")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing and searching constraints")


class ConstraintStorageInterface(ABC):
    """
    Abstract interface for constraint storage systems
    """

    @abstractmethod
    def save_constraint(self, constraint: Constraint) -> bool:
        """Save a constraint to storage"""
        pass

    @abstractmethod
    def load_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """Load a constraint from storage by ID"""
        pass

    @abstractmethod
    def delete_constraint(self, constraint_id: str) -> bool:
        """Delete a constraint from storage"""
        pass

    @abstractmethod
    def list_constraints(self, category: Optional[str] = None, active_only: bool = True) -> List[Constraint]:
        """List constraints, optionally filtered by category"""
        pass

    @abstractmethod
    def update_constraint(self, constraint: Constraint) -> bool:
        """Update an existing constraint"""
        pass


class JSONConstraintStorage(ConstraintStorageInterface):
    """
    JSON-based constraint storage implementation
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.lock = threading.Lock()

        # Ensure storage directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize the storage file if it doesn't exist
        if not self.storage_path.exists():
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def save_constraint(self, constraint: Constraint) -> bool:
        """Save a constraint to JSON storage"""
        with self.lock:
            try:
                # Load existing constraints
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert datetime objects to strings for JSON serialization
                constraint_dict = constraint.dict()
                constraint_dict['created_at'] = constraint.created_at.isoformat()
                constraint_dict['updated_at'] = constraint.updated_at.isoformat()

                # Save the constraint
                data[constraint.id] = constraint_dict

                # Write back to file
                with open(self.storage_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                return True
            except Exception as e:
                print(f"Error saving constraint {constraint.id}: {str(e)}")
                return False

    def load_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """Load a constraint from JSON storage by ID"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if constraint_id not in data:
                return None

            constraint_data = data[constraint_id]

            # Convert datetime strings back to datetime objects
            constraint_data['created_at'] = datetime.fromisoformat(constraint_data['created_at'])
            constraint_data['updated_at'] = datetime.fromisoformat(constraint_data['updated_at'])

            return Constraint(**constraint_data)
        except Exception as e:
            print(f"Error loading constraint {constraint_id}: {str(e)}")
            return None

    def delete_constraint(self, constraint_id: str) -> bool:
        """Delete a constraint from JSON storage"""
        with self.lock:
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if constraint_id in data:
                    del data[constraint_id]

                    with open(self.storage_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)

                    return True
                return False
            except Exception as e:
                print(f"Error deleting constraint {constraint_id}: {str(e)}")
                return False

    def list_constraints(self, category: Optional[str] = None, active_only: bool = True) -> List[Constraint]:
        """List constraints, optionally filtered by category"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            constraints = []
            for constraint_data in data.values():
                # Convert datetime strings back to datetime objects
                constraint_data['created_at'] = datetime.fromisoformat(constraint_data['created_at'])
                constraint_data['updated_at'] = datetime.fromisoformat(constraint_data['updated_at'])

                constraint = Constraint(**constraint_data)

                # Apply filters
                if active_only and not constraint.active:
                    continue
                if category and constraint.category.lower() != category.lower():
                    continue

                constraints.append(constraint)

            return constraints
        except Exception as e:
            print(f"Error listing constraints: {str(e)}")
            return []

    def update_constraint(self, constraint: Constraint) -> bool:
        """Update an existing constraint in JSON storage"""
        return self.save_constraint(constraint)


class SQLiteConstraintStorage(ConstraintStorageInterface):
    """
    SQLite-based constraint storage implementation
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.lock = threading.Lock()

        # Ensure storage directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize the database
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with the required tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create the constraints table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS constraints (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT DEFAULT 'medium',
                    active BOOLEAN DEFAULT 1,
                    source TEXT DEFAULT 'unknown',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    related_files TEXT,
                    tags TEXT
                )
            ''')

            conn.commit()
            conn.close()

    def save_constraint(self, constraint: Constraint) -> bool:
        """Save a constraint to SQLite storage"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Convert related_files and tags to JSON strings
                related_files_json = json.dumps(constraint.related_files)
                tags_json = json.dumps(constraint.tags)

                cursor.execute('''
                    INSERT OR REPLACE INTO constraints
                    (id, name, category, description, severity, active, source, created_at, updated_at, related_files, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    constraint.id,
                    constraint.name,
                    constraint.category,
                    constraint.description,
                    constraint.severity,
                    constraint.active,
                    constraint.source,
                    constraint.created_at.isoformat(),
                    constraint.updated_at.isoformat(),
                    related_files_json,
                    tags_json
                ))

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error saving constraint {constraint.id}: {str(e)}")
                return False

    def load_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """Load a constraint from SQLite storage by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM constraints WHERE id = ?', (constraint_id,))
            row = cursor.fetchone()

            if row is None:
                conn.close()
                return None

            # Extract values from the row
            id_val, name, category, description, severity, active, source, created_at_str, updated_at_str, related_files_json, tags_json = row

            # Parse JSON fields
            related_files = json.loads(related_files_json) if related_files_json else []
            tags = json.loads(tags_json) if tags_json else []

            # Convert datetime strings back to datetime objects
            created_at = datetime.fromisoformat(created_at_str)
            updated_at = datetime.fromisoformat(updated_at_str)

            conn.close()

            return Constraint(
                id=id_val,
                name=name,
                category=category,
                description=description,
                severity=severity,
                active=bool(active),
                source=source,
                created_at=created_at,
                updated_at=updated_at,
                related_files=related_files,
                tags=tags
            )
        except Exception as e:
            print(f"Error loading constraint {constraint_id}: {str(e)}")
            return None

    def delete_constraint(self, constraint_id: str) -> bool:
        """Delete a constraint from SQLite storage"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('DELETE FROM constraints WHERE id = ?', (constraint_id,))
                deleted = cursor.rowcount > 0

                conn.commit()
                conn.close()

                return deleted
            except Exception as e:
                print(f"Error deleting constraint {constraint_id}: {str(e)}")
                return False

    def list_constraints(self, category: Optional[str] = None, active_only: bool = True) -> List[Constraint]:
        """List constraints, optionally filtered by category"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build the query based on filters
            query = "SELECT * FROM constraints"
            params = []

            conditions = []
            if active_only:
                conditions.append("active = 1")
            if category:
                conditions.append("category = ?")
                params.append(category)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            constraints = []
            for row in rows:
                id_val, name, category, description, severity, active, source, created_at_str, updated_at_str, related_files_json, tags_json = row

                # Parse JSON fields
                related_files = json.loads(related_files_json) if related_files_json else []
                tags = json.loads(tags_json) if tags_json else []

                # Convert datetime strings back to datetime objects
                created_at = datetime.fromisoformat(created_at_str)
                updated_at = datetime.fromisoformat(updated_at_str)

                constraints.append(Constraint(
                    id=id_val,
                    name=name,
                    category=category,
                    description=description,
                    severity=severity,
                    active=bool(active),
                    source=source,
                    created_at=created_at,
                    updated_at=updated_at,
                    related_files=related_files,
                    tags=tags
                ))

            conn.close()
            return constraints
        except Exception as e:
            print(f"Error listing constraints: {str(e)}")
            return []

    def update_constraint(self, constraint: Constraint) -> bool:
        """Update an existing constraint in SQLite storage"""
        return self.save_constraint(constraint)


class CompositeConstraintStorage(ConstraintStorageInterface):
    """
    Composite storage that combines multiple storage systems
    """

    def __init__(self, storages: List[ConstraintStorageInterface]):
        self.storages = storages

    def save_constraint(self, constraint: Constraint) -> bool:
        """Save to all storage systems"""
        results = [storage.save_constraint(constraint) for storage in self.storages]
        return all(results)

    def load_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """Try to load from each storage system in order"""
        for storage in self.storages:
            constraint = storage.load_constraint(constraint_id)
            if constraint:
                return constraint
        return None

    def delete_constraint(self, constraint_id: str) -> bool:
        """Delete from all storage systems"""
        results = [storage.delete_constraint(constraint_id) for storage in self.storages]
        return all(results)

    def list_constraints(self, category: Optional[str] = None, active_only: bool = True) -> List[Constraint]:
        """Aggregate constraints from all storage systems"""
        all_constraints = []
        seen_ids = set()

        for storage in self.storages:
            constraints = storage.list_constraints(category, active_only)
            for constraint in constraints:
                if constraint.id not in seen_ids:
                    all_constraints.append(constraint)
                    seen_ids.add(constraint.id)

        return all_constraints

    def update_constraint(self, constraint: Constraint) -> bool:
        """Update in all storage systems"""
        results = [storage.update_constraint(constraint) for storage in self.storages]
        return all(results)


class ProjectConstraintStorage:
    """
    Main constraint storage manager for the project
    """

    def __init__(self, storage_path: Optional[Path] = None, storage_type: str = "json"):
        """
        Initialize the project constraint storage

        Args:
            storage_path: Path for storage (defaults to project config directory)
            storage_type: Type of storage ('json', 'sqlite', or 'composite')
        """
        self.storage_path = storage_path or Path.home() / ".dcae" / "constraints.json"

        if storage_type == "json":
            self.storage = JSONConstraintStorage(self.storage_path)
        elif storage_type == "sqlite":
            sqlite_path = self.storage_path.with_suffix('.db')
            self.storage = SQLiteConstraintStorage(sqlite_path)
        elif storage_type == "composite":
            # Use both JSON and SQLite for redundancy
            json_storage = JSONConstraintStorage(self.storage_path)
            sqlite_path = self.storage_path.with_suffix('.db')
            sqlite_storage = SQLiteConstraintStorage(sqlite_path)
            self.storage = CompositeConstraintStorage([json_storage, sqlite_storage])
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    def save_constraint(self, constraint: Constraint) -> bool:
        """Save a constraint using the underlying storage"""
        return self.storage.save_constraint(constraint)

    def load_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """Load a constraint by ID using the underlying storage"""
        return self.storage.load_constraint(constraint_id)

    def delete_constraint(self, constraint_id: str) -> bool:
        """Delete a constraint by ID using the underlying storage"""
        return self.storage.delete_constraint(constraint_id)

    def list_constraints(self, category: Optional[str] = None, active_only: bool = True) -> List[Constraint]:
        """List constraints using the underlying storage"""
        return self.storage.list_constraints(category, active_only)

    def update_constraint(self, constraint: Constraint) -> bool:
        """Update a constraint using the underlying storage"""
        return self.storage.update_constraint(constraint)

    def get_constraint_by_tag(self, tag: str) -> List[Constraint]:
        """Find constraints by tag"""
        all_constraints = self.list_constraints(active_only=False)
        return [c for c in all_constraints if tag.lower() in [t.lower() for t in c.tags]]

    def get_constraints_by_severity(self, severity: str) -> List[Constraint]:
        """Find constraints by severity level"""
        all_constraints = self.list_constraints(active_only=False)
        return [c for c in all_constraints if c.severity.lower() == severity.lower()]

    def get_constraint_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored constraints"""
        all_constraints = self.list_constraints(active_only=False)

        stats = {
            'total': len(all_constraints),
            'active': len([c for c in all_constraints if c.active]),
            'inactive': len([c for c in all_constraints if not c.active]),
            'by_category': {},
            'by_severity': {},
            'by_source': {}
        }

        for constraint in all_constraints:
            # Category count
            category = constraint.category
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

            # Severity count
            severity = constraint.severity
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1

            # Source count
            source = constraint.source
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1

        return stats


if __name__ == "__main__":
    # Example usage
    storage = ProjectConstraintStorage()

    # Create a sample constraint
    sample_constraint = Constraint(
        id="tech-sample-constraint",
        name="Sample Technical Constraint",
        category="technical",
        description="This is a sample technical constraint for demonstration purposes",
        severity="medium",
        source="example"
    )

    # Save the constraint
    if storage.save_constraint(sample_constraint):
        print(f"Saved constraint: {sample_constraint.name}")

    # Load the constraint
    loaded_constraint = storage.load_constraint("tech-sample-constraint")
    if loaded_constraint:
        print(f"Loaded constraint: {loaded_constraint.name}")

    # List all constraints
    all_constraints = storage.list_constraints()
    print(f"Total constraints: {len(all_constraints)}")

    # Show statistics
    stats = storage.get_constraint_statistics()
    print(f"Statistics: {stats}")