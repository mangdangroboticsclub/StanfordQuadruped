# MiniPupper Web Joystick

Web-based controller for MiniPupper using Web Bluetooth API.

## Requirements

- Modern browser with Web Bluetooth support (Chrome, Edge, or Opera)
- For network access: HTTPS is required
- Python 3 or Node.js (to run a local server)

## Setup on Raspberry Pi

### 1. Generate SSL Certificate

Web Bluetooth API requires HTTPS for network access. Generate a self-signed certificate:

```bash
cd ~/StanfordQuadruped/web_joystick

# Using OpenSSL (recommended)
openssl req -new -x509 -keyout cert.pem -out cert.pem -days 365 -nodes -subj "/CN=MiniPupper-v2"

# Or using Python (requires cryptography package)
pip3 install cryptography
python3 -c "
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
import ipaddress

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'MiniPupper-v2')])
cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
    key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(
    datetime.utcnow()).not_valid_after(datetime.utcnow() + timedelta(days=365)).add_extension(
    x509.SubjectAlternativeName([x509.DNSName('localhost'), x509.IPAddress(ipaddress.IPv4Address('127.0.0.1'))]),
    critical=False).sign(key, hashes.SHA256())
with open('cert.pem', 'wb') as f:
    f.write(key.private_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()))
    f.write(cert.public_bytes(serialization.Encoding.PEM))
print('Certificate generated: cert.pem')
"
```

### 2. Start HTTPS Server

**Using Python:**
```bash
python3 -m http.server 8443 --bind 0.0.0.0
# Note: Python's http.server doesn't support HTTPS directly
# Use the simple HTTPS server below instead:

python3 -c "
import http.server, ssl
server_address = ('0.0.0.0', 8443)
httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile='cert.pem', server_side=True)
print('Server running on https://0.0.0.0:8443')
httpd.serve_forever()
"
```

**Using Node.js:**
```bash
# Install http-server globally (one time)
npm install -g http-server

# Start HTTPS server
http-server -S -C cert.pem -K cert.pem -p 8443 -a 0.0.0.0
```

### 3. Access from Your Device

Get your Raspberry Pi's IP address:
```bash
hostname -I
```

Then open your browser to: `https://<raspberry-pi-ip>:8443`

Example: `https://192.168.1.104:8443`

**Note**: You'll see a security warning for self-signed certificates - this is normal. Click "Advanced" and proceed.

## Development (Local Computer)

For development on your computer, use VS Code's Live Server extension:
1. Install "Live Server" extension in VS Code
2. Right-click `index.html` and select "Open with Live Server"
3. Access at the URL shown by Live Server

## Files

- `index.html` - Web controller UI
- `controller.js` - JavaScript for joystick and Bluetooth communication  
- `cert.pem` - SSL certificate (generated manually)

## Usage

1. Generate certificate and start server (see setup above)
2. Open the URL in your browser
3. Click "Connect via Bluetooth"
4. Select "Minipupper-v2" from the device list
5. Use the virtual joysticks and buttons to control your robot!

## Controls

- **Left Stick**: Forward/backward movement and left/right strafing
- **Right Stick**: Yaw (rotation) and pitch control
- **D-Pad**: Height adjustment (up/down) and roll (left/right)
- **R1 Button**: Toggle between Trot and Rest modes
- **Disconnect Button**: Safely disconnect from robot

## Future Features

The following controls are planned for future implementation:
- Hop mode (X button)
- Dance mode (Circle button)
- Shutdown command (Triangle button)
