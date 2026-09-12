#!/usr/bin/env python3
"""
Сбор реальных поисковых подсказок Яндекса и Google.

Зачем: подсказки строятся на логах реальных запросов. Если формулировка есть
в подсказках — её буквально вводят живые люди. Это ответ на вопрос «что ищет
аудитория», не требующий ни доступов, ни бюджета.

Usage:
  python suggest.py seeds/masking.txt                    # Яндекс + Google
  python suggest.py seeds/152fz.txt --engine yandex      # только Яндекс
  python suggest.py seeds/*.txt --expand --out out.csv   # + буквенное расширение
  python suggest.py seeds/masking.txt --lang en          # английская раскладка

Доступов не требует. Запускать локально: в некоторых окружениях эндпоинты
подсказок закрыты сетевой политикой.
"""
from __future__ import annotations

import argparse
import csv
import json
import ssl
import sys
import time
from pathlib import Path
from urllib import error, parse, request

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

ALPHABET = {
    "ru": "абвгдежзиклмнопрстуфхцчшэюя",
    "en": "abcdefghijklmnopqrstuvwxyz",
}
QUESTIONS = {
    "ru": ["как", "где", "чем", "почему", "можно ли", "что такое", "сколько стоит", "нужно ли"],
    "en": ["how", "where", "what", "why", "can i", "best", "free", "alternative to"],
}

# Маркеры намерения. Частотность без намерения — это трафик, а не выручка.
INTENT = {
    "commercial": ["онлайн", "сервис", "программа", "скачать", "купить", "цена",
                   "заказать", "software", "tool", "app", "pricing", "buy"],
    "free": ["бесплатно", "бесплатный", "free", "open source", "без регистрации"],
    "competitor": ["аналог", "замена", "вместо", "альтернатива", "alternative", "vs", "instead of"],
    "problem": ["штраф", "ответственность", "как", "почему", "можно ли", "риск",
                "запрет", "утечка", "нельзя", "risk", "fine", "leak"],
}


def fetch(url: str) -> list[str]:
    req = request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with request.urlopen(req, timeout=15, context=SSL_CTX) as r:
            raw = r.read().decode("utf-8", errors="replace")
    except error.HTTPError as e:
        print(f"  ! HTTP {e.code} для {url[:70]}", file=sys.stderr)
        return []
    except Exception as e:  # сеть, TLS, таймаут
        print(f"  ! {type(e).__name__}: {e}", file=sys.stderr)
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    # Оба эндпоинта отвечают в формате ["запрос", ["подсказка", ...], ...]
    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
        return [s for s in data[1] if isinstance(s, str)]
    return []


def yandex(q: str, lang: str, country: str = "") -> list[str]:
    return fetch("https://suggest.yandex.ru/suggest-ff.cgi?"
                 + parse.urlencode({"part": q, "uil": lang, "v": "4", "n": "10"}))


def google(q: str, lang: str, country: str = "") -> list[str]:
    params = {"client": "firefox", "hl": lang, "q": q}
    if country:
        params["gl"] = country  # страна меняет подсказки: us и gb дают разные списки
    return fetch("https://suggestqueries.google.com/complete/search?" + parse.urlencode(params))


def classify(phrase: str) -> str:
    low = phrase.lower()
    for name in ("competitor", "commercial", "free", "problem"):
        if any(m in low for m in INTENT[name]):
            return name
    return "other"


def variants(seed: str, lang: str, expand: bool) -> list[str]:
    out = [seed]
    if expand:
        out += [f"{seed} {ch}" for ch in ALPHABET[lang]]
        out += [f"{w} {seed}" for w in QUESTIONS[lang]]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("seeds", nargs="+", help="файлы со стартовыми фразами (по одной в строке)")
    ap.add_argument("--engine", choices=["both", "yandex", "google"], default="both")
    ap.add_argument("--lang", default="ru", choices=["ru", "en"])
    ap.add_argument("--country", default="",
                    help="код страны для подсказок Google (us, gb, de…). Меняет выдачу")
    ap.add_argument("--expand", action="store_true",
                    help="добавить буквенное и вопросное расширение (дольше, но шире охват)")
    ap.add_argument("--delay", type=float, default=0.4, help="пауза между запросами, сек")
    ap.add_argument("--out", default="suggests.csv")
    args = ap.parse_args()

    seeds: list[str] = []
    for path in args.seeds:
        p = Path(path)
        if not p.exists():
            sys.exit(f"Нет файла {p}")
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                seeds.append(line)

    engines = [("yandex", yandex), ("google", google)]
    if args.engine != "both":
        engines = [e for e in engines if e[0] == args.engine]

    found: dict[str, dict] = {}
    queries = [(s, v) for s in seeds for v in variants(s, args.lang, args.expand)]
    print(f"Сидов: {len(seeds)}, запросов к подсказкам: {len(queries) * len(engines)}")

    for i, (seed, q) in enumerate(queries, 1):
        for name, fn in engines:
            for phrase in fn(q, args.lang, args.country):
                rec = found.setdefault(phrase.lower().strip(), {
                    "phrase": phrase.lower().strip(), "seed": seed,
                    "engines": set(), "intent": classify(phrase),
                })
                rec["engines"].add(name)
            time.sleep(args.delay)
        if i % 25 == 0:
            print(f"  {i}/{len(queries)} — найдено уникальных: {len(found)}")

    rows = sorted(found.values(), key=lambda r: (r["intent"], r["phrase"]))
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["phrase", "seed", "engines", "intent", "wordstat_base",
                    "wordstat_phrase", "wordstat_exact"])
        for r in rows:
            w.writerow([r["phrase"], r["seed"], "+".join(sorted(r["engines"])),
                        r["intent"], "", "", ""])

    print(f"\nСохранено {len(rows)} уникальных формулировок → {args.out}")
    by_intent: dict[str, int] = {}
    for r in rows:
        by_intent[r["intent"]] = by_intent.get(r["intent"], 0) + 1
    for k, v in sorted(by_intent.items(), key=lambda kv: -kv[1]):
        print(f"  {k:12} {v}")
    print("\nДалее: проставить частотность в три пустые колонки — вручную из Вордстата\n"
          "или через wordstat.py, затем `python score.py suggests.csv`.")


if __name__ == "__main__":
    main()
