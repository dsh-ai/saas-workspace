# PostHog Integration Design

**Дата:** 2026-03-29
**Статус:** Approved

## Цель

Подключить продуктовую аналитику PostHog для отслеживания воронки онбординг → активация → retention с идентификацией пользователей по плану и профилю компании.

## Решения

- **Deployment:** Self-hosted на Selectel VPS `37.9.7.141` (4vCPU/8GB, там же GlitchTip)
- **Интеграция:** Frontend (posthog-js) + Backend (posthog-node) — гибридный подход
- **Домен:** `posthog.unilist.ru`

## Раздел 1: Развёртывание PostHog

- Docker Compose из официального репо `posthog/posthog`
- Собственный PostgreSQL и ClickHouse (не пересекается с GlitchTip)
- nginx reverse proxy → порт 8000
- SSL через Let's Encrypt (certbot)
- Данные в Docker volumes

## Раздел 2: Frontend интеграция (Next.js)

**Установка:** `posthog-js`

**PostHogProvider** оборачивает приложение:
- `NEXT_PUBLIC_POSTHOG_KEY` — ключ проекта
- `NEXT_PUBLIC_POSTHOG_HOST` — `https://posthog.unilist.ru`
- Pageviews — автоматически через Next.js router

**Идентификация:**
- После логина: `posthog.identify(userId, { email, plan, company, industry })`
- После логаута: `posthog.reset()`

**Стартовые события:**

| Событие | Когда |
|---|---|
| `questionnaire_created` | Создана анкета |
| `questionnaire_sent` | Отправлена ссылка клиенту |
| `ai_summary_viewed` | Открыт AI-анализ |
| `onboarding_completed` | Завершён онбординг |
| `upgrade_clicked` | Клик на апгрейд тарифа |

События расширяются по мере необходимости через `posthog.capture('event_name', { props })`.

## Раздел 3: Backend интеграция (NestJS)

**Установка:** `posthog-node`

**PostHogService** — singleton через DI:
- `POSTHOG_KEY` + `POSTHOG_HOST` из env
- Все вызовы асинхронные, не блокируют основной поток

**Стартовые события:**

| Событие | Где |
|---|---|
| `user_registered` | AuthService |
| `subscription_changed` | SubscriptionService |
| `ai_request_completed` | AI сервис (поля: `model`, `tokens`) |
| `questionnaire_response_received` | Webhook/response handler |

При регистрации — `posthog.identify()` с сервера для enrichment до первого логина.

## Env переменные

**Frontend (.env.local / Coolify):**
```
NEXT_PUBLIC_POSTHOG_KEY=phc_...
NEXT_PUBLIC_POSTHOG_HOST=https://posthog.unilist.ru
```

**Backend (.env / Coolify):**
```
POSTHOG_KEY=phc_...
POSTHOG_HOST=https://posthog.unilist.ru
```
