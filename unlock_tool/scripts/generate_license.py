#!/usr/bin/env python3
import argparse
import base64
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List
from uuid import uuid4

try:
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
except ImportError:
    from Cryptodome.Hash import SHA256
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Signature import pkcs1_15


def _canonical_payload(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_payload(user: str, expiry: str, features: str, license_id: str) -> dict:
    if expiry.lower() == "none":
        expiry_value = None
    else:
        try:
            expiry_value = datetime.fromisoformat(expiry)
            if expiry_value.tzinfo is None:
                expiry_value = expiry_value.replace(tzinfo=timezone.utc)
            expiry_value = expiry_value.isoformat()
        except ValueError:
            delta_days = int(expiry)
            expiry_value = (datetime.now(timezone.utc) + timedelta(days=delta_days)).isoformat()

    feature_list = [item.strip() for item in features.split(",") if item.strip()]
    if not feature_list:
        feature_list = ["all"]

    return {
        "user": user,
        "expiry": expiry_value,
        "features": feature_list,
        "license_id": license_id,
    }


def sign_license(payload: dict, private_key_path: Path) -> str:
    private_key = RSA.import_key(private_key_path.read_bytes())
    h = SHA256.new(_canonical_payload(payload))
    signature = pkcs1_15.new(private_key).sign(h)
    license_obj = {
        "payload": payload,
        "signature": base64.b64encode(signature).decode("utf-8"),
    }
    license_json = json.dumps(license_obj, separators=(",", ":"))
    return base64.b64encode(license_json.encode("utf-8")).decode("utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Base64-encoded license string for unlock_tool."
    )
    parser.add_argument("--user", required=True, help="License holder name")
    parser.add_argument(
        "--expiry",
        default="365",
        help="Expiry in days from now, ISO timestamp, or 'none' for no expiry",
    )
    parser.add_argument(
        "--features",
        default="all",
        help="Comma-separated feature list (default: all)",
    )
    parser.add_argument(
        "--license-id",
        default=None,
        help="Unique license ID base (default: auto-generated)",
    )
    parser.add_argument(
        "--private-key",
        required=True,
        help="Path to PEM-encoded RSA private key used for signing",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of backup license keys to generate",
    )
    parser.add_argument(
        "--output",
        help="Write the Base64 license strings to this file instead of stdout",
    )
    return parser.parse_args()


def write_licenses(output_path: Path, licenses: list[str]) -> None:
    output_path.write_text("\n".join(licenses) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    licenses = []
    for index in range(args.count):
        if args.license_id:
            license_id = args.license_id if args.count == 1 else f"{args.license_id}-{index + 1}"
        else:
            license_id = str(uuid4())

        payload = build_payload(args.user, args.expiry, args.features, license_id)
        licenses.append(sign_license(payload, Path(args.private_key)))

    if args.output:
        write_licenses(Path(args.output), licenses)
        print(f"{len(licenses)} license(s) saved to {args.output}")
    else:
        print("\n".join(licenses))


if __name__ == "__main__":
    main()
