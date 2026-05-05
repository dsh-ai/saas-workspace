#!/usr/bin/env python3
"""
Создаёт цели в Яндекс.Метрике через Management API.

Usage:
  python create-goals.py                # создать все цели из goals.json
  python create-goals.py --list         # показать существующие цели
  python create-goals.py --dry-run      # показать payload без отправки

Требует:
  .secrets/yandex-metrika.env с YM_TOKEN и YM_COUNTER_ID
  goals.json с описанием целей
"""
import argparse
import json
import os
import ssl
import sys
from pathlib import Path
from urllib import request, error

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

ROOT = Path(__file__).resolve().parent
SECRETS = ROOT.parent.parent / ".secrets" / "yandex-metrika.env"
GOALS_FILE = ROOT / "goals.json"
API = "https://api-metrika.yandex.net/management/v1"


def load_env():
    if not SECRETS.exists():
        sys.exit(f"Нет файла {SECRETS}. Скопируйте из .example и впишите YM_TOKEN.")
    env = {}
    for line in SECRETS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    if not env.get("YM_TOKEN"):
        sys.exit("YM_TOKEN не задан в .secrets/yandex-metrika.env")
    if not env.get("YM_COUNTER_ID"):
        sys.exit("YM_COUNTER_ID не задан")
    return env


def http(method, url, token, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"OAuth {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        sys.exit(f"HTTP {e.code} {url}: {body}")


def list_goals(env):
    counter = env["YM_COUNTER_ID"]
    res = http("GET", f"{API}/counter/{counter}/goals", env["YM_TOKEN"])
    goals = res.get("goals", [])
    if not goals:
        print("Целей нет.")
        return goals
    print(f"Существующих целей: {len(goals)}")
    for g in goals:
        print(f"  [{g.get('id')}] {g.get('name')} (type={g.get('type')})")
    return goals


def create_goal(env, goal, dry_run=False):
    counter = env["YM_COUNTER_ID"]
    payload = {"goal": goal}
    if dry_run:
        print(f"DRY-RUN payload:\n{json.dumps(payload, ensure_ascii=False, indent=2)}")
        return
    res = http("POST", f"{API}/counter/{counter}/goals", env["YM_TOKEN"], payload)
    g = res.get("goal", {})
    print(f"  ✓ создано: [{g.get('id')}] {g.get('name')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="показать существующие цели")
    ap.add_argument("--dry-run", action="store_true", help="показать payload без отправки")
    args = ap.parse_args()

    env = load_env()

    if args.list:
        list_goals(env)
        return

    goals = json.loads(GOALS_FILE.read_text())

    existing = list_goals(env) if not args.dry_run else []
    existing_names = {g.get("name") for g in existing}

    print(f"\nЦелей к созданию: {len(goals)}")
    for goal in goals:
        if goal["name"] in existing_names:
            print(f"  ↷ пропуск (уже есть): {goal['name']}")
            continue
        create_goal(env, goal, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
