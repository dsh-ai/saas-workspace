"""Check domains expiring within N days."""
from __future__ import annotations

import argparse
from datetime import date, datetime

from client import call


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    args = p.parse_args()

    services = call("service/get_list", servtype="domain",
                    show_folders=0, show_dates=1).get("services", [])
    today = date.today()
    soon = []
    for s in services:
        end = s.get("expiration_date")
        if not end:
            continue
        try:
            d = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            continue
        delta = (d - today).days
        if delta <= args.days:
            soon.append((delta, s.get("dname"), end))

    soon.sort()
    if not soon:
        print(f"Нет доменов, истекающих в ближайшие {args.days} дней.")
        return 0
    print(f"Истекают в ближайшие {args.days} дней:")
    for delta, name, end in soon:
        marker = "!!!" if delta < 7 else "!!" if delta < 14 else "!"
        print(f"  {marker} {name:35s} {end}  ({delta}d)")
    return 1 if any(d < 7 for d, _, _ in soon) else 0


if __name__ == "__main__":
    raise SystemExit(main())
