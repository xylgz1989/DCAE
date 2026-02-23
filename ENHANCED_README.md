# DCAE - Disciplined Consensus-Driven Agentic Engineering

DCAE (Disciplined Consensus-Driven Agentic Engineering) is an advanced AI-powered software development framework that combines professional role separation (BMAD), multi-model consensus validation (MassGen), and disciplined methodology enforcement (Superpowers) in a unified workflow.

## Overview

The DCAE framework revolutionizes the software development process by implementing a three-layer architecture:

1. **BMAD (Business Manager, Architect, Developer)** - Role-based workflow with specialized agents
2. **MassGen (Multi-Model Consensus Generation)** - Quality validation through multi-model consensus
3. **Superpowers (Methodological Enforcement)** - Disciplined execution of development methodologies

This represents the next evolution from our original DCAE MVP, adding sophisticated workflow orchestration and consensus validation.

## Key Features

- **Role-Based Agents**: Specialized AI agents for Business, Architecture, and Development roles
- **Multi-Model Consensus**: Validation of critical decisions using multiple LLMs
- **Flexible Discipline Levels**: Fast/Balanced/Strict modes to suit project needs
- **Integrated Workflow**: Seamless transition between phases with context preservation
- **Budget Tracking**: Token and cost monitoring for responsible AI usage
- **Customizable Workflows**: Define custom multi-phase development processes
- **Enhanced Context Management**: Preserves knowledge across workflow phases
- **Comprehensive Skill System**: Enforces methodological best practices

## Installation

```bash
# Navigate to the DCAE directory
cd D:\software_dev_project\DCAE

# Install required dependencies
pip install openai anthropic pyyaml aiosqlite pydantic
```

## Configuration

Run the initialization wizard to set up your LLM provider:

```bash
python enhanced_dcae.py init
```

This will guide you through configuring your API keys, models, and budget settings.

## Usage

### Execute BMAD Workflow

Run the complete BMAD workflow with requirements:

```bash
python enhanced_dcae.py bm "Create a blog platform with user authentication"
```

Specify discipline level:
```bash
python enhanced_dcae.py bm "Create a simple calculator app" --level fast
python enhanced_dcae.py bm "Build a complex e-commerce system" --level strict
```

### Execute Custom Workflows

Define your own multi-phase workflow in a YAML file:

```bash
python enhanced_dcae.py workflow my-workflow.yaml
```

### Check Status

Monitor your usage and configuration:

```bash
python enhanced_dcae.py status
```

## BMAD Roles Explained

### Business Manager (PM)
- Analyzes requirements
- Defines user personas
- Establishes success metrics
- Identifies risks and challenges
- Creates product specifications

### System Architect
- Designs system architecture
- Recommends technology stack
- Considers security and scalability
- Plans deployment strategy
- Designs database schemas

### Developer
- Implements core functionality
- Writes clean, well-documented code
- Creates unit and integration tests
- Handles error cases appropriately
- Optimizes performance

## Discipline Levels

### Fast Mode
- Minimal validation steps
- Rapid prototyping and iteration
- Single model execution
- Quick turnaround time
- Suitable for prototypes and POCs

### Balanced Mode
- Moderate validation and checks
- Good balance of speed and quality
- Selective consensus validation
- Recommended for most projects

### Strict Mode
- Full validation and consensus
- Multi-model approval for critical decisions
- Comprehensive methodology enforcement
- Highest quality output
- Required for production systems

## Multi-Model Consensus Engine

The MassGen consensus engine validates critical outputs using multiple LLMs. It evaluates responses for:

- Accuracy and completeness
- Technical correctness
- Security considerations
- Best practice adherence
- Architecture soundness

Consensus is determined through majority voting with a configurable threshold.

## Sample Workflows

The repository includes sample workflow files demonstrating various use cases:

- `sample-workflow.yaml`: Basic workflow demonstrating all phases
- `task-management-requirements.txt`: Sample requirements document

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   DCAE Orchestrator                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬────────────────────────┐
        ▼              ▼              ▼                        ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────┐    ┌─────────────────┐
│    BMAD      │ │Superpowers   │ │  MassGen    │    │   Budget &      │
│(Agent Roles) │ │(Methodology) │ │(Consensus)  │    │  Monitoring     │
└──────────────┘ └──────────────┘ └─────────────┘    └─────────────────┘
        │              │              │                        │
        └──────────────┼──────────────┼────────────────────────┘
                       ▼              ▼
              ┌─────────────────────────────────┐
              │      Context Preservation       │
              │     (Knowledge Transfer)        │
              └─────────────────────────────────┘
```

## Workflow Examples

### Basic BMAD Flow
```
Requirements → Business Manager → Architect → Developer → Implementation
```

### Consensus Validation Flow
```
Critical Decision → Multiple LLMs → Consensus Check → Approval/Revision
```

### Custom Workflow Flow
```
YAML Workflow Definition → Orchestrator → Sequential Agent Execution → Final Output
```

## Integration Points

DCAE is designed for seamless integration with:

- **IDEs**: VS Code, JetBrains products (via MCP protocol)
- **Version Control**: Git with automated branching strategies
- **CI/CD**: GitHub Actions, GitLab CI
- **Cloud Platforms**: AWS, Azure, GCP
- **Monitoring**: Application performance and error tracking
- **Testing Frameworks**: pytest, JUnit, etc.

## Development History

The DCAE framework evolved from the initial MVP version (README-MVP.md) to incorporate the advanced BMAD workflow and consensus mechanisms as outlined in our Product Requirements Document (PRD) and technical research findings.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support, please create an issue in the GitHub repository.