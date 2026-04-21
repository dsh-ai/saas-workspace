"""DNS management for Reg.ru zones."""
from __future__ import annotations

import argparse
import json
import sys

from client import call


def list_records(domain: str) -> None:
    ans = call("zone/get_resource_records", domain_name=domain)
    d = (ans.get("domains") or [{}])[0]
    records = d.get("rrs", [])
    print(f"{domain}: {len(records)} записей")
    for r in records:
        print(f"  {r.get('subname', '@'):20s} {r.get('rectype', '?'):6s} "
              f"prio={r.get('prio', '-'):>3}  {r.get('content', '')}")


def remove(domain: str, subdomain: str, rtype: str, content: str | None) -> None:
    params = {
        "domains": [{"dname": domain}],
        "subdomain": subdomain,
        "record_type": rtype,
    }
    if content:
        params["content"] = content
    call("zone/remove_record", **params)
    print(f"removed {rtype} {subdomain} from {domain}")


def add_txt(domain: str, subdomain: str, text: str) -> None:
    call("zone/add_txt", domain_name=domain, subdomain=subdomain, text=text)
    print(f"+ TXT {subdomain} {domain}: {text[:60]}...")


def add_mx(domain: str, subdomain: str, priority: int, mail_server: str) -> None:
    call(
        "zone/add_mx",
        domain_name=domain,
        subdomain=subdomain,
        priority=priority,
        mail_server=mail_server,
    )
    print(f"+ MX {subdomain} {priority} {mail_server}")


def add_a(domain: str, subdomain: str, ip: str) -> None:
    call("zone/add_alias", domain_name=domain, subdomain=subdomain, ipaddr=ip)
    print(f"+ A {subdomain} {ip}")


def apply_email(domain: str, mx_host: str, mx_prio: int,
                spf: str, dmarc: str,
                dkim_selector: str | None, dkim_key: str | None) -> None:
    """Bulk-apply email DNS: MX + SPF (TXT @) + DMARC (TXT _dmarc) + optional DKIM."""
    add_mx(domain, "@", mx_prio, mx_host)
    add_txt(domain, "@", spf)
    add_txt(domain, "_dmarc", dmarc)
    if dkim_selector and dkim_key:
        add_txt(domain, f"{dkim_selector}._domainkey", dkim_key)
    print(f"email DNS applied to {domain}")


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list"); sp.add_argument("domain")

    sp = sub.add_parser("remove")
    sp.add_argument("domain"); sp.add_argument("subdomain")
    sp.add_argument("type"); sp.add_argument("--content")

    sp = sub.add_parser("add-txt")
    sp.add_argument("domain"); sp.add_argument("subdomain"); sp.add_argument("text")

    sp = sub.add_parser("add-mx")
    sp.add_argument("domain"); sp.add_argument("subdomain")
    sp.add_argument("priority", type=int); sp.add_argument("server")

    sp = sub.add_parser("add-a")
    sp.add_argument("domain"); sp.add_argument("subdomain"); sp.add_argument("ip")

    sp = sub.add_parser("apply-email",
                        help="MX + SPF + DMARC + DKIM одним вызовом")
    sp.add_argument("domain")
    sp.add_argument("--mx-host", required=True)
    sp.add_argument("--mx-prio", type=int, default=10)
    sp.add_argument("--spf", default="v=spf1 include:_spf.google.com ~all")
    sp.add_argument("--dmarc", default="v=DMARC1; p=none; rua=mailto:postmaster@%s")
    sp.add_argument("--dkim-selector")
    sp.add_argument("--dkim-key")

    args = p.parse_args()

    if args.cmd == "list":
        list_records(args.domain)
    elif args.cmd == "remove":
        remove(args.domain, args.subdomain, args.type, args.content)
    elif args.cmd == "add-txt":
        add_txt(args.domain, args.subdomain, args.text)
    elif args.cmd == "add-mx":
        add_mx(args.domain, args.subdomain, args.priority, args.server)
    elif args.cmd == "add-a":
        add_a(args.domain, args.subdomain, args.ip)
    elif args.cmd == "apply-email":
        dmarc = args.dmarc % args.domain if "%s" in args.dmarc else args.dmarc
        apply_email(args.domain, args.mx_host, args.mx_prio, args.spf, dmarc,
                    args.dkim_selector, args.dkim_key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
