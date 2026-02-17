# Custom Domain Setup for Nebula Cost Optimizer

This guide explains how to access the Azure Cost Optimizer application using the custom domain name: **https://nebula-cost-optimizer.com**

**Two Setup Options:**
1. **Basic Setup** - HTTPS with self-signed certificate (shows "Not secure" warning, includes port :5173)
2. **Production-Style Setup** - Trusted HTTPS with mkcert (green padlock, no port number) ⭐ Recommended for demos

**Note**: This is a demo configuration using a production-style domain name with HTTPS for demonstration purposes.

---

## 🚀 Quick Reference

### Automated Setup (Easiest)
```powershell
# Install mkcert first: choco install mkcert
# Then run as Administrator:
.\setup-production-demo.ps1
```

### Manual Commands
```powershell
# Generate certificates
cd frontend
mkcert -install
mkcert -key-file certs/key.pem -cert-file certs/cert.pem nebula-cost-optimizer.com localhost 127.0.0.1

# Setup port forwarding
netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1

# Start app
cd backend && python main.py  # Terminal 1
cd frontend && npm run dev     # Terminal 2

# Access: https://nebula-cost-optimizer.com
```

### Cleanup Commands
```powershell
# Remove port forwarding
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1

# Remove certificates
Remove-Item frontend/certs -Recurse -Force

# Uninstall CA (optional)
mkcert -uninstall
```

---

## 🎯 Production-Style Setup (Recommended for Demos)

This setup provides:
- ✅ **Green padlock** (trusted certificate, no "Not secure" warning)
- ✅ **No port number** (clean URL: `https://nebula-cost-optimizer.com`)
- ✅ **Production appearance** for stakeholder demos

### Quick Setup (3 Commands)

```powershell
# 1. Install mkcert (one-time)
choco install mkcert

# 2. Run the automated setup script as Administrator
cd C:\projects\generative-ai\genai-usecases\azure-cost-optimizer
.\setup-production-demo.ps1

# 3. Done! Access at: https://nebula-cost-optimizer.com
```

### Manual Production-Style Setup

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
Download from: https://github.com/FiloSottile/mkcert/releases

#### Step 2: Configure Windows Hosts File

1. Open Notepad as Administrator
2. Open: `C:\Windows\System32\drivers\etc\hosts`
3. Add: `127.0.0.1    nebula-cost-optimizer.com`
4. Save and close

#### Step 3: Install Local Certificate Authority

```powershell
# Run PowerShell as Administrator
mkcert -install
```

This installs a local CA that your browser automatically trusts!

#### Step 4: Generate SSL Certificates

```powershell
cd frontend
mkdir certs
mkcert -key-file certs/key.pem -cert-file certs/cert.pem nebula-cost-optimizer.com localhost 127.0.0.1
```

#### Step 5: Install Dependencies

```powershell
cd frontend
npm install
```

#### Step 6: Setup Port Forwarding (Remove :5173)

```powershell
# Run PowerShell as Administrator
netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1
```

To verify:
```powershell
netsh interface portproxy show all
```

To remove later:
```powershell
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1
```

#### Step 7: Start the Application

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

The console will show: `Using mkcert certificates for HTTPS`

#### Step 8: Access Your App

Open browser and navigate to:
```
https://nebula-cost-optimizer.com
```

✅ **Green padlock, no port, no warnings!**

---

## 📋 Basic Setup Instructions (With Warnings)

### 1. Configure Windows Hosts File

**Steps:**
1. Open Notepad as Administrator:
   - Press `Win + S` and type "Notepad"
   - Right-click on Notepad and select "Run as administrator"

2. Open the hosts file:
   - Click File → Open
   - Navigate to: `C:\Windows\System32\drivers\etc\`
   - Change file type filter to "All Files (*.*)"
   - Select and open the file named `hosts`

3. Add the following line at the end of the file:
   ```
   127.0.0.1    nebula-cost-optimizer.com
   ```

4. Save the file (Ctrl + S) and close Notepad

### 2. Verify DNS Configuration

Open Command Prompt and test the DNS resolution:

```bash
ping nebula-cost-optimizer.com
```

You should see responses from `127.0.0.1`

### 3. Install HTTPS Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

This will install `@vitejs/plugin-basic-ssl` which provides automatic HTTPS support.

### 4. Start the Application

**Backend:**
```bash
cd backend
python main.py
```
Backend will run on: `http://localhost:8000`

**Frontend (with HTTPS):**
```bash
cd frontend
npm run dev
```
Frontend will run on: `https://localhost:5173` (with auto-generated SSL certificate)

### 5. Access the Application

Open your browser and navigate to:

**Using Custom Domain with HTTPS (Production-style for Demo):**
```
https://nebula-cost-optimizer.com:5173
```

**Using localhost with HTTPS:**
```
https://localhost:5173
```

**⚠️ Security Warning (Expected):**
Your browser will show a security warning because we're using a self-signed certificate.
This is normal for local development. To proceed:

1. Click **"Advanced"** or **"Show Details"**
2. Click **"Proceed to nebula-cost-optimizer.com"** (or similar option)
3. The warning appears only once per browser session

**Alternative HTTP access (without SSL):**
If you prefer to skip HTTPS, you can still access via:
```
http://localhost:5173
```
(After disabling HTTPS in vite.config.js)

## Login Credentials

- **Username**: admin
- **Password**: Raj@777037

## 🆚 Setup Comparison

| Feature | Basic Setup | Production-Style Setup ⭐ |
|---------|------------|--------------------------|
| **URL** | `https://nebula-cost-optimizer.com:5173` | `https://nebula-cost-optimizer.com` |
| **Certificate** | Self-signed (basicSsl) | Trusted (mkcert) |
| **Browser Warning** | ❌ "Not secure" warning | ✅ Green padlock |
| **Port Number** | `:5173` visible | Clean URL |
| **Setup Time** | 2 minutes | 5 minutes |
| **Best For** | Quick testing | Demos & presentations |
| **Requirements** | npm install | mkcert + port forwarding |

**Recommendation:** Use Production-Style Setup for all stakeholder demos and presentations!

## Configuration Files

### Frontend Configuration
- File: `frontend/.env`
- Contains application name and domain settings

### Vite Configuration
- File: `frontend/vite.config.js`
- **Automatically detects** mkcert certificates in `frontend/certs/`
- Falls back to basicSsl if mkcert certs not found
- Updated to accept connections from custom domain

**How it works:**
1. Checks for `certs/cert.pem` and `certs/key.pem`
2. If found → Uses trusted certificates (green padlock!)
3. If not found → Uses basicSsl (shows warning)

### Backend CORS
- File: `backend/main.py`
- Already configured to accept requests from all origins

## Troubleshooting

### Issue: Cannot access custom domain

**Solution:**
1. Verify the hosts file entry is correct
2. Clear browser cache
3. Try accessing in incognito/private mode
4. Restart your browser

### Issue: SSL/HTTPS certificate warning persists

**Solution:**
1. This is expected with self-signed certificates
2. Click "Advanced" → "Proceed" in your browser
3. For Chrome: Type `thisisunsafe` while on the warning page
4. For a cleaner solution, install [mkcert](https://github.com/FiloSottile/mkcert) for trusted local certificates

### Issue: "Your connection is not private" or "NET::ERR_CERT_AUTHORITY_INVALID"

**Solution:**
This is normal for self-signed certificates. To proceed:
- **Chrome/Edge**: Click "Advanced" → "Proceed to nebula-cost-optimizer.com (unsafe)"
- **Firefox**: Click "Advanced" → "Accept the Risk and Continue"
- **Safari**: Click "Show Details" → "visit this website"

### Issue: API calls failing

**Solution:**
1. Ensure backend is running on port 8000
2. Check backend console for errors
3. Verify CORS settings in `backend/main.py`
4. Mixed content warning: Backend is HTTP while frontend is HTTPS (this is okay for local dev)

### Issue: "ERR_NAME_NOT_RESOLVED"

**Solution:**
1. Verify you edited the hosts file as administrator
2. Ensure the hosts file was saved correctly
3. Flush DNS cache:
   ```bash
   ipconfig /flushdns
   ```

### Issue: npm install fails or package not found

**Solution:**
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Ensure you're in the `frontend` directory

### Issue: Still seeing "Not secure" warning with mkcert

**Solution:**
1. Verify certificates were generated:
   ```powershell
   ls frontend/certs/
   # Should show: cert.pem and key.pem
   ```
2. Run `mkcert -install` again as Administrator
3. Restart your browser completely (close all windows)
4. Clear browser SSL state:
   - Chrome: Settings → Privacy → Security → Manage certificates → Clear SSL state
   - Edge: Settings → Privacy → Clear browsing data → Cached images and files
5. Check Vite console output - should say "Using mkcert certificates for HTTPS"

### Issue: mkcert command not found

**Solution:**
1. If using Chocolatey: `choco install mkcert`
2. If using Scoop: `scoop install mkcert`
3. Restart PowerShell after installation
4. Verify: `mkcert -version`

### Issue: Port forwarding not working

**Solution:**
1. Verify rule exists:
   ```powershell
   netsh interface portproxy show all
   ```
2. Remove and re-add:
   ```powershell
   netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1
   netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1
   ```
3. Check if another service is using port 443:
   ```powershell
   netstat -ano | findstr :443
   ```
4. If IIS is running: `iisreset /stop`

### Issue: Vite says "using basicSsl" instead of mkcert

**Solution:**
1. Check certificate files exist in `frontend/certs/`
2. Verify file names are exactly: `cert.pem` and `key.pem`
3. Regenerate certificates if needed
4. Restart Vite dev server

## Alternative Domain Names

If you prefer a different domain name, you can use any of these production-style options:

- `nebula-cost-optimizer.com` ⭐ (Current - Most professional)
- `nebula-ai.io` (Modern tech)
- `nebulaoptimizer.cloud` (Cloud-focused)
- `azure-nebula.ai` (AI-focused)
- `nebula.app` (Clean and simple)
- `costoptimizer.dev` (Developer-friendly)

Simply replace `nebula-cost-optimizer.com` with your preferred name in:
1. Windows hosts file
2. `frontend/.env` file (optional)

## Production Deployment

For production deployment with a real domain:

1. Purchase a domain name (e.g., from GoDaddy, Namecheap, etc.)
2. Configure DNS A record to point to your server IP
3. Update backend CORS settings to allow your specific domain
4. Set up SSL/TLS certificates (Let's Encrypt recommended)
5. Configure environment variables for production

## Notes

- **Demo Purpose**: These domains are configured locally and look like production domains for demonstration
- Custom DNS name works only on the machine where hosts file is configured
- For network-wide custom domain, set up a local DNS server
- This setup creates a professional appearance for demos and presentations
- **Important**: These domains are NOT registered - they only work on your local machine via hosts file
- For actual production deployment, you would need to register and configure the domain properly
