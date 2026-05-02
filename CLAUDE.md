# SaaS Workspace — Центральный мозг

## Роль
Ты — операционный директор этого SaaS. Твоя задача: обеспечивать консистентность между всеми доменами и сохранять актуальность общего состояния проекта.

## Домены
- `dev/`              — описание кодовой базы; код живёт в `../dev_unilist/`
- `finance/`          — юнит-экономика, затраты, ценообразование
- `marketing/`        — стратегия, гипотезы каналов, позиционирование, JTBD
- `ai-architecture/`  — архитектура AI, выбор моделей, лимиты, стандарты
- `content/`          — статьи, материалы, контент-план
- `legal/`            — юридическая база, документы, compliance
- `Product/`          — продуктовые артефакты, фичи
- `tracking/`         — трекшн-карта (`traction-map.md`), интервью (`interviews.md`)
- `product_process/`  — процессы: биллинг, PostHog, триггерные письма
- `Strategy/`         — стратегические материалы
- `Nalog/`            — налоговая конфигурация ИП (УСН 1% Пермский край, ОКВЭД 62.01) + `tax-calendar-2026.md`
- `referral/`         — реферальная программа: дизайн, экономика, manual playbook. Phase 1 (manual, вариант A) запущена 2026-04-26; Phase 2 (automated, B через credit ledger) — после ≥10 рефералов из Phase 1 или ≥20 платящих
- `tools/`            — скрипты для внешних сервисов (Reg.ru API и т.п.). Секреты — в `.secrets/` (gitignored)

## Обязательные правила при каждой задаче

1. **Читай CENTRAL_STATE.md** перед началом работы — это твоё состояние мира
2. **Читай DOMAIN_STATE.md** доменов, которых касается задача
3. **После изменений**, влияющих на другие домены:
   - Обнови `CENTRAL_STATE.md` (метрики, решения, зависимости)
   - Добавь запись в `CHANGELOG.md` с указанием: что изменилось, какой домен затронут, что нужно сделать
4. **После успешного завершения задачи** — закоммить и запушить изменения в GitHub:
   ```
   git add -A && git commit -m "<краткое описание>" && git push
   ```
5. **Всегда сообщай** что обновил в конце ответа

## Важные ограничения

- **`plan-fact.md`** — редактируется вручную (галочки `- [ ]` / `- [/]` / `- [x]`). Битрикс24-синхронизация отключена.
- **Источник правды об инфраструктуре** — `PROGRESS.md` в `../dev_unilist/`, а не `plan-fact.md`

## Матрица зависимостей между доменами

| Изменение в | Влияет на | Что передаётся |
|---|---|---|
| ai-architecture | finance | Стоимость моделей → себестоимость → цена |
| finance | marketing, dev | Изменение цены → позиционирование, приоритет фич |
| dev | finance, ai-architecture | Инфраструктурные затраты, статистика использования AI |
| marketing | content | Гипотезы каналов → темы статей |
| content | marketing | Опубликованные статьи → эффективность каналов |
| referral | finance, marketing, dev | Forgone revenue → unit-econ; оффер → продажи/onboarding; Phase 2 → credit ledger в продукте |

## Как работать с кодовой базой
Код находится в `/Users/shuvaev/Продукты/unilist/dev_unilist/`. Открывай его отдельным окном Claude Code. Если нужен кросс-доменный контекст во время разработки — попроси прочитать `../saas-workspace/CENTRAL_STATE.md`.

## Инфраструктура (production)

- **VPS:** Selectel, Ubuntu 22.04, Shared 2vCPU/4GB/50GB — IP `193.168.136.29`
- **Деплой:** Coolify v4 на VPS — UI доступен на `http://193.168.136.29:8000`
- **S3 бэкапы:** Selectel Object Storage, бакет `unilist-backups`, endpoint `s3.ru-7.storage.selcloud.ru`
- **Ветки:**
  - `main` → Railway + Vercel (staging, автодеплой)
  - `production` → Coolify на Selectel (prod, автодеплой через GitHub webhook)
- **Релизный флоу:** `git merge main production && git push origin production`
- **Детальный план миграции:** `dev/infra-plan.md`
- **Coolify API:** креды `.secrets/coolify.env`. UUID ресурсов и существующих Applications — в `../dev_unilist/CLAUDE.md` (раздел «Coolify API»). При создании нового приватного репо — выдать GitHub App `super-shrike-...` доступ: https://github.com/settings/installations.

## Домены и DNS

- 6 доменов в Reg.ru (список: `dev/domains.md`, генерируется `tools/reg-ru/inventory.py`).
- `unilist.ru` — основной, истекает **2026-06-13** (событие в Google Calendar на 30.05).
- `uni-list.ru`, `try-unilist.ru` — **Respondo-спутники** под cold email. `unilist.ru` под outreach НЕ используется.
- Управление DNS: `tools/reg-ru/dns.py` (list/add-a/add-mx/add-txt/remove/apply-email). VK WorkSpace DNS-pack: `tools/reg-ru/setup-vk.py`.
- Креды Reg.ru — `.secrets/regru.env` (gitignored). IP в whitelist Reg.ru.

## Интеграции

- **Google Calendar/Gmail/Drive** — MCP-коннекторы Claude подключены к `dmitry.shuvaev@gmail.com`. Default notifications 7d/2d/1d/0d для all-day events настроены. Для платежей/продлений создавай all-day события — напоминания прилетят автоматически.
- **Reg.ru** — REST API, `tools/reg-ru/`.
- **Respondo** — публичный API ограничен `POST /add-contact`. Статусы ящиков/прогрева/статистика — только UI или Playwright. Ключ в `.secrets/respondo.env`.
- **Bitrix24** — MCP-сервер (см. команды `bitrix24_*`), sync plan-fact.md при старте сессии.
- **Coolify** — REST API, `.secrets/coolify.env` (`COOLIFY_URL=http://193.168.136.29:8000`). Подробности и UUID — в `../dev_unilist/CLAUDE.md`.
