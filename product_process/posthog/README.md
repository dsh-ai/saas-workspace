# PostHog — Продуктовая аналитика

## Что это

PostHog Self-Hosted — аналитика пользовательского поведения. Отслеживаем события от регистрации до подписки и использования AI.

## Статус (2026-03-29)

| Компонент | Статус |
|---|---|
| Сервер PostHog (37.9.7.141) | Запущен, docker-compose.hobby.yml |
| Домен posthog.unilist.ru | DNS → 37.9.7.141 ✅ |
| SSL-сертификат (Let's Encrypt) | Получен через Caddy ✅ |
| HTTPS https://posthog.unilist.ru | Отвечает 502 (контейнеры, возможно упали) |
| Frontend интеграция (posthog-js) | Реализована ✅ |
| Backend интеграция (posthog-node) | Реализована ✅ |
| Env vars в Coolify | **Не выставлены** ⏳ |
| Smoke test | **Не проведён** ⏳ |

## Архитектура

```
Browser/App → posthog-js → https://posthog.unilist.ru
Backend NestJS → posthog-node → https://posthog.unilist.ru
                                        ↓
                               Caddy (reverse proxy, SSL)
                                        ↓
                               PostHog Docker containers
                               (VPS 37.9.7.141, /opt/posthog/)
```

## Файлы в этой папке

- `infrastructure.md` — сервер, docker-compose, .env, Caddy
- `code-integration.md` — frontend и backend код
- `pending.md` — что осталось сделать
