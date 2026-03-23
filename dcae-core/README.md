# DCAE Framework

**DCAE (Design-Code-Analyze-Evolve)** is a Python-based TDD framework that provides structured, test-driven development methodology.

## Installation

```bash
pip install dcae
```

For development:

```bash
pip install dcae[dev]
```

## Quick Start

### CLI Usage

```bash
# Run complete TDD cycle
dcae run --task "Implement quick sort" --test tests/test_sort.py --source src/sort.py

# Individual phases
dcae design --test tests/test_feature.py
dcae code --source src/feature.py
dcae analyze --threshold 80
dcae evolve --optimize

# Initialize new project
dcae init my_project
```

### Python API

```python
from dcae import DCAEFramework

# Create instance
dcae = DCAEFramework(project_root="/path/to/project")

# Run complete cycle
result = dcae.run(
    test_file="tests/test_feature.py",
    source_file="src/feature.py",
    max_iterations=10
)

# Access results
print(f"Status: {result.status}")
print(f"Coverage: {result.coverage_lines}%")
print(f"Recommendations: {result.recommendations}")
```

### MCP Server

For Claude Code integration, install the MCP server:

```bash
pip install dcae-mcp
```

Then configure in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dcae": {
      "command": "python3",
      "args": ["-m", "dcae_mcp.server"]
    }
  }
}
```

## Core Workflow (DCAE Cycle)

### Phase 1: Design (D)

Write failing test specification:
- Define expected behavior and edge cases
- Establish acceptance criteria
- Document assumptions and constraints

### Phase 2: Code (C)

Write minimal code to pass tests:
- Implement simplest solution
- Follow YAGNI principle
- Keep implementation focused

### Phase 3: Analyze (A)

Review code quality and test coverage:
- Run full test suite
- Check coverage metrics
- Review code style
- Identify technical debt

### Phase 4: Evolve (E)

Refactor and improve without changing behavior:
- Refactor for clarity
- Extract reusable components
- Improve naming and documentation
- Optimize performance if needed

## TDD Iron Laws

1. **No production code without a failing test** - Red phase is mandatory
2. **Write only enough test to fail** - Don't over-specify upfront
3. **Write only enough code to pass** - Don't over-engineer
4. **Refactor only when tests pass** - Green is the gate
5. **Never break existing tests** - Regression is forbidden

## Quality Gates

| Gate | Threshold | Action if Failed |
|------|-----------|------------------|
| Test Pass Rate | 100% | Fix immediately |
| Line Coverage | ≥80% | Add tests |
| Function Coverage | ≥90% | Add edge cases |
| Cyclomatic Complexity | ≤10 | Refactor |
| Code Style Violations | 0 | Fix with linter |

## Cross-Platform Support

DCAE supports all major operating systems:
- ✅ **Linux** - Fully supported
- ✅ **macOS** - Fully supported
- ✅ **Windows** - Fully supported

The framework automatically adapts to:
- Path separators (Path objects handle automatically)
- Python commands (python3 vs python)
- Subprocess execution parameters

## License

MIT License
