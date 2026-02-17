# Remove "Not Secure" Warning and Port Number

This guide shows how to achieve a production-perfect demo URL:
- ❌ `https://nebula-cost-optimizer.com:5173` with "Not secure" warning
- ✅ `https://nebula-cost-optimizer.com` with green padlock 🔒

## Quick Solution (Automated)

### Run the Setup Script (PowerShell as Administrator)

```powershell
cd C:\projects\generative-ai\genai-usecases\azure-cost-optimizer
.\setup-production-demo.ps1
```

This script will:
1. Check for mkcert installation
2. Install local Certificate Authority
3. Generate trusted SSL certificates
4. Update Vite configuration
5. Setup port forwarding (443 → 5173)
6. Verify hosts file

## Manual Solution (Step by Step)

### Part 1: Remove "Not Secure" Warning

#### Step 1: Install mkcert

**Option A - Using Chocolatey (Recommended):**
```powershell
# Run PowerShell as Administrator
choco install mkcert
```

**Option B - Using Scoop:**
```powershell
scoop bucket add extras
scoop install mkcert
```

**Option C - Manual Download:**
1. Go to: https://github.com/FiloSottile/mkcert/releases
2. Download: `mkcert-v1.4.4-windows-amd64.exe`
3. Rename to `mkcert.exe`
4. Move to `C:\Windows\System32\`

#### Step 2: Install Local Certificate Authority

```powershell
# Run PowerShell as Administrator
mkcert -install
```

This creates a local CA that your browser trusts automatically!

#### Step 3: Generate Certificates

```powershell
cd frontend
mkdir certs
mkcert -key-file certs/key.pem -cert-file certs/cert.pem nebula-cost-optimizer.com localhost 127.0.0.1
```

#### Step 4: Update Vite Config

Replace the content of `frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';

// Use mkcert certificates
const certFile = path.resolve(__dirname, 'certs/cert.pem');
const keyFile = path.resolve(__dirname, 'certs/key.pem');

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: {
      key: fs.readFileSync(keyFile),
      cert: fs.readFileSync(certFile),
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

### Part 2: Remove Port Number

#### Option A: Port Forwarding (Recommended)

Run PowerShell as Administrator:

```powershell
# Add port forwarding rule (443 → 5173)
netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1

# Verify the rule
netsh interface portproxy show all
```

Now you can access: `https://nebula-cost-optimizer.com` (no port!)

**To remove later:**
```powershell
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1
```

#### Option B: Run Vite on Port 443 (Requires Admin)

Update `vite.config.js`:
```javascript
server: {
  port: 443, // Standard HTTPS port
  // ... rest of config
}
```

Then start Vite with admin privileges:
```powershell
# Run as Administrator
npm run dev
```

## Complete Setup Checklist

- [ ] Install mkcert
- [ ] Run `mkcert -install`
- [ ] Generate certificates in `frontend/certs/`
- [ ] Update `vite.config.js` to use certificates
- [ ] Setup port forwarding (443 → 5173)
- [ ] Verify hosts file has: `127.0.0.1  nebula-cost-optimizer.com`
- [ ] Start backend: `python backend/main.py`
- [ ] Start frontend: `npm run dev` in frontend folder
- [ ] Access: `https://nebula-cost-optimizer.com`

## Results

### Before:
```
🔴 Not secure | https://nebula-cost-optimizer.com:5173
```
- Red warning badge
- Port number visible
- Browser security warnings

### After:
```
🔒 Secure | https://nebula-cost-optimizer.com
```
- ✅ Green padlock icon
- ✅ No port number
- ✅ No security warnings
- ✅ Looks like production!

## Troubleshooting

### Issue: mkcert command not found

**Solution:**
- Make sure you installed mkcert
- Restart PowerShell after installation
- Add mkcert location to PATH

### Issue: Port 443 already in use

**Solution:**
```powershell
# Check what's using port 443
netstat -ano | findstr :443

# Stop IIS if running
iisreset /stop

# Or use a different port (e.g., 8443) and access via https://nebula-cost-optimizer.com:8443
```

### Issue: Certificate still shows as untrusted

**Solution:**
1. Run `mkcert -install` again as Administrator
2. Restart your browser completely
3. Clear browser cache and SSL state
4. Verify certificates were generated in `frontend/certs/`

### Issue: Port forwarding not working

**Solution:**
```powershell
# Remove existing rule
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1

# Add rule again
netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1

# Restart network adapter or reboot PC
```

### Issue: "Module not found: fs"

**Solution:**
The `fs` module is built into Node.js. If you get this error, make sure you're using a recent version of Node.js (v16+).

## Clean Up

To remove all demo configurations:

```powershell
# Run as Administrator

# Remove port forwarding
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1

# Remove certificates
Remove-Item frontend/certs -Recurse -Force

# Uninstall local CA (optional)
mkcert -uninstall

# Remove from hosts file
# Edit C:\Windows\System32\drivers\etc\hosts and remove the line:
# 127.0.0.1    nebula-cost-optimizer.com
```

## Alternative: Simple Solution (Keep Port, Remove Warning Only)

If you're okay with keeping `:5173` and just want to remove the "Not secure" warning:

1. Install mkcert
2. Run `mkcert -install`
3. Generate certs
4. Update vite.config.js

Access at: `https://nebula-cost-optimizer.com:5173` ✅ (with green padlock, no warning)

## Demo Day Best Practices

Before your presentation:

1. ✅ Test the complete flow
2. ✅ Clear browser cache
3. ✅ Have backend and frontend running
4. ✅ Test login with credentials
5. ✅ Take screenshots of the green padlock
6. ✅ Prepare a backup plan (keep localhost access working)
7. ✅ Close unnecessary browser tabs
8. ✅ Use incognito mode for clean demo

## Perfect Demo URL

After setup, your stakeholders will see:

```
🔒 https://nebula-cost-optimizer.com
```

Clean, professional, and production-ready! 🚀
