#!/usr/bin/env python3
"""
Частотность запросов из Вордстата.

Два режима — потому что доступ к API даётся по заявке, а цифры нужны раньше.

  --phrases   готовит список фраз с операторами для ручной проверки.
              Работает прямо сейчас, без доступов:
                python wordstat.py suggests.csv --phrases > check.txt
              Дальше вставить в Вордстат, выгрузить, заполнить колонки в CSV.

  --api       автоматический сбор. Требует доступ (см. ниже) и дозаполнения
              контракта запроса в fetch_frequency().

Где брать доступ (на сентябрь 2026 — два пути):
  1. API Вордстата (бета, бесплатный) — по заявке в поддержку Яндекс Директа,
     авторизация OAuth-токеном: Authorization: Bearer <token>
  2. Wordstat внутри Yandex Cloud Search API — актуально, если облачный аккаунт
     уже есть (в проекте он есть под AI Studio).
  Точный эндпоинт и формат тела запроса взять из официальной документации —
  контракт намеренно не зашит в код, чтобы не разойтись с реальностью.

Операторы Вордстата (главное, из-за чего цифры врут):
  фраза          — все словоформы И любые вложенные фразы. Самая раздутая цифра
  "фраза"        — только эта фраза, словоформы любые
  "!фраза !така" — ровно эта формулировка. Планировать можно только по ней
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import ssl
import sys
from pathlib import Path
from urllib import error, request

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

SECRETS = Path(__file__).resolve().parents[2] / ".secrets" / "wordstat.env"


def load_env() -> dict[str, str]:
    if not SECRETS.exists():
        sys.exit(f"Нет файла {SECRETS}.\n"
                 f"Создать с WORDSTAT_TOKEN=<OAuth-токен> (и WORDSTAT_FOLDER_ID, "
                 f"если идём через Yandex Cloud).")
    env = {}
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def with_operators(phrase: str) -> tuple[str, str, str]:
    """base, phrase-match, exact-match варианты одной фразы."""
    words = phrase.split()
    return phrase, f'"{phrase}"', '"' + " ".join("!" + w for w in words) + '"'


def fetch_frequency(phrase: str, env: dict[str, str], region: int | None = None) -> int:
    """
    Один запрос частотности.

    НЕ РЕАЛИЗОВАНО НАМЕРЕННО. Контракт (URL, тело запроса, путь к числу в ответе)
    различается у двух путей доступа и у их версий — зашивать его «по памяти»
    означает отдать скрипт, который молча вернёт неправильные числа.

    Что сделать, получив доступ:
      1. Взять эндпоинт и схему запроса из официальной документации своего пути.
      2. Собрать тело: фраза (уже с операторами), регион, период, тип устройств.
      3. Вернуть число показов в месяц из ответа.
    Заголовок авторизации в обоих путях один: Authorization: Bearer <token>.
    Пока не реализовано — рабочий путь это `--phrases` плюс ручная выгрузка.
    """
    raise NotImplementedError(
        "fetch_frequency() не заполнен: см. докстринг. "
        "Пока пользуйтесь режимом --phrases и ручной выгрузкой из Вордстата."
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_path", help="CSV из suggest.py")
    ap.add_argument("--phrases", action="store_true",
                    help="вывести фразы с операторами для ручной проверки")
    ap.add_argument("--api", action="store_true", help="собрать частотность через API")
    ap.add_argument("--region", type=int, default=None, help="ID региона Яндекса")
    ap.add_argument("--limit", type=int, default=0, help="взять только N первых фраз")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.csv_path, encoding="utf-8")))
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        sys.exit("Пустой CSV")

    if args.phrases:
        for r in rows:
            base, phrase, exact = with_operators(r["phrase"])
            print(base)
            print(phrase)
            print(exact)
        print(f"\n# {len(rows)} фраз × 3 варианта. "
              f"Проверить в Вордстате, числа вписать в колонки "
              f"wordstat_base / wordstat_phrase / wordstat_exact.", file=sys.stderr)
        return

    if not args.api:
        sys.exit("Укажите --phrases или --api")

    env = load_env()
    out = []
    for i, r in enumerate(rows, 1):
        base, phrase, exact = with_operators(r["phrase"])
        r["wordstat_base"] = fetch_frequency(base, env, args.region)
        r["wordstat_phrase"] = fetch_frequency(phrase, env, args.region)
        r["wordstat_exact"] = fetch_frequency(exact, env, args.region)
        out.append(r)
        if i % 20 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)

    w = csv.DictWriter(sys.stdout, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)


if __name__ == "__main__":
    main()
