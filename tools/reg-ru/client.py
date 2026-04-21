"""Reg.ru API v2 client (username/password auth)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

API_BASE = "https://api.reg.ru/api/regru2"
SECRETS = Path(__file__).resolve().parents[2] / ".secrets" / "regru.env"


def _load_env() -> dict[str, str]:
    if not SECRETS.exists():
        sys.exit(f"No credentials: {SECRETS} (copy from regru.env.example)")
    env: dict[str, str] = {}
    for line in SECRETS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


class RegRuError(RuntimeError):
    pass


def call(method: str, **params: Any) -> dict:
    """POST to api.reg.ru. `domains` param is auto-JSON-encoded."""
    env = _load_env()
    data: dict[str, Any] = {
        "username": env["REGRU_USERNAME"],
        "password": env["REGRU_PASSWORD"],
        "output_format": "json",
        "io_encoding": "utf8",
    }
    for k, v in params.items():
        data[k] = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v

    r = requests.post(f"{API_BASE}/{method}", data=data, timeout=30)
    r.raise_for_status()
    body = r.json()
    if body.get("result") != "success":
        raise RegRuError(f"{method}: {body.get('error_code')} — {body.get('error_text')}")
    return body.get("answer", {})


if __name__ == "__main__":
    # Ping: domain/nop — checks auth + whitelist
    try:
        print(json.dumps(call("nop"), indent=2, ensure_ascii=False))
    except (RegRuError, requests.HTTPError) as e:
        sys.exit(f"FAIL: {e}")
