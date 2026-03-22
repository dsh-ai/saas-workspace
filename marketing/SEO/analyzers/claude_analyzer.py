import json
import anthropic

ANALYSIS_PROMPT = """Ты — SEO-аналитик. Тебе дан JSON с данными о конкурентах и ключевых словах.

Данные:
{data}

Выполни анализ и верни структурированный Markdown-документ со следующими разделами:

## Анализ конкурентов
Для каждого конкурента: контент-стратегия (какие типы страниц есть — сравнения, интеграции, ниши, гайды), сильные стороны, ключевые слова которых нет у нас.

## Кластеры ключевых слов
Сгруппируй все ключевые слова по темам. Для каждого кластера: название, суммарный объём, наша текущая позиция.

## GAP-анализ
Ключевые слова и темы, по которым конкуренты ранжируются, а мы — нет.

## Приоритизированный план страниц
Для каждой рекомендуемой страницы:
- URL (slug)
- Тип страницы (статья / лендинг / сравнение / гайд)
- Целевой кластер
- Объём запросов
- Почему в этом приоритете (объём + слабость конкурентов + GAP)

Приоритет 1 — создать в ближайшие 2 недели (высокий объём, слабые конкуренты).
Приоритет 2 — следующий месяц.
Приоритет 3 — следующий квартал.
"""


class ClaudeAnalyzer:
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze(self, data: dict) -> str:
        """Принимает объединённые данные, возвращает Markdown-анализ."""
        data_json = json.dumps(data, ensure_ascii=False, indent=2)
        prompt = ANALYSIS_PROMPT.format(data=data_json)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
