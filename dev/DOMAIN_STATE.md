# Dev — Domain State

> Последнее обновление: 2026-04-19

## Задеплоено (production)
- AI-кэширование ответов (SHA256 по тексту промпта)
- Анализ отдельного ответа и батч-анализ
- Ретроспективный аудит шаблона
- Онбординг v3 (full-screen, 4 шага)
- Фильтр по периоду в Homestead
- Prompt Registry (управление промтами через Homestead)

## В работе
*(нет активных задач)*

## Технический долг
*(нет зафиксированных)*

## Интеграции (saas-workspace/tools/)

### Reg.ru API (v2)
- **Назначение:** массовое управление DNS (Respondo-спутники) + инвентаризация/мониторинг доменов
- **Путь:** `tools/reg-ru/` (client.py, inventory.py, monitor.py, dns.py)
- **Auth:** username+password, креды в `.secrets/regru.env` (в `.gitignore`)
- **Префлайт:** включить API и добавить IP в whitelist в ЛК Reg.ru (`/user/account/#/settings/api/`)
- **Статус:** MVP готов, не тестирован на живом аккаунте
- **TODO:** мигрировать на signature-auth, когда интеграция пойдёт в prod-код

## Ключевые файлы кодовой базы
- `backend/src/` — NestJS модули
- `frontend/app/` — Next.js App Router страницы
- `CLAUDE.md` в корне dev_unilist — полная архитектурная документация
