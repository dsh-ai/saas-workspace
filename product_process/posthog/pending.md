# PostHog — Что осталось сделать

## Срочно (блокирует работу аналитики)

### 1. Починить PostHog на сервере

**Проблема:** `https://posthog.unilist.ru` возвращает `502 Bad Gateway`.
Caddy работает, SSL есть, но PostHog backend не отвечает. Вероятно упали контейнеры.

**Нужен SSH доступ.** Наш IP `62.4.45.151` забанен fail2ban.

Варианты зайти:
- SSH с другого IP (мобильный интернет)
- Добавить Selectel Security Group: Allow TCP 22 for `62.4.45.151`

После входа проверить и поднять:
```bash
fail2ban-client set sshd unbanip 62.4.45.151
fail2ban-client set recidive unbanip 62.4.45.151
cd /opt/posthog
docker compose -f docker-compose.hobby.yml ps
docker compose -f docker-compose.hobby.yml up -d
```

### 2. Выставить env vars в Coolify

В Coolify (http://193.168.136.29:8000) добавить переменные для **обоих сервисов**:

**Frontend (Next.js):**
```
NEXT_PUBLIC_POSTHOG_KEY=<project api key из PostHog UI>
NEXT_PUBLIC_POSTHOG_HOST=https://posthog.unilist.ru
```

**Backend (NestJS):**
```
POSTHOG_KEY=<project api key из PostHog UI>
POSTHOG_HOST=https://posthog.unilist.ru
```

API Key: PostHog UI → Settings → Project → Project API Key

### 3. Smoke test

После деплоя с env vars:
1. Зарегистрировать тестового пользователя
2. Проверить PostHog → People — должен появиться `user_registered`
3. Сделать AI запрос — должен появиться `ai_request_completed`
4. Проверить pageview через `posthog.capture('$pageview')`

## Опционально

- Настроить алерты в PostHog (email при аномалиях)
- Добавить Cohorts для сегментации (trial vs paid)
- Dashboard с ключевыми метриками: DAU, retention, AI usage, conversion
- Добавить `$set_once` для first_seen_at при identify
