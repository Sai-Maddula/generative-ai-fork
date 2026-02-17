/**
 * Generate Self-Signed SSL Certificate for Development
 * This script creates SSL certificates for HTTPS support in local development
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const certsDir = path.join(__dirname, 'certs');

// Create certs directory if it doesn't exist
if (!fs.existsSync(certsDir)) {
  fs.mkdirSync(certsDir);
  console.log('✓ Created certs directory');
}

const certPath = path.join(certsDir, 'cert.pem');
const keyPath = path.join(certsDir, 'key.pem');

// Check if certificates already exist
if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
  console.log('✓ SSL certificates already exist');
  console.log(`  Certificate: ${certPath}`);
  console.log(`  Key: ${keyPath}`);
  process.exit(0);
}

console.log('Generating self-signed SSL certificate...');

try {
  // Generate self-signed certificate using OpenSSL
  const command = `openssl req -x509 -newkey rsa:2048 -nodes -sha256 -days 365 ` +
    `-keyout "${keyPath}" -out "${certPath}" ` +
    `-subj "/C=US/ST=State/L=City/O=Nebula/CN=nebula-cost-optimizer.com" ` +
    `-addext "subjectAltName=DNS:nebula-cost-optimizer.com,DNS:*.nebula-cost-optimizer.com,DNS:localhost"`;

  execSync(command, { stdio: 'inherit' });

  console.log('\n✓ SSL certificates generated successfully!');
  console.log(`  Certificate: ${certPath}`);
  console.log(`  Key: ${keyPath}`);
  console.log('\n⚠ Note: This is a self-signed certificate for development only.');
  console.log('  Your browser will show a security warning - this is expected.');
  console.log('  Click "Advanced" and "Proceed" to continue.\n');
} catch (error) {
  console.error('\n✗ Error generating SSL certificates');
  console.error('  Make sure OpenSSL is installed on your system.');
  console.error('\nAlternative: Install mkcert for better local HTTPS support:');
  console.error('  https://github.com/FiloSottile/mkcert\n');
  process.exit(1);
}
