#!/usr/bin/env python3
"""
Driver support report helper script.

This script scans connected USB devices and prints driver/connection guidance for
popular Android and iOS brands and modes.
"""

import argparse
import json
from pathlib import Path

from core.device_detector import DeviceDetector
from core.driver_manager import DriverManager


def format_report(report: dict) -> str:
    lines = []
    device_info = report.get('device_info', {})

    if report.get('status') == 'no_device':
        lines.append('No device detected.')
        lines.append('System summary:')
        lines.append(json.dumps(report.get('os', {}), indent=2) if isinstance(report.get('os'), dict) else str(report.get('os')))
        lines.append('Guidance:')
        lines.append(report.get('guidance', ''))
        return '\n'.join(lines)

    lines.append('Detected device:')
    for key in ('brand', 'mode', 'platform', 'vendor_id', 'product_id', 'serial'):
        if key in device_info:
            lines.append(f'  {key}: {device_info[key]}')
    lines.append('')
    lines.append('Available tools: ' + ', '.join(report.get('available_tools', [])))
    lines.append('')
    lines.append('Guidance:')
    lines.append(report.get('guidance', ''))
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate a driver support report for connected devices.')
    parser.add_argument('--json', action='store_true', help='Output the report in JSON format')
    parser.add_argument('--device', choices=['android', 'ios', 'all'], default='all', help='Filter by device platform')
    args = parser.parse_args()

    detector = DeviceDetector()
    manager = DriverManager()

    devices = detector.usb_scanner.list_devices()
    reports = []

    if not devices:
        report = manager.evaluate_device_driver_status(None)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(format_report(report))
        return

    for usb_dev in devices:
        device_info = detector._match_android_device(usb_dev) if usb_dev.vendor_id else None
        if not device_info and usb_dev.protocol:
            device_info = {
                'platform': 'android' if usb_dev.protocol != 'dfu' else 'ios',
                'mode': usb_dev.protocol,
                'vendor_id': f'{usb_dev.vendor_id:04x}',
                'product_id': f'{usb_dev.product_id:04x}',
                'serial': usb_dev.serial_number,
                'product': usb_dev.product,
                'manufacturer': usb_dev.manufacturer,
                'brand': 'Unknown'
            }

        report = manager.evaluate_device_driver_status(device_info)
        reports.append(report)

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for report in reports:
            print(format_report(report))
            print('\n' + ('=' * 80) + '\n')


if __name__ == '__main__':
    main()
