import pytest
from unittest.mock import MagicMock, patch
from analyzers.claude_analyzer import ClaudeAnalyzer

FAKE_DATA = {
    "keywords": [
        {"keyword": "опросный лист продажи", "volume": 4400},
        {"keyword": "форма для клиента B2B", "volume": 1200},
    ],
    "competitors": [
        {
            "domain": "competitor.ru",
            "traffic": 15000,
            "top_pages": [{"url": "/oprosnik", "traffic": 4000}],
        }
    ],
    "own_positions": [
        {"query": "опросный лист продажи", "position": 0, "clicks": 0},
    ],
    "own_domain": "unilist.ru",
}

FAKE_CLAUDE_RESPONSE = """
## Кластеры ключевых слов

### Кластер 1: Опросные листы в продажах
...

## Анализ конкурентов
...

## Приоритизированный план страниц

### Приоритет 1
/blog/oprosnyy-list-dlya-prodazh — объём 4400, конкуренты слабые
"""

def test_analyze_returns_string():
    with patch("analyzers.claude_analyzer.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text=FAKE_CLAUDE_RESPONSE)]
        )

        analyzer = ClaudeAnalyzer(api_key="fake_key")
        result = analyzer.analyze(FAKE_DATA)

        assert isinstance(result, str)
        assert "Приоритет" in result
        mock_client.messages.create.assert_called_once()
