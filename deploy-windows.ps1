#===============================================================================
# Real Property Deal Management System - Windows Deployment Script
# For Windows 10/11 with PowerShell
#===============================================================================

#Requires -RunAsAdministrator

param(
    [string]$InstallPath = "$env:USERPROFILE\Desktop\real-estate-system"
)

# Disable all confirmation prompts
$ErrorActionPreference = "Continue"
$ConfirmPreference = "None"
$ProgressPreference = "SilentlyContinue"

# Set environment variable to auto-confirm Chocolatey
$env:ChocolateyToolsLocation = "C:\tools"

# Function to refresh environment variables without restarting PowerShell
function Update-Environment {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    foreach($level in "Machine","User") {
        [Environment]::GetEnvironmentVariables($level).GetEnumerator() | ForEach-Object {
            if($_.Name -ne 'Path') {
                Set-Item -Path "Env:\$($_.Name)" -Value $_.Value -ErrorAction SilentlyContinue
            }
        }
    }
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

function Write-ErrorMsg($message) {
    Write-Host "    $message" -ForegroundColor Red
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
    Update-Environment

    # Configure Chocolatey to not prompt
    choco feature enable -n allowGlobalConfirmation 2>$null
    Write-Success "Chocolatey installed successfully"
} else {
    # Ensure Chocolatey doesn't prompt
    choco feature enable -n allowGlobalConfirmation 2>$null
    Write-Success "Chocolatey already installed"
}

#-------------------------------------------------------------------------------
# Step 2: Check and Install Docker Desktop
#-------------------------------------------------------------------------------
Write-Step "2/8" "Checking Docker Desktop..."

$dockerRunning = $false

if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
        $dockerVersion = docker version --format '{{.Server.Version}}' 2>$null
        if ($dockerVersion) {
            $dockerRunning = $true
            Write-Success "Docker Desktop is running (version: $dockerVersion)"
        }
    } catch {
        Write-Info "Docker is installed but not running properly"
    }
}

if (-not $dockerRunning) {
    $dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktopPath) {
        Write-Info "Docker Desktop is installed but not running."
        Write-Info "Starting Docker Desktop..."
        Start-Process $dockerDesktopPath

        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Yellow
        Write-Host "  Waiting for Docker Desktop to start..." -ForegroundColor Yellow
        Write-Host "================================================================" -ForegroundColor Yellow

        $retries = 0
        $maxRetries = 60
        while ($retries -lt $maxRetries) {
            Start-Sleep -Seconds 3
            try {
                $dockerVersion = docker version --format '{{.Server.Version}}' 2>$null
                if ($dockerVersion) {
                    $dockerRunning = $true
                    Write-Success "Docker Desktop is now running!"
                    break
                }
            } catch { }
            $retries++
            Write-Host "    Waiting... ($retries/$maxRetries)" -ForegroundColor Gray
        }

        if (-not $dockerRunning) {
            Write-ErrorMsg "Docker Desktop failed to start. Please start it manually and run this script again."
            exit 1
        }
    } else {
        Write-Info "Installing Docker Desktop (this may take a few minutes)..."
        choco install docker-desktop -y --no-progress 2>$null

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
}

#-------------------------------------------------------------------------------
# Step 3: Check and Install Git
#-------------------------------------------------------------------------------
Write-Step "3/8" "Checking Git..."

Update-Environment

if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Git..."
    choco install git -y --no-progress 2>$null
    Update-Environment

    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Success "Git installed successfully"
    } else {
        Write-ErrorMsg "Git installation may require a restart. Please restart PowerShell and run again."
    }
} else {
    $gitVersion = git --version
    Write-Success "$gitVersion already installed"
}

#-------------------------------------------------------------------------------
# Step 4: Check and Install Node.js
#-------------------------------------------------------------------------------
Write-Step "4/8" "Checking Node.js..."

Update-Environment

if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Node.js LTS..."
    choco install nodejs-lts -y --no-progress 2>$null
    Update-Environment

    if (Get-Command node -ErrorAction SilentlyContinue) {
        $nodeVersion = node --version
        Write-Success "Node.js $nodeVersion installed successfully"
    } else {
        Write-ErrorMsg "Node.js installation may require a restart. Please restart PowerShell and run again."
    }
} else {
    $nodeVersion = node --version
    Write-Success "Node.js $nodeVersion already installed"
}

#-------------------------------------------------------------------------------
# Step 5: Check and Install Python
#-------------------------------------------------------------------------------
Write-Step "5/8" "Checking Python..."

Update-Environment

# Try multiple ways to find Python
$pythonCmd = $null
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
)

foreach ($pyPath in $pythonPaths) {
    try {
        $version = & $pyPath --version 2>$null
        if ($version -match "Python") {
            $pythonCmd = $pyPath
            break
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Info "Installing Python 3..."
    choco install python --version=3.12.0 -y --no-progress 2>$null
    Update-Environment

    Start-Sleep -Seconds 3
    Update-Environment

    foreach ($pyPath in $pythonPaths) {
        try {
            $version = & $pyPath --version 2>$null
            if ($version -match "Python") {
                $pythonCmd = $pyPath
                break
            }
        } catch { }
    }

    if ($pythonCmd) {
        $pythonVersion = & $pythonCmd --version
        Write-Success "$pythonVersion installed successfully"
    } else {
        Write-ErrorMsg "Python installation completed but requires PATH refresh."
        Write-ErrorMsg "Please close this PowerShell window, open a new one as Administrator,"
        Write-ErrorMsg "and run the script again."
        Write-Host ""
        Write-Host "Press any key to exit..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
} else {
    $pythonVersion = & $pythonCmd --version
    Write-Success "$pythonVersion already installed"
}

$global:PythonExe = $pythonCmd

#-------------------------------------------------------------------------------
# Step 6: Clone or Update Repository
#-------------------------------------------------------------------------------
Write-Step "6/8" "Setting up project directory..."

Update-Environment

if (Test-Path $InstallPath) {
    Write-Info "Project directory exists, pulling latest changes..."
    Set-Location $InstallPath
    git pull origin main 2>$null
} else {
    Write-Info "Cloning repository..."
    git clone https://github.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System.git $InstallPath
    Set-Location $InstallPath
}

# Copy .env.example to .env if .env doesn't exist
$envFile = "$InstallPath\backend\.env"
$envExample = "$InstallPath\backend\.env.example"
if (!(Test-Path $envFile) -and (Test-Path $envExample)) {
    Write-Info "Creating backend .env file from template..."
    Copy-Item $envExample $envFile
    Write-Success "Backend .env file created"
}

Write-Success "Project directory: $InstallPath"

#-------------------------------------------------------------------------------
# Step 7: Start Docker Services
#-------------------------------------------------------------------------------
Write-Step "7/8" "Starting Docker services (MongoDB, MySQL, Redis)..."

Set-Location $InstallPath

Write-Info "Stopping existing containers and removing volumes..."
docker compose down -v 2>$null

Write-Info "Starting fresh containers..."
docker compose up -d 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Docker Compose failed. Trying again..."
    Start-Sleep -Seconds 5
    docker compose up -d
}

Write-Info "Waiting for databases to initialize (20 seconds)..."
Start-Sleep -Seconds 20

Write-Success "Docker services started"

#-------------------------------------------------------------------------------
# Step 8: Setup Backend and Frontend
#-------------------------------------------------------------------------------
Write-Step "8/8" "Setting up Backend and Frontend..."

# Backend setup
Write-Info "Setting up Python backend..."
Set-Location "$InstallPath\backend"

if (!(Test-Path "venv")) {
    Write-Info "Creating Python virtual environment..."
    & $global:PythonExe -m venv venv
}

$pipExe = "$InstallPath\backend\venv\Scripts\pip.exe"

Write-Info "Installing Python dependencies (this may take a minute)..."
& $pipExe install --upgrade pip -q 2>$null
& $pipExe install -r requirements.txt -q 2>$null

Write-Success "Backend dependencies installed"

# Frontend setup
Write-Info "Setting up Vue.js frontend..."
Set-Location "$InstallPath\frontend"

Write-Info "Installing npm packages (this may take a few minutes)..."
# Use --yes and --legacy-peer-deps to avoid prompts
npm install --yes --legacy-peer-deps 2>$null

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

$backendScript = @"
@echo off
echo Starting Backend API...
cd /d "$InstallPath\backend"
call venv\Scripts\activate.bat
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"@
Set-Content -Path "$InstallPath\start-backend.bat" -Value $backendScript

$frontendScript = @"
@echo off
echo Starting Frontend...
cd /d "$InstallPath\frontend"
npm run dev -- --host --port 5173
"@
Set-Content -Path "$InstallPath\start-frontend.bat" -Value $frontendScript

$startAllScript = @"
@echo off
echo ================================================================
echo   Starting Real Property Deal Management System...
echo ================================================================
echo.

REM Start Docker containers if not running
echo Starting Docker containers...
docker compose -f "$InstallPath\docker-compose.yml" up -d

REM Wait for databases
echo Waiting for databases...
timeout /t 5 /nobreak > nul

REM Start backend in new window
echo Starting Backend API...
start "Backend API - Port 8001" cmd /k "cd /d $InstallPath\backend && call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Start frontend in new window
echo Starting Frontend App...
start "Frontend App - Port 5173" cmd /k "cd /d $InstallPath\frontend && npm run dev -- --host --port 5173"

echo.
echo ================================================================
echo   All services are starting!
echo ================================================================
echo.
echo   Wait about 10 seconds, then open your browser to:
echo.
echo   Frontend App:        http://localhost:5173
echo   Backend API:         http://localhost:8001
echo   API Documentation:   http://localhost:8001/docs
echo   phpMyAdmin:          http://localhost:8080
echo   Mongo Express:       http://localhost:8081
echo.
echo   HOW TO USE:
echo   1. Click "Register here" to create an account
echo   2. Choose a role (Buyer, Seller, Agent, or Lawyer)
echo   3. Login with your email and password
echo   4. Explore Dashboard, Properties, Deals, Transactions
echo.
echo   SEED TEST DATA (create test accounts for all roles):
echo   Run: seed-data.bat
echo.
echo   Press any key to close this window (services will keep running)
echo.
pause > nul
"@
Set-Content -Path "$InstallPath\start-all.bat" -Value $startAllScript

$stopScript = @"
@echo off
echo Stopping all services...
taskkill /F /IM "node.exe" 2>nul
taskkill /F /FI "WINDOWTITLE eq Backend API*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Frontend App*" 2>nul
docker compose -f "$InstallPath\docker-compose.yml" down
echo.
echo All services stopped.
pause
"@
Set-Content -Path "$InstallPath\stop-all.bat" -Value $stopScript

# Create seed-data.bat wrapper
$seedScript = @"
@echo off
echo Running seed data script...
powershell -ExecutionPolicy Bypass -File "$InstallPath\seed-data.ps1"
pause
"@
Set-Content -Path "$InstallPath\seed-data.bat" -Value $seedScript

Write-Success "Start scripts created"

Set-Location $InstallPath

#-------------------------------------------------------------------------------
# Display Success Message
#-------------------------------------------------------------------------------
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "         Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Project Location:" -ForegroundColor Cyan
Write-Host "    $InstallPath" -ForegroundColor White
Write-Host "    (on your Desktop)" -ForegroundColor Gray
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Yellow
Write-Host "    Double-click 'start-all.bat' in the project folder" -ForegroundColor White
Write-Host ""
Write-Host "Access URLs (after starting):" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------"
Write-Host "| Frontend App        | http://localhost:5173              |" -ForegroundColor White
Write-Host "| Backend API         | http://localhost:8001              |" -ForegroundColor White
Write-Host "| API Documentation   | http://localhost:8001/docs         |" -ForegroundColor White
Write-Host "| phpMyAdmin          | http://localhost:8080              |" -ForegroundColor White
Write-Host "| Mongo Express       | http://localhost:8081              |" -ForegroundColor White
Write-Host "----------------------------------------------------------------"
Write-Host ""
Write-Host "How to Use:" -ForegroundColor Yellow
Write-Host "  1. Run start-all.bat (on Desktop in real-estate-system folder)"
Write-Host "  2. Open http://localhost:5173 in your browser"
Write-Host "  3. Click 'Register here' to create an account"
Write-Host "  4. Choose a role: Buyer, Seller, Agent, or Lawyer"
Write-Host "  5. Login and explore the system!"
Write-Host ""
Write-Host "Seed Test Data:" -ForegroundColor Yellow
Write-Host "  Run: seed-data.bat"
Write-Host "  Creates 12 test accounts (2 per role) with password: test123"
Write-Host ""
Write-Host "Default Database Credentials:" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------"
Write-Host "| MySQL:    user: reuser / pass: repassword                   |" -ForegroundColor White
Write-Host "| MongoDB:  No authentication (development mode)              |" -ForegroundColor White
Write-Host "----------------------------------------------------------------"
Write-Host ""
Write-Host "Would you like to start the application now? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Starting application..." -ForegroundColor Green
    Start-Process -FilePath "$InstallPath\start-all.bat"
    Write-Host ""
    Write-Host "Opening browser in 10 seconds..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    Start-Process "http://localhost:5173"
}

Write-Host ""
Write-Host "Happy coding!" -ForegroundColor Green
Write-Host ""
