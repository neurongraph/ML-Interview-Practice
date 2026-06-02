#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Interview Prep Portal — First-time Setup Script
#
# Purpose: Bootstrap a fresh clone — installs uv, just, and dependencies,
#          then walks you through creating your first profile.
#
# Once this script has run, use 'just <command>' for everyday operations.
# See 'just help' or README.md for available commands.
# ─────────────────────────────────────────────────────────────────────────────

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}✓${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET}  $*"; }
err()  { echo -e "${RED}✗${RESET} $*"; }
info() { echo -e "${CYAN}→${RESET} $*"; }
hdr()  { echo -e "\n${BOLD}$*${RESET}"; }

echo ""
echo -e "${BOLD}Interview Prep Portal — Setup${RESET}"
echo "────────────────────────────────────────"

# ── 1. uv ────────────────────────────────────────────────────────────────────
hdr "1. Checking uv (Python package manager)"

if command -v uv &> /dev/null; then
    ok "uv $(uv --version 2>&1 | head -1) already installed"
else
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Make uv available in this shell session
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    ok "uv installed"
    warn "You may need to restart your shell or run:  source \$HOME/.local/bin/env"
fi

# ── 2. just ──────────────────────────────────────────────────────────────────
hdr "2. Checking just (command runner)"

if command -v just &> /dev/null; then
    ok "just $(just --version) already installed"
else
    warn "'just' is not installed."
    echo ""
    echo "   Install it with one of:"
    echo "     macOS:   brew install just"
    echo "     Cargo:   cargo install just"
    echo "     Script:  curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin"
    echo ""
    echo "   After installing just, re-run this script, or run these manually:"
    echo "     uv sync"
    echo "     uv run python main.py list-profiles"
    echo ""
    read -rp "Continue without just? (y/N) " choice
    [[ "$choice" =~ ^[Yy]$ ]] || exit 1
fi

# ── 3. Ollama ────────────────────────────────────────────────────────────────
hdr "3. Checking Ollama"

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    ok "Ollama is running"
else
    warn "Ollama is not running (or not installed)."
    echo ""
    echo "   Install from https://ollama.ai, then start it:"
    echo "     ollama serve"
    echo ""
    echo "   Pull a model (the default):"
    echo "     ollama pull ministral-3:14b"
    echo ""
    echo "   Ollama is required to generate questions and evaluate answers."
    echo "   You can finish setup now and start Ollama before running interviews."
    echo ""
fi

# ── 4. .env ──────────────────────────────────────────────────────────────────
hdr "4. Environment config"

if [ -f ".env" ]; then
    ok ".env already exists"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        ok "Created .env from .env.example"
        info "Edit .env to change the Ollama model or timeout if needed"
    else
        warn ".env.example not found — skipping"
    fi
fi

# ── 5. Dependencies ───────────────────────────────────────────────────────────
hdr "5. Installing Python dependencies"

uv sync
ok "Dependencies installed (virtual environment in .venv/)"

# ── 6. Profiles ───────────────────────────────────────────────────────────────
hdr "6. Interview profiles"

PROFILE_COUNT=$(uv run python -c "
from profile_manager import ProfileManager
from config import PROFILES_DIR
m = ProfileManager(PROFILES_DIR)
profiles = m.list_profiles()
print(len(profiles))
" 2>/dev/null || echo "0")

if [ "$PROFILE_COUNT" -gt 0 ]; then
    ok "$PROFILE_COUNT profile(s) found:"
    uv run python main.py list-profiles 2>/dev/null || true
else
    warn "No profiles found."
    echo "   Create your first profile with:  just create-profile"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}────────────────────────────────────────${RESET}"
echo -e "${GREEN}${BOLD}✓ Setup complete!${RESET}"
echo ""
echo "  Everyday commands (run from this directory):"
echo ""
echo -e "  ${CYAN}just help${RESET}                         List all commands"
echo -e "  ${CYAN}just list-profiles${RESET}                See available interview profiles"
echo -e "  ${CYAN}just start${RESET}                        Start a new interview"
echo -e "  ${CYAN}just start --profile ml-engineering${RESET}  Start with the ML/DE profile"
echo ""
echo "  To set up a new interview profile for a different role:"
echo ""
echo -e "  ${CYAN}just create-profile${RESET}               Interactive wizard"
echo -e "  ${CYAN}just generate --profile <name>${RESET}    Generate questions (needs Ollama)"
echo ""
echo "  See README.md for the full workflow."
echo ""
