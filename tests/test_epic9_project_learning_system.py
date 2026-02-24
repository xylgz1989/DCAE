import unittest
from src.dcae.knowledge_fusion.project_learning_system import ProjectLearningSystem, ConstraintType, PreferenceCategory, ProjectConstraint, ProjectPreference
from src.dcae.knowledge_fusion.knowledge_fuser import KnowledgeItem, KnowledgeSourceType


class TestEpic9ProjectLearningSystem(unittest.TestCase):
    """Test cases for Project Learning System (FR50)."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.learning_system = ProjectLearningSystem()

    def test_register_and_retrieve_constraints(self):
        """Test registering and retrieving project constraints."""
        # Register different types of constraints
        constraint1_id = self.learning_system.register_constraint(
            constraint_type=ConstraintType.TECHNICAL,
            description="Must use Python 3.8+ for compatibility",
            priority=4,
            impact_level="high",
            justification="Required for async features"
        )

        constraint2_id = self.learning_system.register_constraint(
            constraint_type=ConstraintType.PERFORMANCE,
            description="API response time must be under 100ms",
            priority=5,
            impact_level="critical",
            justification="Business requirement for user experience"
        )

        constraint3_id = self.learning_system.register_constraint(
            constraint_type=ConstraintType.SECURITY,
            description="All user data must be encrypted at rest",
            priority=5,
            impact_level="critical",
            justification="Compliance requirement"
        )

        # Verify IDs were returned
        self.assertTrue(constraint1_id.startswith("cnstr_"))
        self.assertTrue(constraint2_id.startswith("cnstr_"))
        self.assertTrue(constraint3_id.startswith("cnstr_"))

        # Get constraints by type
        tech_constraints = self.learning_system.get_constraints_by_type(ConstraintType.TECHNICAL)
        perf_constraints = self.learning_system.get_constraints_by_type(ConstraintType.PERFORMANCE)
        security_constraints = self.learning_system.get_constraints_by_type(ConstraintType.SECURITY)

        self.assertEqual(len(tech_constraints), 1)
        self.assertEqual(len(perf_constraints), 1)
        self.assertEqual(len(security_constraints), 1)

        # Verify content
        self.assertEqual(tech_constraints[0].description, "Must use Python 3.8+ for compatibility")
        self.assertEqual(perf_constraints[0].impact_level, "critical")
        self.assertEqual(security_constraints[0].priority, 5)

    def test_register_and_retrieve_preferences(self):
        """Test registering and retrieving project preferences."""
        # Register different categories of preferences
        pref1_id = self.learning_system.register_preference(
            category=PreferenceCategory.CODING_STYLE,
            preference_value="Use black formatter for Python code",
            priority=3,
            justification="Team consistency requirement"
        )

        pref2_id = self.learning_system.register_preference(
            category=PreferenceCategory.LIBRARY_CHOICE,
            preference_value="Use SQLAlchemy for database operations",
            priority=4,
            justification="ORM requirements and team expertise"
        )

        pref3_id = self.learning_system.register_preference(
            category=PreferenceCategory.TESTING_APPROACH,
            preference_value="100% test coverage required for critical modules",
            priority=4,
            justification="Quality requirements"
        )

        # Verify IDs were returned
        self.assertTrue(pref1_id.startswith("pref_"))
        self.assertTrue(pref2_id.startswith("pref_"))

        # Get preferences by category
        coding_prefs = self.learning_system.get_preferences_by_category(PreferenceCategory.CODING_STYLE)
        lib_prefs = self.learning_system.get_preferences_by_category(PreferenceCategory.LIBRARY_CHOICE)
        testing_prefs = self.learning_system.get_preferences_by_category(PreferenceCategory.TESTING_APPROACH)

        self.assertEqual(len(coding_prefs), 1)
        self.assertEqual(len(lib_prefs), 1)
        self.assertEqual(len(testing_prefs), 1)

        # Verify content
        self.assertIn("black formatter", coding_prefs[0].preference_value)
        self.assertIn("SQLAlchemy", lib_prefs[0].preference_value)
        self.assertIn("test coverage", testing_prefs[0].preference_value)

    def test_update_constraint(self):
        """Test updating an existing constraint."""
        # Register a constraint
        constraint_id = self.learning_system.register_constraint(
            constraint_type=ConstraintType.COMPLIANCE,
            description="GDPR compliance required for EU users",
            priority=3,
            impact_level="high",
            justification="Legal requirement"
        )

        # Verify initial values
        initial_constraint = self.learning_system.constraints[constraint_id]
        self.assertEqual(initial_constraint.description, "GDPR compliance required for EU users")
        self.assertEqual(initial_constraint.priority, 3)
        self.assertEqual(initial_constraint.impact_level, "high")

        # Update the constraint
        update_success = self.learning_system.update_constraint(
            constraint_id=constraint_id,
            description="GDPR and CCPA compliance required for all users",
            priority=5,
            impact_level="critical",
            justification="Expanded legal requirements"
        )

        # Verify update was successful
        self.assertTrue(update_success)

        # Verify updated values
        updated_constraint = self.learning_system.constraints[constraint_id]
        self.assertEqual(updated_constraint.description, "GDPR and CCPA compliance required for all users")
        self.assertEqual(updated_constraint.priority, 5)
        self.assertEqual(updated_constraint.impact_level, "critical")
        self.assertEqual(updated_constraint.justification, "Expanded legal requirements")

    def test_update_preference(self):
        """Test updating an existing preference."""
        # Register a preference
        preference_id = self.learning_system.register_preference(
            category=PreferenceCategory.DOCUMENTATION_STYLE,
            preference_value="Use Google style docstrings",
            priority=2,
            justification="Team familiarity"
        )

        # Verify initial values
        initial_preference = self.learning_system.preferences[preference_id]
        self.assertEqual(initial_preference.preference_value, "Use Google style docstrings")
        self.assertEqual(initial_preference.priority, 2)

        # Update the preference
        update_success = self.learning_system.update_preference(
            preference_id=preference_id,
            preference_value="Use Sphinx-style docstrings with type hints",
            priority=4,
            justification="Better integration with documentation tools"
        )

        # Verify update was successful
        self.assertTrue(update_success)

        # Verify updated values
        updated_preference = self.learning_system.preferences[preference_id]
        self.assertEqual(updated_preference.preference_value, "Use Sphinx-style docstrings with type hints")
        self.assertEqual(updated_preference.priority, 4)
        self.assertEqual(updated_preference.justification, "Better integration with documentation tools")

    def test_remove_constraint_and_preference(self):
        """Test removing (deactivating) constraints and preferences."""
        # Register items
        constraint_id = self.learning_system.register_constraint(
            constraint_type=ConstraintType.RESOURCE,
            description="Memory usage must be under 1GB",
            priority=3
        )

        preference_id = self.learning_system.register_preference(
            category=PreferenceCategory.DEPLOYMENT_STRATEGY,
            preference_value="Use Docker containers",
            priority=3
        )

        # Verify they exist initially
        all_constraints = self.learning_system.get_active_constraints()
        all_preferences = self.learning_system.get_active_preferences()

        original_constraint_count = len(all_constraints)
        original_preference_count = len(all_preferences)

        # Remove the constraint
        remove_constraint_success = self.learning_system.remove_constraint(constraint_id)
        self.assertTrue(remove_constraint_success)

        # Remove the preference
        remove_preference_success = self.learning_system.remove_preference(preference_id)
        self.assertTrue(remove_preference_success)

        # Verify counts after removal
        new_constraints = self.learning_system.get_active_constraints()
        new_preferences = self.learning_system.get_active_preferences()

        # The items should no longer appear in active lists (due to soft deletion)
        self.assertEqual(len(new_constraints), original_constraint_count - 1)
        self.assertEqual(len(new_preferences), original_preference_count - 1)

        # But they should still exist in the system
        self.assertIn(constraint_id, self.learning_system.constraints)
        self.assertIn(preference_id, self.learning_system.preferences)

        # And they should be marked as inactive
        self.assertFalse(self.learning_system.constraints[constraint_id].active)
        self.assertFalse(self.learning_system.preferences[preference_id].active)

    def test_learn_from_project_event(self):
        """Test learning from project events."""
        # Learn from a critical issue
        insight1_id = self.learning_system.learn_from_project_event(
            event_type="critical_issue",
            context="database_connection_timeout",
            details={
                "description": "Database connections timing out under load",
                "solution": "Implemented connection pooling",
                "applicable_projects": ["high_volume_web_app", "database_intensive_app"]
            }
        )

        # Learn from a major decision
        insight2_id = self.learning_system.learn_from_project_event(
            event_type="major_decision",
            context="technology_selection",
            details={
                "description": "Selected PostgreSQL over MySQL",
                "reasoning": "Better support for complex queries",
                "applicable_projects": ["analytics_app", "reporting_system"]
            }
        )

        # Verify insights were created
        self.assertTrue(insight1_id.startswith("insight_"))
        self.assertTrue(insight2_id.startswith("insight_"))

        # Get insights with minimum importance
        all_insights = self.learning_system.get_learning_insights(min_importance=1)
        self.assertGreaterEqual(len(all_insights), 2)

        # Find our specific insights
        found_insight1 = next((insight for insight in all_insights if insight.id == insight1_id), None)
        found_insight2 = next((insight for insight in all_insights if insight.id == insight2_id), None)

        self.assertIsNotNone(found_insight1)
        self.assertIsNotNone(found_insight2)

        # Verify properties
        self.assertEqual(found_insight1.context, "database_connection_timeout")
        self.assertEqual(found_insight2.insight_type, "major_decision")
        self.assertIn("high_volume_web_app", found_insight1.applicable_projects)

    def test_get_applicable_knowledge_items(self):
        """Test converting constraints and preferences to knowledge items."""
        # Register some constraints and preferences
        self.learning_system.register_constraint(
            constraint_type=ConstraintType.SECURITY,
            description="JWT token validation required",
            priority=4,
            impact_level="high"
        )

        self.learning_system.register_preference(
            category=PreferenceCategory.CODING_STYLE,
            preference_value="Use type hints everywhere",
            priority=3
        )

        # Get knowledge items
        knowledge_items = self.learning_system.get_applicable_knowledge_items()

        # Verify we get knowledge items
        self.assertGreaterEqual(len(knowledge_items), 2)

        # Verify the knowledge items have proper structure
        for item in knowledge_items:
            self.assertIsInstance(item, KnowledgeItem)
            self.assertIsNotNone(item.id)
            self.assertIsNotNone(item.content)
            self.assertIsNotNone(item.source_type)
            self.assertIsInstance(item.tags, list)

        # Check that project-specific items are included
        security_items = [ki for ki in knowledge_items if "SECURITY" in ki.content]
        style_items = [ki for ki in knowledge_items if "CODING_STYLE" in ki.content]

        self.assertGreaterEqual(len(security_items), 1)
        self.assertGreaterEqual(len(style_items), 1)

    def test_set_and_get_project_context(self):
        """Test setting and getting project context."""
        # Define project context
        project_context = {
            "project_id": "proj_e_commerce_123",
            "project_name": "E-commerce Platform",
            "start_date": "2023-01-15",
            "team_size": 5,
            "deadline": "2023-06-30",
            "budget": 100000,
            "technologies": ["Python", "React", "PostgreSQL"],
            "domain": "e-commerce"
        }

        # Set the context
        self.learning_system.set_project_context(project_context)

        # Get the context
        retrieved_context = self.learning_system.get_project_context()

        # Verify all values are preserved
        self.assertEqual(retrieved_context["project_id"], "proj_e_commerce_123")
        self.assertEqual(retrieved_context["project_name"], "E-commerce Platform")
        self.assertEqual(retrieved_context["team_size"], 5)
        self.assertIn("Python", retrieved_context["technologies"])
        self.assertEqual(retrieved_context["domain"], "e-commerce")

    def test_export_import_project_memory(self):
        """Test exporting and importing project memory."""
        # Set up some constraints and preferences
        constraint_id = self.learning_system.register_constraint(
            constraint_type=ConstraintType.COMPLIANCE,
            description="HIPAA compliance required",
            priority=5,
            impact_level="critical",
            justification="Healthcare domain requirement"
        )

        preference_id = self.learning_system.register_preference(
            category=PreferenceCategory.DOCUMENTATION_STYLE,
            preference_value="Use MkDocs for documentation",
            priority=3,
            justification="Easy integration with GitHub"
        )

        # Set project context
        project_context = {
            "project_id": "health_app_456",
            "domain": "healthcare",
            "regulations": ["HIPAA", "GDPR"]
        }
        self.learning_system.set_project_context(project_context)

        # Learn from an event
        self.learning_system.learn_from_project_event(
            event_type="important_lesson",
            context="data_encryption",
            details={
                "description": "Client-side encryption is mandatory",
                "applicable_projects": ["healthcare", "finance"]
            }
        )

        # Export project memory
        export_json = self.learning_system.export_project_memory()
        self.assertIsNotNone(export_json)
        self.assertIn("HIPAA compliance required", export_json)
        self.assertIn("MkDocs for documentation", export_json)

        # Create a new learning system and import
        new_learning_system = ProjectLearningSystem()
        import_success = new_learning_system.import_project_memory(export_json)

        # Verify import was successful
        self.assertTrue(import_success)

        # Verify constraints were imported
        imported_constraints = new_learning_system.get_active_constraints()
        self.assertGreaterEqual(len(imported_constraints), 1)

        # Find our specific constraint
        hipaa_constraint = None
        for constraint in imported_constraints:
            if "HIPAA compliance required" in constraint.description:
                hipaa_constraint = constraint
                break

        self.assertIsNotNone(hipaa_constraint)
        self.assertEqual(hipaa_constraint.priority, 5)
        self.assertEqual(hipaa_constraint.impact_level, "critical")

        # Verify preferences were imported
        imported_preferences = new_learning_system.get_active_preferences()
        self.assertGreaterEqual(len(imported_preferences), 1)

        # Find our specific preference
        mkdocs_preference = None
        for preference in imported_preferences:
            if "MkDocs" in preference.preference_value:
                mkdocs_preference = preference
                break

        self.assertIsNotNone(mkdocs_preference)
        self.assertEqual(mkdocs_preference.priority, 3)

        # Verify project context was imported
        imported_context = new_learning_system.get_project_context()
        self.assertEqual(imported_context["project_id"], "health_app_456")
        self.assertEqual(imported_context["domain"], "healthcare")

        # Verify insights were imported
        imported_insights = new_learning_system.get_learning_insights(min_importance=1)
        self.assertGreaterEqual(len(imported_insights), 1)

    def test_get_adaptive_guidance(self):
        """Test getting adaptive guidance from accumulated knowledge."""
        # Add some critical constraints
        self.learning_system.register_constraint(
            constraint_type=ConstraintType.SECURITY,
            description="All communications must be encrypted",
            priority=5,
            impact_level="critical"
        )

        self.learning_system.register_constraint(
            constraint_type=ConstraintType.COMPLIANCE,
            description="Audit logs required for all actions",
            priority=5,
            impact_level="critical"
        )

        # Add some high-priority preferences
        self.learning_system.register_preference(
            category=PreferenceCategory.LIBRARY_CHOICE,
            preference_value="Use FastAPI for web framework",
            priority=4
        )

        # Learn from some events
        self.learning_system.learn_from_project_event(
            event_type="important_lesson",
            context="api_design",
            details={
                "description": "Async patterns improve performance significantly",
                "importance": 4,
                "applicable_projects": ["high_traffic_app"]
            }
        )

        # Get adaptive guidance
        guidance = self.learning_system.get_adaptive_guidance()

        # Verify guidance structure
        self.assertIn("critical_constraints", guidance)
        self.assertIn("high_priority_preferences", guidance)
        self.assertIn("key_lessons_learned", guidance)
        self.assertIn("recommended_approaches", guidance)

        # Verify content
        self.assertGreaterEqual(len(guidance["critical_constraints"]), 2)
        self.assertGreaterEqual(len(guidance["high_priority_preferences"]), 1)
        self.assertGreaterEqual(len(guidance["key_lessons_learned"]), 1)
        self.assertGreaterEqual(len(guidance["recommended_approaches"]), 1)

        # Verify specific content
        critical_constraint_found = any(
            "encrypted" in c["description"] or "audit" in c["description"]
            for c in guidance["critical_constraints"]
        )
        self.assertTrue(critical_constraint_found)

        fastapi_preference_found = any(
            "FastAPI" in p["value"] for p in guidance["high_priority_preferences"]
        )
        self.assertTrue(fastapi_preference_found)


if __name__ == '__main__':
    unittest.main()