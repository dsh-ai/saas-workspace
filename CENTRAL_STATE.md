# Central State

> Последнее обновление: 2026-03-22
> Обновляется Claude после каждой сессии с кросс-доменными изменениями

## Текущий фокус
Настройка SaaS Workspace — единого контекстного поля для управления продуктом через Claude Code.

## Ключевые метрики
- MRR: —
- Активных пользователей: —
- Стоимость AI на пользователя/мес: ~215₽ (dual-provider: Yandex AI Studio + Anthropic Haiku; диапазон 70–410₽)
- CAC: —
- Burn rate: —

## Планы и ценообразование
- trial: бесплатно
- basic: 1990₽/мес или 19900₽/год
- ai: 4990₽/мес или 49900₽/год

## Активные зависимости
*(нет активных кросс-доменных зависимостей)*

## Последние решения
- 2026-03-07: Создан SaaS Workspace. Маркетинговые файлы перенесены из dev_unilist. Домены: dev, finance, marketing, ai-architecture, content.
- 2026-03-07: Выбрана стратегия запуска — Вариант В (мягкий запуск → публичный). Жёсткие требования: 152-ФЗ обязателен до запуска для реальных клиентов, миграция Railway/Vercel → VPS в РФ. Аналитика: Яндекс.Метрика + события в PostgreSQL. Цена AI-плана скорректирована: 2990₽ → 4990₽/мес. Трекер задач: plan-fact.md.

## Инфраструктура мониторинга
- GlitchTip self-hosted: `http://37.9.7.141:8080` (Selectel VPS, 4vCPU/8GB)
- Backend errors → проект `unilist-backend` (DSN: `/1`)
- Frontend errors → проект `unilist-frontend` (DSN: `/2`)
- Автозапуск: systemd unit `glitchtip.service`

## Техническое состояние (из dev/)
- Stack: Next.js 16 (Vercel) + NestJS 11 (Railway) + PostgreSQL
- AI: Anthropic claude-3-haiku-20240307 для всех AI-функций (haiku-4-5 недоступен на аккаунте)
- Последний деплой: fix(demo) — фикс 500 на /demo/trends (модель + fallback на ошибки API)
- MCP-интеграции: Bitrix24 (task.stages, "Мой план", маппинг доменов → колонки)
- 2026-03-15: Company Profile — 5 полей компании в User (industry, product, audience, avgDeal, description). AI-промпты получают контекст компании. Онбординг + настройки + баннер.
