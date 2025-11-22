#!/usr/bin/env python3
"""
Simple HTTP server for MiniPupper web joystick interface
Run this script to serve the web interface on your local network
"""

import http.server
import socketserver
import socket
import os
from pathlib import Path

PORT = 8000

# Change to web_joystick directory
web_dir = Path(__file__).parent / "web_joystick"
os.chdir(web_dir)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for security
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[Web] {self.address_string()} - {format % args}")


def get_local_ip():
    """Get the local IP address"""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"


if __name__ == "__main__":
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("MiniPupper Web Joystick Server")
    print("="*60)
    print(f"\nServing at:")
    print(f"  Local:   http://localhost:{PORT}")
    print(f"  Network: http://{local_ip}:{PORT}")
    print("\nAccess from your mobile device:")
    print(f"  1. Connect to the same WiFi network")
    print(f"  2. Open browser and go to: http://{local_ip}:{PORT}")
    print(f"  3. Click 'Connect via Bluetooth'")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        print("Try a different port with: python3 serve_web_joystick.py")
