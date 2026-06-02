#!/bin/bash

# ML Interview Prep - Setup Script
# This script sets up the project for first-time use

set -e

echo "🚀 ML Interview Prep - Setup Script"
echo "===================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✓ uv installed successfully"
    echo ""
    # Source the new uv installation
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✓ uv is already installed"
fi

# Check if Ollama is running
echo ""
echo "Checking Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "⚠️  Ollama is not running"
    echo "Please start Ollama with: ollama run mistral"
    echo "Then run this script again"
    exit 1
fi

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
uv sync
echo "✓ Dependencies installed"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start an interview:  uv run python main.py start"
echo "  2. Check progress:      uv run python main.py status"
echo "  3. Resume interview:    uv run python main.py resume"
echo ""
echo "For more details, see README.md"
