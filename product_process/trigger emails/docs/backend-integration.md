# Email Lifecycle — Backend Integration Docs

> Версия: 1.0 · 2026-03-28
> ESP: UnisenderGo (transactional email API)
> Stack: NestJS 11 + PostgreSQL

---

## 1. Обзор

14 писем, разбитых на два типа:

| Тип | Отправка | Писем |
|-----|----------|-------|
| **Transactional** (T1–T5) | Мгновенно, в ответ на событие | 5 |
| **Lifecycle** (L1–L9) | Scheduled / условные | 9 |

Все шаблоны загружены в UnisenderGo. Каждый шаблон имеет `template_id` в системе UnisenderGo. Переменные передаются в поле `substitutions` при отправке.

---

## 2. UnisenderGo API

**Метод отправки:** `POST /en/transactional/smtp/messages`

Базовый запрос:
```typescript
{
  message: {
    template_id: "unilist-T1-confirm-email", // ID шаблона в UnisenderGo
    to: [{ email: "user@example.com" }],
    substitutions: {
      confirm_url: "https://app.unilist.ru/auth/confirm?token=...",
    },
    from_email: "no-reply@unilist.ru",
    from_name: "Unilist",
  }
}
```

**Переменные в шаблонах** используют формат `{{variable_name}}`.

---

## 3. Transactional письма (T1–T5)

Отправляются синхронно в момент события через `EmailService.send(template, to, vars)`.

---

### T1 — Подтверждение email

**Событие:** пользователь зарегистрировался
**Когда слать:** сразу при создании `User` в БД, до подтверждения email
**Template ID:** `unilist-T1-confirm-email`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `confirm_url` | `string` | `https://app.unilist.ru/auth/confirm?token={token}` — токен одноразовый, TTL 24ч |

**Примечание:** Токен хранить в таблице `email_confirmations` с `expires_at = NOW() + INTERVAL '24 hours'`.

---

### T2 — Добро пожаловать

**Событие:** пользователь подтвердил email
**Когда слать:** после успешной верификации токена из T1
**Template ID:** `unilist-T2-welcome`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `create_url` | `string` | `https://app.unilist.ru/surveys/new` |
| `demo_url` | `string` | `https://app.unilist.ru/demo` |

---

### T3 — Квитанция об оплате

**Событие:** успешное списание через платёжный шлюз
**Когда слать:** в webhook-обработчике `payment.succeeded`
**Template ID:** `unilist-T3-payment-success`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `plan_name` | `string` | `"Basic"` или `"AI"` |
| `amount` | `string` | Сумма без знака, например `"1990"` |
| `period` | `string` | Человекочитаемый период, например `"апрель 2026"` |
| `next_billing_date` | `string` | Дата след. списания, например `"28 апреля 2026"` |
| `account_url` | `string` | `https://app.unilist.ru/settings/billing` |

---

### T4 — Ошибка оплаты

**Событие:** платёж не прошёл (первая попытка)
**Когда слать:** в webhook-обработчике `payment.failed` (iteration = 1)
**Template ID:** `unilist-T4-payment-failed`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `amount` | `string` | Сумма, которую пытались списать |
| `days_left` | `string` | Количество дней до блокировки, `"7"` |
| `payment_url` | `string` | `https://app.unilist.ru/settings/billing` |

---

### T5 — Сброс пароля

**Событие:** пользователь запросил сброс пароля
**Когда слать:** сразу при POST `/auth/forgot-password`
**Template ID:** `unilist-T5-reset-password`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `reset_url` | `string` | `https://app.unilist.ru/auth/reset-password?token={token}` — TTL 1ч |

---

## 4. Lifecycle письма (L1–L9)

Отправляются через scheduled jobs (cron или queue). Рекомендуется использовать Bull/BullMQ queue для надёжности.

---

### L1 — Онбординг: день 1

**Триггер:** +1 час после T2 (подтверждение email)
**Условие:** всегда (нет ограничений)
**Реализация:** при отправке T2 добавить job в очередь с `delay: 3600000` (1ч)
**Template ID:** `unilist-L1-onboarding-day1`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `create_url` | `string` | `https://app.unilist.ru/surveys/new` |
| `templates_url` | `string` | `https://app.unilist.ru/templates` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | `https://app.unilist.ru/unsubscribe?token={unsubscribe_token}` |

---

### L2 — Онбординг: день 3

**Триггер:** день 3 после регистрации (cron, запускается раз в сутки)
**Условие:** пользователь ни разу не отправил анкету (`surveys.sent_count = 0`)
**Template ID:** `unilist-L2-onboarding-day3`

**SQL для выборки получателей:**
```sql
SELECT u.id, u.email
FROM users u
WHERE u.email_confirmed = true
  AND u.created_at::date = CURRENT_DATE - INTERVAL '3 days'
  AND NOT EXISTS (
    SELECT 1 FROM survey_sends ss
    WHERE ss.user_id = u.id
  )
  AND NOT EXISTS (
    SELECT 1 FROM email_suppressions es
    WHERE es.user_id = u.id AND es.type = 'lifecycle'
  );
```

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `create_url` | `string` | `https://app.unilist.ru/surveys/new` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

### L3 — Онбординг: день 7

**Триггер:** день 7 после регистрации (cron ежедневно)
**Условие:** нет подключённой CRM-интеграции (`integrations WHERE type = 'bitrix24'` не существует)
**Template ID:** `unilist-L3-onboarding-day7`

**SQL для выборки:**
```sql
SELECT u.id, u.email
FROM users u
WHERE u.email_confirmed = true
  AND u.created_at::date = CURRENT_DATE - INTERVAL '7 days'
  AND NOT EXISTS (
    SELECT 1 FROM integrations i
    WHERE i.user_id = u.id AND i.type = 'bitrix24' AND i.active = true
  )
  AND NOT EXISTS (
    SELECT 1 FROM email_suppressions es
    WHERE es.user_id = u.id AND es.type = 'lifecycle'
  );
```

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `integrations_url` | `string` | `https://app.unilist.ru/settings/integrations` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

### L4 — Trial заканчивается (за 3 дня)

**Триггер:** cron ежедневно, за 3 дня до `subscription.trial_ends_at`
**Условие:** пользователь на trial, не перешёл на платный тариф
**Template ID:** `unilist-L4-trial-ending`

**SQL для выборки:**
```sql
SELECT u.id, u.email, s.trial_ends_at
FROM users u
JOIN subscriptions s ON s.user_id = u.id
WHERE s.plan = 'trial'
  AND s.trial_ends_at::date = CURRENT_DATE + INTERVAL '3 days'
  AND NOT EXISTS (
    SELECT 1 FROM email_suppressions es
    WHERE es.user_id = u.id AND es.type = 'lifecycle'
  );
```

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `trial_end_date` | `string` | Дата окончания, например `"31 марта 2026"` |
| `pricing_url` | `string` | `https://app.unilist.ru/settings/billing/upgrade` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

### L5 — Trial истёк

**Триггер:** cron ежедневно, в день окончания trial
**Условие:** `trial_ends_at::date = CURRENT_DATE`, план всё ещё `trial`
**Template ID:** `unilist-L5-trial-expired`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `pricing_url` | `string` | `https://app.unilist.ru/settings/billing/upgrade` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

### L6 — Напоминание об оплате (за 5 дней)

**Триггер:** cron ежедневно, за 5 дней до `subscription.next_billing_date`
**Условие:** активная платная подписка, есть привязанная карта
**Template ID:** `unilist-L6-payment-reminder-5d`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `plan_name` | `string` | `"Basic"` или `"AI"` |
| `amount` | `string` | Сумма списания, `"1990"` |
| `billing_date` | `string` | Дата списания, `"2 апреля 2026"` |
| `card_last4` | `string` | Последние 4 цифры карты, `"4242"` |
| `billing_url` | `string` | `https://app.unilist.ru/settings/billing` |
| `pricing_url` | `string` | `https://app.unilist.ru/settings/billing/upgrade` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

### L7 — Предстоящее списание (за 1 день)

**Триггер:** cron ежедневно, за 1 день до `subscription.next_billing_date`
**Template ID:** `unilist-L7-payment-reminder-1d`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `plan_name` | `string` | `"Basic"` или `"AI"` |
| `amount` | `string` | Сумма списания |
| `card_last4` | `string` | Последние 4 цифры карты |
| `billing_url` | `string` | `https://app.unilist.ru/settings/billing` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

### L8 — Подписка приостановлена

**Триггер:** webhook `payment.failed` при iteration = 2 (второй неуспешный платёж подряд)
**Действие:** помимо письма — установить `subscription.status = 'paused'`, ограничить доступ
**Template ID:** `unilist-L8-subscription-paused`

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `payment_url` | `string` | `https://app.unilist.ru/settings/billing` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

### L9 — Реактивация

**Триггер:** cron ежедневно, 14 дней без активности
**Условие:** `last_active_at < NOW() - INTERVAL '14 days'`, подписка активна
**Template ID:** `unilist-L9-reactivation`

**SQL для выборки:**
```sql
SELECT u.id, u.email
FROM users u
JOIN subscriptions s ON s.user_id = u.id
WHERE s.status = 'active'
  AND u.last_active_at < NOW() - INTERVAL '14 days'
  AND u.last_active_at >= NOW() - INTERVAL '15 days' -- только новые, не повторять
  AND NOT EXISTS (
    SELECT 1 FROM email_suppressions es
    WHERE es.user_id = u.id AND es.type = 'lifecycle'
  );
```

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `dashboard_url` | `string` | `https://app.unilist.ru/dashboard` |
| `feedback_url` | `string` | `https://app.unilist.ru/feedback` |
| `settings_url` | `string` | `https://app.unilist.ru/settings/notifications` |
| `unsubscribe_url` | `string` | Персональный unsubscribe-токен |

---

## 5. Инфраструктура отписки

Каждому пользователю генерировать `unsubscribe_token` (UUID) при создании аккаунта.

**Маршрут:** `GET /unsubscribe?token={token}`
**Действие:** установить `email_suppressions.type = 'lifecycle'` — пользователь перестаёт получать lifecycle-письма, но продолжает получать transactional (T1–T5).

Transactional письма отпискам не подчиняются (подтверждение, сброс пароля, квитанции — это критическая коммуникация).

---

## 6. Таблицы БД (минимальный набор)

```sql
-- Уже существующие (предположительно)
users (id, email, email_confirmed, created_at, last_active_at)
subscriptions (id, user_id, plan, status, trial_ends_at, next_billing_date)
survey_sends (id, user_id, survey_id, sent_at)
integrations (id, user_id, type, active)

-- Новые таблицы
CREATE TABLE email_confirmations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE email_suppressions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(20) NOT NULL CHECK (type IN ('lifecycle', 'all')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, type)
);

-- Для unsubscribe-токена: добавить колонку в users
ALTER TABLE users ADD COLUMN unsubscribe_token UUID DEFAULT gen_random_uuid();
CREATE UNIQUE INDEX ON users(unsubscribe_token);
```

---

## 7. NestJS — структура EmailService

```typescript
// email/email.service.ts
@Injectable()
export class EmailService {
  async send(templateId: string, to: string, vars: Record<string, string>) {
    // Вызов UnisenderGo API
  }

  // Transactional
  async sendConfirmEmail(user: User, token: string) { ... }
  async sendWelcome(user: User) { ... }
  async sendPaymentSuccess(user: User, payment: Payment) { ... }
  async sendPaymentFailed(user: User, payment: Payment, daysLeft: number) { ... }
  async sendResetPassword(user: User, token: string) { ... }

  // Lifecycle (вызываются из SchedulerService или QueueService)
  async sendOnboardingDay1(user: User) { ... }
  async sendOnboardingDay3(user: User) { ... }
  async sendOnboardingDay7(user: User) { ... }
  async sendTrialEnding(user: User, subscription: Subscription) { ... }
  async sendTrialExpired(user: User) { ... }
  async sendPaymentReminder5d(user: User, subscription: Subscription) { ... }
  async sendPaymentReminder1d(user: User, subscription: Subscription) { ... }
  async sendSubscriptionPaused(user: User) { ... }
  async sendReactivation(user: User) { ... }
}
```

---

## 8. Cron-расписание

| Job | Расписание | Письмо |
|-----|-----------|--------|
| `onboarding-day3` | `0 10 * * *` (каждый день в 10:00) | L2 |
| `onboarding-day7` | `0 10 * * *` | L3 |
| `trial-ending-3d` | `0 10 * * *` | L4 |
| `trial-expired` | `0 10 * * *` | L5 |
| `payment-reminder-5d` | `0 10 * * *` | L6 |
| `payment-reminder-1d` | `0 10 * * *` | L7 |
| `reactivation` | `0 10 * * *` | L9 |

L1 — через Bull queue с delay, не cron.
L8 — через payment webhook, не cron.

---

## 9. Защита от дублирования

Перед отправкой каждого lifecycle-письма проверять таблицу `email_sends_log`:

```sql
CREATE TABLE email_sends_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  template_id VARCHAR(50) NOT NULL,
  sent_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX ON email_sends_log(user_id, template_id, DATE(sent_at));
```

Если запись уже есть за сегодня — не отправлять повторно.
