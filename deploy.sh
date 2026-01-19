#!/bin/bash

#===============================================================================
# Real Property Deal Management System - One-Key Deployment Script
# For Ubuntu 22.04 LTS
#===============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}  Real Property Deal Management System - Deployment Script${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

#-------------------------------------------------------------------------------
# Step 1: Update system
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

#-------------------------------------------------------------------------------
# Step 2: Install Docker
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[2/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    sudo apt-get install -y -qq ca-certificates curl gnupg lsb-release
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
    echo -e "${GREEN}   Docker installed successfully${NC}"
    echo -e "${YELLOW}   NOTE: You may need to log out and back in for Docker permissions${NC}"
else
    echo -e "${GREEN}   Docker already installed${NC}"
fi

#-------------------------------------------------------------------------------
# Step 3: Install Node.js
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[3/8] Installing Node.js 20.x...${NC}"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>/dev/null
    sudo apt-get install -y -qq nodejs
    echo -e "${GREEN}   Node.js $(node --version) installed${NC}"
else
    echo -e "${GREEN}   Node.js $(node --version) already installed${NC}"
fi

#-------------------------------------------------------------------------------
# Step 4: Install Python
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[4/8] Installing Python 3 and pip...${NC}"
sudo apt-get install -y -qq python3 python3-pip python3-venv
echo -e "${GREEN}   Python $(python3 --version) installed${NC}"

#-------------------------------------------------------------------------------
# Step 5: Setup project directory
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[5/8] Setting up project directory...${NC}"
PROJECT_DIR="$HOME/real-estate-system"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}   Project directory exists, pulling latest changes...${NC}"
    cd "$PROJECT_DIR"
    git pull origin main 2>/dev/null || true
else
    echo -e "${YELLOW}   Cloning repository...${NC}"
    git clone https://github.com/yao00057/Hybrid-Database-Real-Property-Deal-Management-System.git "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}   Project directory: $PROJECT_DIR${NC}"

#-------------------------------------------------------------------------------
# Step 6: Start Docker services
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[6/8] Starting Docker services (MongoDB, MySQL, Redis)...${NC}"

# Stop existing containers first
docker compose down 2>/dev/null || sudo docker compose down 2>/dev/null || true

# Start containers - use sudo for first run if user hasn't logged out/in after docker group add
if groups $USER | grep -q docker; then
    docker compose up -d 2>/dev/null || sudo docker compose up -d
else
    sudo docker compose up -d
fi

# Wait for databases to be ready
echo -e "   Waiting for databases to initialize (15 seconds)..."
sleep 15

# Setup MySQL user
echo -e "   Configuring MySQL user..."
sudo docker exec re_mysql mysql -u root -prootpassword -e "CREATE DATABASE IF NOT EXISTS real_estate_financial; DROP USER IF EXISTS 'real_estate_user'@'%'; CREATE USER 'real_estate_user'@'%' IDENTIFIED WITH mysql_native_password BY 'real_estate_pass'; GRANT ALL PRIVILEGES ON real_estate_financial.* TO 'real_estate_user'@'%'; FLUSH PRIVILEGES;" 2>/dev/null || true

echo -e "${GREEN}   Docker services started${NC}"

#-------------------------------------------------------------------------------
# Step 7: Setup Backend
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[7/8] Setting up Python backend...${NC}"
cd "$PROJECT_DIR"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Install dependencies
source venv/bin/activate
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q

# Stop existing backend
pkill -f "uvicorn main:app.*8001" 2>/dev/null || true
sleep 2

# Start backend
cd backend
nohup "$PROJECT_DIR/venv/bin/uvicorn" main:app --host 0.0.0.0 --port 8001 --reload > "$HOME/backend.log" 2>&1 &
cd "$PROJECT_DIR"

echo -e "${GREEN}   Backend started on port 8001${NC}"

#-------------------------------------------------------------------------------
# Step 8: Setup Frontend
#-------------------------------------------------------------------------------
echo -e "${YELLOW}[8/8] Setting up Vue.js frontend...${NC}"
cd "$PROJECT_DIR/frontend"

# Install npm dependencies
npm install --silent 2>/dev/null

# Update API URL to use current server IP
sed -i "s|baseURL:.*|baseURL: 'http://$SERVER_IP:8001/api',|g" src/api/index.ts

# Update CORS in backend
sed -i "s|allow_origins=\[.*\]|allow_origins=[\"http://localhost:5173\", \"http://127.0.0.1:5173\", \"http://$SERVER_IP:5173\"]|g" "$PROJECT_DIR/backend/main.py"

# Stop existing frontend
pkill -f "vite.*5173" 2>/dev/null || true
sleep 2

# Start frontend with --host to allow external access
nohup npm run dev -- --host --port 5173 > "$HOME/frontend.log" 2>&1 &

echo -e "${GREEN}   Frontend started on port 5173${NC}"

# Wait for services to start
sleep 5

#-------------------------------------------------------------------------------
# Display access information
#-------------------------------------------------------------------------------
echo ""
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}         Deployment Completed Successfully!${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo "----------------------------------------------------------------"
printf "| %-20s | %-40s |\n" "Frontend App" "http://$SERVER_IP:5173"
printf "| %-20s | %-40s |\n" "Backend API" "http://$SERVER_IP:8001"
printf "| %-20s | %-40s |\n" "API Documentation" "http://$SERVER_IP:8001/docs"
printf "| %-20s | %-40s |\n" "phpMyAdmin" "http://$SERVER_IP:8080"
printf "| %-20s | %-40s |\n" "Mongo Express" "http://$SERVER_IP:8081"
echo "----------------------------------------------------------------"
echo ""
echo -e "${BLUE}Default Credentials:${NC}"
echo "----------------------------------------------------------------"
echo "| MySQL:    user: real_estate_user / pass: real_estate_pass   |"
echo "| MongoDB:  No authentication (development mode)              |"
echo "----------------------------------------------------------------"
echo ""
echo -e "${BLUE}How to Use:${NC}"
echo "  1. Open http://$SERVER_IP:5173 in your browser"
echo "  2. Click 'Register here' to create an account"
echo "  3. Choose a role: Buyer, Seller, Agent, or Lawyer"
echo "  4. Login with your email and password"
echo "  5. Explore the Dashboard, Properties, Deals, and Transactions"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View backend logs:   tail -f ~/backend.log"
echo "  View frontend logs:  tail -f ~/frontend.log"
echo "  Restart backend:     pkill -f uvicorn && cd ~/real-estate-system/backend && ~/real-estate-system/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 --reload &"
echo "  Restart frontend:    pkill -f vite && cd ~/real-estate-system/frontend && npm run dev -- --host --port 5173 &"
echo "  Stop all services:   docker compose down && pkill -f uvicorn && pkill -f vite"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
