# Выбор российской AI-модели для unilist

> Дата анализа: 2026-03-21
> Статус: решение принято, ожидает реализации

## Контекст

По требованиям 152-ФЗ, функции, обрабатывающие персональные данные клиентов, должны использовать российский облачный провайдер. Выбор провайдера — Yandex AI Studio (aistudio.yandex.ru).

Функции с ПД клиентов:
- `analyze_single` — анализ одного ответа клиента
- `analyze_batch` — пакетный анализ ответов (до 50K символов)
- `document_import.*` — импорт из PDF/DOCX (документ может содержать ПД)

---

## Ключевое открытие: AI Studio — OpenAI-совместимый API

Yandex AI Studio предоставляет **OpenAI-совместимый API** (quickstart рекомендует `npm install openai`). Это означает:

- Не нужен нативный YandexGPT API (`/foundationModels/v1/completion`), который мы реализовали
- Через один endpoint доступны ВСЕ модели платформы: YandexGPT, DeepSeek, Qwen, Gemma и др.
- Смена модели — это просто изменение `model` в запросе, без изменения кода

**Вывод:** текущую реализацию `YandexGptService` нужно переписать с нативного API на OpenAI-совместимый клиент. Код упростится, а доступ к открытым моделям станет возможным.

---

## Доступные модели в Yandex AI Studio

### Собственные модели Яндекса

| Модель | Контекст | Цена | Назначение |
|--------|----------|------|------------|
| YandexGPT 5 Lite | 32K | 0.20₽/1K | Быстрые задачи, классификация |
| YandexGPT 5.1 Pro | 128K | 0.80₽/1K | Анализ документов, RAG, сложные задачи |
| Alice AI LLM | 32K | 0.50₽/1K in / 1.20₽/1K out | Диалоги, ассистенты |

### Открытые модели (через AI Studio, данные на серверах Яндекса)

| Модель | Контекст | Цена | Примечание |
|--------|----------|------|------------|
| DeepSeek V3 / V3.2 | 128K | $0.028/M (cache hit) / $0.28/M (cache miss) | MoE 671B/37B активных |
| DeepSeek V4 | 1M+ | ~$0.14/M | Только анонсирован |
| Qwen 2.5 (7B-72B) | 128K | Open source | Нужен self-hosting |
| Gemma 3 27B | 130K | ~$0.08-0.10/M | Мультимодальный |

---

## Сравнение цены с текущим Anthropic Haiku

| Модель | Цена input | Цена output | Среднее, ₽/1K токенов |
|--------|-----------|------------|----------------------|
| Claude Haiku (текущий) | $0.8/M | $4.0/M | ~0.18₽/1K |
| **YandexGPT Lite** | 0.20₽/1K | 0.20₽/1K | **0.20₽/1K** |
| **YandexGPT Pro** | 0.80₽/1K | 0.80₽/1K | **0.80₽/1K** |
| **DeepSeek V3 (cache miss)** | $0.28/M | $0.42/M | **~0.033₽/1K** |
| **DeepSeek V3 (cache hit)** | $0.028/M | — | **~0.0025₽/1K** |

Вывод: DeepSeek V3 при cache hit в 70-100 раз дешевле Haiku. При cache miss — в 5-7 раз дешевле.
Наш `AiCacheModule` кэширует ответы на уровне SHA256(prompt) — повторные одинаковые запросы = cache hit у нас, не у DeepSeek.

---

## Доступные модели (подтверждено в каталоге AI Studio)

Аккаунт cloud-unilist-team. Все модели доступны для вызова:

**Яндекс:** Alice AI LLM, YandexGPT 5 Lite, YandexGPT 5 Pro, YandexGPT 5.1 Pro
**DeepSeek:** DeepSeek 3.2 ✅, DeepSeek R1 Distill Llama 70B, DeepSeek R1 Distill Qwen 32B, DeepSeek VL2
**Alibaba:** Qwen2.5 (7B/32B/72B), Qwen3 (0.6B/1.7B/4B/8B/14B/32B/30B A3B/235B A22B), QwQ-32B, Qwen2.5 VL
**Google:** Gemma 3 (1B/4B/12B/27B IT)
**OpenAI:** GPT OSS 20B, GPT OSS 120B
**Meta:** Llama 3.1 70B Instruct
**Microsoft:** Phi-4

---

## Финальное решение по моделям

### `analyze_batch` — анализ пакета ответов клиентов

**Требования:** до 50K символов входных данных, сложный JSON (тренды, сегменты, рекомендации), нужен 128K контекст, сильный reasoning.

**✅ Рекомендация: DeepSeek 3.2**
- 128K контекст — покрывает задачу
- Лучший reasoning среди доступных: MoE 671B параметров, 37B активных
- Значительно дешевле YandexGPT Pro ($0.028/M vs 0.80₽/1K)
- Хорошо понимает русский язык

**Почему не YandexGPT Pro:** дороже при сопоставимом или уступающем reasoning. DeepSeek 3.2 — лучший выбор по price/quality.

---

### `analyze_single` — анализ одного ответа клиента

**Требования:** умеренная сложность, JSON с summary/signals/readiness, до 4K токенов.

**✅ Рекомендация: YandexGPT 5 Lite**
- 32K контекста достаточно с запасом
- 0.20₽/1K — самый дешёвый вариант
- Оптимизирована под русский язык
- Задача не требует топ-класса модели

**Альтернатива если качество недостаточно:** Qwen3 8B или DeepSeek 3.2.

---

### `document_import.*` — импорт из PDF/DOCX

**Требования:** структурное извлечение полей из текста, JSON-массив, лёгкая задача.

**✅ Рекомендация: YandexGPT 5 Lite**
- Простое извлечение структуры — не нужен мощный reasoning
- Быстро и дёшево

---

### Итоговая таблица решений

| Задача | Модель | Провайдер в коде | Причина |
|--------|--------|-----------------|---------|
| `analyze_batch` | **DeepSeek 3.2** | `callRussian('pro')` | Лучший reasoning, дешевле Pro |
| `analyze_single` | **YandexGPT 5 Lite** | `callRussian('lite')` | Достаточно, дёшево |
| `document_import.*` | **YandexGPT 5 Lite** | `callRussian('lite')` | Лёгкая задача |

**На перспективу:** если YandexGPT Lite не справляется с `analyze_single` — переключить на Qwen3 8B или DeepSeek 3.2. Это смена одной строки (`model` в config).

---

## Необходимые изменения в коде

### 1. Переписать YandexGptService на OpenAI-совместимый клиент AI Studio

Текущая реализация использует нативный Yandex API (`/foundationModels/v1/completion`). AI Studio предоставляет OpenAI-совместимый endpoint — через него доступны все модели каталога (YandexGPT, DeepSeek, Qwen и др.).

```typescript
// npm install openai
import OpenAI from 'openai';

// Клиент настраивается один раз:
const client = new OpenAI({
  apiKey: process.env.YANDEX_API_KEY,    // API-ключ из AI Studio
  baseURL: 'https://llm.api.cloud.yandex.net/v1',
  defaultHeaders: {
    'x-folder-id': process.env.YANDEX_FOLDER_ID,  // уточнить — может быть в заголовке
  },
});

// Вызов с указанием модели по задаче:
const response = await client.chat.completions.create({
  model: 'deepseek-v3',         // analyze_batch
  // model: 'yandexgpt-lite',   // analyze_single, document_import
  messages: [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userPrompt },
  ],
  max_tokens: 4096,
  temperature: 0.3,
});
const text = response.choices[0].message.content ?? '';
```

> ⚠️ **Уточнить:** точный baseURL и способ передачи folder_id (заголовок vs параметр) — проверить в quickstart AI Studio после получения API-ключа.

### 2. Параметризовать модель в AiRouterService

```typescript
// Передаём 'lite' или 'pro' в зависимости от задачи:
callRussian(system, user, model: 'lite' | 'pro' = 'lite')

// Сервисы вызывают:
this.aiRouter.callRussian('', prompt, 'pro')   // analyze_batch
this.aiRouter.callRussian('', prompt, 'lite')  // analyze_single, document_import
```

### 3. Env-переменные (обновить)

```env
YANDEX_API_KEY=...                      # API-ключ из AI Studio
YANDEX_FOLDER_ID=...                    # ID каталога (folder)
YANDEX_MODEL_LITE=yandexgpt-lite        # для analyze_single, document_import
YANDEX_MODEL_PRO=deepseek-v3            # для analyze_batch (DeepSeek 3.2)
```

> Точные идентификаторы моделей (`yandexgpt-lite`, `deepseek-v3`) — уточнить в карточках моделей AI Studio или в API Reference.

---

## Шаги для реализации

1. **Получить API-ключ** в AI Studio → Создать API-ключ (кнопка в правом верхнем углу)
2. **Уточнить baseURL и model IDs** — нажать на карточку DeepSeek 3.2 и YandexGPT Lite в каталоге, посмотреть примеры запросов
3. **Сообщить** — переделаем `YandexGptService` на OpenAI-совместимый клиент с двумя моделями

---

## Распознавание документов — улучшение через VL-модели

### Проблема текущего подхода

Сейчас `DocumentImportService` работает так:
1. PDF/DOCX → извлечь текст (pdf-parse / mammoth)
2. Текст → LLM → JSON-поля

**Проблема:** pdf-parse теряет визуальную структуру документа. Чекбоксы, таблицы, подчёркивания, колонки, отступы — всё это в тексте превращается в плоский поток строк. Сложные бланки распознаются плохо.

### Решение: Vision-Language модели

В каталоге AI Studio есть модели, которые принимают **изображение/PDF напрямую** и понимают визуальную структуру:

| Модель | Размер | Специализация |
|--------|--------|--------------|
| **Qwen2.5 VL 32B Instruct** | 32B | Лучшее понимание документов, таблиц, форм |
| **Qwen2.5 VL 7B Instruct** | 7B | Лёгкий вариант, быстрее |
| **DeepSeek VL2** | 32B | Визуальный анализ документов |
| **DeepSeek VL2 Tiny** | ~3B | Самый быстрый VL-вариант |
| Gemma 3 27B IT | 27B | image-text-to-text, хорошее качество |

### Рекомендация для document_import

**✅ Переключить PDF-путь на Qwen2.5 VL 7B Instruct** (первый этап):
- Отправляем страницы PDF как изображения — модель видит реальную форму
- Понимает: чекбоксы, таблицы, подчёркивания, формы с полями
- В 7B весе — разумная скорость и стоимость
- Если качества не хватит — 32B версия

**Как это изменит код:**
```typescript
// Текущий подход (теряет структуру):
const text = await pdfParse(buffer);   // плоский текст
const result = await aiRouter.callRussian(system, text);

// Новый подход (видит визуальную структуру):
const base64 = buffer.toString('base64');
const response = await client.chat.completions.create({
  model: 'qwen2.5-vl-7b-instruct',  // уточнить model ID
  messages: [{
    role: 'user',
    content: [
      { type: 'image_url', image_url: { url: `data:application/pdf;base64,${base64}` } },
      { type: 'text', text: systemPrompt },
    ],
  }],
});
```

**Для DOCX/DOC:** оставить текущий подход (mammoth хорошо извлекает структуру) или конвертировать в PDF → использовать VL.

### Итог по document_import

| Формат | Модель | Подход |
|--------|--------|--------|
| PDF | **Qwen2.5 VL 7B** | Прямая передача как изображение |
| DOCX | YandexGPT 5 Lite | Текст через mammoth (работает хорошо) |
| DOC | YandexGPT 5 Lite | Текст через word-extractor |
| XLS/XLSX | Без LLM | Структурный парсинг (уже работает) |

---

## Стратегия на будущее

| Этап | Модель | Когда |
|------|--------|-------|
| Сейчас | YandexGPT Lite + Pro via AI Studio | Сразу после регистрации |
| При дорогом Pro | DeepSeek V3 через AI Studio | После проверки доступности |
| При масштабировании | Self-hosted Qwen 2.5 на VPS | Когда стоимость AI станет ощутимой |

---

## Влияние на другие домены

- **finance/ai-costs.md** — обновить: YandexGPT Lite 0.20₽/1K, Pro 0.80₽/1K
- **dev/DOMAIN_STATE.md** — обновить: модели изменились, добавился AiModule
