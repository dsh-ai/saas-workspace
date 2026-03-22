# SEO Research Pipeline — Design Doc

*Дата: 2026-03-22*

## Цель

Автоматический еженедельный pipeline, который:
1. Находит конкурентов по ключевым словам ниши
2. Собирает их семантику и анализирует контент-стратегии
3. Сравнивает с позициями Unilist
4. Генерирует приоритизированный план страниц

## Источники данных

| Источник | Что даёт | Статус |
|---|---|---|
| Яндекс Вордстат API | Расширение семантики, частотности | Токен есть |
| PR-CY API | Анализ сайтов конкурентов, топ страниц | API-ключ есть |
| Яндекс Вебмастер API | Свои позиции по запросам | Сайт верифицирован |
| keys.so | Ключевые слова конкурентов | Нет ключа — v2 |

## Архитектура: Модульный pipeline

### Структура файлов

```
SEO/
├── pipeline.py              # Оркестратор
├── config.yaml              # Seed-ключевые слова, API-ключи
├── collectors/
│   ├── wordstat.py          # Яндекс Вордстат API
│   ├── prcry.py             # PR-CY API
│   └── webmaster.py         # Яндекс Вебмастер API
├── analyzers/
│   └── claude_analyzer.py   # Claude API — анализ + план
├── reports/
│   └── YYYY-MM-DD/
│       ├── competitors.md
│       ├── keywords.md
│       └── action-plan.md
└── docs/plans/              # Этот файл
```

### Поток данных

```
config.yaml (seed keywords)
    │
    ▼
[wordstat.py]
50-100 связанных запросов с частотностью
    │
    ▼
[prcry.py]
Топ-10 запросов → сайты в выдаче → анализ страниц конкурентов
    │
    ▼
[webmaster.py]
Свои позиции по тем же запросам → GAP-анализ
    │
    ▼
[claude_analyzer.py]
Весь JSON → Claude API → кластеризация + анализ + план
    │
    ▼
reports/YYYY-MM-DD/*.md
```

### Запуск

Claude Code cron-хук: `python pipeline.py` каждое воскресенье в 09:00.

## Конфигурация

```yaml
seed_keywords:
  - "опросный лист продажи"
  - "B2B анкета клиента"
  - "квалификация лидов форма"

your_domain: "unilist.ru"

apis:
  wordstat_token: "${WORDSTAT_TOKEN}"
  prcry_key: "${PRCRY_API_KEY}"
  webmaster_token: "${WEBMASTER_TOKEN}"
  claude_api_key: "${ANTHROPIC_API_KEY}"

schedule: "every sunday 09:00"

limits:
  wordstat_keywords_per_seed: 50
  prcry_competitors_to_analyze: 10
  max_pages_per_competitor: 20
```

## Формат отчётов

### competitors.md
По каждому конкуренту: URL, трафик, топ-5 страниц, контент-стратегия (типы страниц), ключи которых нет у нас.

### keywords.md
Семантика по кластерам с объёмами и нашими текущими позициями.

### action-plan.md
Приоритизированный план страниц: что создать первым, почему (объём + слабость конкурентов + GAP).

## Обработка ошибок

- Каждый коллектор независим — сбой одного не останавливает pipeline
- Ошибки → `reports/YYYY-MM-DD/errors.log`
- Частичный отчёт предпочтительнее отсутствия отчёта

## Roadmap

- **v1:** Вордстат + PR-CY + Вебмастер + Claude-анализ
- **v2:** Добавить keys.so как коллектор когда появится ключ
- **v3:** Claude-agent loop — итеративное исследование вместо фиксированного pipeline
