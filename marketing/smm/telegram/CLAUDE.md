# telegram

## Структура проекта

```
/Users/shuvaev/Продукты/unilist/saas-workspace/marketing/smm/telegram
CLAUDE.md
MEMORY.md
README.md
strategy.md          — основная стратегия канала (90 дней / 12 мес)
growth-channels.md   — список Telegram-каналов для гостевых постов / обмена / закупки
```

## Готовые артефакты

| Файл | Содержит | Статус |
|------|---------|--------|
| `strategy.md` | Стратегия Telegram-канала «Продажи без тёмных пятен»: позиционирование, 5 контент-столпов, форматы, расписание, 30-дневный календарь, KPI, бюджет, риски, todo первой недели | v1 (2026-05-11) |
| `growth-channels.md` | 19 каналов в 3 тирах (A — прямая ниша B2B-продажи / РОПы, B — B2B-маркетинг и лидген, C — продукт/AI). Tier A квалифицирован через TGStat: подтверждены 9 username с подписчиками, 1 (@dmitriyshamko) невалиден. Контакты для рекламы, критерии отбора, шаблон таблицы для Tier B/C. | v1 (2026-05-11) |

## Правила работы

- **Все username каналов проверяй через TGStat** (firecrawl со stealth-прокси: `https://tgstat.ru/channel/@<username>`) перед использованием. Подборки из vc.ru / b2bpress расходятся в написании.
- **ERR из карточки TGStat не извлекается через JSON-scrape** (требует JS-рендера или авторизации) — собирать вручную.
- **Список каналов где не размещают рекламу** держи отдельной пометкой — для них только гостевой формат / обмен (на 2026-05-11: @aterracons, @avsoln).
- При обновлении `strategy.md` не дублируй списки каналов — выноси в `growth-channels.md` и оставляй короткий указатель.

## Генерация постов для бота

Канал «Продажи без тёмных пятен» обслуживается полу-автоматическим ботом
(см. `../../../tools/telegram-bot/`, деплой на VPS `kinsey` 193.168.136.29,
systemd unit `telegram-bot`).

### Цикл работы

1. **Каждое воскресенье** генерируй 4 черновика на следующую неделю в
   `posts/drafts/<YYYY-MM-DD-HHMM>-<slug>.md`. Источники:
   - `strategy.md` §3 (контент-столпы)
   - `strategy.md` §4 (форматы)
   - `strategy.md` §8 (30-дневный календарь)
   - `MEMORY.md` (что уже шло — не дублировать)
2. **Обязательный frontmatter:**
   ```yaml
   ---
   id: 2026-05-12-1000-lost-deal   # должен совпадать с именем файла без .md
   publish_at: 2026-05-12T10:00:00+03:00   # ISO с TZ
   pillar: pain | management | cases | ai | behind-scenes
   format: text | longread | poll | carousel | video
   ---
   ```
3. **После генерации** — закоммить и запушь:
   ```bash
   git add marketing/smm/telegram/posts/drafts/
   git commit -m "telegram: drafts на неделю <дата>"
   git push
   ```
4. **Дальше делает бот:** VPS-cron каждые 5 мин делает `git pull`, бот раз в минуту
   сканирует `posts/drafts/`. За 24ч до `publish_at` пришлёт владельцу карточку
   approve/reject/snooze в Telegram. На approve — публикует в канал в момент
   `publish_at`.
5. **Не публикуй сам.** Бот сам отметит DB и (в будущем) переместит в `published/`.

### Известные ограничения MVP

- Drafts остаются в `drafts/` даже после публикации (история живёт в БД на VPS).
  Чтобы посмотреть статус: `ssh kinsey 'sudo -u unilist /opt/unilist-bot/app/.venv/bin/python -m src list'`
- Edit-флоу не реализован: Reject = удалить из drafts/ вручную, переписать, новый коммит.
- API Telegram доступен с VPS только через pin `149.154.167.220` в `/etc/hosts`
  (см. `tools/telegram-bot/deploy/install.sh`).
