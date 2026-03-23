#!/bin/bash
# DCAE Installation Script
# Installs dcae and dcae-mcp packages

set -e

echo "🚀 DCAE Installation Script"
echo "============================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "✓ Python version: $PYTHON_VERSION"

# Check if version is 3.11+
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Error: Python 3.11+ required"
    exit 1
fi

# Install dcae-core
echo ""
echo "📦 Installing dcae-core..."
cd "$(dirname "$0")/dcae-core"
pip install -e .
echo "✓ dcae-core installed"

# Install dcae-mcp
echo ""
echo "📦 Installing dcae-mcp..."
cd "$(dirname "$0")/../dcae-mcp"
pip install -e .
echo "✓ dcae-mcp installed"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
if command -v dcae &> /dev/null; then
    echo "✓ dcae CLI available"
    dcae --version 2>/dev/null || echo "  (version command not available)"
else
    echo "⚠️  dcae CLI not in PATH (may need to add ~/.local/bin)"
fi

# Test import
python3 -c "from dcae import DCAEFramework; print('✓ dcae import successful')"
python3 -c "from dcae_mcp.server import server; print('✓ dcae_mcp import successful')"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Configure Claude Code MCP (optional):"
echo "   Edit ~/.config/claude/claude_desktop_config.json"
echo "   Add: {\"mcpServers\": {\"dcae\": {\"command\": \"python3\", \"args\": [\"-m\", \"dcae_mcp.server\"]}}}"
echo ""
echo "2. Test CLI:"
echo "   dcae --help"
echo ""
echo "3. Read documentation:"
echo "   cat DEPLOYMENT_GUIDE.md"
echo ""
