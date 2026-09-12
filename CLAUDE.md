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
- `pet-projects/`     — побочные продукты вне Unilist: фильтр идей, пул идей, плейбук добычи из Reddit/HN/vc.ru. Лимит — 4 ч/нед, иначе продукт закрывается
- `tools/`            — скрипты для внешних сервисов (Reg.ru API, Я.Метрика, keyword-research). Секреты — в `.secrets/` (gitignored)

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

## Разбор интервью с РОПами (кастдев)

Когда пользователь приносит диалоги с РОПами (файлом в `tracking/interviews/`, вставкой в чат или расшифровкой голоса):

1. **Сырьё** — в `tracking/interviews/ГГГГ-ММ-ДД-rop-<кто>.md` (дословно, не пересказ). **Сводка/скоринг** — в `tracking/interviews.md`. Гайд вопросов — `tracking/interview-guide.md`. Стратегические выкладки — `Strategy/gtm-plg-strategy.md`.
2. **Скоринг по критерию трекшн-карты:** проблема подтверждена, если **3 из 5** интервью — РОП называет ущерб **в цифрах** И **сам**, без наводки, описывает сценарий.
3. **Проверь на «отравленность»:** если в диалоге основатель сам произнёс решение (алерт/уведомление при открытии/видеть путь заполнения/на каком вопросе отвалился) — интервью **не считается**, скоринг по нему обнуляется.
4. **Скори по формулировкам РОПа, не по пересказу основателя.** Пересказ скорить нельзя — проси дословные цитаты.
5. **Вытаскивай ответы на открытые вопросы** из `Strategy/gtm-plg-strategy.md`: какой уровень (L1/L2/L3) болит сам, реакция realtime/пачкой, цифра ущерба в рублях/мес (потолок цены), как сегмент покупает инструменты (→ PLG возможен да/нет), объём опросников/мес.
6. **После разбора** обнови: `tracking/interviews.md` (сводка), `tracking/traction-map.md` (лог + статус красной ячейки), при сдвиге выводов — `Strategy/gtm-plg-strategy.md` и `CENTRAL_STATE.md`.

## Матрица зависимостей между доменами

| Изменение в | Влияет на | Что передаётся |
|---|---|---|
| ai-architecture | finance | Стоимость моделей → себестоимость → цена |
| finance | marketing, dev | Изменение цены → позиционирование, приоритет фич |
| dev | finance, ai-architecture | Инфраструктурные затраты, статистика использования AI |
| marketing | content | Гипотезы каналов → темы статей |
| content | marketing | Опубликованные статьи → эффективность каналов |
| pet-projects | finance, legal | Отдельная статья затрат и выручки; дисклеймеры по регуляторным продуктам |
| referral | finance, marketing, dev | Forgone revenue → unit-econ; оффер → продажи/onboarding; Phase 2 → credit ledger в продукте |

## Как работать с кодовой базой
Код находится в `/Users/shuvaev/Продукты/unilist/dev_unilist/`. Открывай его отдельным окном Claude Code. Если нужен кросс-доменный контекст во время разработки — попроси прочитать `../saas-workspace/CENTRAL_STATE.md`.

## Инфраструктура (production)

- **VPS:** Selectel, Ubuntu 22.04, Shared 2vCPU/4GB/50GB — IP `193.168.136.29`, hostname `kinsey`
- **SSH:** `ssh -i ~/.ssh/id_ed25519 root@193.168.136.29`. Публичный ключ в `/root/.ssh/authorized_keys`. Если доступ внезапно пропал — добавить ключ через Selectel-консоль VPS (root). **Не путать** с VPS Sentry/GlitchTip `37.9.7.141` (hostname `tessa-sentry`, `/opt/glitchtip/`).
- **Swap:** `/swapfile` 4 GB, прописан в `/etc/fstab` (добавлен 2026-05-10 — без него `npm ci` бэка падал OOM при сборке в Coolify).
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
- **Яндекс.Метрика** — счётчик `97774201`, OAuth-токен в `.secrets/yandex-metrika.env` (права `metrika:write`). Управление целями: `tools/yandex-metrika/create-goals.py` + `goals.json` (идемпотентно). Каталог событий: `marketing/analytics/yandex-metrika-events.md`. **Один счётчик на лендинг и продукт** — для сквозной воронки. Префиксы целей: лендинг — `cta_*`/`nav_*`/`blog_*`, продукт — `app_*`. Identify юзеров в продукте — в `dev_unilist/frontend/components/providers/auth-provider.tsx` (login/register/restore-session).
- **Вордстат / спрос** — `tools/keyword-research/`: `suggest.py` (реальные формулировки из подсказок Яндекса и Google, доступов не требует), `wordstat.py` (частотность; режим `--phrases` готовит фразы с операторами для ручной выгрузки, `--api` требует доступа и дозаполнения контракта), `score.py` (вердикт по кластерам). Доступ к частотности: API Вордстата (бета, по заявке в поддержку Директа) либо Wordstat в Yandex Cloud Search API. Креды — `.secrets/wordstat.env`. Метод и правила чтения — `pet-projects/demand-research.md`.
- **Яндекс.Вебмастер** — Webmaster API v4, креды `.secrets/yandex-webmaster.env` (`YWM_TOKEN`, `YWM_USER_ID=1995823460`, `YWM_HOST_ID=http:unilist.ru:80`). CLI: `tools/yandex-webmaster/wm.py` — команды `whoami | hosts | summary | queries | query-history | problems | links | sitemaps | recrawl | recrawl-quota`. На 2026-05-03 подтверждён только HTTP-хост; HTTPS-зеркало надо верифицировать через UI. Sitemap пустой → 0 страниц в индексе (см. `marketing/SEO/MEMORY.md`).

## Landing — деплой website_dev

- `dev` ветка → `lp.unilist.ru` (staging, noindex), Coolify UUID `gfubqn2hodbpezv5rx68fg5g`.
- `main` ветка → `unilist.ru` (prod), Coolify UUID `qv3mhlmk7b8eov7ge9u5myn3`.
- Флоу: коммит в `dev` → проверка на staging → `git checkout main && git merge dev && git push` → автодеплой prod.
