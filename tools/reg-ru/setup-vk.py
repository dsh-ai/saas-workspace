"""Apply VK WorkSpace DNS records to a Reg.ru domain.

Usage:
  1) verify: python setup-vk.py verify <domain> <mailruverify-value>
  2) mail:   python setup-vk.py mail <domain> \\
               --mx <mx-host>[:prio] \\
               --spf "<spf txt value>" \\
               --dkim-selector mail._domainkey \\
               --dkim-value "<dkim txt value>"
             (DMARC v=DMARC1; p=none добавляется автоматически)
"""
from __future__ import annotations

import argparse
import sys

from dns import add_a, add_mx, add_txt


def step_verify(domain: str, value: str) -> None:
    """Шаг 1: TXT на @ для верификации домена в VK.
    value — полная строка из VK, напр. 'mailru-domain: XXXX'."""
    add_txt(domain, "@", value)
    print(f"✓ verification TXT установлен для {domain}: {value}")
    print("→ подожди 10-15 мин и нажми «Проверить» в VK WorkSpace")


def step_mail(domain: str, mx: str, spf: str,
              dkim_selector: str, dkim_value: str) -> None:
    """Шаг 2: MX + SPF + DKIM + DMARC."""
    host, _, prio = mx.partition(":")
    add_mx(domain, "@", int(prio or 10), host)
    add_txt(domain, "@", spf)
    add_txt(domain, dkim_selector, dkim_value)
    add_txt(domain, "_dmarc", "v=DMARC1; p=none")
    print(f"✓ VK WorkSpace DNS применён для {domain}")
    print("  подожди 15-60 мин (до 72ч) и проверь mail-tester.com")


def main() -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("verify", help="шаг 1: установить mailruverify TXT")
    sp.add_argument("domain")
    sp.add_argument("value", help="значение mailruverify из VK")

    sp = sub.add_parser("mail", help="шаг 2: MX+SPF+DKIM+DMARC")
    sp.add_argument("domain")
    sp.add_argument("--mx", required=True, help="host[:priority], напр. emx.mail.ru:10")
    sp.add_argument("--spf", required=True)
    sp.add_argument("--dkim-selector", default="mail._domainkey",
                    help="имя хоста DKIM, по умолч. mail._domainkey")
    sp.add_argument("--dkim-value", required=True)

    args = p.parse_args()
    if args.cmd == "verify":
        step_verify(args.domain, args.value)
    elif args.cmd == "mail":
        step_mail(args.domain, args.mx, args.spf,
                  args.dkim_selector, args.dkim_value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
