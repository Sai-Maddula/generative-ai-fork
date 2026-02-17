# HTTPS Setup Guide for Nebula Cost Optimizer

This guide provides quick reference for setting up HTTPS for a production-style demo experience.

## 🔒 What's Included

- **Automatic SSL Certificate Generation** using `@vitejs/plugin-basic-ssl`
- **Self-Signed Certificate** for local development
- **HTTPS-enabled Vite Dev Server**
- **Production-style URL**: `https://nebula-cost-optimizer.com:5173`

## ⚡ Quick Setup (2 Minutes)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This installs the `@vitejs/plugin-basic-ssl` package.

### 2. Update Hosts File (Windows)

Open `C:\Windows\System32\drivers\etc\hosts` as Administrator and add:

```
127.0.0.1    nebula-cost-optimizer.com
```

### 3. Start the Application

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

### 4. Access the App

Open browser and navigate to:
```
https://nebula-cost-optimizer.com:5173
```

**First time:** Click "Advanced" → "Proceed" to bypass the security warning.

## 🎯 What Happens

1. Vite automatically generates a self-signed SSL certificate
2. Dev server starts with HTTPS enabled
3. Browser shows security warning (expected for self-signed certs)
4. After accepting the warning, your app looks like a real production site!

## 🔧 Configuration Files

### Vite Config ([frontend/vite.config.js](frontend/vite.config.js))

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import basicSsl from '@vitejs/plugin-basic-ssl';

export default defineConfig({
  plugins: [
    react(),
    basicSsl() // Enables HTTPS
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: true, // Enable HTTPS
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false, // Allow mixed content (HTTPS → HTTP)
      },
    },
  },
});
```

### Package.json Addition

```json
{
  "devDependencies": {
    "@vitejs/plugin-basic-ssl": "^1.1.0"
  }
}
```

## 🌐 Browser Security Warning

### Why Does This Happen?

- We're using a **self-signed certificate** (not issued by a trusted Certificate Authority)
- This is **normal and safe** for local development
- Production sites use certificates from Let's Encrypt, DigiCert, etc.

### How to Proceed

**Chrome/Edge:**
1. Click "Advanced"
2. Click "Proceed to nebula-cost-optimizer.com (unsafe)"
3. OR type `thisisunsafe` while on the warning page

**Firefox:**
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

**Safari:**
1. Click "Show Details"
2. Click "visit this website"

### One-Time Setup per Browser

Once you accept the certificate, you typically won't see the warning again until:
- You close and reopen the browser
- The certificate expires (default: 30 days)
- You clear browser data

## 🎨 For an Even Better Demo Experience

### Option 1: Use mkcert (Recommended for Frequent Demos)

[mkcert](https://github.com/FiloSottile/mkcert) creates locally-trusted certificates with no browser warnings.

**Installation (Windows):**
```bash
# Using Chocolatey
choco install mkcert

# Or download from: https://github.com/FiloSottile/mkcert/releases
```

**Setup:**
```bash
# Install local CA
mkcert -install

# Generate certificate
cd frontend
mkcert nebula-cost-optimizer.com localhost 127.0.0.1

# Update vite.config.js to use these certs
```

### Option 2: Add Exception in Browser

Most browsers allow you to permanently trust a specific certificate:
- Chrome: Settings → Privacy and security → Security → Manage certificates
- Firefox: Settings → Privacy & Security → Certificates → View Certificates

## 🔄 Switching Between HTTP and HTTPS

### Disable HTTPS (Use HTTP Only)

Edit `frontend/vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()], // Remove basicSsl()
  server: {
    host: '0.0.0.0',
    port: 5173,
    https: false, // Disable HTTPS
    // ... rest of config
  },
});
```

Then access via: `http://nebula-cost-optimizer.com:5173`

### Enable HTTPS Again

Add back the `basicSsl()` plugin and set `https: true`.

## 📊 Mixed Content (HTTPS Frontend + HTTP Backend)

### Current Setup

- **Frontend**: `https://nebula-cost-optimizer.com:5173` (HTTPS)
- **Backend**: `http://localhost:8000` (HTTP)

### Why This Works

The Vite proxy configuration has `secure: false`, which allows HTTPS frontend to communicate with HTTP backend.

### For Production

In production, both frontend and backend should use HTTPS:
- Frontend: `https://nebula-cost-optimizer.com`
- Backend: `https://api.nebula-cost-optimizer.com`

## 🎬 Demo Checklist

Before your demo:

- [ ] Hosts file updated with domain
- [ ] Dependencies installed (`npm install`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173 with HTTPS
- [ ] Browser certificate exception accepted
- [ ] Test login with credentials (admin / Raj@777037)
- [ ] Clear browser cache/cookies if needed

## 🆘 Common Issues

### "Module not found: @vitejs/plugin-basic-ssl"

**Solution:** Run `npm install` in the frontend directory

### Certificate expired

**Solution:**
- Auto-generated certificates expire after 30 days
- Restart the dev server to generate a new one
- Or use mkcert for longer-lived certificates

### "NET::ERR_CERT_COMMON_NAME_INVALID"

**Solution:**
- Ensure hosts file has the exact domain name
- Clear browser cache
- Restart browser

### Mixed content blocked

**Solution:**
- Our proxy config handles this automatically
- If blocked, check `vite.config.js` has `secure: false` in proxy settings

## 📚 Additional Resources

- [Vite HTTPS Documentation](https://vitejs.dev/config/server-options.html#server-https)
- [@vitejs/plugin-basic-ssl](https://github.com/vitejs/vite-plugin-basic-ssl)
- [mkcert - Trusted Local Certificates](https://github.com/FiloSottile/mkcert)
- [Self-Signed Certificates Explained](https://letsencrypt.org/docs/certificates-for-localhost/)

## 🎉 Result

Your application now runs with:
- ✅ Production-style domain name
- ✅ HTTPS encryption (with green padlock icon after accepting cert)
- ✅ Professional appearance for demos and screenshots
- ✅ No port 5173 shown in URL (if configured with reverse proxy)
- ✅ Looks like a real production deployment!

Perfect for impressing stakeholders during demos! 🚀
