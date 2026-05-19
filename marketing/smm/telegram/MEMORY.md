# Рабочая память — Telegram

## Текущий статус (2026-05-19)
- **Бот в production** — `@unilist_post_bot` на VPS Selectel (`kinsey`, 193.168.136.29), systemd unit `telegram-bot`, активен
- **Стратегия v1** в `strategy.md`, 19 каналов для роста в `growth-channels.md` (9/10 Tier A верифицированы)
- **Канал** «Продажи без тёмных пятен» создан, бот добавлен админом, channel_id `-1003253037787`
- Канал ещё не запущен публично, 0 подписчиков (нет первых постов — режим сбора сырья)
- **E2E приёмка пройдена 2026-05-11 22:43 MSK** — полный цикл draft → cron sync → approval card → Approve → publish прошёл
- **Voice + text inbox в бота (2026-05-11):** admin шлёт голосовое или текст → бот сохраняет в `/opt/unilist-bot/raw-inbox/`. Голосовые → `<ts>-voice.ogg`, текстовые заметки → `<ts>-note.md`. Расшифровку делает пользователь вручную (TG встроенная кнопка), копирует текстом в бот.
- **Первая попытка генерации постов (4 драфта на 18–24 мая) отвергнута пользователем 2026-05-11** — «AI-копирайтер прёт, синтетический подход, нет искры». Драфты удалены, не пушились. См. global memory `no-ai-copywriter-tone.md`.

## Архитектура approval-бота (MVP)

```
Claude (локально) → markdown с frontmatter в posts/drafts/ → git push
                                                                ↓
                                  VPS cron каждые 5 мин: git pull + cp -n
                                                                ↓
                                       /opt/unilist-bot/posts/drafts/
                                                                ↓
                                  scheduler раз в 60с: scan + register в SQLite
                                                                ↓
                                  T-24h до publish_at: approval card в DM admin
                                                                ↓
                                                ✅ Approve / ❌ Reject / ⏰ Snooze
                                                                ↓
                                  publish_at: send в канал + admin DM-уведомление
```

Код: `saas-workspace/tools/telegram-bot/` (Python 3.11, python-telegram-bot, aiosqlite).
21 unit-тестов, deploy через `tools/telegram-bot/deploy/install.sh`.

## Принятые решения
- Списки каналов вынесены из `strategy.md` в `growth-channels.md`
- Tier A — прямая ниша B2B-продаж; Tier B — B2B-маркетинг и лидген; Tier C — продукт/AI
- Markdown как content source, SQLite — runtime state (разделение immutable / mutable)
- VPS — Selectel ru-7 (тот же, где Coolify). Telegram API доступен только через pin `149.154.167.220` в `/etc/hosts` (Selectel фильтрует CIDR)
- Edit-флоу — out of MVP. Reject = удалить файл из git, переписать, новый коммит
- Drafts не перемещаются в `published/` после публикации (для совместимости с git-sync); state в БД
- Sync через `cp -n` (no-clobber) — files стираются вручную при очистке drafts/

## TODO
- [ ] Финализировать название канала (3 варианта → фидбэк 5 РОПов)
- [ ] **Дождаться сырья от пользователя через voice/text inbox**, потом обрабатывать. НЕ генерировать «из головы».
- [ ] Найти корректный username Дмитрия Шамко (или исключить) — @dmitriyshamko невалиден
- [ ] Собрать ERR для Tier A каналов через TGStat (вручную, JS-рендер)
- [ ] Квалифицировать Tier B/C (9 каналов): подписчики, ERR, цена
- [ ] Пройтись по реестру партнёров Bitrix24 на предмет каналов интеграторов
- [ ] Добавить ссылку на канал в подпись Respondo и виджет в подвал блога Unilist
- [ ] **Out-of-MVP backlog для бота:** edit-флоу, webhook вместо polling, авто-генерация по cron, метрики канала через 24ч, multi-channel, `/unpublish <id>`

## Контекст
- Целевые метрики: 200 подп. / 3–5 платящих за 90 дней, 1000 подп. / 10–20 платящих за 12 мес
- Бюджет 90 дней: 15–40К₽ + 96 ч основателя
- Outreach по гостевым запускать только после 100+ собственных подписчиков

## Операционные команды

```bash
# Логи бота
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 'journalctl -u telegram-bot -f'

# Статус всех постов в БД
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 \
    'cd /opt/unilist-bot/app && sudo -u unilist ./.venv/bin/python -m src list'

# Ручной запуск sync (если нужно ускорить cron)
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 'sudo -u unilist /opt/unilist-bot/sync-drafts.sh'

# Перезапуск
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 'systemctl restart telegram-bot'

# Локально — unit-тесты
cd ../../tools/telegram-bot && .venv/bin/pytest -v

# Прочитать raw-inbox (сырьё от пользователя)
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 'ls -la /opt/unilist-bot/raw-inbox/'
ssh -i ~/.ssh/id_ed25519 root@193.168.136.29 'cat /opt/unilist-bot/raw-inbox/*-note.md'
# OGG голосовые — забирать только если нужны (бинарь, не читается)
```
