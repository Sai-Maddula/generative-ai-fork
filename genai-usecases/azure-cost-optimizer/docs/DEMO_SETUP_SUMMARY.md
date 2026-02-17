# Demo Setup Summary - Nebula Cost Optimizer

## 🎯 Goal
Transform your local development URL into a production-style demo:
- **From**: `🔴 Not secure | https://nebula-cost-optimizer.com:5173`
- **To**: `🔒 https://nebula-cost-optimizer.com`

## ⚡ Quick Setup (3 Steps)

### 1. Install mkcert
```powershell
# Run PowerShell as Administrator
choco install mkcert
```

### 2. Run Automated Setup
```powershell
# As Administrator
cd C:\projects\generative-ai\genai-usecases\azure-cost-optimizer
.\setup-production-demo.ps1
```

### 3. Start & Access
```powershell
# Terminal 1
cd backend
python main.py

# Terminal 2
cd frontend
npm run dev

# Browser
# Open: https://nebula-cost-optimizer.com
```

## 📋 What Gets Configured

### Files Created/Modified:
- ✅ `frontend/certs/cert.pem` - Trusted SSL certificate
- ✅ `frontend/certs/key.pem` - Private key
- ✅ `frontend/vite.config.js` - Auto-detects mkcert certificates
- ✅ `C:\Windows\System32\drivers\etc\hosts` - Domain mapping
- ✅ Port forwarding rule (443 → 5173)

### System Changes:
- ✅ Local Certificate Authority installed (trusted by browser)
- ✅ Port forwarding: `443 → 5173`
- ✅ Hosts file entry: `127.0.0.1 nebula-cost-optimizer.com`

## 🔍 Verification Checklist

```powershell
# 1. Check mkcert installed
mkcert -version

# 2. Verify certificates exist
ls frontend/certs/
# Should show: cert.pem, key.pem

# 3. Check hosts file
cat C:\Windows\System32\drivers\etc\hosts | Select-String "nebula-cost-optimizer"
# Should show: 127.0.0.1    nebula-cost-optimizer.com

# 4. Verify port forwarding
netsh interface portproxy show all
# Should show: 443 → 5173 mapping

# 5. Test DNS resolution
ping nebula-cost-optimizer.com
# Should respond from 127.0.0.1
```

## 🎬 Demo Day Checklist

Before your presentation:

- [ ] Backend running (`python backend/main.py`)
- [ ] Frontend running (`npm run dev` in frontend/)
- [ ] Vite console shows: "Using mkcert certificates for HTTPS"
- [ ] Browser shows green padlock at `https://nebula-cost-optimizer.com`
- [ ] Test login: admin / Raj@777037
- [ ] Close unnecessary browser tabs
- [ ] Consider using incognito mode for clean demo
- [ ] Have backup: `https://nebula-cost-optimizer.com:5173` still works

## 🛠️ Troubleshooting Quick Fixes

### "Not secure" warning still showing?
```powershell
# Restart browser completely
# Clear SSL state (Chrome: Settings → Privacy → Security → Clear SSL state)
# Verify certificates: ls frontend/certs/
```

### Port number still visible?
```powershell
# Check port forwarding
netsh interface portproxy show all

# Re-add if missing
netsh interface portproxy add v4tov4 listenport=443 listenaddress=127.0.0.1 connectport=5173 connectaddress=127.0.0.1
```

### Certificate errors?
```powershell
# Reinstall CA
mkcert -install

# Regenerate certificates
cd frontend
Remove-Item certs -Recurse -Force
mkdir certs
mkcert -key-file certs/key.pem -cert-file certs/cert.pem nebula-cost-optimizer.com localhost 127.0.0.1
```

## 🧹 Cleanup (After Demo)

```powershell
# Run as Administrator

# Remove port forwarding
netsh interface portproxy delete v4tov4 listenport=443 listenaddress=127.0.0.1

# Optional: Remove certificates
Remove-Item frontend/certs -Recurse -Force

# Optional: Uninstall CA
mkcert -uninstall

# Optional: Remove from hosts file
# Edit C:\Windows\System32\drivers\etc\hosts
# Delete line: 127.0.0.1    nebula-cost-optimizer.com
```

## 📚 Full Documentation

- **[CUSTOM_DOMAIN_SETUP.md](CUSTOM_DOMAIN_SETUP.md)** - Complete setup guide
- **[REMOVE_WARNINGS_AND_PORT.md](REMOVE_WARNINGS_AND_PORT.md)** - Detailed SSL and port setup
- **[HTTPS_SETUP_GUIDE.md](HTTPS_SETUP_GUIDE.md)** - HTTPS deep dive
- **[setup-production-demo.ps1](setup-production-demo.ps1)** - Automated script

## 🎯 Expected Results

After setup:
```
Browser URL:    https://nebula-cost-optimizer.com
Status:         🔒 Secure
Certificate:    Trusted (mkcert)
Port:           Hidden (443 default)
Warning:        None
```

Perfect for stakeholder presentations! 🎉

## ⚙️ Technical Details

### How It Works:

1. **mkcert** creates a local Certificate Authority
2. CA is installed in Windows trusted root store
3. Certificates signed by this CA are automatically trusted
4. **Port forwarding** redirects HTTPS default port (443) to Vite (5173)
5. **Hosts file** maps domain name to localhost
6. **Vite** serves with trusted certificate
7. **Result**: Production-like HTTPS setup on localhost

### File Structure:
```
azure-cost-optimizer/
├── frontend/
│   ├── certs/
│   │   ├── cert.pem          # SSL certificate
│   │   └── key.pem           # Private key
│   ├── vite.config.js        # Auto-detects certs
│   └── .env                  # App configuration
├── backend/
│   └── main.py               # API server
└── setup-production-demo.ps1 # Automated setup
```

## 💡 Tips

- **Browser**: Chrome and Edge work best with mkcert
- **Firewall**: May need to allow port 443
- **Multiple Projects**: Reuse same mkcert installation
- **Expiration**: mkcert certificates valid for 2+ years
- **Network**: Works only on local machine (hosts file)
- **Team Demos**: Share setup script with team members

## 🔗 Useful Links

- [mkcert GitHub](https://github.com/FiloSottile/mkcert)
- [Vite HTTPS Docs](https://vitejs.dev/config/server-options.html#server-https)
- [Chocolatey](https://chocolatey.org/)
