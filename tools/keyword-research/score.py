#!/usr/bin/env python3
"""
Интерпретация собранного спроса: превращает таблицу частотностей в вердикт.

Usage:
  python score.py suggests.csv
  python score.py suggests.csv --min-exact 50

Ожидает CSV из suggest.py с заполненными колонками wordstat_base /
wordstat_phrase / wordstat_exact (руками из Вордстата или через wordstat.py).
Пустые значения игнорируются, не ломают отчёт.

Три частотности — не прихоть:
  base   — «ремонт окон» без операторов: включает все словоформы и любые
           вложенные фразы. Самая большая и самая лживая цифра.
  phrase — "ремонт окон": только эта фраза, словоформы любые.
  exact  — "!ремонт !окон": ровно эта формулировка. Единственная, по которой
           можно планировать трафик.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict


def num(v: str) -> int | None:
    v = (v or "").strip().replace(" ", "").replace(" ", "")
    if not v:
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv_path")
    ap.add_argument("--min-exact", type=int, default=30,
                    help="порог точной частотности, ниже — считаем шумом")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.csv_path, encoding="utf-8")))
    if not rows:
        sys.exit("Пустой файл")

    by_seed: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_seed[r.get("seed", "—")].append(r)

    filled = [r for r in rows if num(r.get("wordstat_exact")) is not None]
    print(f"Фраз всего: {len(rows)}; с проставленной точной частотностью: {len(filled)}")
    if not filled:
        print("\nЧастотности не заполнены — отчёт будет только по формулировкам.\n"
              "Сам факт наличия фразы в подсказках уже означает, что её вводят живые люди.")

    print("\n" + "=" * 78)
    for seed, group in sorted(by_seed.items()):
        exact_vals = [(r["phrase"], num(r.get("wordstat_exact"))) for r in group]
        exact_vals = [(p, v) for p, v in exact_vals if v is not None]
        total_exact = sum(v for _, v in exact_vals)

        intents: dict[str, int] = defaultdict(int)
        for r in group:
            intents[r.get("intent", "other")] += 1

        print(f"\n### {seed}")
        print(f"формулировок: {len(group)}   "
              + "   ".join(f"{k}: {v}" for k, v in sorted(intents.items(), key=lambda kv: -kv[1])))

        if exact_vals:
            print(f"суммарная точная частотность: {total_exact}/мес")
            for p, v in sorted(exact_vals, key=lambda pv: -pv[1])[:8]:
                mark = " " if v >= args.min_exact else " (шум)"
                print(f"    {v:>7}  {p}{mark}")

            # Проверка на раздутую базовую частотность
            ratios = []
            for r in group:
                b, e = num(r.get("wordstat_base")), num(r.get("wordstat_exact"))
                if b and e is not None and b > 0:
                    ratios.append(e / b)
            if ratios:
                avg = sum(ratios) / len(ratios)
                if avg < 0.05:
                    print(f"    ! точная/базовая = {avg:.1%} — базовые цифры по этому кластеру "
                          f"раздуты вложенными фразами, ориентироваться только на точную")

        # Вердикт
        commercial = intents.get("commercial", 0) + intents.get("competitor", 0)
        if not exact_vals:
            verdict = "нет цифр — заполнить частотность"
        elif total_exact < args.min_exact:
            verdict = ("спроса на решение нет → SEO как канал закрыт. Это не приговор идее: "
                       "категория может быть новой. Искать людей там, где они жалуются, "
                       "а не там, где ищут")
        elif commercial == 0:
            verdict = ("спрос есть, но чисто информационный → это трафик, не выручка. "
                       "Нужен платный момент внутри контента")
        elif intents.get("competitor", 0) > 0:
            verdict = ("есть запросы про аналоги/замену → спрос доказан деньгами конкурента, "
                       "лучший вход")
        else:
            verdict = "спрос есть и он коммерческий → SEO работает как канал"
        print(f"    → {verdict}")

    print("\n" + "=" * 78)
    print("Правило: ноль частотности убивает канал SEO, а не идею.\n"
          "Правило: частотность без коммерческого намерения — это посетители, а не клиенты.")


if __name__ == "__main__":
    main()
