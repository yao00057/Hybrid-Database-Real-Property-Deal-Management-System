#!/bin/bash

#===============================================================================
# Seed Test Data Script - Creates test users for all roles
# Run this after deployment to populate the database with test data
#===============================================================================

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

API_URL="http://localhost:8001/api"

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}  Seeding Test Data - Creating Users for All Roles${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s "$API_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Backend not responding. Please ensure the backend is running.${NC}"
        exit 1
    fi
    sleep 1
done

echo ""
echo -e "${YELLOW}Creating test users...${NC}"
echo ""

# Function to create a user
create_user() {
    local email=$1
    local name=$2
    local role=$3
    local phone=$4

    response=$(curl -s -X POST "$API_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$email\",
            \"password\": \"test123\",
            \"name\": \"$name\",
            \"role\": \"$role\",
            \"phone\": \"$phone\"
        }")

    if echo "$response" | grep -q "id"; then
        echo -e "${GREEN}  ✓ Created: $name ($role) - $email${NC}"
    elif echo "$response" | grep -q "already registered"; then
        echo -e "${YELLOW}  ⚠ Already exists: $email${NC}"
    else
        echo -e "${RED}  ✗ Failed: $email - $response${NC}"
    fi
}

# Create users for each role
echo -e "${BLUE}Creating Buyers:${NC}"
create_user "buyer1@test.com" "John Buyer" "buyer" "555-0101"
create_user "buyer2@test.com" "Jane Purchaser" "buyer" "555-0102"

echo ""
echo -e "${BLUE}Creating Sellers:${NC}"
create_user "seller1@test.com" "Mike Seller" "seller" "555-0201"
create_user "seller2@test.com" "Sarah Owner" "seller" "555-0202"

echo ""
echo -e "${BLUE}Creating Buyer Agents:${NC}"
create_user "buyeragent1@test.com" "Tom Agent" "buyer_agent" "555-0301"
create_user "buyeragent2@test.com" "Lisa Realtor" "buyer_agent" "555-0302"

echo ""
echo -e "${BLUE}Creating Seller Agents:${NC}"
create_user "selleragent1@test.com" "Bob Broker" "seller_agent" "555-0401"
create_user "selleragent2@test.com" "Amy Agent" "seller_agent" "555-0402"

echo ""
echo -e "${BLUE}Creating Buyer Lawyers:${NC}"
create_user "buyerlawyer1@test.com" "David Attorney" "buyer_lawyer" "555-0501"
create_user "buyerlawyer2@test.com" "Emma Counsel" "buyer_lawyer" "555-0502"

echo ""
echo -e "${BLUE}Creating Seller Lawyers:${NC}"
create_user "sellerlawyer1@test.com" "Chris Legal" "seller_lawyer" "555-0601"
create_user "sellerlawyer2@test.com" "Kate Lawyer" "seller_lawyer" "555-0602"

echo ""
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}  Test Data Seeding Complete!${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo -e "${BLUE}Test Accounts Created:${NC}"
echo "----------------------------------------------------------------"
echo "| Role          | Email                  | Password  |"
echo "----------------------------------------------------------------"
echo "| Buyer         | buyer1@test.com        | test123   |"
echo "| Buyer         | buyer2@test.com        | test123   |"
echo "| Seller        | seller1@test.com       | test123   |"
echo "| Seller        | seller2@test.com       | test123   |"
echo "| Buyer Agent   | buyeragent1@test.com   | test123   |"
echo "| Buyer Agent   | buyeragent2@test.com   | test123   |"
echo "| Seller Agent  | selleragent1@test.com  | test123   |"
echo "| Seller Agent  | selleragent2@test.com  | test123   |"
echo "| Buyer Lawyer  | buyerlawyer1@test.com  | test123   |"
echo "| Buyer Lawyer  | buyerlawyer2@test.com  | test123   |"
echo "| Seller Lawyer | sellerlawyer1@test.com | test123   |"
echo "| Seller Lawyer | sellerlawyer2@test.com | test123   |"
echo "----------------------------------------------------------------"
echo ""
echo -e "${BLUE}You can now login with any of these accounts to test!${NC}"
echo ""
