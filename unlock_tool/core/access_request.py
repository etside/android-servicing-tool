"""
Access request flow via Vercel API relay.
Set VERCEL_API_URL env var to your deployed Vercel project URL.
"""
import hashlib
import json
import os
import platform
import socket
import time
import urllib.request

VERCEL_API_URL = os.environ.get("VERCEL_API_URL", "https://etool-api.vercel.app").rstrip("/")
POLL_INTERVAL = 5
TIMEOUT = 300


def _machine_id() -> str:
    raw = f"{platform.node()}-{os.environ.get('USER', os.environ.get('USERNAME', 'user'))}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _public_ip() -> str:
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as r:
            return r.read().decode().strip()
    except Exception:
        return "unknown"


def _post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{VERCEL_API_URL}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{VERCEL_API_URL}{path}", timeout=10) as r:
        return json.loads(r.read())


def submit_request() -> str:
    resp = _post("/api/request", {
        "machine_id": _machine_id(),
        "user_ip": _public_ip(),
        "hostname": socket.gethostname(),
    })
    return resp["id"]


def poll_for_decision(request_id: str) -> str:
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            record = _get(f"/api/request/{request_id}")
            if record.get("status") != "pending":
                return record["status"]
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)
    return "timeout"


def request_access(logger=None) -> bool:
    def log(msg):
        if logger:
            logger.info(msg)
        else:
            print(msg)

    if not VERCEL_API_URL:
        log("WARNING: VERCEL_API_URL not set — skipping access request check.")
        return True

    try:
        log("Submitting access request to admin...")
        req_id = submit_request()
        log(f"Waiting for admin approval (id={req_id})...")
        status = poll_for_decision(req_id)
        if status == "approved":
            log("✅ Access approved.")
            return True
        log(f"❌ Access {status}.")
        return False
    except Exception as e:
        log(f"Access request error: {e}. Denying access.")
        return False
