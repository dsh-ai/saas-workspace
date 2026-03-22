# AI Costs

> Связь: ai-architecture/DOMAIN_STATE.md → сюда
> Последнее обновление: 2026-03-22 (на основе ai-architecture/russian-ai-model-selection.md)

## Архитектура провайдеров

Два провайдера в зависимости от наличия ПД клиентов:
- **Yandex AI Studio** — функции, обрабатывающие персональные данные (152-ФЗ)
- **Anthropic** — структурные функции без ПД

---

## Тарифы по провайдерам

### Yandex AI Studio

| Модель | Цена | Применение |
|--------|------|------------|
| YandexGPT 5 Lite | 0.20₽/1K токенов (flat) | `analyze_single`, `document_import (DOCX)` |
| YandexGPT 5.1 Pro | 0.80₽/1K токенов (flat) | резерв |
| DeepSeek 3.2 | $0.028/M (cache hit) / $0.28/M (cache miss) input; $0.42/M output | `analyze_batch` |
| Qwen2.5 VL 7B | ~$0.08–0.10/M (уточнить в AI Studio) | `document_import (PDF)` |

*Курс для расчётов: 90₽/$*

### Anthropic

| Модель | Input | Output | Применение |
|--------|-------|--------|------------|
| claude-haiku-4-5-20251001 | $0.80/M | $4.00/M | `retrospective`, `generate_fields`, `improve_labels`, `suggest_types`, `product_desk.classify` |

---

## Стоимость по функциям

| Функция | Модель | ~Input | ~Output | ~₽/вызов |
|---------|--------|--------|---------|----------|
| `analyze_single` | YandexGPT 5 Lite | 2K tok | 1K tok | **~0.60₽** |
| `analyze_batch` (50 ответов) | DeepSeek 3.2 | 50K tok | 3K tok | **~1.40₽** (cache miss) |
| `document_import` PDF | Qwen2.5 VL 7B | — | ~1K tok | **~0.10₽** (уточнить) |
| `document_import` DOCX | YandexGPT 5 Lite | 3K tok | 1K tok | **~0.80₽** |
| `retrospective` | Haiku | 5K tok | 2K tok | **~1.10₽** |
| `generate_fields` | Haiku | 2K tok | 1K tok | **~0.50₽** |
| `improve_labels` | Haiku | 1K tok | 0.5K tok | **~0.25₽** |
| `suggest_types` | Haiku | 1K tok | 0.5K tok | **~0.25₽** |
| `product_desk.classify` | Haiku | 0.5K tok | 0.2K tok | **~0.11₽** |

*+50–200 токенов к каждому вызову если заполнен Company Profile*

---

## Оценка затрат на пользователя/мес (AI-план)

Сценарий: 10 форм/мес, каждая — 30 ответов

| Активность | Вызовы | Стоимость |
|------------|--------|-----------|
| analyze_single | 300 вызовов × 0.60₽ | 180₽ |
| analyze_batch | 10 вызовов × 1.40₽ | 14₽ |
| retrospective | 5 вызовов × 1.10₽ | 5.5₽ |
| generate_fields | 10 вызовов × 0.50₽ | 5₽ |
| прочее (labels/classify) | ~20 вызовов | ~5₽ |
| **ИТОГО** | | **~210₽/пользователь/мес** |

**Диапазон по активности:**
- Лёгкий пользователь (3–5 форм/мес): ~60–80₽
- Средний (10 форм/мес): ~200₽
- Активный (20+ форм/мес): ~400₽

---

## Кэширование

AI-ответы кэшируются по SHA256(provider + serviceType + prompt) → таблица `ai_cache`.
- Повторные вызовы с одинаковыми данными = 0 затрат
- Для `analyze_batch` наш кэш работает на уровне системы; cache hit у DeepSeek ($0.0025₽/1K) применяется только при точном совпадении промпта у провайдера

---

## Динамика затрат vs. старая модель

| | Старая оценка (до 2026-03-22) | Новая оценка |
|--|-------------------------------|--------------|
| Модель | Claude Haiku (все функции) | Yandex AI Studio + Anthropic |
| AI затраты/пользователь/мес | ~—₽ (не рассчитывались) | ~60–400₽ |
| Gross margin при AI-плане 4990₽ | — | **~92–98%** по AI-статье |
