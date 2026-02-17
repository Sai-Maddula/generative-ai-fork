import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';

// Check if mkcert certificates exist
const certsPath = path.resolve(__dirname, 'certs');
const certFile = path.join(certsPath, 'cert.pem');
const keyFile = path.join(certsPath, 'key.pem');

const httpsConfig = fs.existsSync(certFile) && fs.existsSync(keyFile)
  ? {
      key: fs.readFileSync(keyFile),
      cert: fs.readFileSync(certFile),
    }
  : true; // Fallback to basicSsl if mkcert certs don't exist

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow access from custom domain
    port: 5173,
    https: httpsConfig, // Use mkcert certificates or fallback
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false, // Allow self-signed certificates
      },
    },
  },
});
