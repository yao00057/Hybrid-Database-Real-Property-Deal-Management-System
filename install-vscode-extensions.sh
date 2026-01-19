#!/bin/bash
#===============================================================================
# Install VS Code Extensions for Real Property Deal Management System
# Run: ./install-vscode-extensions.sh
#===============================================================================

echo "Installing VS Code extensions for the project..."
echo ""

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    echo "ERROR: VS Code is not installed or 'code' command is not in PATH."
    echo ""
    echo "Install VS Code from: https://code.visualstudio.com/"
    echo ""
    echo "After installing, make sure to add 'code' to PATH:"
    echo "  - Open VS Code"
    echo "  - Press Ctrl+Shift+P"
    echo "  - Type 'Shell Command: Install code command in PATH'"
    exit 1
fi

echo "[1/9] Installing Python extension..."
code --install-extension ms-python.python --force

echo "[2/9] Installing Pylint extension..."
code --install-extension ms-python.pylint --force

echo "[3/9] Installing Vue (Volar) extension..."
code --install-extension Vue.volar --force

echo "[4/9] Installing ESLint extension..."
code --install-extension dbaeumer.vscode-eslint --force

echo "[5/9] Installing Prettier extension..."
code --install-extension esbenp.prettier-vscode --force

echo "[6/9] Installing Docker extension..."
code --install-extension ms-azuretools.vscode-docker --force

echo "[7/9] Installing MongoDB extension..."
code --install-extension mongodb.mongodb-vscode --force

echo "[8/9] Installing SQLTools extension..."
code --install-extension mtxr.sqltools --force

echo "[9/9] Installing SQLTools MySQL Driver..."
code --install-extension mtxr.sqltools-driver-mysql --force

echo ""
echo "================================================================"
echo "  All VS Code extensions installed successfully!"
echo "================================================================"
echo ""
echo "Installed extensions:"
echo "  - Python (IntelliSense, debugging)"
echo "  - Pylint (Python linting)"
echo "  - Vue - Official (Vue 3 support)"
echo "  - ESLint (JavaScript/TypeScript linting)"
echo "  - Prettier (Code formatting)"
echo "  - Docker (Container management)"
echo "  - MongoDB for VS Code (Database browsing)"
echo "  - SQLTools + MySQL (Database browsing)"
echo ""
echo "You may need to restart VS Code for all extensions to activate."
