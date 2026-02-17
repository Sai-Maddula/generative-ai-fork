# Setup Trusted SSL Certificate with mkcert

This guide shows how to remove the "Not secure" warning and port number for a production-like demo.

## Step 1: Install mkcert

### Option A: Using Chocolatey (Recommended)
```powershell
# Run PowerShell as Administrator
choco install mkcert
```

### Option B: Manual Installation
1. Download from: https://github.com/FiloSottile/mkcert/releases
2. Download `mkcert-v1.4.4-windows-amd64.exe`
3. Rename to `mkcert.exe`
4. Move to a folder in your PATH (e.g., `C:\Windows\System32\`)

### Option C: Using Scoop
```powershell
scoop bucket add extras
scoop install mkcert
```

## Step 2: Install Local CA

Run in PowerShell as Administrator:
```powershell
mkcert -install
```

This installs a local Certificate Authority that your browser trusts.

## Step 3: Generate Certificates

Navigate to your frontend directory:
```powershell
cd C:\projects\generative-ai\genai-usecases\azure-cost-optimizer\frontend

# Create certs directory
mkdir certs

# Generate certificate for your domain
mkcert -key-file certs/key.pem -cert-file certs/cert.pem nebula-cost-optimizer.com localhost 127.0.0.1 ::1
```

## Step 4: Update Vite Configuration

The vite.config.js needs to be updated to use the generated certificates instead of basicSsl.

## Step 5: Remove Port Number from URL

To access without `:5173`, you have two options:

### Option A: Run on Port 443 (Standard HTTPS)
Update vite config to use port 443, but requires running as Administrator.

### Option B: Use Windows Port Forwarding (Recommended)
Redirect port 443 to 5173 without admin privileges for the dev server.

```powershell
# Run PowerShell as Administrator
netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1
```

To remove port forwarding later:
```powershell
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1
```

To view current port forwarding rules:
```powershell
netsh interface portproxy show all
```

## Complete Setup Steps

1. **Install mkcert** (choose one method above)
2. **Install Local CA**: `mkcert -install`
3. **Generate Certificates**:
   ```powershell
   cd frontend
   mkdir certs
   mkcert -key-file certs/key.pem -cert-file certs/cert.pem nebula-cost-optimizer.com localhost 127.0.0.1
   ```
4. **Update vite.config.js** (see below)
5. **Setup Port Forwarding** (as Administrator):
   ```powershell
   netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1
   ```
6. **Update hosts file** (already done):
   ```
   127.0.0.1    nebula-cost-optimizer.com
   ```
7. **Start the app**: `npm run dev`
8. **Access**: `https://nebula-cost-optimizer.com` (no port, no warning!)

## Result

After this setup:
- ✅ Green padlock (secure connection)
- ✅ No "Not secure" warning
- ✅ No port number in URL
- ✅ URL: `https://nebula-cost-optimizer.com`

Perfect for professional demos! 🎉
