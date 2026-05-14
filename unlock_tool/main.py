#!/usr/bin/env python3
"""
eTool v2.2.0 - Mobile Device Unlock Tool
Command-line tool for device servicing operations.

This is a functional CLI tool with optional web UI for interactive use.
"""

import sys
import os
import threading
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.device_detector import DeviceDetector
from core.logger import setup_logger
from core.adb_interface import ADBInterface
from core.fastboot_interface import FastbootInterface
from core.access_request import request_access

# Setup logging
logger = setup_logger("etool")
API_HOST = "127.0.0.1"
API_PORT = 5000


def start_api_server(host: str = API_HOST, port: int = API_PORT):
    try:
        from backend import run_api_server
        logger.info(f"Starting backend API server on http://{host}:{port}")
        run_api_server(host=host, port=port)
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)

def list_devices():
    """List all connected devices"""
    logger.info("Listing connected devices...")
    detector = DeviceDetector(logger)
    
    adb_interface = ADBInterface(logger)
    if adb_interface.adb_path:
        adb_devices = adb_interface.get_devices()
        if adb_devices:
            logger.info("ADB Devices:")
            for device in adb_devices:
                logger.info(f"  - {device['serial']} ({device['state']})")
    
    fastboot_interface = FastbootInterface(logger)
    if fastboot_interface.fastboot_path:
        fastboot_devices = fastboot_interface.get_devices()
        if fastboot_devices:
            logger.info("Fastboot Devices:")
            for device in fastboot_devices:
                logger.info(f"  - {device['serial']} ({device['state']})")

def get_device_info(serial):
    """Get detailed device information"""
    logger.info(f"Getting device info for {serial}...")
    adb = ADBInterface(logger)
    result = adb.run_command(['shell', 'getprop'], device=serial, timeout=10)
    
    if result[0] == 0:
        logger.info("Device Properties:")
        for line in result[1].splitlines()[:10]:  # Show first 10 properties
            if ': [' in line:
                logger.info(f"  {line}")
    else:
        logger.error(f"Failed to get device info: {result[1]}")

def start_web_ui():
    """Start the standalone web UI server (backend + frontend)."""
    logger.info("Starting eTool v2.2.0 standalone web interface...")
    logger.info(f"Web UI: http://localhost:{API_PORT}")
    logger.info(f"Backend API: http://localhost:{API_PORT}/api")
    logger.info("Opening browser automatically...")

    try:
        import webbrowser
        import threading
        import time

        # Start the backend server in a thread
        api_thread = threading.Thread(target=start_api_server, daemon=True)
        api_thread.start()

        # Give the server a moment to start
        time.sleep(1)

        # Open the browser
        webbrowser.open(f"http://localhost:{API_PORT}")

        logger.info("eTool web interface is now running!")
        logger.info("Press Ctrl+C to stop the server")

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Web UI stopped by user")

    except Exception as e:
        logger.error(f"Failed to start web UI: {e}")
        sys.exit(1)

def start_gui():
    """Start the native GUI."""
    try:
        from gui_main import main as gui_main
        logger.info("Starting native GUI...")
        gui_main()
    except ImportError as e:
        logger.error(f"GUI dependencies not available: {e}")
        logger.info("Install PyQt6: pip install PyQt6")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start GUI: {e}")
        sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="eTool v2.2.0 - Mobile Device Unlock Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Device Operations:
  %(prog)s detect              # Detect connected devices
  %(prog)s list                # List all devices
  %(prog)s info <serial>       # Get device information
  
Interfaces:
  %(prog)s gui                 # Start native GUI
  %(prog)s ui                  # Start web UI server
  
Examples:
  %(prog)s detect              # Auto-detect device
  %(prog)s list                # Show connected devices
  %(prog)s info emulator-5554  # Get device details
  %(prog)s gui                 # Launch native GUI
  %(prog)s ui                  # Launch web interface
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Device detection
    detect_parser = subparsers.add_parser('detect', help='Detect connected devices')
    
    # List devices
    list_parser = subparsers.add_parser('list', help='List all connected devices')
    
    # Device info
    info_parser = subparsers.add_parser('info', help='Get device information')
    info_parser.add_argument('serial', help='Device serial number')
    
    # API server
    api_parser = subparsers.add_parser('api', help='Start backend API server')

    # Web UI
    ui_parser = subparsers.add_parser('ui', help='Start web UI server')
    
    # GUI
    gui_parser = subparsers.add_parser('gui', help='Start native GUI')
    
    args = parser.parse_args()

    # Access approval gate
    if not request_access(logger):
        logger.error("Access not approved. Exiting.")
        sys.exit(1)

    # Execute command
    if args.command == 'detect':
        list_devices()
    elif args.command == 'list':
        list_devices()
    elif args.command == 'info':
        get_device_info(args.serial)
    elif args.command == 'api':
        start_api_server()
    elif args.command == 'ui':
        start_web_ui()
    elif args.command == 'gui':
        start_gui()
    else:
        # Default: detect devices
        list_devices()

if __name__ == "__main__":
    main()