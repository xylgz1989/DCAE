# DCAE - Disciplined Consensus-Driven Agentic Engineering Framework

DCAE is a comprehensive AI-assisted software engineering platform with sophisticated knowledge fusion capabilities. This project has evolved from a distributed coding agent environment into a complete framework supporting 9 major epics with integrated components for knowledge management, constraint validation, code review, and workflow orchestration.

## Features

- **Knowledge Fusion System**: Sophisticated architecture for cross-domain intelligence
- **Constraint Management**: Comprehensive validation across technical, security, and performance domains
- **Product Knowledge Access**: Intelligent search and retrieval with relevance ranking
- **Code Generation**: Generate code from natural language prompts
- **Code Review & Validation**: Multi-layered code quality assurance system with comprehensive review mechanisms
- **Requirements Management**: Create detailed requirement documents with conflict identification and resolution
- **Architecture Design**: Generate and validate architectural solutions with best practices integration
- **Debugging**: Help identify and solve coding issues
- **Testing & Validation**: Comprehensive test generation with multiple test types and coverage analysis
- **Multi-Component Platform Integration**: Integration with multiple LLM providers, MCP systems, and IDE plugins
- **Process Discipline Control**: Configurable discipline levels with adjustable validation strictness
- **Progress Monitoring**: Real-time tracking of development workflows
- **Workflow Integration**: Seamless incorporation into development processes
- **Interactive Mode**: Enhanced interactive session with context tracking

## Project Scope

The DCAE framework represents a comprehensive AI-assisted software engineering platform with sophisticated knowledge fusion capabilities. The project successfully delivered 9 major epics:

- **Epic 1**: Project Initialization & Setup - Established foundational project structure
- **Epic 2**: Requirements Management - Implemented requirements gathering and management tools
- **Epic 3**: Architecture Design & Planning - Generated and validated architectural solutions
- **Epic 4**: Code Generation & Implementation - Created code structure generation tools
- **Epic 5**: Code Review & Validation - Built comprehensive review mechanisms
- **Epic 6**: Multi-Component Platform Integration - Integrated multiple LLM providers and systems
- **Epic 7**: Process Discipline Control - Created configurable discipline levels
- **Epic 8**: Testing & Validation - Generated comprehensive test cases and implemented various test types
- **Epic 9**: Product Knowledge Integration - Fused development and product knowledge systems

## Major Accomplishments

- **Modular Architecture**: Clear component boundaries with standardized interfaces and data models
- **Comprehensive Testing**: Extensive unit and integration test coverage with automated validation
- **Knowledge Integration**: Successful implementation of cross-domain intelligence capabilities
- **Scalability**: Architecture designed to support growth and addition of new features
- **Quality Assurance**: Multi-layered validation and comprehensive documentation
- **Performance**: Responsive operation despite sophisticated processing requirements

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd DCAE
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize DCAE:
   ```bash
   python dcae.py init
   ```

   This will guide you through the configuration process, including selecting an LLM provider and setting budget limits.

## Configuration

The configuration wizard (`python dcae.py init`) will create a config file in your home directory (`~/.dcae/config.json`) with:

- Selected LLM provider (Qwen, GLM, OpenAI, etc.)
- API key
- Daily/monthly usage limits
- Model preference settings
- Fallback model for budget management

## Budget Management

DCAE includes built-in budget tracking to help manage API costs:

- Configurable daily and monthly limits
- Token-based or monetary-based tracking
- Warning when approaching limits (80% threshold)
- Automatic model fallback when budgets are tight

## Supported Models

The system supports various models based on your provider:

- Qwen series (Turbo, Plus, Coder Plus, Max)
- GLM-4
- GPT-4o
- Claude 3.5 Sonnet

Model selection is automated based on task complexity and budget constraints.

## Development

The interactive mode was developed using Test-Driven Development with comprehensive test coverage in the `tests/` directory.

To run tests:
```bash
python -m pytest tests/ -v
```

## License

This project is licensed under the MIT License.