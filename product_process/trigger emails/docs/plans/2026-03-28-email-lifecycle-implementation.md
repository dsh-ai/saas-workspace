# Email Lifecycle — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать полный Email Design System из 14 HTML-шаблонов для UnisenderGo — 2 базовых шаблона (transactional + lifecycle) и 14 папок с готовыми письмами.

**Architecture:** Две семьи шаблонов (Transactional / Lifecycle). Каждое письмо — отдельная папка с `template.html` (финальный HTML для UnisenderGo) и `content.md` (тема, прехедер, переменные). Базовые шаблоны в `_base/` — основа для всех писем.

**Tech Stack:** HTML email (таблицы, inline CSS), UnisenderGo variables `{{variable}}`, Golos Text (web font + Arial fallback), цвета #0000FF / #111111 / #F6F6F6.

**Design reference:** `docs/plans/2026-03-28-email-lifecycle-design.md`

---

## Task 1: Структура директорий

**Files:**
- Create: `templates/_base/` (директория)
- Create: `templates/T1-confirm-email/` и ещё 13 папок

**Step 1: Создать структуру**

```bash
cd "/Users/shuvaev/Продукты/unilist/saas-workspace/product_process/trigger emails"
mkdir -p templates/_base
mkdir -p templates/T1-confirm-email
mkdir -p templates/T2-welcome
mkdir -p templates/T3-payment-success
mkdir -p templates/T4-payment-failed
mkdir -p templates/T5-reset-password
mkdir -p templates/L1-onboarding-day1
mkdir -p templates/L2-onboarding-day3
mkdir -p templates/L3-onboarding-day7
mkdir -p templates/L4-trial-ending
mkdir -p templates/L5-trial-expired
mkdir -p templates/L6-payment-reminder-5d
mkdir -p templates/L7-payment-reminder-1d
mkdir -p templates/L8-subscription-paused
mkdir -p templates/L9-reactivation
```

**Step 2: Проверить**

```bash
ls templates/
```
Ожидается: 15 папок (`_base` + 14 писем)

**Step 3: Commit**

```bash
git add -A && git commit -m "feat(emails): scaffold directory structure for 14 email templates"
```

---

## Task 2: Базовый шаблон — Семья A (Transactional)

**Files:**
- Create: `templates/_base/transactional.html`

Минималистичный шаблон: белый фон письма, #F6F6F6 фон страницы, без синей полоски сверху, простой футер.

**Step 1: Создать файл**

```html
<!-- templates/_base/transactional.html -->
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>{{subject}}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;700;900&display=swap');
  body { margin: 0; padding: 0; background-color: #F6F6F6; font-family: 'Golos Text', Arial, sans-serif; }
  .email-wrapper { background-color: #F6F6F6; padding: 32px 16px; }
  .email-container { max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; }
  .email-header { padding: 28px 40px 20px; border-bottom: 1px solid #F0F0F0; }
  .email-logo { font-family: 'Golos Text', Arial, sans-serif; font-weight: 900; font-size: 20px; color: #111111; text-decoration: none; letter-spacing: -0.5px; }
  .email-body { padding: 32px 40px; }
  .email-h1 { font-family: 'Golos Text', Arial, sans-serif; font-weight: 900; font-size: 24px; color: #111111; margin: 0 0 16px; line-height: 1.3; }
  .email-text { font-family: 'Golos Text', Arial, sans-serif; font-weight: 400; font-size: 15px; color: #111111; line-height: 1.6; margin: 0 0 24px; }
  .email-btn { display: inline-block; background-color: #0000FF; color: #FFFFFF !important; font-family: 'Golos Text', Arial, sans-serif; font-weight: 700; font-size: 15px; text-decoration: none; padding: 14px 28px; border-radius: 8px; margin-bottom: 24px; }
  .email-small { font-family: 'Golos Text', Arial, sans-serif; font-weight: 400; font-size: 12px; color: #999999; line-height: 1.5; margin: 0 0 8px; }
  .email-footer { padding: 20px 40px 28px; border-top: 1px solid #F0F0F0; }
  .email-footer-text { font-family: 'Golos Text', Arial, sans-serif; font-weight: 400; font-size: 12px; color: #999999; margin: 0; }
  .email-footer-text a { color: #999999; text-decoration: underline; }
</style>
</head>
<body>
<div class="email-wrapper">
  <table class="email-container" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;margin:0 auto;">
    <!-- HEADER -->
    <tr>
      <td class="email-header">
        <a href="https://app.unilist.ru" class="email-logo">Unilist</a>
      </td>
    </tr>
    <!-- BODY -->
    <tr>
      <td class="email-body">
        <!-- PASTE CONTENT HERE -->
        <h1 class="email-h1">{{h1}}</h1>
        <p class="email-text">{{body_text}}</p>
        <a href="{{cta_url}}" class="email-btn">{{cta_label}}</a>
        <p class="email-small">{{small_text}}</p>
      </td>
    </tr>
    <!-- FOOTER -->
    <tr>
      <td class="email-footer">
        <p class="email-footer-text">© 2026 Unilist &nbsp;·&nbsp; <a href="{{unsubscribe_url}}">Отписаться</a></p>
      </td>
    </tr>
  </table>
</div>
</body>
</html>
```

**Step 2: Визуальная проверка**

Открыть файл в браузере. Проверить:
- Фон страницы #F6F6F6
- Карточка письма белая, border-radius 12px
- Логотип "Unilist" жирный, чёрный
- Кнопка синяя #0000FF

**Step 3: Commit**

```bash
git add templates/_base/transactional.html
git commit -m "feat(emails): add base transactional template (Family A)"
```

---

## Task 3: Базовый шаблон — Семья B (Lifecycle)

**Files:**
- Create: `templates/_base/lifecycle.html`

Отличия от transactional: синяя полоска 4px сверху карточки, акцентный подзаголовок синим, блок-инсайт с левой синей чертой, вторичная ссылка, расширенный футер.

**Step 1: Создать файл**

```html
<!-- templates/_base/lifecycle.html -->
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>{{subject}}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;700;900&display=swap');
  body { margin: 0; padding: 0; background-color: #F6F6F6; font-family: 'Golos Text', Arial, sans-serif; }
  .email-wrapper { background-color: #F6F6F6; padding: 32px 16px; }
  .email-container { max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border-radius: 12px; overflow: hidden; border-top: 4px solid #0000FF; }
  .email-header { padding: 24px 40px 20px; border-bottom: 1px solid #F0F0F0; }
  .email-logo { font-family: 'Golos Text', Arial, sans-serif; font-weight: 900; font-size: 20px; color: #111111; text-decoration: none; letter-spacing: -0.5px; }
  .email-body { padding: 32px 40px; }
  .email-h1 { font-family: 'Golos Text', Arial, sans-serif; font-weight: 900; font-size: 24px; color: #111111; margin: 0 0 8px; line-height: 1.3; }
  .email-accent { font-family: 'Golos Text', Arial, sans-serif; font-weight: 700; font-size: 16px; color: #0000FF; margin: 0 0 20px; line-height: 1.4; }
  .email-text { font-family: 'Golos Text', Arial, sans-serif; font-weight: 400; font-size: 15px; color: #111111; line-height: 1.6; margin: 0 0 24px; }
  .email-insight { background-color: #F6F6F6; border-left: 3px solid #0000FF; border-radius: 0 8px 8px 0; padding: 16px 20px; margin: 0 0 28px; }
  .email-insight p { font-family: 'Golos Text', Arial, sans-serif; font-weight: 700; font-size: 14px; color: #111111; margin: 0; line-height: 1.5; }
  .email-btn { display: inline-block; background-color: #0000FF; color: #FFFFFF !important; font-family: 'Golos Text', Arial, sans-serif; font-weight: 700; font-size: 15px; text-decoration: none; padding: 14px 28px; border-radius: 8px; margin-bottom: 20px; }
  .email-secondary { font-family: 'Golos Text', Arial, sans-serif; font-weight: 400; font-size: 14px; color: #0000FF; text-decoration: none; display: block; margin-bottom: 8px; }
  .email-footer { padding: 20px 40px 28px; border-top: 1px solid #F0F0F0; }
  .email-footer-text { font-family: 'Golos Text', Arial, sans-serif; font-weight: 400; font-size: 12px; color: #999999; margin: 0; }
  .email-footer-text a { color: #999999; text-decoration: underline; }
</style>
</head>
<body>
<div class="email-wrapper">
  <table class="email-container" cellpadding="0" cellspacing="0" width="100%" style="max-width:600px;margin:0 auto;">
    <!-- HEADER -->
    <tr>
      <td class="email-header">
        <a href="https://app.unilist.ru" class="email-logo">Unilist</a>
      </td>
    </tr>
    <!-- BODY -->
    <tr>
      <td class="email-body">
        <!-- PASTE CONTENT HERE -->
        <h1 class="email-h1">{{h1}}</h1>
        <p class="email-accent">{{accent_text}}</p>
        <p class="email-text">{{body_text}}</p>
        <!-- INSIGHT BLOCK (optional, remove if not needed) -->
        <div class="email-insight">
          <p>{{insight_text}}</p>
        </div>
        <a href="{{cta_url}}" class="email-btn">{{cta_label}}</a><br>
        <a href="{{secondary_url}}" class="email-secondary">{{secondary_label}}</a>
      </td>
    </tr>
    <!-- FOOTER -->
    <tr>
      <td class="email-footer">
        <p class="email-footer-text">© 2026 Unilist &nbsp;·&nbsp; <a href="{{settings_url}}">Настройки уведомлений</a> &nbsp;·&nbsp; <a href="{{unsubscribe_url}}">Отписаться</a></p>
      </td>
    </tr>
  </table>
</div>
</body>
</html>
```

**Step 2: Визуальная проверка**

Открыть в браузере. Проверить:
- Синяя полоска 4px сверху карточки
- Акцент-текст синим
- Блок-инсайт с серым фоном и синей левой чертой
- Кнопка + вторичная ссылка

**Step 3: Commit**

```bash
git add templates/_base/lifecycle.html
git commit -m "feat(emails): add base lifecycle template (Family B)"
```

---

## Task 4: T1 — Подтверждение email

**Files:**
- Create: `templates/T1-confirm-email/template.html`
- Create: `templates/T1-confirm-email/content.md`

**Step 1: Создать content.md**

```markdown
# T1 — Подтверждение email

**Семья:** Transactional (A)
**Триггер:** Регистрация нового пользователя
**Тип:** Мгновенный

## Метаданные
- **Subject:** Подтвердите почту — и начнём
- **Preheader:** Одна кнопка, и ваш аккаунт готов

## Переменные UnisenderGo
- `{{confirm_url}}` — ссылка для подтверждения (действует 24 часа)

## Контент
- **H1:** Почти готово
- **Текст:** Вы зарегистрировались в Unilist. Нажмите кнопку ниже, чтобы подтвердить email и войти в аккаунт.
- **CTA:** Подтвердить email → `{{confirm_url}}`
- **Мелкий текст:** Ссылка действует 24 часа. Если вы не регистрировались — просто проигнорируйте это письмо.
```

**Step 2: Создать template.html** (на основе `_base/transactional.html`, подставить контент T1)

Скопировать `_base/transactional.html`, заменить переменные на реальный контент T1. Убрать неиспользуемые блоки. Inline CSS оставить как есть.

**Step 3: Визуальная проверка в браузере**

**Step 4: Commit**

```bash
git add templates/T1-confirm-email/
git commit -m "feat(emails): add T1 confirm email template"
```

---

## Task 5: T2 — Добро пожаловать

**Files:**
- Create: `templates/T2-welcome/template.html`
- Create: `templates/T2-welcome/content.md`

**content.md:**
```markdown
# T2 — Добро пожаловать

**Семья:** Transactional (A)
**Триггер:** Пользователь подтвердил email
**Тип:** Мгновенный

## Метаданные
- **Subject:** Добро пожаловать в Unilist
- **Preheader:** Аккаунт подтверждён — вот с чего начать

## Переменные
- `{{create_url}}` — ссылка на создание опросного листа
- `{{demo_url}}` — ссылка на демо

## Контент
- **H1:** Аккаунт активирован
- **Текст:** Теперь вы можете создавать опросные листы, отправлять их клиентам и видеть всё, что происходит после отправки — открыл, перечитал, завис на вопросе.
- **CTA:** Создать первый опросный лист → `{{create_url}}`
- **Вторичная:** Посмотреть демо → `{{demo_url}}`
```

**Commit:**
```bash
git add templates/T2-welcome/
git commit -m "feat(emails): add T2 welcome template"
```

---

## Task 6: T3 — Квитанция об оплате

**Files:**
- Create: `templates/T3-payment-success/template.html`
- Create: `templates/T3-payment-success/content.md`

**Особенность:** Добавить таблицу с данными об оплате (тариф / период / сумма / следующее списание). Стиль таблицы — строки с `border-bottom: 1px solid #F0F0F0`, label `#666666 13px`, value `#111111 15px bold`.

**content.md:**
```markdown
# T3 — Квитанция об оплате

**Семья:** Transactional (A)
**Триггер:** Успешный платёж
**Тип:** Мгновенный

## Метаданные
- **Subject:** Оплата прошла — квитанция внутри
- **Preheader:** Тариф {{plan_name}}, списано {{amount}}₽

## Переменные
- `{{plan_name}}` — название тарифа (Basic / AI)
- `{{amount}}` — сумма списания
- `{{period}}` — период (например, "апрель 2026")
- `{{next_billing_date}}` — дата следующего списания
- `{{account_url}}` — ссылка в аккаунт

## Контент
- **H1:** Оплата подтверждена
- **Таблица:** Тариф / Период / Сумма / Следующее списание
- **CTA:** Открыть аккаунт → `{{account_url}}`
- **Мелкий текст:** Для бухгалтерии: закрывающие документы доступны в настройках аккаунта.
```

**Commit:**
```bash
git add templates/T3-payment-success/
git commit -m "feat(emails): add T3 payment success template"
```

---

## Task 7: T4 — Ошибка оплаты

**Files:**
- Create: `templates/T4-payment-failed/template.html`
- Create: `templates/T4-payment-failed/content.md`

**content.md:**
```markdown
# T4 — Ошибка оплаты

**Семья:** Transactional (A)
**Триггер:** Неуспешный платёж (первая попытка)
**Тип:** Мгновенный

## Метаданные
- **Subject:** Не удалось списать оплату
- **Preheader:** Проверьте карту — доступ сохраняется ещё {{days_left}} дней

## Переменные
- `{{amount}}` — сумма, которую не удалось списать
- `{{days_left}}` — количество дней до блокировки (7)
- `{{payment_url}}` — ссылка на страницу оплаты

## Контент
- **H1:** Платёж не прошёл
- **Текст:** Мы попробовали списать {{amount}}₽, но что-то пошло не так. Доступ к аккаунту сохраняется ещё {{days_left}} дней — обновите способ оплаты, чтобы не прерывать работу.
- **CTA:** Обновить способ оплаты → `{{payment_url}}`
```

**Commit:**
```bash
git add templates/T4-payment-failed/
git commit -m "feat(emails): add T4 payment failed template"
```

---

## Task 8: T5 — Сброс пароля

**Files:**
- Create: `templates/T5-reset-password/template.html`
- Create: `templates/T5-reset-password/content.md`

**content.md:**
```markdown
# T5 — Сброс пароля

**Семья:** Transactional (A)
**Триггер:** Пользователь запросил сброс пароля
**Тип:** Мгновенный

## Метаданные
- **Subject:** Сброс пароля Unilist
- **Preheader:** Ссылка действует 1 час

## Переменные
- `{{reset_url}}` — ссылка для сброса (действует 1 час)

## Контент
- **H1:** Сброс пароля
- **Текст:** Мы получили запрос на сброс пароля для вашего аккаунта. Если это были вы — нажмите кнопку ниже.
- **CTA:** Установить новый пароль → `{{reset_url}}`
- **Мелкий текст:** Если вы не запрашивали сброс — просто проигнорируйте. Пароль останется прежним. Ссылка действует 1 час.
```

**Commit:**
```bash
git add templates/T5-reset-password/
git commit -m "feat(emails): add T5 reset password template"
```

---

## Task 9: L1 — Онбординг день 1

**Files:**
- Create: `templates/L1-onboarding-day1/template.html`
- Create: `templates/L1-onboarding-day1/content.md`

**Семья B.** Включить блок-инсайт.

**content.md:**
```markdown
# L1 — Онбординг: день 1

**Семья:** Lifecycle (B)
**Триггер:** +1 час после подтверждения email
**Тип:** Задержанный (delay: 1h)

## Метаданные
- **Subject:** Один шаг — и вы уже видите клиента
- **Preheader:** Создайте первый опросный лист за 3 минуты

## Переменные
- `{{create_url}}` — создать опросный лист
- `{{templates_url}}` — галерея шаблонов

## Контент
- **H1:** Создайте первый опросный лист
- **Акцент (синий):** Пока клиент не заполнил анкету — вы не знаете, что у него происходит
- **Текст:** Unilist показывает, открыл ли клиент анкету, сколько раз вернулся, на каком вопросе завис. Это именно тот момент, когда стоит позвонить — не через неделю, а сейчас.
- **Инсайт:** Клиенты, которые возвращаются к анкете дважды, закрываются в 2,3× чаще. Вы будете видеть таких в реальном времени.
- **CTA:** Создать опросный лист → `{{create_url}}`
- **Вторичная:** Посмотреть шаблоны → `{{templates_url}}`
```

**Commit:**
```bash
git add templates/L1-onboarding-day1/
git commit -m "feat(emails): add L1 onboarding day 1 template"
```

---

## Task 10: L2 — Онбординг день 3

**Files:**
- Create: `templates/L2-onboarding-day3/template.html`
- Create: `templates/L2-onboarding-day3/content.md`

**Семья B. Условие:** отправляется только если пользователь не создал ни одной анкеты.

**content.md:**
```markdown
# L2 — Онбординг: день 3

**Семья:** Lifecycle (B)
**Триггер:** День 3 после регистрации + нет отправленных анкет
**Тип:** Условный

## Метаданные
- **Subject:** Как быстро понять, стоит ли тратить время на лида
- **Preheader:** РОПы из вашей отрасли используют этот подход

## Переменные
- `{{create_url}}` — создать анкету

## Контент
- **H1:** Квалификация за 5 минут — без лишних звонков
- **Акцент:** —
- **Текст:** Обычная ситуация: менеджер час общался с клиентом, отправил анкету — и тишина. Неизвестно: он думает, забыл или уже выбрал конкурента. Unilist убирает эту неопределённость. Вы видите активность клиента в анкете — и менеджер звонит в нужный момент, а не наугад.
- **Инсайт:** Создайте анкету под ваш типовой лид и отправьте первому клиенту — результат увидите уже сегодня.
- **CTA:** Создать анкету сейчас → `{{create_url}}`
```

**Commit:**
```bash
git add templates/L2-onboarding-day3/
git commit -m "feat(emails): add L2 onboarding day 3 template"
```

---

## Task 11: L3 — Онбординг день 7

**Files:**
- Create: `templates/L3-onboarding-day7/template.html`
- Create: `templates/L3-onboarding-day7/content.md`

**Семья B. Условие:** нет подключённой CRM-интеграции.

**content.md:**
```markdown
# L3 — Онбординг: день 7

**Семья:** Lifecycle (B)
**Триггер:** День 7 после регистрации + нет CRM-интеграции
**Тип:** Условный

## Метаданные
- **Subject:** Ваши анкеты уже в Unilist — данные ещё не в CRM
- **Preheader:** Подключите Bitrix24 за 2 минуты

## Переменные
- `{{integrations_url}}` — страница интеграций

## Контент
- **H1:** Подключите CRM — данные пойдут сами
- **Текст:** Когда клиент заполняет анкету, Unilist может автоматически создавать лид или сделку в Bitrix24 — без ручного переноса. Менеджер видит заполненный профиль до первого звонка.
- **CTA:** Подключить Bitrix24 → `{{integrations_url}}`
```

**Commit:**
```bash
git add templates/L3-onboarding-day7/
git commit -m "feat(emails): add L3 onboarding day 7 template"
```

---

## Task 12: L4 + L5 — Trial заканчивается / истёк

**Files:**
- Create: `templates/L4-trial-ending/template.html`
- Create: `templates/L4-trial-ending/content.md`
- Create: `templates/L5-trial-expired/template.html`
- Create: `templates/L5-trial-expired/content.md`

**content.md L4:**
```markdown
# L4 — Trial заканчивается (за 3 дня)

**Семья:** Lifecycle (B)
**Триггер:** За 3 дня до окончания trial
**Тип:** Scheduled

## Метаданные
- **Subject:** Ваш пробный период заканчивается через 3 дня
- **Preheader:** Выберите тариф и сохраните все данные

## Переменные
- `{{trial_end_date}}` — дата окончания trial
- `{{pricing_url}}` — страница тарифов

## Контент
- **H1:** До конца trial — 3 дня
- **Текст:** Все ваши опросные листы, шаблоны и история активности клиентов сохранятся при переходе на платный тариф. Если не продлить — данные будут заморожены через 3 дня.
- **Инсайт:** Basic — 1 990₽/мес. AI-тариф с анализом ответов и автоматическими инсайтами — 4 990₽/мес.
- **CTA:** Выбрать тариф → `{{pricing_url}}`
- **Вторичная:** Остались вопросы? Ответим → mailto:hello@unilist.ru
```

**content.md L5:**
```markdown
# L5 — Trial истёк

**Семья:** Lifecycle (B)
**Триггер:** День окончания trial
**Тип:** Scheduled

## Метаданные
- **Subject:** Пробный период завершён
- **Preheader:** Данные сохранены — активируйте тариф, чтобы продолжить

## Переменные
- `{{pricing_url}}` — страница тарифов

## Контент
- **H1:** Ваш trial завершён
- **Текст:** Все ваши данные в безопасности. Чтобы продолжить работу и сохранить доступ к истории — выберите тариф. Это займёт 2 минуты.
- **CTA:** Активировать тариф → `{{pricing_url}}`
```

**Commit:**
```bash
git add templates/L4-trial-ending/ templates/L5-trial-expired/
git commit -m "feat(emails): add L4 trial ending and L5 trial expired templates"
```

---

## Task 13: L6 + L7 — Напоминания об оплате

**Files:**
- Create: `templates/L6-payment-reminder-5d/template.html`
- Create: `templates/L6-payment-reminder-5d/content.md`
- Create: `templates/L7-payment-reminder-1d/template.html`
- Create: `templates/L7-payment-reminder-1d/content.md`

**content.md L6:**
```markdown
# L6 — Напоминание об оплате (за 5 дней)

**Семья:** Lifecycle (B)
**Триггер:** За 5 дней до даты следующего списания
**Тип:** Scheduled

## Метаданные
- **Subject:** Напоминание: списание через 5 дней
- **Preheader:** {{amount}}₽ с карты •••{{card_last4}} {{billing_date}}

## Переменные
- `{{plan_name}}`, `{{amount}}`, `{{billing_date}}`, `{{card_last4}}`
- `{{billing_url}}` — управление подпиской
- `{{pricing_url}}` — изменить тариф

## Контент
- **H1:** Плановое продление подписки
- **Таблица:** Тариф / Сумма / Дата / Карта
- **Текст:** Всё пройдёт автоматически. Если хотите изменить тариф или способ оплаты — сделайте это до {{billing_date}}.
- **CTA:** Управление подпиской → `{{billing_url}}`
- **Вторичная:** Изменить тариф → `{{pricing_url}}`
```

**content.md L7:**
```markdown
# L7 — Предстоящее списание (за 1 день)

**Семья:** Lifecycle (B)
**Триггер:** За 1 день до даты следующего списания
**Тип:** Scheduled

## Метаданные
- **Subject:** Завтра спишем {{amount}}₽ за Unilist
- **Preheader:** Карта •••{{card_last4}} · Тариф {{plan_name}}

## Переменные
- `{{plan_name}}`, `{{amount}}`, `{{card_last4}}`
- `{{billing_url}}` — управление подпиской

## Контент
- **H1:** Напоминание: завтра продление
- **Таблица:** Тариф / Сумма / Карта
- **CTA:** Управление подпиской → `{{billing_url}}`
```

**Commit:**
```bash
git add templates/L6-payment-reminder-5d/ templates/L7-payment-reminder-1d/
git commit -m "feat(emails): add L6 and L7 payment reminder templates"
```

---

## Task 14: L8 — Подписка приостановлена

**Files:**
- Create: `templates/L8-subscription-paused/template.html`
- Create: `templates/L8-subscription-paused/content.md`

**content.md:**
```markdown
# L8 — Подписка приостановлена

**Семья:** Lifecycle (B)
**Триггер:** Неуспешный платёж × 2 подряд
**Тип:** Триггерный

## Метаданные
- **Subject:** Доступ приостановлен — восстановите за 2 минуты
- **Preheader:** Не удалось провести 2 платежа подряд

## Переменные
- `{{payment_url}}` — страница обновления оплаты

## Контент
- **H1:** Доступ к аккаунту приостановлен
- **Текст:** Нам дважды не удалось провести платёж. Все ваши данные сохранены — обновите способ оплаты, чтобы сразу восстановить доступ.
- **CTA:** Обновить способ оплаты → `{{payment_url}}`
```

**Commit:**
```bash
git add templates/L8-subscription-paused/
git commit -m "feat(emails): add L8 subscription paused template"
```

---

## Task 15: L9 — Реактивация

**Files:**
- Create: `templates/L9-reactivation/template.html`
- Create: `templates/L9-reactivation/content.md`

**content.md:**
```markdown
# L9 — Реактивация

**Семья:** Lifecycle (B)
**Триггер:** 14 дней без активности в аккаунте
**Тип:** Scheduled

## Метаданные
- **Subject:** Что происходит с вашими клиентами прямо сейчас?
- **Preheader:** Вы не заходили 2 недели — возможно, пропустили сигналы

## Переменные
- `{{dashboard_url}}` — дашборд активности
- `{{feedback_url}}` — форма обратной связи

## Контент
- **H1:** Кто-то из клиентов, возможно, ждёт звонка
- **Текст:** Когда клиент возвращается к анкете — это сигнал. Зайдите в Unilist и посмотрите, была ли активность за последние 2 недели.
- **CTA:** Посмотреть активность → `{{dashboard_url}}`
- **Вторичная:** Если продукт не подходит — расскажите почему → `{{feedback_url}}`
```

**Commit:**
```bash
git add templates/L9-reactivation/
git commit -m "feat(emails): add L9 reactivation template"
```

---

## Task 16: Обновить CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

Обновить таблицу "Готовые артефакты" — добавить все 14 шаблонов со статусом.

**Commit:**
```bash
git add CLAUDE.md
git commit -m "docs(emails): update CLAUDE.md with completed email templates"
```

---

## Финальная проверка

После всех задач:

```bash
ls templates/
# Ожидается: _base + 14 папок

find templates -name "template.html" | wc -l
# Ожидается: 14

find templates -name "content.md" | wc -l
# Ожидается: 14
```

Открыть все 14 `template.html` в браузере и визуально проверить корректность отображения.

```bash
git push
```
