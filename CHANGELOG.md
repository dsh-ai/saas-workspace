# Changelog — Кросс-доменные изменения

> Каждая запись: что изменилось, в каком домене, что нужно сделать в других доменах.
> Формат: `[домен-источник → домен-получатель]`

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
