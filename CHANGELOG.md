# Changelog — Кросс-доменные изменения

> Каждая запись: что изменилось, в каком домене, что нужно сделать в других доменах.
> Формат: `[домен-источник → домен-получатель]`

## 2026-04-26 — Referral: разделение на Phase 1 (manual) + Phase 2 (automated)

### [referral → marketing, gtm, finance]

**Решение:** запустить Phase 1 в ручном формате сейчас, не дожидаясь ≥20 платящих. Получить сигнал по механике до dev-инвестиций.

**Phase 1 (manual, готов к запуску):**
- Вариант A: 1 месяц бесплатно рефереру + -30% приглашённому
- Forgone revenue ~6 490₽ на реферала, breakeven при retention ≥2 мес
- Учёт в Google Sheet, скидки в Модульбанке вручную, промокоды формата `RU-<surname>-<random4>`
- Где предлагать: кастдев-интервью, onboarding-письмо, поддержка, страница тарифов

**Phase 2 (automated, отложено):**
- Вариант B: 20% кредитом × 12 мес + -25%
- Запуск после ≥10 успешных рефералов из Phase 1 ИЛИ ≥20 платящих
- Credit ledger в продукте (модель данных и edge cases в `referral/program-design.md`)

**В дизайн добавлено:**
- Сравнение 4 вариантов (A/B/C/D) по unit-econ
- Manual playbook: оффер, точки касания, промокоды, учёт, применение скидки

**Обновлено:**
- `referral/README.md`, `referral/program-design.md` — две фазы
- `finance/DOMAIN_STATE.md` — экономика обеих фаз
- `marketing/DOMAIN_STATE.md` — Phase 1 в активные офферы, Phase 2 в отложенные каналы
- `marketing/go-to-market/activities.md` — активность 4a (Phase 1), 9 (Phase 2)
- `marketing/go-to-market/hypotheses.md` — H8a (Phase 1), H8b (Phase 2)

---

## 2026-04-22 — Referral: дизайн реферальной программы

### [referral → finance, marketing, gtm, dev]

**Создано:**
- `referral/README.md` — hub реферальной программы
- `referral/program-design.md` — механика, экономика, credit ledger, защита от фрода

**Ключевые решения:**
- Механика: 20% кредитом рефереру от платежей приглашённого (12 мес) + -25% приглашённому на первый месяц
- Бенефит через внутренний **credit ledger**, а не полноценный кошелёк (не ломает рекуррент Модульбанка и 54-ФЗ)
- Триггер начисления — фактическая оплата приглашённого
- Кеш-выплаты исключены (решение фаундера)
- Запуск отложен до ≥20 платящих + подтверждённого H2

**Обновлено:**
- `finance/DOMAIN_STATE.md` — блок про реферальную программу и влияние на unit-econ
- `marketing/DOMAIN_STATE.md` — реферал в "отложенных каналах"
- `marketing/go-to-market/activities.md` — активность #9
- `marketing/go-to-market/hypotheses.md` — H8

**Что требуется от dev при запуске:** модель `referral_credits`, `referrals`, промокоды, хук списания кредита перед charge в Модульбанке.

---

## 2026-04-20 — Marketing: GTM-хаб + старт прогрева Respondo

### [marketing → tracking]

**Создано:**
- `marketing/go-to-market/` — GTM-хаб: README, activities, hypotheses, scenarios, todos
- `gtm-strategy.md` перенесён внутрь хаба (был в `marketing/`)
- `strategy-2026.md` остался в `marketing/` как родительский документ

**Email-outreach инфраструктура:**
- DNS (MX/SPF/DKIM/DMARC) на uni-list.ru и try-unilist.ru доехали
- 4 ящика VK WorkSpace подключены к Respondo, прогрев стартовал 2026-04-20
- Старт цепочки NOSE по Сег1 — 2026-05-04 (событие в Google Calendar)

**Обновлено:**
- `CENTRAL_STATE.md` — два новых решения (DNS + GTM-хаб)
- `marketing/CLAUDE.md` — секция «Файлы» переписана под новую структуру
- `marketing/DOMAIN_STATE.md` — статус Email-outreach обновлён на «Прогрев»

## 2026-04-19 — Marketing: запуск email-outreach кампании

### [marketing → finance, tracking]
Подготовка холодной email-кампании через Respondo для Сегмента 1 (производство/промышленность).

**Решения:**
- Платформа: Respondo (respondo.ru)
- Куплены 2 домена-спутника: try-unilist.ru, uni-list.ru (reg.ru)
- Почтовый провайдер: VK WorkSpace (Яндекс 360 отклонён — блокирует SMTP новым ящикам)
- 4 ящика (sales@, dmitry@ на обоих доменах), ~1000₽/мес
- Оффер: 2 бесплатных месяца Unilist за 30-мин интервью (уже в подвале unilist.ru)
- Цепочка 5 писем по NOSE, интервалы 2–5 дней
- Основной unilist.ru в outreach не используется

**Создано:**
- `marketing/email/email-outreach-plan.md` — полный план с текстами писем
- `marketing/DOMAIN_STATE.md` — обновлён, добавлены гипотезы каналов

**Что нужно в других доменах:**
- finance: учесть +1000₽/мес на почту, +стоимость Respondo (уточнить тариф)
- tracking: лиды с интервью через outreach → обновить traction-map по факту откликов

## 2026-03-22 — SEO→Контент: правила связки и контент-план

### [marketing/SEO → marketing/Контент]
Установлена связка: SEO первично, контент не пишется без SEO-обоснования.

**Создано:**
- `marketing/Контент/content-plan.md` — единый контент-план с аудитом публикаций

**Обновлены правила:**
- `marketing/SEO/CLAUDE.md` — добавлен 5-шаговый процесс после каждого обновления SEO-ядра
- `marketing/CLAUDE.md` — принцип SEO-первичности для контента

**Процесс (кратко):**
После каждого обновления ключей/кластеров → проверить наличие материала → статус на unilist.ru/blog → соответствие текущим ключам → обновить content-plan.md

**Текущий аудит:** 8 существующих статей в `Контент/` — статус публикации не проверен (🔲), нужно сверить с unilist.ru/blog вручную или через WebFetch.

---

## 2026-03-22 — Обновление юнит-экономики по AI-архитектуре

### [ai-architecture → finance]
Пересчитана себестоимость AI на основе принятого решения по моделям (2026-03-21).

**Ключевые изменения:**
- Старая модель (все функции → Haiku) заменена на dual-provider: Yandex AI Studio + Anthropic
- Функции с ПД клиентов → YandexGPT 5 Lite (0.20₽/1K) + DeepSeek 3.2 ($0.28/M)
- Функции без ПД → Haiku остаётся ($0.80/$4.00/M)

**Новые расчёты:**
- AI затраты на пользователя: ~215₽/мес (диапазон 70–410₽)
- Gross margin AI-плана (4990₽): ~86%
- Точка безубыточности: 1–2 подписки покрывают fixed costs (~3 050₽)

**Обновлены файлы:**
- `finance/ai-costs.md` — полный пересчёт по функциям
- `finance/unit-economics-operations.md` — актуализирован под текущий продукт
- `finance/unit-economics.md` — COGS заполнены
- `finance/DOMAIN_STATE.md` — AI-провайдеры и gross margin
- `CENTRAL_STATE.md` — метрика стоимости AI на пользователя

**Требует проверки:**
- Реальные token counts после интеграции Yandex AI Studio
- Цена Qwen2.5 VL 7B в AI Studio (используется для PDF-импорта)

---

## 2026-03-15 — Company Profile для AI

### [dev → ai-architecture]
Добавлен профиль компании в модель User. AI-промпты теперь получают контекст бизнеса создателя формы.

**Изменения:**
- `user.entity.ts`: +5 полей (companyIndustry, companyProduct, companyAudience, companyAvgDeal, companyDescription)
- `common/utils/company-context.util.ts`: shared `buildCompanyContext()` — вставляется в начало промпта
- `demo.service.ts` и `response-analysis.service.ts`: контекст компании в AI-промптах
- `frontend/profile/page.tsx`: секция "Профиль компании для AI" в таб Компания
- `onboarding-modal.tsx`: новый шаг компании между builder и done
- `responses/page.tsx`: баннер если companyDescription пуст

**Требует:** миграция БД — добавить 5 новых колонок в таблицу users (TypeORM автомиграция или вручную)

**Влияние на другие домены:**
- ai-architecture: стоимость промпта увеличится незначительно (+50-200 токенов если профиль заполнен)
- marketing: теперь можно позиционировать точность AI как конкурентное преимущество

---

## 2026-03-15 — Bitrix24 MCP интеграция

### [dev → инфраструктура]
MCP-сервер bitrix24 подключён локально. Поддержка "Моего плана" через `task.stages` API.
- Инструменты: `bitrix24_create_task`, `bitrix24_add_to_my_plan`, `bitrix24_list_my_plan`, `bitrix24_sync_workspace`
- Маппинг доменов → колонки: `~/bitrix24-mcp/config.json`
- Статус: `create_task` — работает ✅, `sync_workspace` — баг (HTTP 400), нужно отладить

---

## 2026-03-07

### [setup]
Создан SaaS Workspace. Домены инициализированы.
Маркетинговые файлы перенесены из `dev_unilist/Маркетинг/` в `marketing/`.
