# AI Architecture — Domain State

> Последнее обновление: 2026-03-21

## Текущие модели
| Назначение | Модель | Провайдер | Статус |
|---|---|---|---|
| analyze_batch | YandexGPT Pro (планируется) | Yandex AI Studio | Planned |
| analyze_single | YandexGPT Lite (планируется) | Yandex AI Studio | Planned |
| document_import.* | YandexGPT Lite (планируется) | Yandex AI Studio | Planned |
| retrospective, generate_fields, improve_labels, suggest_types | claude-haiku-4-5-20251001 | Anthropic | Active |
| product_desk.classify | claude-haiku-4-5-20251001 | Anthropic | Active |

## Архитектура провайдеров (реализовано 2026-03-21)
- `AiRouterService.callRussian()` → Yandex AI Studio (функции с ПД клиентов, 152-ФЗ)
- `AiRouterService.callGlobal()` → Anthropic (структурные данные, без ПД)
- Подробнее: `russian-ai-model-selection.md`

## Паттерны
- Кэширование: SHA256(provider + serviceType + prompt) → таблица `ai_cache`
- Billing: `BillingService.recordTokenUsage()` на каждый вызов (пропускается при cache hit)
- Prompt Registry: промты хранятся в БД, управляются через Homestead `/homestead/ai`

## Лимиты
- YandexGPT Lite: 32K контекст
- YandexGPT Pro: 128K контекст
- Claude Haiku: 200K контекст

## Функции в продукте
| Функция | Провайдер | ПД клиентов |
|---|---|---|
| `analyze_single` | Yandex (callRussian) | Да |
| `analyze_batch` | Yandex (callRussian) | Да |
| `document_import.*` | Yandex (callRussian) | Да (возможно) |
| `retrospective` | Anthropic (callGlobal) | Нет |
| `generate_fields` | Anthropic (прямой) | Нет |
| `improve_labels` / `suggest_types` | Anthropic (прямой) | Нет |
| `product_desk.classify` | Anthropic (прямой) | Нет |

## Следующие шаги
1. Зарегистрировать Yandex Cloud, получить YANDEX_API_KEY + YANDEX_FOLDER_ID
2. Уточнить OpenAI-совместимый endpoint AI Studio
3. Переписать `YandexGptService` с нативного API на OpenAI-клиент
4. Добавить выбор модели (Lite / Pro) по задаче в AiRouterService
5. Добавить env-переменные в Coolify и Railway
