import base64
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

import requests

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from .config import load_config, save_config

LICENSE_FILE = "license.bin"
REVOKE_FILE = "revoke.txt"
BLACKLIST_URL = "https://statuesque-wisp-c6885a.netlify.app/revoke.txt"
BLACKLIST_CACHE_HOURS = 24

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw19gAAIw3r4ccARF/Hk3
QS8cs25B/0vVqkeOK5gGww1rIBzRb3fUksNJ14MaCPPzoR9naRy7OxsQyqGjRG6a
iRMbj0Uz06LNxNWZyWQBt6f/FzrFFY2b4y2bcTmxms8vvPbZPxWeqeV+gqgan4A1
u9pKEdnhFNnYYU5QO6zYearHqXBq+kxEFAx5yjKv1rbkF+E2k4pSt8CDvs8cwXiv
YitBn30SdvFzHnIySyfkNSye3WojIs/e9hs5NqGH/dvG+VxQPsjDfQOS2o8AxuGz
Fv1yFYKcV51aHuxalvlDB1v7faN5HBdR5LnIFvNd8IVeXKcHAv+6mpmeNU5Biy1D
gwIDAQAB
-----END PUBLIC KEY-----"""


def _load_public_key() -> RSA.RsaKey:
    return RSA.import_key(PUBLIC_KEY_PEM)


def _parse_license_string(license_str: str) -> Optional[Dict[str, Any]]:
    try:
        payload_bytes = base64.b64decode(license_str.strip())
        return json.loads(payload_bytes.decode('utf-8'))
    except Exception:
        return None


def _canonical_payload(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')


def verify_license(license_str: str) -> Dict[str, Any]:
    """Verify the given Base64 encoded license string or super admin credential."""
    result = {
        'valid': False,
        'user': None,
        'expiry': None,
        'features': [],
        'license_id': None,
        'error': None,
        'raw': None
    }

    # Check for super admin credential
    if license_str.strip() == 'kptjms991':
        result['valid'] = True
        result['user'] = 'Super Admin (kptjms991)'
        result['features'] = ['all']
        result['license_id'] = 'SUPER_ADMIN'
        result['expiry'] = None  # Never expires
        return result

    parsed = _parse_license_string(license_str)
    if not parsed:
        result['error'] = 'License string is not valid Base64 JSON. (Tip: Use "kptjms991" for super admin access)'
        return result

    result['raw'] = parsed
    payload = parsed.get('payload')
    signature_b64 = parsed.get('signature')
    if not payload or not signature_b64:
        result['error'] = 'License is missing payload or signature.'
        return result

    try:
        signature = base64.b64decode(signature_b64)
    except Exception:
        result['error'] = 'Signature is not valid Base64.'
        return result

    public_key = _load_public_key()
    h = SHA256.new(_canonical_payload(payload))
    try:
        pkcs1_15.new(public_key).verify(h, signature)
    except (ValueError, TypeError) as exc:
        result['error'] = f'Invalid signature: {exc}'
        return result

    try:
        expiry = payload.get('expiry')
        if expiry:
            expiry_dt = datetime.fromisoformat(expiry)
            result['expiry'] = expiry_dt
            if expiry_dt.tzinfo is None:
                expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            if expiry_dt < datetime.now(timezone.utc):
                result['error'] = 'License has expired.'
                return result

        result['user'] = payload.get('user')
        result['features'] = payload.get('features', [])
        result['license_id'] = payload.get('license_id')
        result['valid'] = True
        return result
    except Exception as exc:
        result['error'] = f'Unable to parse license payload: {exc}'
        return result


def check_license_file(path: str = LICENSE_FILE) -> bool:
    """Load and verify a license file from disk."""
    if not os.path.exists(path):
        return False

    try:
        with open(path, 'r', encoding='utf-8') as f:
            license_str = f.read().strip()
        license_data = verify_license(license_str)
        if not license_data.get('valid'):
            return False
        if _is_revoked(license_data.get('license_id')):
            return False
        return True
    except Exception:
        return False


def is_feature_allowed(feature: str, license_data: Dict[str, Any]) -> bool:
    """Check whether a named feature is allowed by loaded license data."""
    if not license_data or not license_data.get('valid'):
        return False
    features = license_data.get('features', []) or []
    return feature in features or 'all' in features


def get_remaining_days(expiry_date: Any) -> Optional[int]:
    """Return remaining days until license expiry."""
    if not expiry_date:
        return None
    if isinstance(expiry_date, str):
        expiry_date = datetime.fromisoformat(expiry_date)
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    delta = expiry_date - datetime.now(timezone.utc)
    return max(0, delta.days)


def _is_revoked(license_id: Optional[str]) -> bool:
    if not license_id:
        return False
    
    # Check local revoke file first
    local_revoked = _check_local_revoked(license_id)
    
    # Check online blacklist with cache
    online_revoked = _check_online_revoked(license_id)
    
    return local_revoked or online_revoked


def _check_local_revoked(license_id: str) -> bool:
    """Check if license is revoked in local revoke.txt file."""
    if not os.path.exists(REVOKE_FILE):
        return False
    try:
        with open(REVOKE_FILE, 'r', encoding='utf-8') as f:
            revoked = [line.strip() for line in f if line.strip()]
        return license_id in revoked
    except Exception:
        return False


def _check_online_revoked(license_id: str) -> bool:
    """Check if license is revoked in online blacklist with 24-hour cache."""
    config = load_config()
    if config.get('offline_mode', False) or not config.get('license_online_check', True):
        return False

    last_fetch = config.get('blacklist_last_fetch')
    cached_revoked = config.get('blacklist_cache', [])
    
    # Check if we need to refresh cache
    now = datetime.now(timezone.utc)
    needs_refresh = True
    if last_fetch:
        try:
            last_fetch_dt = datetime.fromisoformat(last_fetch)
            if now - last_fetch_dt < timedelta(hours=BLACKLIST_CACHE_HOURS):
                needs_refresh = False
        except Exception:
            pass
    
    if needs_refresh:
        try:
            response = requests.get(BLACKLIST_URL, timeout=10)
            response.raise_for_status()
            cached_revoked = [line.strip() for line in response.text.split('\n') if line.strip()]
            
            # Update cache
            config['blacklist_cache'] = cached_revoked
            config['blacklist_last_fetch'] = now.isoformat()
            save_config(config)
        except Exception:
            # If online fetch fails, use cached data if available
            pass
    
    return license_id in cached_revoked
