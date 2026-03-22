# Инфраструктура — план миграции на Selectel

> Цель: production на российском железе (152-ФЗ), staging остаётся Railway/Vercel
> Обновлено: 2026-03-10

## Итоговая архитектура

```
unilist.ru               → Tilda (лендинг, не трогаем)
app.unilist.ru           → Selectel VPS (production)
Railway / Vercel         → staging (дефолтные домены, как сейчас)
```

| Компонент | Staging | Production |
|-----------|---------|------------|
| Frontend (Next.js) | Vercel (дефолтный домен) | Coolify → app.unilist.ru |
| Backend (NestJS) | Railway (дефолтный домен) | Coolify → api.unilist.ru |
| PostgreSQL | Railway managed | Coolify (self-hosted) |
| Бэкапы БД | — | pg_dump → Selectel Object Storage |
| SSL | Vercel/Railway auto | Let's Encrypt via Coolify |

## Ветки и CI/CD

- `main` → автодеплой на Railway + Vercel (без изменений)
- `production` → автодеплой на Coolify через GitHub webhook

Релизный флоу: merge `main` → `production` = деплой на прод.

## Стоимость (ориентир)

| Ресурс | Цена/мес |
|--------|----------|
| Selectel VPS (2 CPU / 4 GB / 50 GB SSD) | ~1 500 ₽ |
| Selectel Object Storage (бэкапы, ~5 GB) | ~50 ₽ |
| **Итого** | **~1 550 ₽** |

Railway + Vercel (staging) остаются бесплатными на текущих объёмах.

---

## Пошаговый план

### Шаг 1: Selectel — создать VPS
- [x] Зарегистрироваться на selectel.ru (если нет аккаунта)
- [x] Создать VPS: Ubuntu 22.04 LTS, 2 CPU / 4 GB RAM / 50 GB SSD — IP: `193.168.136.29`
- [x] Настроить SSH-ключ (не пароль)
- [x] Зафиксировать IP адрес

### Шаг 2: Selectel — Object Storage для бэкапов
- [x] Создать бакет (приватный) для бэкапов PostgreSQL
- [x] Получить Access Key + Secret Key для S3 API

**S3 реквизиты** (ключи хранятся в 1Password → "Selectel S3 Keys"):
```
S3 Access Key: [1Password → Selectel S3 Keys]
S3 Secret Key: [1Password → Selectel S3 Keys]
S3 Endpoint:   s3.ru-7.storage.selcloud.ru
Bucket:        unilist-backups
```

### Шаг 3: Установка Coolify на VPS
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```
- [x] Войти в Coolify UI (http://193.168.136.29:8000)
- [x] Создать аккаунт, сохранить credentials

### Шаг 4: Подключить GitHub репозиторий в Coolify
- [x] Добавить GitHub App в Coolify
- [x] Подключить репозиторий dsh-ai/my_saas
- [x] Настроить два сервиса: frontend (Next.js) и backend (NestJS)
- [x] Указать ветку `production` для деплоя

### Шаг 5: PostgreSQL в Coolify
- [x] Создать PostgreSQL instance в Coolify (Databases → PostgreSQL 16)
- [x] Настроить бэкапы: ежедневно → Selectel S3

**DATABASE_URL (internal):** `postgres://postgres:[password]@ydzgd8zcytusx7lnd9fmcmwk:5432/postgres`
Полный URL → 1Password → "Coolify DATABASE_URL"
  - S3 endpoint: `s3.selcdn.ru`
  - Bucket: созданный на шаге 2
  - Расписание: каждый день в 03:00 MSK
- [ ] Retention: хранить последние 14 дней

### Шаг 6: Перенос данных из Railway
- [x] Сделать дамп Railway PostgreSQL (435KB)
- [x] Залить в Selectel PostgreSQL (через docker exec)

### Шаг 7: Environment variables
- [x] Скопировать все .env переменные из Railway/Vercel в Coolify
- [x] Обновить DATABASE_URL → Selectel PostgreSQL
- [x] Обновить FRONTEND_URL → https://app.unilist.ru
- [x] Обновить BACKEND_URL → https://api.unilist.ru

### Шаг 8: DNS на reg.ru
- [x] Сменить NS с tildadns.com на ns1/ns2.reg.ru
- [x] Добавить A-запись: `app.unilist.ru` → 193.168.136.29
- [x] Добавить A-запись: `api.unilist.ru` → 193.168.136.29
- [ ] Дождаться propagation (до 24 часов, обычно быстрее)

### Шаг 9: Тестирование
- [x] Проверить https://app.unilist.ru — фронт открывается
- [x] Проверить https://api.unilist.ru — бэкенд отвечает
- [x] Проверить регистрацию — работает
- [ ] Проверить вход, создание шаблона, оплату
- [ ] Проверить, что бэкап создался в Object Storage

### Шаг 10: Переключение
- [x] Исправить Dockerfile фронтенда (dev → production build)
- [x] Исправить Dockerfile фронтенда: BACKEND_URL как build ARG (иначе Next.js бакает localhost в сборку)
- [x] BACKEND_URL = https://api.unilist.ru (стабильный публичный домен, не зависит от имени контейнера)
- [ ] Уведомить тестовых пользователей (если есть)
- [ ] Production готов — Railway/Vercel остаются staging

---

## После миграции — дополнительно

- [ ] Настроить мониторинг (Coolify встроенный или UptimeRobot — бесплатный)
- [ ] Настроить алерты на падение сервиса (email/telegram)
- [ ] Подключить Яндекс.Метрику на app.unilist.ru

---

## PostHog self-hosted (продуктовая аналитика)

> Разворачивается на **отдельном** VPS — ClickHouse + Kafka + Redis не совместимы по ресурсам с основным приложением.

### Архитектура

```
analytics.unilist.ru  →  Selectel VPS #2 (PostHog)
app.unilist.ru        →  Selectel VPS #1 (основное приложение)
```

### Стоимость (дополнительно)

| Ресурс | Цена/мес |
|--------|----------|
| Selectel VPS #2 (2 CPU / 4 GB / 50 GB SSD) | ~1 500 ₽ |
| **Итого с основным** | **~3 050 ₽** |

> Лимит hobby-деплоя PostHog: ~1M событий/мес — хватит надолго.

### Шаг 11: VPS #2 для PostHog

- [ ] Создать VPS #2 на Selectel: Ubuntu 22.04, 2 CPU / 4 GB RAM / 50 GB SSD
- [ ] Настроить SSH-ключ
- [ ] Установить Docker + Docker Compose:
  ```bash
  curl -fsSL https://get.docker.com | sh
  ```

### Шаг 12: Установка PostHog

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/posthog/posthog/HEAD/bin/deploy-hobby)"
```

- [ ] Запустить скрипт установки (hobby deployment)
- [ ] Указать домен `analytics.unilist.ru` при установке
- [ ] Дождаться запуска всех контейнеров (~5-10 мин)

### Шаг 13: DNS для PostHog

- [ ] Добавить A-запись: `analytics.unilist.ru` → IP VPS #2
- [ ] SSL настраивается автоматически через Caddy (в комплекте PostHog)

### Шаг 14: Подключить PostHog к приложению

**Frontend (Next.js):**
```bash
npm install posthog-js
```
- [ ] Добавить `NEXT_PUBLIC_POSTHOG_KEY` и `NEXT_PUBLIC_POSTHOG_HOST=https://analytics.unilist.ru` в env
- [ ] Инициализировать PostHog в `_app.tsx` или layout

**Backend (NestJS):**
```bash
npm install posthog-node
```
- [ ] Трекать серверные события (регистрация, создание шаблона, оплата)

### Шаг 15: Настроить ключевые события и воронки

- [ ] Воронка онбординга: `signed_up` → `template_created` → `survey_sent` → `link_filled`
- [ ] Воронка монетизации: `trial_started` → `payment_page_viewed` → `subscription_created`
- [ ] Dashboard: активные пользователи, retention, конверсия trial→paid
