# Production-Style Demo Setup Script
# This script sets up trusted SSL and removes port numbers for a professional demo

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Nebula Cost Optimizer - Demo Setup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] This script requires Administrator privileges for some steps." -ForegroundColor Yellow
    Write-Host "          Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host "[OK] Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Step 1: Check if mkcert is installed
Write-Host "Step 1: Checking for mkcert..." -ForegroundColor Cyan
$mkcertInstalled = Get-Command mkcert -ErrorAction SilentlyContinue

if (-not $mkcertInstalled) {
    Write-Host "[ERROR] mkcert not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install mkcert first:" -ForegroundColor Yellow
    Write-Host "  Option 1 (Chocolatey): choco install mkcert" -ForegroundColor White
    Write-Host "  Option 2 (Scoop): scoop install mkcert" -ForegroundColor White
    Write-Host "  Option 3 (Manual): Download from https://github.com/FiloSottile/mkcert/releases" -ForegroundColor White
    Write-Host ""
    Write-Host "After installing mkcert, run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host "[OK] mkcert is installed" -ForegroundColor Green
Write-Host ""

# Step 2: Install local CA
Write-Host "Step 2: Installing local Certificate Authority..." -ForegroundColor Cyan
try {
    mkcert -install 2>&1 | Out-Null
    Write-Host "[OK] Local CA installed" -ForegroundColor Green
}
catch {
    Write-Host "[WARNING] CA installation may have already been done" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Generate certificates
Write-Host "Step 3: Generating SSL certificates..." -ForegroundColor Cyan
$frontendPath = Join-Path $PSScriptRoot "frontend"
$certsPath = Join-Path $frontendPath "certs"

if (-not (Test-Path $certsPath)) {
    New-Item -ItemType Directory -Path $certsPath | Out-Null
    Write-Host "[OK] Created certs directory" -ForegroundColor Green
}

Push-Location $frontendPath

$certFile = Join-Path $certsPath "cert.pem"
$keyFile = Join-Path $certsPath "key.pem"

if (Test-Path $certFile) {
    Write-Host "[WARNING] Certificates already exist. Regenerating..." -ForegroundColor Yellow
    Remove-Item $certFile -Force
    Remove-Item $keyFile -Force
}

mkcert -key-file "certs\key.pem" -cert-file "certs\cert.pem" nebula-cost-optimizer.com localhost 127.0.0.1 ::1 2>&1 | Out-Null

Pop-Location

if (Test-Path $certFile) {
    Write-Host "[OK] SSL certificates generated successfully" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Failed to generate certificates" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}
Write-Host ""

# Step 4: Update Vite configuration
Write-Host "Step 4: Updating Vite configuration..." -ForegroundColor Cyan
$viteConfigPath = Join-Path $frontendPath "vite.config.js"
$trustedConfigPath = Join-Path $frontendPath "vite.config.trusted-ssl.js"

if (Test-Path $trustedConfigPath) {
    Copy-Item $trustedConfigPath $viteConfigPath -Force
    Write-Host "[OK] Vite configuration updated to use trusted certificates" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Trusted SSL config template not found, keeping current config" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Setup port forwarding
Write-Host "Step 5: Setting up port forwarding (443 -> 5173)..." -ForegroundColor Cyan

# Check if port forwarding already exists
$existingRule = netsh interface portproxy show all | Select-String "443.*127.0.0.1.*5173"

if ($existingRule) {
    Write-Host "[WARNING] Port forwarding rule already exists. Removing old rule..." -ForegroundColor Yellow
    netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1 | Out-Null
}

netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Port forwarding configured (443 -> 5173)" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Failed to setup port forwarding" -ForegroundColor Red
}
Write-Host ""

# Step 6: Check hosts file
Write-Host "Step 6: Checking hosts file..." -ForegroundColor Cyan
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$hostsContent = Get-Content $hostsPath -Raw

if ($hostsContent -match "127\.0\.0\.1\s+nebula-cost-optimizer\.com") {
    Write-Host "[OK] Hosts file already configured" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Domain not found in hosts file" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please add this line to your hosts file:" -ForegroundColor Yellow
    Write-Host "  127.0.0.1    nebula-cost-optimizer.com" -ForegroundColor White
    Write-Host ""

    $addToHosts = Read-Host "Would you like me to add it now? (Y/N)"
    if ($addToHosts -eq "Y" -or $addToHosts -eq "y") {
        Add-Content -Path $hostsPath -Value "`n127.0.0.1    nebula-cost-optimizer.com"
        Write-Host "[OK] Domain added to hosts file" -ForegroundColor Green
    }
}
Write-Host ""

# Summary
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start the backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access your app at:" -ForegroundColor White
Write-Host "   https://nebula-cost-optimizer.com" -ForegroundColor Green
Write-Host "   (No port, No warning!)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: Raj@777037" -ForegroundColor White
Write-Host ""
Write-Host "To remove port forwarding later:" -ForegroundColor Yellow
Write-Host "  netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
