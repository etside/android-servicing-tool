#!/usr/bin/env python3
"""
Generate udev rules for Android device support.

Use this script to create a Linux udev rules file that includes common vendor IDs
for Qualcomm, MediaTek, Samsung, Xiaomi, OnePlus, Huawei, Motorola, and more.
"""

import argparse
from pathlib import Path

from core.driver_manager import DriverManager


def main():
    parser = argparse.ArgumentParser(description='Generate /etc/udev/rules.d/51-android.rules content.')
    parser.add_argument('--output', '-o', type=Path, default=Path('51-android.rules'), help='Output rule file path')
    args = parser.parse_args()

    manager = DriverManager()
    content = manager.get_udev_rule_content()
    args.output.write_text(content, encoding='utf-8')
    print(f'Generated udev rules to: {args.output}')


if __name__ == '__main__':
    main()
