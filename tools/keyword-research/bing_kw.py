#!/usr/bin/env python3
"""
Частотность для международного трека — Bing Webmaster Tools Keyword Research.

Почему именно Bing: он отдаёт **точные** числа, бесплатно и без рекламного аккаунта.
Google Keyword Planner без открученного бюджета показывает диапазоны («1K–10K»),
что для принятия решения бесполезно.

Цена вопроса: доля Bing сильно меньше доли Google, поэтому абсолютные числа —
это НЕ трафик, который ты получишь. Их назначение другое: **ранжировать запросы
между собой**. Какой кластер в 10 раз больше другого — Bing покажет честно.
Пересчитывать в Google можно только через коэффициент, который ты сам откалибруешь
позже по Search Console. Коэффициент «из головы» даст красивые и неверные цифры.

Usage:
  python bing_kw.py --stats suggests-en.csv --country us --language en-US
  python bing_kw.py --related "redact before chatgpt" --country us
  python bing_kw.py --stats suggests-en.csv --raw | head    # посмотреть сырой ответ

Доступ: подтверждённый сайт в Bing Webmaster Tools → Settings → API Access →
сгенерировать ключ. Положить в .secrets/bing-webmaster.env как BWT_APIKEY.

Замечание про поля ответа: разбор сделан защитно — имена ключей ищутся по нескольким
вариантам, а `--raw` печатает полезную нагрузку как есть. Если формат разойдётся,
смотреть `--raw` и поправить KEY_BROAD / KEY_STRICT ниже.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
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

API = "https://ssl.bing.com/webmaster/api.svc/json"
SECRETS = Path(__file__).resolve().parents[2] / ".secrets" / "bing-webmaster.env"

# Broad ≈ широкое соответствие (аналог базовой частотности Вордстата)
# Strict ≈ точное соответствие (аналог "!фразы") — решения принимать по нему
KEY_BROAD = ("Broad", "BroadImpressions", "broad")
KEY_STRICT = ("Strict", "StrictImpressions", "strict")
KEY_QUERY = ("Query", "Keyword", "query")


def load_key() -> str:
    if not SECRETS.exists():
        sys.exit(f"Нет файла {SECRETS}.\n"
                 f"Bing Webmaster Tools → Settings → API Access → сгенерировать ключ,\n"
                 f"положить строкой BWT_APIKEY=<ключ>")
    for line in SECRETS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("BWT_APIKEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("BWT_APIKEY не найден в .secrets/bing-webmaster.env")


def call(method: str, **params) -> object:
    url = f"{API}/{method}?" + parse.urlencode(params)
    req = request.Request(url, headers={"Accept": "application/json"})
    try:
        with request.urlopen(req, timeout=30, context=SSL_CTX) as r:
            payload = json.loads(r.read().decode("utf-8", errors="replace"))
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        print(f"  ! HTTP {e.code} на {method}: {body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ! {type(e).__name__}: {e}", file=sys.stderr)
        return None
    # WCF заворачивает результат в {"d": ...}
    return payload.get("d", payload) if isinstance(payload, dict) else payload


def pick(item: dict, names: tuple[str, ...]):
    for n in names:
        if n in item:
            return item[n]
    return None


def parse_date(v) -> str:
    if isinstance(v, str):
        m = re.search(r"/Date\((\d+)", v)
        if m:
            return time.strftime("%Y-%m-%d", time.gmtime(int(m.group(1)) / 1000))
        return v
    return str(v)


def summarize(rows: list, weeks: int) -> tuple[int | None, int | None]:
    """Последние N недель → среднее в неделю × 4.33 = оценка в месяц."""
    if not rows:
        return None, None
    tail = rows[-weeks:] if len(rows) > weeks else rows
    broad = [pick(r, KEY_BROAD) for r in tail if isinstance(r, dict)]
    strict = [pick(r, KEY_STRICT) for r in tail if isinstance(r, dict)]
    broad = [v for v in broad if isinstance(v, (int, float))]
    strict = [v for v in strict if isinstance(v, (int, float))]
    b = round(sum(broad) / len(broad) * 4.33) if broad else None
    s = round(sum(strict) / len(strict) * 4.33) if strict else None
    return b, s


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--stats", metavar="CSV", help="проставить частотность фразам из CSV (suggest.py)")
    g.add_argument("--related", metavar="PHRASE", help="показать связанные запросы к фразе")
    ap.add_argument("--country", default="us")
    ap.add_argument("--language", default="en-US")
    ap.add_argument("--weeks", type=int, default=8, help="сколько последних недель усреднять")
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--raw", action="store_true", help="печатать сырой ответ и выйти")
    ap.add_argument("--out", default=None, help="куда писать CSV (по умолчанию — перезаписать вход)")
    args = ap.parse_args()

    key = load_key()

    if args.related:
        data = call("GetRelatedKeywords", q=args.related, country=args.country,
                    language=args.language, apikey=key)
        if args.raw or not isinstance(data, list):
            print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
            return
        for item in data:
            if isinstance(item, dict):
                print(f"{pick(item, KEY_BROAD) or '':>10}  {pick(item, KEY_QUERY) or item}")
        return

    rows = list(csv.DictReader(open(args.stats, encoding="utf-8")))
    if not rows:
        sys.exit("Пустой CSV")

    for i, r in enumerate(rows, 1):
        data = call("GetKeywordStats", q=r["phrase"], country=args.country,
                    language=args.language, apikey=key)
        if args.raw:
            print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
            return
        broad, strict = summarize(data if isinstance(data, list) else [], args.weeks)
        # Пишем в те же колонки, что и Вордстат, — score.py читает их одинаково
        r["wordstat_base"] = broad if broad is not None else ""
        r["wordstat_exact"] = strict if strict is not None else ""
        r.setdefault("wordstat_phrase", "")
        if i % 10 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)
        time.sleep(args.delay)

    out = args.out or args.stats
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    filled = sum(1 for r in rows if r.get("wordstat_exact") not in ("", None))
    print(f"Заполнено {filled}/{len(rows)} → {out}", file=sys.stderr)
    print("Дальше: python score.py " + out, file=sys.stderr)


if __name__ == "__main__":
    main()
