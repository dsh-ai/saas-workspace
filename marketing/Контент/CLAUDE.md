# Контент — правила для агента

## Источники правды

| Файл | Что описывает |
|---|---|
| `CONTENT_STANDARDS.md` | Frontmatter, meta, H1, FAQ, CTA, тон («вы»), запрещённые слова и AI-паттерны, **формат Schema.org микроразметки** (Article + FAQPage JSON-LD). |
| `GEO_GUIDE.md` | GEO-стратегия, programmatic AEO, технический чек-лист. |
| `content-plan.md` | Кластеры, статусы, целевые запросы, аудит соответствия CONTENT_STANDARDS. Перед написанием новой статьи — проверить здесь, есть ли SEO-обоснование. |
| `MEMORY.md` | Локальная память кластеров и решений. |

## Жёсткие правила

1. **SEO первично.** Не создавать статьи без записи в `content-plan.md`.
2. **Папка на статью.** Файлы лежат в `<slug>/blog-<slug>.md`. Никаких файлов напрямую в `Контент/`.
3. **Зеркало для сайта.** После правки статьи в `Контент/<slug>/` синхронизировать с `../landing/website_dev/content/<slug>/` (с сохранением поля `published` в frontmatter и нормализаций — нет строки «Целевая аудитория:», нет висячих `---` после H1). Без зеркала изменения не попадут на блог.
4. **Schema.org обязателен.** В конце каждой статьи — блок `<!-- SEO-метаданные -->` с двумя JSON-LD (Article + FAQPage) по шаблону из `CONTENT_STANDARDS.md`. Без блока статья не отрендерится с rich-results.
5. **Только «вы».** Никакого «ты», в том числе в глаголах и императивах.
6. **Запрещённые слова и AI-паттерны** перечислены в `CONTENT_STANDARDS.md`. После написания — прогон через скилл `humanizer`.
7. **Любую фамилию/факт верифицировать** перед публикацией. Не подставлять авторов «по созвучию». Список проверенных русскоязычных авторов по продажам — в локальной памяти.

## Деплой блога

Источник: `Контент/<slug>/blog-<slug>.md` → зеркало: `../landing/website_dev/content/<slug>/blog-<slug>.md` → git репо `unilist-landing`.

Флоу:
```
cd ../landing/website_dev
git add content/
git commit -m "content: <что изменено>"
git push origin dev          # автодеплой staging lp.unilist.ru
git checkout main && git merge dev && git push origin main   # автодеплой prod unilist.ru
git checkout dev
```

Coolify UUID: staging `gfubqn2hodbpezv5rx68fg5g`, prod `qv3mhlmk7b8eov7ge9u5myn3` (CLAUDE.md уровня выше).

## Bulk-операция: добавить хвостовой блок (CTA / JSON-LD) в существующие статьи

Если нужно вписать одинаковый хвостовой блок в N статей сразу:
1. Сгенерировать блок в `/tmp/block-<short>.md` через Write tool (UTF-8 + JSON безопасно).
2. `cat /tmp/block-<short>.md >> Контент/<slug>/blog-<slug>.md && cat /tmp/block-<short>.md >> ../landing/website_dev/content/<slug>/blog-<slug>.md`.

Это безопаснее, чем bash-heredoc с кириллицей и JSON.

## Текущие кластеры

| ID | Тема | Статус |
|---|---|---|
| К1 | Клиент завис | в публикации |
| К2 | Конверсия воронки | в публикации |
| К3 | Контроль менеджеров | в публикации |
| К4 | Философия и метрики РОПа | новый, запущен 2026-05-11 (3 pillar) |
