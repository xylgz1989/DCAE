# DCAE Interactive Mode Usage Guide

This guide explains how to use the enhanced interactive mode of DCAE (Distributed Coding Agent Environment).

## Starting Interactive Mode

To start the interactive mode, run:

```bash
python dcae.py
```

This enters the interactive session where you can run commands without the `python dcae.py` prefix:

```
dcae>
```

## Interactive Commands

### Code Generation
```bash
# Basic code generation
dcae> gen write a function to reverse a string

# Generate code to a specific file
dcae> gen "create a calculator class with add and subtract methods" -o calculator.py
```

### Code Review
```bash
# Review a code file
dcae> review my_app.py

# Review with path
dcae> review src/utils/helper.py
```

### Debugging
```bash
# Debug an error
dcae> debug "AttributeError: 'NoneType' object has no attribute 'name'"

# Debug with context from a file
dcae> debug "TypeError: unsupported operand type(s)" -c problematic_file.py
```

### Documentation
```bash
# Generate requirements
dcae> req "REST API for user management system"

# Generate test documentation
dcae> test-doc src/models/user.py

# Generate test cases
dcae> test-case src/models/user.py
```

### Internal Commands (start with /)
```bash
# Show current status
dcae> /status

# Show help
dcae> /help

# Clear conversation history
dcae> /clear

# Show conversation history
dcae> /history

# Exit interactive mode
dcae> /exit
```

## Enhanced Features

### 1. Smart File Completion
When typing commands that involve files (like `review`, `test-doc`, `test-case`), you can start typing a filename and press Tab to see available files in the current directory.

Examples:
```bash
dcae> review main.  # Press Tab for .py files
dcae> test-doc util.  # Press Tab for available files
```

Supported file extensions include: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.cpp`, `.c`, `.html`, `.css`, `.txt`, `.json`, `.yaml`, `.yml`, `.md`

### 2. Conversation Context
The system maintains conversation history to provide context for your requests:

```bash
dcae> gen "function to validate email address"
[Generates code...]
dcae> review temp_file.py
[Reviews the code with context from previous interaction...]
dcae> gen "add tests for the email validation function"
[Understands the context and generates relevant tests...]
```

### 3. Progress Indicators
Long-running operations show progress bars with estimated time remaining:

```
[==========          ] 50% ETA: 12s
```

### 4. Budget Tracking
The system monitors your API usage and warns when approaching limits:

```
WARNING: Daily budget at 82%
```

### 5. Error Handling
The system handles errors gracefully and maintains session state even if API calls fail.

## Best Practices

1. **Start with /help** to see all available commands
2. **Use /status** to check your API usage limits
3. **Use /clear** periodically to reset conversation context if needed
4. **Use /history** to review your conversation history
5. **Use descriptive prompts** for better results
6. **Specify file extensions** when working with files

## Troubleshooting

### Common Issues:

- **File not found**: Make sure to provide correct file paths (relative to current directory)
- **API key errors**: Run `python dcae.py init` to reconfigure your settings
- **Rate limits**: Wait before making additional requests if you hit rate limits
- **Context confusion**: Use `/clear` to reset conversation history

### Getting Help:

- Type `/help` for command list
- Use `/exit` to leave interactive mode and start fresh
- Check your configuration in `~/.dcae/config.json`

## Exiting Interactive Mode

To exit the interactive mode, you can use any of these commands:

```bash
dcae> /exit
dcae> exit
dcae> quit
dcae> q
```

Or use Ctrl+C to cancel the current request (not the entire session).