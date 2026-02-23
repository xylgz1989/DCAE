---
project_name: 'DCAE - Distributed Coding Agent Environment'
user_name: 'User'
date: '2026-02-23'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 42
optimized_for_llm: true
existing_patterns_found: 8
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Primary Language**: Python 3.11+
- **Dependencies**:
  - pydantic (^2.5) - Data validation
  - pydantic-settings (^2.1) - Settings management
  - typer (^0.9) - CLI creation
  - anthropic (^0.18) - Anthropic API client
  - openai (^1.5) - OpenAI API client
  - aiosqlite (^0.19) - SQLite async driver
  - pyyaml (^6.0) - YAML processing
  - httpx (^0.25) - HTTP client
  - zhipuai (^2.0) - Zhipu AI client
  - dashscope (^1.17) - Alibaba Tongyi client
- **Build System**: Poetry
- **Testing**: pytest, pytest-asyncio
- **Formatting**: black, ruff

## Critical Implementation Rules

### Language-Specific Rules
- **Encoding Handling**: Always handle Windows encoding properly using sys.stdout/stderr wrapper as shown in dcae.py lines 31-33
- **Async/Await**: Use asyncio for all async operations; prefer AsyncOpenAI for OpenAI interactions
- **Configuration**: Use DCAEConfig class for all configuration management with proper JSON file handling
- **Error Handling**: Implement graceful error handling with fallbacks, especially for API calls
- **Token Management**: Handle token counting and rate limiting for API providers
- **Budget Tracking**: Follow built-in budget tracking to manage API costs with configurable daily/monthly limits
- **Type Hints**: Always use proper type hints, especially for function parameters and return values
- **Path Handling**: Use pathlib.Path for cross-platform file path operations

### Framework-Specific Rules
- **Typer CLI**: Follow Typer patterns for CLI creation, using decorators and proper command structure
- **Pydantic Models**: Use Pydantic for data validation and settings management
- **Async Context Managers**: Use proper async context managers for resource cleanup

### Testing Rules
- **Pytest**: Use pytest for all testing with appropriate fixtures
- **Async Tests**: Use pytest-asyncio for asynchronous test functions
- **Test Coverage**: Maintain high test coverage especially for core functionality
- **Integration Tests**: Include tests for API integrations with proper mocking
- **Test Organization**: Place tests in the tests/ directory with matching file names

### Code Quality & Style Rules
- **Naming Conventions**:
  - Files: Use snake_case for Python files (e.g., dcae.py, dcae_mvp.py)
  - Classes: Use PascalCase (e.g., DCAEConfig)
  - Functions: Use snake_case (e.g., _load, save)
  - Constants: Use UPPER_CASE
- **Formatting**: Use black for code formatting and ruff for linting
- **Imports**: Follow import organization standards (stdlib, third-party, first-party)
- **Docstrings**: Include detailed docstrings for classes and functions following Google or NumPy style
- **Comments**: Add inline comments for complex logic, especially around API integrations

### Development Workflow Rules
- **File Structure**:
  - Main Files: dcae.py serves as the primary entry point
  - Configuration: Store user configuration in ~/.dcae/config.json
  - Commands: Implement CLI commands using argparse with clear usage documentation
  - Interactive Mode: Maintain conversation history with token-aware trimming
  - Tests: Store all tests in the tests/ directory
  - Docs: Documentation files in docs/ directory
  - POC: Proof-of-concept implementation in dcae-poc/ directory with pyproject.toml
- **Configuration**: Use the config wizard approach with JSON configuration in user home directory
- **Command Line Interface**: Follow the documented CLI patterns with consistent command structure

### Critical Don't-Miss Rules
- **Anti-Patterns to Avoid**:
  - Don't hardcode API keys or sensitive information in source code
  - Don't ignore async/await when working with API clients
  - Don't forget to handle platform-specific encoding issues (especially Windows)
  - Don't bypass budget tracking mechanisms
  - Don't skip input validation for user-provided parameters
- **Security Rules**:
  - Always validate and sanitize user inputs before processing
  - Securely store API keys and credentials
  - Use proper rate limiting and backoff for API calls
- **Performance Considerations**:
  - Implement proper token counting to track usage
  - Use appropriate model selection based on task complexity
  - Cache responses when appropriate to avoid unnecessary API calls
- **Edge Cases**:
  - Handle network failures gracefully with retry logic
  - Account for API rate limits with proper backoff strategies
  - Manage memory usage during long-running operations
  - Handle cancellation of ongoing operations properly

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**

- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

Last Updated: 2026-02-23