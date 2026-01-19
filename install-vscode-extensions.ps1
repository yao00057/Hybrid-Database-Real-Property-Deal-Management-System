#===============================================================================
# Install VS Code Extensions for Real Property Deal Management System
# Run: .\install-vscode-extensions.ps1
#===============================================================================

Write-Host ""
Write-Host "Installing VS Code extensions for the project..." -ForegroundColor Cyan
Write-Host ""

# Check if VS Code is installed
$codeCmd = Get-Command code -ErrorAction SilentlyContinue
if (-not $codeCmd) {
    Write-Host "ERROR: VS Code is not installed or 'code' command is not in PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install VS Code from: https://code.visualstudio.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing, make sure to add 'code' to PATH:" -ForegroundColor Yellow
    Write-Host "  - Open VS Code"
    Write-Host "  - Press Ctrl+Shift+P"
    Write-Host "  - Type 'Shell Command: Install code command in PATH'"
    exit 1
}

Write-Host "[1/9] Installing Python extension..." -ForegroundColor Yellow
code --install-extension ms-python.python --force

Write-Host "[2/9] Installing Pylint extension..." -ForegroundColor Yellow
code --install-extension ms-python.pylint --force

Write-Host "[3/9] Installing Vue (Volar) extension..." -ForegroundColor Yellow
code --install-extension Vue.volar --force

Write-Host "[4/9] Installing ESLint extension..." -ForegroundColor Yellow
code --install-extension dbaeumer.vscode-eslint --force

Write-Host "[5/9] Installing Prettier extension..." -ForegroundColor Yellow
code --install-extension esbenp.prettier-vscode --force

Write-Host "[6/9] Installing Docker extension..." -ForegroundColor Yellow
code --install-extension ms-azuretools.vscode-docker --force

Write-Host "[7/9] Installing MongoDB extension..." -ForegroundColor Yellow
code --install-extension mongodb.mongodb-vscode --force

Write-Host "[8/9] Installing SQLTools extension..." -ForegroundColor Yellow
code --install-extension mtxr.sqltools --force

Write-Host "[9/9] Installing SQLTools MySQL Driver..." -ForegroundColor Yellow
code --install-extension mtxr.sqltools-driver-mysql --force

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  All VS Code extensions installed successfully!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installed extensions:" -ForegroundColor Cyan
Write-Host "  - Python (IntelliSense, debugging)"
Write-Host "  - Pylint (Python linting)"
Write-Host "  - Vue - Official (Vue 3 support)"
Write-Host "  - ESLint (JavaScript/TypeScript linting)"
Write-Host "  - Prettier (Code formatting)"
Write-Host "  - Docker (Container management)"
Write-Host "  - MongoDB for VS Code (Database browsing)"
Write-Host "  - SQLTools + MySQL (Database browsing)"
Write-Host ""
Write-Host "You may need to restart VS Code for all extensions to activate." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
