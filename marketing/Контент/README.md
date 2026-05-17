# Контент Unilist — блог

Папка содержит исходники статей для блога `unilist.ru/blog`. Каждая статья — в своей подпапке `<slug>/blog-<slug>.md`.

## Где что лежит

| Файл / папка | Назначение |
|---|---|
| `CONTENT_STANDARDS.md` | Стандарты оформления статей: frontmatter, meta, FAQ, CTA, тон, Schema.org микроразметка. |
| `GEO_GUIDE.md` | GEO-стратегия: AEO, технический чек-лист, ловушки. |
| `content-plan.md` | Контент-план: кластеры, статусы статей, аудит соответствия стандартам. |
| `CLAUDE.md` | Правила для агента (как править, как деплоить). |
| `MEMORY.md` | Сводка решений по контенту. |
| `<slug>/blog-<slug>.md` | Исходник одной статьи. |

## Кластеры (по состоянию на 2026-05-11)

| ID | Тема | Pillar / Спутники |
|---|---|---|
| К1 | Клиент завис | klient-zavis-chto-delat-ropu / 5-signalov, pochemu-klienty, risk-poteri |
| К2 | Конверсия воронки | konversiya-voronki-prodazh, sales-velocity-dlya-ropa, temnoe-pyatno-voronki-prodazh / kak-izmerit, oprosnyye-listy-ubivayut, gde-teryayutsya |
| К3 | Контроль менеджеров | kontrol-menedzherov-bez-zvonkov, funktsii-ropa-i-sedmaya / kpi, oprosnyy-list-est-u-vsekh, kak-oprosnyy-list-vliyaet |
| К4 | Философия и метрики РОПа | temnoe-pyatno-voronki-prodazh, funktsii-ropa-i-sedmaya, sales-velocity-dlya-ropa (запущен 2026-05-11) |

> К4 пересекается с К2/К3 — статьи могут одновременно работать на два кластера. Главный кластер для каждой статьи — в её frontmatter (поле `cluster`).

## Внешние материалы (не SEO-блог)

| Файл | Площадка |
|---|---|
| `ai-v-rabote-s-oprosnymi-listami/` | VC/Habr |
| `ai-v-seyslzovykh-protsessakh/` | VC/Habr |

## Как опубликовать новую статью

1. Проверить SEO-обоснование в `content-plan.md` (или добавить запись).
2. Создать папку `<slug>/` и файл `blog-<slug>.md` по шаблону `CONTENT_STANDARDS.md`.
3. Написать тело, FAQ, CTA на `/dlya-ropa`.
4. Добавить SEO-блок с двумя JSON-LD в конце.
5. Прогнать через скилл `humanizer`, проверить запрещённые слова.
6. Скопировать в зеркало `../landing/website_dev/content/<slug>/` (добавить `published: "YYYY-MM-DD"` в frontmatter).
7. Закоммитить в репо `unilist-landing` на ветку `dev` → проверить staging → merge в `main` → prod.

Подробный регламент для агента — в `CLAUDE.md`.

## Аудит готовности (см. content-plan.md)

На 2026-05-11: 17 статей, 13 полностью соответствуют CONTENT_STANDARDS, 2 «внешние» без frontmatter (допустимо). Таблица «Что починить» — в `content-plan.md`.
