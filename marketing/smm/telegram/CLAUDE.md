# telegram

## Структура проекта

```
/Users/shuvaev/Продукты/unilist/saas-workspace/marketing/smm/telegram
CLAUDE.md
MEMORY.md
README.md
strategy.md          — основная стратегия канала (90 дней / 12 мес)
growth-channels.md   — список Telegram-каналов для гостевых постов / обмена / закупки
posts/drafts/        — черновики для approval-бота (Claude пишет, бот публикует)
docs/plans/          — план реализации approval-бота
```

## Готовые артефакты

| Файл | Содержит | Статус |
|------|---------|--------|
| `strategy.md` | Стратегия Telegram-канала «Продажи без тёмных пятен»: позиционирование, 5 контент-столпов, форматы, расписание, 30-дневный календарь, KPI, бюджет, риски, todo первой недели | v1 (2026-05-11) |
| `growth-channels.md` | 19 каналов в 3 тирах (A — прямая ниша B2B-продажи / РОПы, B — B2B-маркетинг и лидген, C — продукт/AI). Tier A квалифицирован через TGStat: подтверждены 9 username с подписчиками, 1 (@dmitriyshamko) невалиден. | v1 (2026-05-11) |
| `posts/drafts/` | Источник черновиков для approval-бота. Claude кладёт MD с frontmatter, VPS-cron каждые 5 мин подтягивает через `git pull`. | в работе |
| `docs/plans/2026-05-11-approval-bot.md` | 11-task план реализации MVP approval-бота. Все задачи выполнены, E2E приёмка 2026-05-11 22:43 MSK. | done |
| `../../../tools/telegram-bot/` | Код бота: Python 3.11, python-telegram-bot, aiosqlite. 21 unit-тестов. Deploy через `deploy/install.sh`. | production |

## Правила работы

- **Все username каналов проверяй через TGStat** (firecrawl со stealth-прокси: `https://tgstat.ru/channel/@<username>`) перед использованием. Подборки из vc.ru / b2bpress расходятся в написании.
- **ERR из карточки TGStat не извлекается через JSON-scrape** (требует JS-рендера или авторизации) — собирать вручную.
- **Список каналов где не размещают рекламу** держи отдельной пометкой — для них только гостевой формат / обмен (на 2026-05-11: @aterracons, @avsoln).
- При обновлении `strategy.md` не дублируй списки каналов — выноси в `growth-channels.md` и оставляй короткий указатель.

## Генерация постов для бота

Канал «Продажи без тёмных пятен» обслуживается полу-автоматическим ботом
(см. `../../../tools/telegram-bot/`, деплой на VPS `kinsey` 193.168.136.29,
systemd unit `telegram-bot`).

### ⚠️ ЖЁСТКОЕ ПРАВИЛО (2026-05-11)

**НЕ генерировать посты из `strategy.md` «из головы».** Это даёт AI-копирайтерский
тон — формально правильный, но синтетический. Пользователь отверг 4 черновика
именно за это («полнейшая шляпа, AI-копирайтер прёт»). Подробности в global
memory `no-ai-copywriter-tone.md`.

**Правильный workflow:** пользователь шлёт сырьё (голосовое + расшифровка) в
`@unilist_post_bot` → бот сохраняет в `/opt/unilist-bot/raw-inbox/` → ты
обрабатываешь по запросу «обработай инбокс». См. секцию «Raw inbox» ниже.

### Цикл работы (когда есть сырьё)

1. **По запросу** пользователя «обработай инбокс» — SSH на VPS, читай
   `/opt/unilist-bot/raw-inbox/*-note.md`, оформляй мысли в пост-формат.
   Источники для структуры (НЕ контента):
   - `strategy.md` §3 (контент-столпы — для классификации pillar)
   - `strategy.md` §4 (форматы)
   - `strategy.md` §5 (расписание слотов — Пн 10:00 / Ср 14:00 / Пт 11:00 / Вс 19:00 MSK)
   - `MEMORY.md` (что уже шло — не дублировать)
2. **НЕ выдумывать факты** — если в сырье нет цифры, не вставлять. Лучше короче.
3. После обработки — перенести/пометить обработанные ноты в `raw-inbox/archive/` на VPS.
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

### Raw inbox (приём сырья от пользователя)

Бот принимает в личке от админа:
- **Голосовое** → сохраняет OGG в `/opt/unilist-bot/raw-inbox/<ts>-voice.ogg` + отвечает «🎙 записал».
- **Текст** (не команда) → сохраняет MD в `/opt/unilist-bot/raw-inbox/<ts>-note.md` + отвечает «📝 записал».

Расшифровка голосовых — на стороне пользователя (TG умеет встроенно), он копирует
текст следующим сообщением. OGG храним как архив, читать не пытайся (бинарь).

```bash
# Прочитать всё накопленное сырьё
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 'cat /opt/unilist-bot/raw-inbox/*-note.md'

# Список со временем
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 'ls -la /opt/unilist-bot/raw-inbox/'
```

### Известные ограничения MVP

- Drafts остаются в `drafts/` даже после публикации (история живёт в БД на VPS).
  Чтобы посмотреть статус: `ssh kinsey 'sudo -u unilist /opt/unilist-bot/app/.venv/bin/python -m src list'`
- Edit-флоу не реализован: Reject = удалить из drafts/ вручную, переписать, новый коммит.
- API Telegram доступен с VPS только через pin `149.154.167.220` в `/etc/hosts`
  (см. `tools/telegram-bot/deploy/install.sh`).
- Raw inbox не имеет автоматической архивации — обработанные ноты переноси вручную.
