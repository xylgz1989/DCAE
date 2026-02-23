# Project Structure Document for DCAE Framework

## Epic 3: Architecture Design & Planning - Story 3.6

### Status
- **Epic:** Epic #3: Architecture Design & Planning
- **Story:** 3.6 - Core BMAD Workflow Implementation
- **Status:** In Progress
- **Author:** DCAE Framework
- **Date:** February 23, 2026

### Overview
This document defines the complete project structure for the DCAE (Development Coding Agent Environment) framework. It addresses FR61: "Core BMAD workflow (requirements analysis, architecture design, code development, quality assurance) must be implemented in MVP" from Epic #3 requirements.

### User Story
"As a developer, I want to have a complete project structure, so that I can begin implementing the core BMAD workflow with clearly defined boundaries and components."

### Complete Project Tree

```
dcae-framework/
├── .claude/                    # Claude Code configuration
│   ├── settings.json          # Global settings
│   └── settings.local.json    # Local settings
├── .git/                     # Git repository metadata
├── .github/                  # GitHub workflow configurations
│   └── workflows/            # CI/CD workflows
│       ├── test.yml          # Testing workflow
│       ├── deploy.yml        # Deployment workflow
│       └── security.yml      # Security scanning workflow
├── api/                      # API layer - handles requests/responses
│   ├── __init__.py
│   ├── main.py               # Main API router
│   ├── deps.py               # API dependencies
│   ├── models/               # API models and schemas
│   │   ├── __init__.py
│   │   ├── base.py           # Base Pydantic models
│   │   ├── request.py        # Request schemas
│   │   └── response.py       # Response schemas
│   └── routes/               # API route definitions
│       ├── __init__.py
│       ├── health.py         # Health check endpoints
│       ├── requirements.py   # Requirements analysis endpoints
│       ├── architecture.py   # Architecture generation endpoints
│       ├── codegen.py        # Code generation endpoints
│       └── qa.py             # Quality assurance endpoints
├── core/                     # Core business logic and configuration
│   ├── __init__.py
│   ├── config.py             # Application configuration
│   ├── exceptions.py         # Custom exceptions
│   ├── logger.py             # Logging configuration
│   ├── security.py           # Security utilities
│   └── validators.py         # Input validators
├── bmads/                    # BMAD (Business Manager, Architect, Developer) agents
│   ├── __init__.py
│   ├── base.py               # Base BMAD agent class
│   ├── business_manager.py   # Business Manager agent implementation
│   ├── architect.py          # Architect agent implementation
│   ├── developer.py          # Developer agent implementation
│   └── coordinator.py        # BMAD workflow coordinator
├── services/                 # Business service layer
│   ├── __init__.py
│   ├── requirements_service.py    # Requirements analysis service
│   ├── architecture_service.py    # Architecture generation service
│   ├── code_generation_service.py # Code generation service
│   ├── qa_service.py              # Quality assurance service
│   └── workflow_service.py        # Overall workflow management
├── models/                   # Domain models and data structures
│   ├── __init__.py
│   ├── base.py               # Base model definitions
│   ├── project.py            # Project model
│   ├── requirements.py       # Requirements model
│   ├── architecture.py       # Architecture model
│   ├── code_component.py     # Code component model
│   └── quality_metrics.py    # Quality metrics model
├── repositories/             # Data access layer
│   ├── __init__.py
│   ├── base.py               # Base repository
│   ├── project_repository.py # Project data access
│   ├── requirements_repository.py # Requirements data access
│   ├── architecture_repository.py # Architecture data access
│   └── code_repository.py    # Code data access
├── utils/                    # Utility functions and helpers
│   ├── __init__.py
│   ├── file_operations.py    # File system utilities
│   ├── string_utils.py       # String manipulation utilities
│   ├── validation.py         # Validation utilities
│   └── formatting.py         # Formatting utilities
├── templates/                # Template files for code generation
│   ├── __init__.py
│   ├── project_structure/    # Project structure templates
│   ├── api_endpoints/        # API endpoint templates
│   ├── models/               # Model templates
│   └── documentation/        # Documentation templates
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Test configuration
│   ├── test_api/             # API layer tests
│   │   ├── __init__.py
│   │   ├── test_health.py
│   │   ├── test_requirements.py
│   │   ├── test_architecture.py
│   │   ├── test_codegen.py
│   │   └── test_qa.py
│   ├── test_services/        # Service layer tests
│   │   ├── __init__.py
│   │   ├── test_requirements_service.py
│   │   ├── test_architecture_service.py
│   │   ├── test_code_generation_service.py
│   │   └── test_workflow_service.py
│   ├── test_bmads/           # BMAD agent tests
│   │   ├── __init__.py
│   │   ├── test_business_manager.py
│   │   ├── test_architect.py
│   │   └── test_developer.py
│   └── fixtures/             # Test fixtures and data
├── scripts/                  # Utility scripts
│   ├── __init__.py
│   ├── setup_db.py           # Database setup script
│   ├── migrate.py            # Migration script
│   └── run_tests.py          # Test runner script
├── docs/                     # Documentation
│   ├── architecture.md       # Architecture documentation
│   ├── api_reference.md      # API reference
│   ├── user_guide.md         # User guide
│   └── contributing.md       # Contribution guidelines
├── _bmad-output/             # BMAD output artifacts
│   ├── planning-artifacts/   # Planning documents
│   ├── architecture-artifacts/ # Architecture documents
│   ├── implementation-artifacts/ # Implementation documents
│   ├── bmb-creations/        # Business Manager creations
│   └── test-artifacts/       # Test artifacts
├── requirements/             # Requirements files
│   ├── base.txt              # Base dependencies
│   ├── dev.txt               # Development dependencies
│   └── prod.txt              # Production dependencies
├── .env.example              # Example environment variables
├── .gitignore                # Files to exclude from Git
├── .pre-commit-config.yaml   # Pre-commit hook configuration
├── Dockerfile                # Container definition
├── docker-compose.yml        # Multi-container setup
├── README.md                 # Project overview
├── LICENSE                   # License information
├── pyproject.toml            # Project metadata and build configuration
├── poetry.lock               # Locked dependencies (if using Poetry)
├── setup.py                  # Package setup
├── MANIFEST.in               # Package manifest
└── main.py                   # Application entry point
```

### Directory Purposes

#### api/
Contains all API-related code including route definitions, request/response models, and API-level validation. This layer should be thin and delegate business logic to the services layer.

#### core/
Contains core application logic including configuration, security utilities, and shared utilities that don't fit elsewhere. This is the heart of the application's infrastructure.

#### bmads/
Contains the implementation of the BMAD (Business Manager, Architect, Developer) agents that are central to the DCAE framework. Each agent has specific responsibilities in the workflow.

#### services/
Contains business logic and service orchestration. These components coordinate between repositories and other services to implement business rules.

#### models/
Contains domain models that represent the core entities of the system. These are used throughout the application to represent data structures.

#### repositories/
Contains data access logic that abstracts the underlying database or storage mechanism. This layer should only contain CRUD operations and simple queries.

#### utils/
Contains utility functions that are used throughout the application. These should be pure functions with no side effects.

#### templates/
Contains templates used for code generation and project scaffolding. These templates should follow the architectural patterns defined in the framework.

#### tests/
Contains all test code organized by the layer being tested. Tests should follow the same organizational structure as the code they test.

#### docs/
Contains all documentation for the project including architecture docs, API reference, and user guides.

#### _bmad-output/
Contains artifacts produced by the BMAD workflow including planning, architecture, and implementation documents.

### Key Files and Their Responsibilities

#### main.py
Application entry point that initializes the FastAPI application and sets up middleware.

#### api/main.py
Defines the main API router and includes all route definitions.

#### core/config.py
Manages application configuration including environment variables, API keys, and other settings.

#### services/workflow_service.py
Coordinates the overall BMAD workflow and manages the handoffs between different agents.

#### bmads/coordinator.py
Manages the interactions between the Business Manager, Architect, and Developer agents.

### Implementation Guidelines
1. Each directory should have an `__init__.py` file to make it a Python package
2. Follow the naming conventions defined in the consistency rules
3. Implement proper error handling in each layer
4. Include comprehensive logging for debugging and monitoring
5. Write tests for all business-critical functionality
6. Document public APIs and interfaces

### Next Steps
- Create the directory structure in the actual project
- Implement the core configuration
- Set up the main API router
- Initialize the BMAD agents
- Create basic models and repositories