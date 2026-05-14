#!/usr/bin/env python3
import os
import sys
import json
import threading
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from core.logger import setup_logger
from core.device_detector import DeviceDetector

logger = setup_logger("etool-api")

# Determine the folder for static UI assets.
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent

DIST_DIR = BASE_DIR
logger.info(f"Serving files from: {DIST_DIR}")


class EToolRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for eTool web interface."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # API endpoints
        if path.startswith('/api/'):
            self.handle_api_request(path, parsed_path.query)
            return

        # Serve static files from dist directory
        if path == '/' or path == '':
            self.serve_file('index.html')
        elif path.startswith('/assets/') or path in ['/favicon.ico', '/robots.txt', '/placeholder.svg']:
            self.serve_file(path[1:])  # Remove leading slash
        else:
            # For SPA routing, serve index.html for any other path
            self.serve_file('index.html')

    def serve_file(self, filename):
        """Serve a file from the dist directory."""
        file_path = DIST_DIR / filename
        if file_path.exists():
            self.send_response(200)
            if filename.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif filename.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif filename.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif filename.endswith('.ico'):
                self.send_header('Content-type', 'image/x-icon')
            elif filename.endswith('.png'):
                self.send_header('Content-type', 'image/png')
            elif filename.endswith('.svg'):
                self.send_header('Content-type', 'image/svg+xml')
            else:
                self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()

            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, f"File not found: {filename}")

    def handle_api_request(self, path, query):
        """Handle API requests."""
        try:
            if path == '/api/health':
                self.send_json_response({'status': 'ok', 'version': '2.2.0'})
            elif path == '/api/devices':
                devices = self.get_devices()
                self.send_json_response(devices)
            elif path.startswith('/api/devices/'):
                serial = path.split('/api/devices/')[1]
                device_info = self.get_device_info(serial)
                if device_info:
                    self.send_json_response(device_info)
                else:
                    self.send_error(404, "Device not found")
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            logger.error(f"API error: {e}")
            self.send_error(500, str(e))

    def send_json_response(self, data):
        """Send a JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_devices(self):
        """Get all connected devices across all modes."""
        result = {
            "adb": [],
            "fastboot": [],
            "usb": [],       # EDL, MTK, Samsung Download, charging, MTP, etc.
            "ios": [],
        }

        # ADB devices (all states)
        try:
            from core.adb_interface import ADBInterface
            adb = ADBInterface(logger)
            raw = adb.get_devices()
            STATE_MODE = {
                'device': 'adb', 'recovery': 'recovery',
                'sideload': 'sideload', 'offline': 'charging',
                'unauthorized': 'unauthorized', 'bootloader': 'fastboot',
            }
            for d in raw:
                mode = STATE_MODE.get(d.get('state', ''), d.get('state', 'unknown'))
                result["adb"].append({"serial": d["serial"], "state": d["state"], "mode": mode})
        except Exception:
            logger.warning("ADB device scan failed")

        # Fastboot devices
        try:
            from core.fastboot_interface import FastbootInterface
            fb = FastbootInterface(logger)
            for d in fb.get_devices():
                result["fastboot"].append({"serial": d["serial"], "mode": "fastboot"})
        except Exception:
            logger.warning("Fastboot device scan failed")

        # USB-level detection (EDL, MTK, Samsung DL, charging, iOS, etc.)
        try:
            from core.usb_manager import USBScanner
            scanner = USBScanner(logger)
            for dev in scanner.list_devices():
                if not dev.protocol:
                    continue
                entry = {
                    "vendor_id": f"{dev.vendor_id:04x}",
                    "product_id": f"{dev.product_id:04x}",
                    "mode": dev.protocol,
                    "serial": dev.serial_number,
                    "manufacturer": dev.manufacturer,
                    "product": dev.product,
                }
                if dev.vendor_id == 0x05ac:  # Apple
                    result["ios"].append(entry)
                else:
                    result["usb"].append(entry)
        except Exception:
            logger.warning("USB device scan failed")

        return result

    def get_device_info(self, serial):
        """Get detailed device information."""
        try:
            from core.adb_interface import ADBInterface
            adb = ADBInterface(logger)
            devices = adb.get_devices()
            if any(device.get("serial") == serial for device in devices):
                success, output = adb.shell("getprop", device=serial, timeout=10)
                if success:
                    props = {}
                    for line in output.splitlines():
                        if ": [" in line and line.endswith("]"):
                            key = line.split(": [")[0].strip()
                            value = line.split(": [")[1].rsplit("]", 1)[0]
                            props[key] = value
                    return {"serial": serial, "platform": "android", "properties": props}
        except Exception:
            logger.error(f"Failed to get device info for {serial}")
        return None

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(format % args)


def run_api_server(host: str = "127.0.0.1", port: int = 5000):
    """Run the HTTP server."""
    with socketserver.TCPServer((host, port), EToolRequestHandler) as httpd:
        logger.info(f"Starting eTool web server on http://{host}:{port}")
        httpd.serve_forever()