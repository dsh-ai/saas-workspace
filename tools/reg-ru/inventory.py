"""List domains + expiration → markdown report."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from client import call


def fetch_domains() -> list[dict]:
    ans = call("service/get_list", servtype="domain", show_folders=0, show_dates=1)
    services = ans.get("services", [])
    for s in services:
        try:
            ns = call("domain/get_nss", domain_name=s["dname"])
            entries = (ns.get("domains") or [{}])[0].get("nss", [])
            s["_ns"] = ", ".join(e.get("ns", "") for e in entries)
        except Exception:
            s["_ns"] = "—"
    return services


def render(services: list[dict]) -> str:
    rows = []
    for s in sorted(services, key=lambda x: x.get("expiration_date", "")):
        rows.append(
            f"| {s.get('dname', '?')} "
            f"| {s.get('expiration_date', '—')} "
            f"| {s.get('state', '—')} "
            f"| {s.get('_ns') or '—'} |"
        )
    header = (
        "| Домен | Истекает | Статус | NS |\n"
        "|---|---|---|---|\n"
    )
    return (
        f"# Домены Reg.ru\n\n"
        f"> Сгенерировано {datetime.now():%Y-%m-%d %H:%M} — `tools/reg-ru/inventory.py`\n\n"
        f"Всего: {len(services)}\n\n"
        + header + "\n".join(rows) + "\n"
    )


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "dev" / "domains.md"
    services = fetch_domains()
    out.write_text(render(services), encoding="utf-8")
    print(f"{len(services)} домен(ов) → {out}")
