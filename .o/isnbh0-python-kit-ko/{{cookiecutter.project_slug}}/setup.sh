#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "Setting up development environment (uv, pre-commit)..."

# Check for uv
if command -v uv >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} uv is installed"
else
    echo -e "${RED}✗${NC} uv is not installed"
    echo -e "${YELLOW}Installing uv is recommended for package management.${NC}"
    echo "You can install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    read -p "Would you like to install uv now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo -e "${GREEN}✓${NC} uv installed successfully"
    else
        echo "Skipping uv installation. Some project commands may not work."
    fi
fi

# Check for pre-commit
if command -v pre-commit >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} pre-commit is installed"
else
    echo -e "${RED}✗${NC} pre-commit is not installed"
    echo -e "${YELLOW}Installing pre-commit is recommended for code quality checks.${NC}"
    echo "You can install it with: brew install pre-commit"
    read -p "Would you like to install pre-commit now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install pre-commit
        echo -e "${GREEN}✓${NC} pre-commit installed successfully"
    else
        echo "Skipping pre-commit installation. Git hooks won't be installed."
    fi
fi

echo -e "${GREEN}Setup complete!${NC}"
