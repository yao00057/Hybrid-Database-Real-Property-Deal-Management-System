#===============================================================================
# Real Property Deal Management System - Windows Deployment Script
# For Windows 10/11 with PowerShell
#===============================================================================

#Requires -RunAsAdministrator

param(
    [string]$InstallPath = "$env:USERPROFILE\real-estate-system"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Step($step, $message) {
    Write-Host ""
    Write-Host "[$step] $message" -ForegroundColor Yellow
}

function Write-Success($message) {
    Write-Host "    $message" -ForegroundColor Green
}

function Write-Info($message) {
    Write-Host "    $message" -ForegroundColor Cyan
}

# Banner
Write-Host ""
Write-Host "================================================================" -ForegroundColor Blue
Write-Host "  Real Property Deal Management System - Windows Deployment" -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue
Write-Host ""

#-------------------------------------------------------------------------------
# Step 1: Check and Install Chocolatey
#-------------------------------------------------------------------------------
Write-Step "1/8" "Checking Chocolatey package manager..."

if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Success "Chocolatey installed successfully"
} else {
    Write-Success "Chocolatey already installed"
}

#-------------------------------------------------------------------------------
# Step 2: Check and Install Docker Desktop
#-------------------------------------------------------------------------------
Write-Step "2/8" "Checking Docker Desktop..."

$dockerInstalled = $false
if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
        docker version | Out-Null
        $dockerInstalled = $true
        Write-Success "Docker Desktop already installed and running"
    } catch {
        Write-Info "Docker installed but not running"
    }
}

if (-not $dockerInstalled) {
    Write-Info "Installing Docker Desktop..."
    choco install docker-desktop -y

    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  IMPORTANT: Docker Desktop has been installed!" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please complete these steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart your computer" -ForegroundColor White
    Write-Host "  2. Launch Docker Desktop from Start Menu" -ForegroundColor White
    Write-Host "  3. Wait for Docker to fully start (whale icon in system tray)" -ForegroundColor White
    Write-Host "  4. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "  Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
}

# Verify Docker is running
Write-Info "Verifying Docker is running..."
$retries = 0
$maxRetries = 30
while ($retries -lt $maxRetries) {
    try {
        docker version | Out-Null
        break
    } catch {
        $retries++
        if ($retries -eq $maxRetries) {
            Write-Host "Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
            exit 1
        }
        Write-Info "Waiting for Docker to start... ($retries/$maxRetries)"
        Start-Sleep -Seconds 2
    }
}
Write-Success "Docker is running"

#-------------------------------------------------------------------------------
# Step 3: Check and Install Git
#-------------------------------------------------------------------------------
Write-Step "3/8" "Checking Git..."

if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Git..."
    choco install git -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Success "Git installed successfully"
} else {
    Write-Success "Git already installed"
}

#-------------------------------------------------------------------------------
# Step 4: Check and Install Node.js
#-------------------------------------------------------------------------------
Write-Step "4/8" "Checking Node.js..."

if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Node.js 20.x..."
    choco install nodejs-lts -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Success "Node.js installed successfully"
} else {
    $nodeVersion = node --version
    Write-Success "Node.js $nodeVersion already installed"
}

#-------------------------------------------------------------------------------
# Step 5: Check and Install Python
#-------------------------------------------------------------------------------
Write-Step "5/8" "Checking Python..."

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Python 3..."
    choco install python3 -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Success "Python installed successfully"
} else {
    $pythonVersion = python --version
    Write-Success "$pythonVersion already installed"
}

#-------------------------------------------------------------------------------
# Step 6: Clone or Update Repository
#-------------------------------------------------------------------------------
Write-Step "6/8" "Setting up project directory..."

if (Test-Path $InstallPath) {
    Write-Info "Project directory exists, pulling latest changes..."
    Set-Location $InstallPath
    git pull origin main
} else {
    Write-Info "Cloning repository..."
    git clone https://github.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System.git $InstallPath
    Set-Location $InstallPath
}
Write-Success "Project directory: $InstallPath"

#-------------------------------------------------------------------------------
# Step 7: Start Docker Services
#-------------------------------------------------------------------------------
Write-Step "7/8" "Starting Docker services (MongoDB, MySQL, Redis)..."

docker compose down 2>$null
docker compose up -d

Write-Info "Waiting for databases to initialize..."
Start-Sleep -Seconds 15

# Setup MySQL user
Write-Info "Configuring MySQL user..."
$mysqlSetup = @"
CREATE DATABASE IF NOT EXISTS real_estate_financial;
DROP USER IF EXISTS 'real_estate_user'@'%';
CREATE USER 'real_estate_user'@'%' IDENTIFIED WITH mysql_native_password BY 'real_estate_pass';
GRANT ALL PRIVILEGES ON real_estate_financial.* TO 'real_estate_user'@'%';
FLUSH PRIVILEGES;
"@

try {
    docker exec re_mysql mysql -u root -prootpassword -e $mysqlSetup 2>$null
    Write-Success "MySQL user configured"
} catch {
    Write-Info "MySQL user may already exist, continuing..."
}

Write-Success "Docker services started"

#-------------------------------------------------------------------------------
# Step 8: Setup Backend and Frontend
#-------------------------------------------------------------------------------
Write-Step "8/8" "Setting up Backend and Frontend..."

# Backend setup
Write-Info "Setting up Python backend..."
Set-Location "$InstallPath\backend"

if (!(Test-Path "venv")) {
    python -m venv venv
}

# Activate venv and install dependencies
& "$InstallPath\backend\venv\Scripts\pip.exe" install --upgrade pip -q
& "$InstallPath\backend\venv\Scripts\pip.exe" install -r requirements.txt -q

Write-Success "Backend dependencies installed"

# Frontend setup
Write-Info "Setting up Vue.js frontend..."
Set-Location "$InstallPath\frontend"
npm install --silent 2>$null

# Update API URL to localhost
$apiFile = "$InstallPath\frontend\src\api\index.ts"
if (Test-Path $apiFile) {
    (Get-Content $apiFile) -replace "baseURL:.*", "baseURL: 'http://localhost:8001/api'," | Set-Content $apiFile
}

Write-Success "Frontend dependencies installed"

#-------------------------------------------------------------------------------
# Create Start Scripts
#-------------------------------------------------------------------------------
Write-Info "Creating start scripts..."

# Create backend start script
$backendScript = @"
@echo off
cd /d "$InstallPath\backend"
call venv\Scripts\activate.bat
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"@
Set-Content -Path "$InstallPath\start-backend.bat" -Value $backendScript

# Create frontend start script
$frontendScript = @"
@echo off
cd /d "$InstallPath\frontend"
npm run dev -- --port 5173
"@
Set-Content -Path "$InstallPath\start-frontend.bat" -Value $frontendScript

# Create combined start script
$startAllScript = @"
@echo off
echo Starting Real Property Deal Management System...
echo.

REM Start Docker containers if not running
docker compose -f "$InstallPath\docker-compose.yml" up -d

REM Wait for databases
timeout /t 5 /nobreak > nul

REM Start backend in new window
start "Backend API" cmd /k "cd /d $InstallPath\backend && call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Start frontend in new window
start "Frontend App" cmd /k "cd /d $InstallPath\frontend && npm run dev -- --port 5173"

echo.
echo ================================================================
echo   Services are starting...
echo ================================================================
echo.
echo   Frontend App:        http://localhost:5173
echo   Backend API:         http://localhost:8001
echo   API Documentation:   http://localhost:8001/docs
echo   phpMyAdmin:          http://localhost:8080
echo   Mongo Express:       http://localhost:8081
echo.
echo   Press any key to close this window (services will keep running)
pause > nul
"@
Set-Content -Path "$InstallPath\start-all.bat" -Value $startAllScript

# Create stop script
$stopScript = @"
@echo off
echo Stopping all services...
taskkill /F /IM "node.exe" 2>nul
taskkill /F /FI "WINDOWTITLE eq Backend API*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Frontend App*" 2>nul
docker compose -f "$InstallPath\docker-compose.yml" down
echo All services stopped.
pause
"@
Set-Content -Path "$InstallPath\stop-all.bat" -Value $stopScript

Write-Success "Start scripts created"

#-------------------------------------------------------------------------------
# Display Success Message
#-------------------------------------------------------------------------------
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "         Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Project Location: $InstallPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Start Commands:" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------"
Write-Host "  Start Everything:    " -NoNewline; Write-Host "$InstallPath\start-all.bat" -ForegroundColor White
Write-Host "  Stop Everything:     " -NoNewline; Write-Host "$InstallPath\stop-all.bat" -ForegroundColor White
Write-Host "  Start Backend Only:  " -NoNewline; Write-Host "$InstallPath\start-backend.bat" -ForegroundColor White
Write-Host "  Start Frontend Only: " -NoNewline; Write-Host "$InstallPath\start-frontend.bat" -ForegroundColor White
Write-Host "----------------------------------------------------------------"
Write-Host ""
Write-Host "Access URLs (after running start-all.bat):" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------"
Write-Host "| Frontend App        | http://localhost:5173              |" -ForegroundColor White
Write-Host "| Backend API         | http://localhost:8001              |" -ForegroundColor White
Write-Host "| API Documentation   | http://localhost:8001/docs         |" -ForegroundColor White
Write-Host "| phpMyAdmin          | http://localhost:8080              |" -ForegroundColor White
Write-Host "| Mongo Express       | http://localhost:8081              |" -ForegroundColor White
Write-Host "----------------------------------------------------------------"
Write-Host ""
Write-Host "Default Credentials:" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------"
Write-Host "| MySQL:    user: real_estate_user / pass: real_estate_pass   |" -ForegroundColor White
Write-Host "| MongoDB:  No authentication (development mode)              |" -ForegroundColor White
Write-Host "----------------------------------------------------------------"
Write-Host ""
Write-Host "How to Use:" -ForegroundColor Yellow
Write-Host "  1. Run start-all.bat to start all services"
Write-Host "  2. Open http://localhost:5173 in your browser"
Write-Host "  3. Register a new account or use the API at /docs"
Write-Host "  4. When done, run stop-all.bat to stop all services"
Write-Host ""
Write-Host "Would you like to start the application now? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Starting application..." -ForegroundColor Green
    Start-Process -FilePath "$InstallPath\start-all.bat"
}

Write-Host ""
Write-Host "Happy coding!" -ForegroundColor Green
Write-Host ""
