import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Check if mkcert certificates exist
const certFile = path.resolve(__dirname, 'certs', 'cert.pem');
const keyFile = path.resolve(__dirname, 'certs', 'key.pem');

// Use mkcert certificates if they exist, otherwise use basicSsl
let httpsConfig = true;
if (fs.existsSync(certFile) && fs.existsSync(keyFile)) {
  httpsConfig = {
    key: fs.readFileSync(keyFile),
    cert: fs.readFileSync(certFile),
  };
  console.log('Using mkcert certificates for HTTPS');
} else {
  console.log('mkcert certificates not found, using basicSsl');
}

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow access from custom domain
    port: 5173,
    https: httpsConfig, // Use mkcert certificates or fallback to basicSsl
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false, // Allow self-signed certificates
      },
    },
  },
});