# DCAE Framework

**Disciplined Consensus-Driven Agentic Engineering** - A comprehensive AI-assisted software engineering framework.

[English](README.md) | [中文](README_CN.md)

---

## What is DCAE?

DCAE is an intelligent development assistant that helps you build better software faster. It combines AI-powered code generation with disciplined engineering practices to enhance your productivity and code quality.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Initialize DCAE
python dcae.py init

# Start coding with AI assistance
python dcae.py --help
```

## Core Features

### 🎯 Requirements Management
- Generate detailed requirement documents from natural language descriptions
- Identify conflicts and issues early in the development process
- Export and share requirements with your team

### 🏗️ Architecture Design
- Generate architectural solutions based on your requirements
- Review and validate architecture against best practices
- Interactive modification and refinement

### 💻 Code Generation
- Generate code structure from specifications
- Implement business logic automatically
- Support for multiple technology stacks and languages

### 🔍 Code Review
- Automated code quality analysis
- Issue identification and fix suggestions
- Multi-layer validation system

### 🧪 Testing & Documentation
- Generate comprehensive test cases
- Multiple test types support (unit, integration, etc.)
- Automatic test documentation

### 🧠 Knowledge Fusion
- Cross-domain knowledge integration
- Best practices recommendations
- Project-specific constraint learning

### ⚙️ Multi-LLM Support
- Support for Qwen, GLM, GPT-4, Claude, and more
- Intelligent model selection based on task complexity
- Budget management and usage tracking

### 📊 Process Discipline
- Configurable discipline levels
- Adjustable validation strictness
- Compliance tracking

## Project Structure

```
DCAE/
├── src/                    # Source code
│   └── dcae/
│       ├── cli.py          # Command-line interface
│       ├── knowledge_fusion/
│       ├── product_knowledge/
│       ├── task_management/
│       └── ...
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example code
├── templates/              # Project templates
└── config/                 # Configuration files
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- API key for your preferred LLM provider

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/xylgz1989/DCAE.git
   cd DCAE
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Initialize configuration**
   ```bash
   python dcae.py init
   ```

4. **Configure your LLM provider**
   - Select provider (Qwen, GLM, OpenAI, Claude, etc.)
   - Enter API key
   - Set budget limits (optional)

## Usage Examples

### Generate Requirements Document
```bash
python dcae.py req "Build a user authentication system with OAuth2 support"
```

### Generate Code
```bash
python dcae.py gen "Create a REST API endpoint for user registration"
```

### Review Code
```bash
python dcae.py review src/my_module.py
```

### Generate Tests
```bash
python dcae.py test-case src/my_module.py
```

## Configuration

DCAE stores configuration in `~/.dcae/config.json`:

```json
{
  "provider": "qwen",
  "api_key": "your-api-key",
  "model": "qwen-plus",
  "daily_limit": 100,
  "monthly_limit": 1000
}
```

## Supported LLM Providers

| Provider | Models | Region |
|----------|--------|--------|
| Qwen | Turbo, Plus, Coder Plus, Max | Global/China |
| GLM | GLM-4 | China |
| OpenAI | GPT-4o | Global |
| Anthropic | Claude 3.5 Sonnet | Global |

## Documentation

- [Best Practices Guide](docs/best_practices.md)
- [Constraint Handling](docs/constraint_handling_guide.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing](CONTRIBUTING.md)

## Development

### Running Tests
```bash
python -m pytest tests/ -v
```

### Building Package
```bash
python setup.py build
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/xylgz1989/DCAE/issues)
- **Discussions**: [GitHub Discussions](https://github.com/xylgz1989/DCAE/discussions)

## Acknowledgments

Built using the BMAD methodology for systematic software engineering.

---

**Version**: 1.0.0 | **Status**: Stable
