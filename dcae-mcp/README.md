# DCAE MCP Server

MCP (Model Context Protocol) server for DCAE TDD framework. Enables Claude Code and other MCP-compatible AI agents to directly invoke DCAE tools.

## Installation

```bash
pip install dcae-mcp
```

## Configuration

### Claude Code / Claude Desktop

Add to your `claude_desktop_config.json`:

**Linux/macOS**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

## Available Tools

After configuration, Claude Code will discover these tools:

| Tool | Description |
|------|-------------|
| `tdd_run` | Run complete DCAE TDD cycle |
| `tdd_design` | Phase 1: Create failing tests |
| `tdd_code` | Phase 2: Implement code to pass tests |
| `tdd_analyze` | Phase 3: Check quality and coverage |
| `tdd_evolve` | Phase 4: Refactor code |
| `tdd_init` | Initialize new project |
| `tdd_status` | Get current DCAE state |

## Usage Example

In Claude Code:

```
Please use the DCAE framework to implement quick sort:
- Call tdd_run tool
- task: "Implement quick sort algorithm"
- test_file: "tests/test_quick_sort.py"
- source_file: "src/quick_sort.py"
```

## Running Manually

```bash
# Start MCP server via stdio
python3 -m dcae_mcp.server
```

## License

MIT License
