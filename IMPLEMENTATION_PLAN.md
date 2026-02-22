# DCAE Implementation Plan

## Context

This plan implements **DCAE (Disciplined Consensus-Driven Agentic Engineering)** - a new software engineering framework that integrates three complementary AI development frameworks:

1. **BMAD** - Role-based workflow orchestration (PM → Architect → Developer → QA)
2. **MassGen** - Multi-LLM consensus quality validation
3. **Superpowers** - Forced methodology enforcement (TDD, planning, reviews)

The project aims to solve key problems in AI-assisted software development:
- Context drift across long workflows
- Lack of process discipline (AI "skipping steps")
- Single-model bias in code/design decisions
- Poor traceability of AI-made decisions

**Target MVP**: Complete user login feature implementation using all three frameworks.

---

## Technical Stack

| Component | Language | Purpose |
|------------|-----------|----------|
| Python Core | Python 3.11+ | Orchestrator, MassGen integration, memory layer |
| CLI | TypeScript | Command-line interface |
| VS Code Extension | TypeScript | IDE integration and visualization |
| Shared Types | TypeScript | Type definitions shared across TS packages |

---

## Project Directory Structure

```
D:\software_dev_project\DCAE\
├── README.md
├── pyproject.toml                          # Python project config
├── package.json                            # TypeScript monorepo config
├── .dcae/                                 # Framework runtime directory
│   ├── config.yaml                          # Main configuration file
│   ├── skills/                             # Superpowers skill definitions
│   │   ├── brainstorming/SKILL.md
│   │   ├── writing-plans/SKILL.md
│   │   ├── executing-plans/SKILL.md
│   │   ├── test-driven-development/SKILL.md
│   │   ├── requesting-code-review/SKILL.md
│   │   └── receiving-code-review/SKILL.md
│   ├── agents/                             # BMAD agent definitions
│   │   ├── pm.md
│   │   ├── architect.md
│   │   ├── developer.md
│   │   ├── qa.md
│   │   └── ux-designer.md
│   ├── workflows/                          # BMAD workflow definitions
│   │   ├── analysis/
│   │   ├── planning/
│   │   ├── architecture/
│   │   └── implementation/
│   └── memory/                             # Decision tracking layer
│       ├── decisions.jsonl
│       └── consensus_reports/
├── src/
│   ├── python/                             # Python core
│   │   ├── dcae/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py             # Main DCAE orchestrator
│   │   │   ├── config/
│   │   │   │   ├── loader.py
│   │   │   │   ├── schema.py
│   │   │   │   └── defaults.yaml
│   │   │   ├── bmad/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── workflow.py
│   │   │   │   ├── agent_parser.py
│   │   │   │   └── project_context.py
│   │   │   ├── massgen/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── consensus_gateway.py
│   │   │   │   ├── bmad_adapter.py
│   │   │   │   ├── voting_engine.py
│   │   │   │   └── config_builder.py
│   │   │   ├── superpowers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── skill_manager.py
│   │   │   │   ├── skill_parser.py
│   │   │   │   ├── discipline_enforcer.py
│   │   │   │   └── skill_hooks.py
│   │   │   ├── memory/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tracker.py
│   │   │   │   ├── consensus_logger.py
│   │   │   │   └── capability_graph.py
│   │   │   └── cli/
│   │   │       └── main.py
│   │   └── tests/
│   ├── typescript/
│   │   ├── packages/
│   │   │   ├── cli/                    # TypeScript CLI
│   │   │   ├── vscode-extension/        # VS Code extension
│   │   │   └── shared/                # Shared types
│   └── examples/
│       └── user-login-mvp/              # MVP example project
└── docs/
    ├── architecture/
    ├── user-guide/
    └── api/
```

---

## Core Components

### 1. Orchestrator (`src/python/dcae/orchestrator.py`)

Main coordinator that:
- Manages DCAE context and session state
- Sequences BMAD agent execution
- Triggers Superpowers skill injection
- Invokes MassGen consensus at configured points
- Logs decisions to memory layer

Key methods:
- `initialize()` - Set up session context
- `execute_workflow()` - Run complete BMAD workflow with skill/consensus integration

### 2. BMAD Integration (`src/python/dcae/bmad/`)

- `agent_parser.py` - Parse agent.md files with YAML frontmatter
- `workflow.py` - Define standard BMAD workflow (Analysis → Planning → Architecture → Implementation)
- `project_context.py` - Manage shard files and project artifacts

### 3. Superpowers Integration (`src/python/dcae/superpowers/`)

- `skill_manager.py` - Load and parse SKILL.md files
- `discipline_enforcer.py` - Enforce skill completion (checklists, hard gates)
- `skill_hooks.py` - Integration points between BMAD and skills

### 4. MassGen Integration (`src/python/dcae/massgen/`)

- `consensus_gateway.py` - Gateway to trigger MassGen consensus sessions
- `bmad_adapter.py` - Adapter for BMAD agents to participate in voting
- `voting_engine.py` - Handle voting strategies (unanimous/majority/weighted)
- `config_builder.py` - Convert DCAE config to MassGen format

### 5. Memory Layer (`src/python/dcae/memory/`)

- `tracker.py` - Track all decisions with metadata
- `consensus_logger.py` - Log MassGen voting results
- `capability_graph.py` - Build capability graphs from history

---

## Configuration Schema (`.dcae/config.yaml`)

```yaml
# Project metadata
project:
  name: "User Login Feature"
  level: 3  # BMAD complexity level (0-4)
  workflow: "standard"

# BMAD Layer - Workflow orchestration
bmad:
  agents:
    - role: architect
      file: ".dcae/agents/architect.md"
      skills: ["brainstorming", "writing-plans"]
      consensus:
        enabled: true
        models: ["claude-3.5-sonnet", "gemini-2.5-pro", "gpt-4o"]
        voting_strategy: "unanimous"
        threshold: 0.8
        timeout: 300

    - role: developer
      file: ".dcae/agents/developer.md"
      skills: ["test-driven-development", "executing-plans", "requesting-code-review"]
      consensus:
        enabled: true
        models: ["claude-code", "gpt-4o-mini", "gemini-2.5-flash"]
        voting_strategy: "majority"
        threshold: 0.67
        mode: "fast_pass"

    - role: qa
      file: ".dcae/agents/qa.md"
      skills: ["verification-before-completion"]
      consensus:
        enabled: true
        models: ["claude-3.5-sonnet", "gpt-4o"]
        voting_strategy: "unanimous"
        threshold: 1.0

# Superpowers Layer - Discipline enforcement
superpowers:
  discipline:
    enforce_tdd: true
    enforce_planning: true
    enforce_reviews: true
    skip_protection: "strict"

  skills:
    brainstorming:
      enabled: true
      mandatory_before: ["implementation", "architecture"]
    test-driven-development:
      enabled: true
      mandatory_for: ["implementation", "bugfix"]
      watch_fail: true

# MassGen Layer - Consensus configuration
massgen:
  orchestrator:
    timeout: 1800
    max_rounds: 3

  backends:
    claude:
      type: "claude"
      models:
        - id: "claude-3.5-sonnet-20241022"
        - id: "claude-opus-4-20250514"
    openai:
      type: "openai"
      models:
        - id: "gpt-4o"
        - id: "gpt-4o-mini"
    gemini:
      type: "gemini"
      models:
        - id: "gemini-2.5-pro"
        - id: "gemini-2.5-flash"

# Integration hooks
integrations:
  skill_to_consensus:
    writing-plans: true
    executing-plans:
      code_only: true
      threshold_lines: 100

# Memory settings
memory:
  enabled: true
  path: ".dcae/memory"
  track_decisions: true
  track_consensus: true
```

---

## Integration Flow (User Login MVP)

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DCAE Orchestrator initializes session                      │
└────────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. PM Agent (no consensus required)                          │
│     └─> Produces brief.md with requirements                     │
└────────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Architect Agent + Superpowers Skills                     │
│     ├─> /brainstorming (required before architecture)          │
│     ├─> /write-plan (creates architecture document)            │
│     └─> MassGen Consensus (3 models, unanimous)              │
│         └─> Validates architecture design                       │
└────────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Developer Agent + TDD + Consensus                     │
│     ├─> /test-driven-development (RED-GREEN-REFACTOR)        │
│     ├─> /execute-plan (batch execution, 3 tasks/batch)       │
│     ├─> /request-code-review (after each batch)              │
│     └─> MassGen Consensus (3 models, majority, code>100L)   │
│         └─> Validates code quality                           │
└────────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. QA Agent + Verification                               │
│     ├─> /verification-before-completion                       │
│     └─> MassGen Consensus (2 models, unanimous)             │
│         └─> Validates test coverage                          │
└────────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Memory Layer - Track all decisions and consensus reports   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Create project directory structure
- Set up Python project (pyproject.toml, dependencies)
- Set up TypeScript monorepo (CLI, VS Code extension, shared)
- Implement configuration schema and loader
- Implement basic orchestrator skeleton
- Set up test framework

### Phase 2: BMAD Integration (Week 3-4)
- Implement agent.md parser (YAML frontmatter)
- Implement standard BMAD workflow
- Implement project context/sharding manager
- Create sample agent definitions
- Add BMAD integration tests

### Phase 3: Superpowers Integration (Week 5-6)
- Implement SKILL.md parser
- Implement skill manager
- Implement discipline enforcer
- Create MVP skill definitions
- Implement skill injection hooks
- Add skill system tests

### Phase 4: MassGen Integration (Week 7-8)
- Implement consensus gateway
- Implement MassGen config builder
- Implement BMAD adapter
- Implement voting engine
- Implement consensus logging
- Add MassGen integration tests

### Phase 5: Memory/Tracking Layer (Week 9)
- Implement decision tracker
- Implement consensus logger
- Implement capability graph builder
- Add memory hooks to orchestrator
- Implement query/retrieval API

### Phase 6: CLI Implementation (Week 10-11)
- Implement CLI command structure
- Config commands (init, validate, edit)
- Workflow commands (start, status, resume)
- Skill and consensus commands
- Memory query commands
- Add CLI tests

### Phase 7: VS Code Extension (Week 12-13)
- Implement extension skeleton
- DCAE status panel
- Skill view with checklists
- Consensus results visualization
- Decision history viewer
- Quick commands

### Phase 8: MVP - User Login (Week 14-15)
- Create example project structure
- Write BMAD agents for user login
- Configure DCAE workflow
- Execute complete workflow end-to-end
- Document the flow
- Create tutorial

---

## Critical Files to Create

| File | Purpose |
|------|---------|
| `src/python/dcae/orchestrator.py` | Main orchestration logic |
| `src/python/dcae/config/loader.py` | Configuration loading and validation |
| `src/python/dcae/bmad/agent_parser.py` | Parse BMAD agent.md files |
| `src/python/dcae/superpowers/skill_manager.py` | Load and manage Superpowers skills |
| `src/python/dcae/massgen/consensus_gateway.py` | Gateway to MassGen consensus system |
| `src/python/dcae/memory/tracker.py` | Decision tracking and persistence |
| `.dcae/config.yaml` | Main configuration file |
| `.dcae/skills/test-driven-development/SKILL.md` | TDD skill definition |
| `.dcae/agents/developer.md` | BMAD agent definition for developer |
| `examples/user-login-mvp/.dcae/config.yaml` | MVP example configuration |

---

## Verification

After implementation, verify the MVP by:

1. **Configuration Test**: Run `dcae init` in a new project and validate config
2. **Workflow Execution**: Run `dcae workflow start user-login` and observe:
   - PM agent produces requirements brief
   - Architect agent runs with brainstorming skill
   - MassGen consensus validates architecture design
   - Developer agent follows TDD cycle
   - MassGen consensus validates code quality (>100 lines)
   - QA agent runs verification
3. **Memory Check**: Run `dcae memory query` and verify decisions are tracked
4. **Consensus Reports**: Run `dcae consensus report` and view voting results
5. **VS Code Integration**: Open project in VS Code extension and view:
   - DCAE status panel
   - Skill checklists
   - Consensus voting results
   - Decision history

---

## Dependencies

- Python 3.11+
- Node.js 20+
- MassGen (via pip install massgen)
- BMAD skills (copy from `.dcae/skills/`)
- Claude Code / Cursor / Trae (for skill integration)
