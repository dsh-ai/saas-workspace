# Unit Economics

## Формулы
- LTV = ARPU × Avg lifetime (months)
- CAC = Marketing spend / New customers
- LTV/CAC ratio (цель: >3)
- Gross margin = (Revenue - COGS) / Revenue

## Постоянные затраты (fixed costs, не зависят от числа пользователей)

| Ресурс | Цена/мес |
|--------|----------|
| Selectel VPS #1 (приложение, 2CPU/4GB) | ~1 500 ₽ |
| Selectel VPS #2 (PostHog аналитика, 2CPU/4GB) | ~1 500 ₽ |
| Selectel Object Storage (бэкапы) | ~50 ₽ |
| **Итого fixed** | **~3 050 ₽** |

## COGS на пользователя/мес (переменные)
- AI токены: ~210₽ (средний пользователь, диапазон 70–410₽) — детали в `ai-costs.md`
- Хранение данных: ~5₽
- Поддержка: —₽
- **Итого переменные COGS:** ~215₽/пользователь/мес

## Расчёт (AI-план 4990₽/мес)
- Gross margin по AI-плану: ~86% (при средней нагрузке)
- Точка безубыточности: 1–2 платных AI-подписки покрывают fixed costs
- Подробности: `unit-economics-operations.md`
