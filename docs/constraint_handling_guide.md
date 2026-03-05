# Project Constraint Handling Guide

## Overview
This document provides guidance on how to handle project-specific constraints during development. The constraint management system helps ensure code quality, security, and adherence to project requirements by automatically checking code against defined constraints.

## Understanding Constraints

### Constraint Categories

#### Technical Constraints
Technical constraints relate to language features, frameworks, libraries, and platform requirements. These constraints ensure code compatibility and proper use of technology stack components.

Examples:
- Python version requirements (e.g., Python 3.11+)
- Asynchronous programming patterns (async/await usage)
- Specific library usage patterns
- Type hint requirements

#### Security Constraints
Security constraints focus on preventing vulnerabilities and protecting sensitive information.

Examples:
- No hardcoded API keys or passwords
- Proper input validation
- Safe file handling
- Encryption requirements

#### Performance Constraints
Performance constraints ensure code efficiency and optimal resource usage.

Examples:
- Token counting for API usage
- Memory usage limits
- Execution time limits
- Efficient algorithm implementation

#### Coding Standard Constraints
Coding standard constraints maintain code quality and consistency across the project.

Examples:
- Type hint requirements
- Naming conventions
- Code structure patterns
- Comment and documentation requirements

## Working with Constraints During Development

### During Code Generation
When generating new code, the system automatically validates against project constraints:

```python
from dcae.knowledge_fusion.workflow_integration import DCAEConstraintIntegration

integration = DCAEConstraintIntegration()

# Validate generated code
sample_code = '''
def example_function():
    # Your generated code here
    return "Hello World"
'''

issues = integration.validate_agent_output(sample_code, "example_module.py")
if issues:
    print(f"Found {len(issues)} constraint violations:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Code passes all constraint checks!")
```

### Using the Pre-Commit Hook
The system includes a pre-commit hook that automatically validates staged files before allowing commits. To install the pre-commit hook:

1. Run the initialization function:
```python
from dcae.knowledge_fusion.workflow_integration import initialize_constraint_workflow
from pathlib import Path

project_root = Path("/path/to/your/project")
initialize_constraint_workflow(project_root)
```

2. The pre-commit hook will automatically run whenever you commit changes and block commits that violate critical or high severity constraints.

### Adding New Constraints
To add a new constraint to the project:

```python
from dcae.knowledge_fusion.constraint_storage import ProjectConstraintStorage
from dcae.knowledge_fusion.constraint_storage import Constraint
from datetime import datetime

storage = ProjectConstraintStorage()

new_constraint = Constraint(
    id="custom-security-check-1",
    name="Custom Security Constraint",
    category="security",
    description="Description of what this constraint enforces",
    severity="high",  # critical, high, medium, low
    source="developer-added"
)

success = storage.save_constraint(new_constraint)
if success:
    print(f"Constraint {new_constraint.name} added successfully!")
```

### Viewing Active Constraints
To see all active constraints in your project:

```python
from dcae.knowledge_fusion.constraint_storage import ProjectConstraintStorage

storage = ProjectConstraintStorage()

# Get all active constraints
active_constraints = storage.list_constraints(active_only=True)
print(f"Active constraints: {len(active_constraints)}")

# Get constraints by category
tech_constraints = storage.list_constraints(category="technical", active_only=True)
print(f"Technical constraints: {len(tech_constraints)}")

# Get constraint statistics
stats = storage.get_constraint_statistics()
print(f"Statistics: {stats}")
```

## Constraint Violation Severity Levels

### Critical
Critical violations indicate issues that could cause system failures or security breaches. These violations block commits and pull requests.

Examples:
- Security vulnerabilities
- Critical runtime errors
- System stability issues

### High
High severity violations indicate significant problems that impact functionality or maintainability. These violations also block commits and pull requests.

Examples:
- Major architectural violations
- Significant performance issues
- Important security concerns

### Medium
Medium severity violations indicate noticeable issues that impact code quality or performance. These violations are reported but don't block commits.

Examples:
- Code style issues
- Moderate performance concerns
- Suboptimal implementation patterns

### Low
Low severity violations indicate minor deviations from best practices. These violations are noted for improvement but don't block development.

Examples:
- Minor style inconsistencies
- Small optimization opportunities
- Documentation suggestions

## Troubleshooting Common Issues

### Pre-Commit Hook Not Running
If the pre-commit hook isn't running when you commit:
1. Ensure Git is initialized in your project directory
2. Reinstall the hook using `initialize_constraint_workflow()`
3. Check file permissions on `.git/hooks/pre-commit`

### False Positive Violations
If you encounter what appears to be a false positive:
1. Review the constraint description to understand its purpose
2. If the violation is legitimate, update your code accordingly
3. If the constraint is incorrectly flagging valid code, consider adjusting the constraint or its severity

### Managing Constraint Overhead
If constraint checking is slowing down your development process:
1. Consider running validation only on changed files rather than the entire project
2. Adjust constraint severity levels appropriately
3. Review and refine constraints periodically to remove outdated or redundant ones

## Best Practices

### For Individual Developers
1. Familiarize yourself with project constraints before starting work
2. Run manual validation on complex code changes before committing
3. Add new constraints when you identify important project-specific requirements
4. Review constraint violations carefully to understand the underlying issues

### For Teams
1. Regularly review and update constraints to match evolving project requirements
2. Document the rationale behind each constraint for team members
3. Use consistent severity levels across similar types of constraints
4. Periodically audit constraints to remove obsolete ones

## Integration with Development Tools

The constraint management system can be integrated with various development tools:

### IDE Integration
Consider configuring your IDE to highlight constraint violations in real-time during coding.

### CI/CD Pipeline
Add constraint validation to your CI pipeline to catch violations before merging pull requests:

```bash
# Example CI script
python -c "
from dcae.knowledge_fusion.constraint_validation import DevelopmentValidator
from dcae.knowledge_fusion.constraint_storage import ProjectConstraintStorage

validator = DevelopmentValidator(ProjectConstraintStorage())
results = validator.validator.validate_project(Path('.'))

for file_path, issues in results.items():
    critical_high_issues = [i for i in issues if i.severity in ['critical', 'high']]
    if critical_high_issues:
        print(f'Failing: {file_path} has {len(critical_high_issues)} critical/high issues')
        exit(1)
"
```

### Code Review Process
Include constraint validation results as part of your code review process to help reviewers focus on important issues.