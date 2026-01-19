#===============================================================================
# Seed Test Data Script - Creates test users for all roles
# Run this after deployment to populate the database with test data
#===============================================================================

$API_URL = "http://localhost:8001/api"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Blue
Write-Host "  Seeding Test Data - Creating Users for All Roles" -ForegroundColor Blue
Write-Host "================================================================" -ForegroundColor Blue
Write-Host ""

# Wait for backend to be ready
Write-Host "Waiting for backend to be ready..." -ForegroundColor Yellow
$ready = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $API_URL -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "Backend is ready!" -ForegroundColor Green
            $ready = $true
            break
        }
    } catch {
        # Continue waiting
    }
    Start-Sleep -Seconds 1
}

if (-not $ready) {
    Write-Host "Backend not responding. Please ensure the backend is running." -ForegroundColor Red
    Write-Host "Run start-all.bat first, then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Creating test users..." -ForegroundColor Yellow
Write-Host ""

# Function to create a user
function Create-User {
    param(
        [string]$Email,
        [string]$Name,
        [string]$Role,
        [string]$Phone
    )

    $body = @{
        email = $Email
        password = "test123"
        name = $Name
        role = $Role
        phone = $Phone
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "$API_URL/auth/register" -Method Post -ContentType "application/json" -Body $body -ErrorAction Stop
        Write-Host "  [OK] Created: $Name ($Role) - $Email" -ForegroundColor Green
    } catch {
        $errorMsg = $_.ErrorDetails.Message
        if ($errorMsg -match "already registered") {
            Write-Host "  [SKIP] Already exists: $Email" -ForegroundColor Yellow
        } else {
            Write-Host "  [FAIL] Failed: $Email - $errorMsg" -ForegroundColor Red
        }
    }
}

# Create users for each role
Write-Host "Creating Buyers:" -ForegroundColor Cyan
Create-User -Email "buyer1@test.com" -Name "John Buyer" -Role "buyer" -Phone "555-0101"
Create-User -Email "buyer2@test.com" -Name "Jane Purchaser" -Role "buyer" -Phone "555-0102"

Write-Host ""
Write-Host "Creating Sellers:" -ForegroundColor Cyan
Create-User -Email "seller1@test.com" -Name "Mike Seller" -Role "seller" -Phone "555-0201"
Create-User -Email "seller2@test.com" -Name "Sarah Owner" -Role "seller" -Phone "555-0202"

Write-Host ""
Write-Host "Creating Buyer Agents:" -ForegroundColor Cyan
Create-User -Email "buyeragent1@test.com" -Name "Tom Agent" -Role "buyer_agent" -Phone "555-0301"
Create-User -Email "buyeragent2@test.com" -Name "Lisa Realtor" -Role "buyer_agent" -Phone "555-0302"

Write-Host ""
Write-Host "Creating Seller Agents:" -ForegroundColor Cyan
Create-User -Email "selleragent1@test.com" -Name "Bob Broker" -Role "seller_agent" -Phone "555-0401"
Create-User -Email "selleragent2@test.com" -Name "Amy Agent" -Role "seller_agent" -Phone "555-0402"

Write-Host ""
Write-Host "Creating Buyer Lawyers:" -ForegroundColor Cyan
Create-User -Email "buyerlawyer1@test.com" -Name "David Attorney" -Role "buyer_lawyer" -Phone "555-0501"
Create-User -Email "buyerlawyer2@test.com" -Name "Emma Counsel" -Role "buyer_lawyer" -Phone "555-0502"

Write-Host ""
Write-Host "Creating Seller Lawyers:" -ForegroundColor Cyan
Create-User -Email "sellerlawyer1@test.com" -Name "Chris Legal" -Role "seller_lawyer" -Phone "555-0601"
Create-User -Email "sellerlawyer2@test.com" -Name "Kate Lawyer" -Role "seller_lawyer" -Phone "555-0602"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Test Data Seeding Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Test Accounts Created:" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------"
Write-Host "| Role          | Email                  | Password  |"
Write-Host "----------------------------------------------------------------"
Write-Host "| Buyer         | buyer1@test.com        | test123   |"
Write-Host "| Buyer         | buyer2@test.com        | test123   |"
Write-Host "| Seller        | seller1@test.com       | test123   |"
Write-Host "| Seller        | seller2@test.com       | test123   |"
Write-Host "| Buyer Agent   | buyeragent1@test.com   | test123   |"
Write-Host "| Buyer Agent   | buyeragent2@test.com   | test123   |"
Write-Host "| Seller Agent  | selleragent1@test.com  | test123   |"
Write-Host "| Seller Agent  | selleragent2@test.com  | test123   |"
Write-Host "| Buyer Lawyer  | buyerlawyer1@test.com  | test123   |"
Write-Host "| Buyer Lawyer  | buyerlawyer2@test.com  | test123   |"
Write-Host "| Seller Lawyer | sellerlawyer1@test.com | test123   |"
Write-Host "| Seller Lawyer | sellerlawyer2@test.com | test123   |"
Write-Host "----------------------------------------------------------------"
Write-Host ""
Write-Host "You can now login with any of these accounts to test!" -ForegroundColor Cyan
Write-Host ""
