# SEO Research Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Модульный Python-pipeline, который еженедельно собирает SEO-данные о конкурентах через Яндекс Вордстат, PR-CY и Яндекс Вебмастер, анализирует их через Claude API и генерирует Markdown-отчёты с приоритизированным планом страниц.

**Architecture:** Три независимых коллектора собирают данные в JSON, оркестратор `pipeline.py` их объединяет и передаёт в `claude_analyzer.py`, который возвращает структурированный анализ. Каждый коллектор независим — сбой одного не останавливает pipeline. Запуск через Claude Code cron-хук каждое воскресенье.

**Tech Stack:** Python 3.11+, `requests`, `pyyaml`, `anthropic`, `pytest`, `responses` (mock HTTP)

---

## Структура файлов (итог)

```
SEO/
├── pipeline.py
├── config.yaml
├── requirements.txt
├── collectors/
│   ├── __init__.py
│   ├── wordstat.py
│   ├── prcry.py
│   └── webmaster.py
├── analyzers/
│   ├── __init__.py
│   └── claude_analyzer.py
├── reports/               # генерируется автоматически
└── tests/
    ├── test_wordstat.py
    ├── test_prcry.py
    ├── test_webmaster.py
    ├── test_claude_analyzer.py
    └── test_pipeline.py
```

---

### Task 1: Scaffold — структура проекта и конфиг

**Files:**
- Create: `SEO/requirements.txt`
- Create: `SEO/config.yaml`
- Create: `SEO/collectors/__init__.py`
- Create: `SEO/analyzers/__init__.py`
- Create: `SEO/tests/__init__.py` (пустой)

**Step 1: Создать `requirements.txt`**

```
requests==2.32.3
pyyaml==6.0.2
anthropic==0.40.0
responses==0.25.3
pytest==8.3.4
python-dotenv==1.0.1
```

**Step 2: Создать `config.yaml`**

```yaml
seed_keywords:
  - "опросный лист продажи"
  - "B2B анкета клиента"
  - "квалификация лидов форма"
  - "форма для клиента Bitrix24"
  - "опросник менеджера по продажам"

your_domain: "unilist.ru"

apis:
  wordstat_token: "${WORDSTAT_TOKEN}"
  prcry_key: "${PRCRY_API_KEY}"
  webmaster_token: "${WEBMASTER_TOKEN}"
  webmaster_user_id: "${WEBMASTER_USER_ID}"
  claude_api_key: "${ANTHROPIC_API_KEY}"

limits:
  wordstat_keywords_per_seed: 50
  prcry_competitors_to_analyze: 10
  max_pages_per_competitor: 20

schedule: "sunday 09:00"
```

**Step 3: Создать пустые `__init__.py`**

```python
# пустой файл
```

**Step 4: Установить зависимости**

```bash
cd /Users/shuvaev/Продукты/unilist/saas-workspace/marketing/SEO
pip install -r requirements.txt
```

Ожидаемый вывод: `Successfully installed ...`

**Step 5: Commit**

```bash
git add requirements.txt config.yaml collectors/__init__.py analyzers/__init__.py tests/__init__.py
git commit -m "feat(seo): scaffold pipeline structure and config"
```

---

### Task 2: Config loader

**Files:**
- Create: `SEO/config.py`
- Test: `SEO/tests/test_config.py`

**Step 1: Написать failing test**

```python
# tests/test_config.py
import os
import pytest
from config import load_config

def test_load_config_returns_dict(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("""
seed_keywords:
  - "test keyword"
your_domain: "example.com"
apis:
  wordstat_token: "${TEST_TOKEN}"
limits:
  wordstat_keywords_per_seed: 10
""")
    config = load_config(str(cfg_file))
    assert config["your_domain"] == "example.com"
    assert config["seed_keywords"] == ["test keyword"]
    assert config["limits"]["wordstat_keywords_per_seed"] == 10

def test_load_config_expands_env_vars(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_TOKEN", "abc123")
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("""
apis:
  wordstat_token: "${TEST_TOKEN}"
""")
    config = load_config(str(cfg_file))
    assert config["apis"]["wordstat_token"] == "abc123"
```

**Step 2: Запустить тест, убедиться что падает**

```bash
cd SEO && pytest tests/test_config.py -v
```

Ожидаемый вывод: `ImportError: cannot import name 'load_config'`

**Step 3: Написать `config.py`**

```python
import os
import re
import yaml

def _expand_env_vars(value):
    """Заменяет ${VAR} на значение переменной окружения."""
    if not isinstance(value, str):
        return value
    pattern = re.compile(r'\$\{([^}]+)\}')
    def replacer(match):
        return os.environ.get(match.group(1), match.group(0))
    return pattern.sub(replacer, value)

def _expand_recursive(obj):
    if isinstance(obj, dict):
        return {k: _expand_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_recursive(i) for i in obj]
    return _expand_env_vars(obj)

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return _expand_recursive(raw)
```

**Step 4: Запустить тест, убедиться что проходит**

```bash
pytest tests/test_config.py -v
```

Ожидаемый вывод: `2 passed`

**Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat(seo): add config loader with env var expansion"
```

---

### Task 3: Wordstat коллектор

**Files:**
- Create: `SEO/collectors/wordstat.py`
- Test: `SEO/tests/test_wordstat.py`

**Справка по API:**
Яндекс Вордстат — SOAP/XML API (`https://api.wordstat.yandex.com/v2`).
Основной метод: `GetWordstatReport` (async: создать отчёт → подождать → получить результат).
OAuth-токен передаётся в заголовке `Authorization: OAuth <token>`.

**Step 1: Написать failing test**

```python
# tests/test_wordstat.py
import responses as resp_mock
import pytest
from collectors.wordstat import WordstatCollector

FAKE_TOKEN = "fake_token"

FAKE_CREATE_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetWordstatReportResponse>
      <data>12345</data>
    </GetWordstatReportResponse>
  </soap:Body>
</soap:Envelope>"""

FAKE_GET_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetWordstatReportResponse>
      <data>
        <phrases>
          <item>
            <phrase>опросный лист продажи</phrase>
            <shows>4400</shows>
          </item>
          <item>
            <phrase>опросник для клиента</phrase>
            <shows>1200</shows>
          </item>
        </phrases>
      </data>
    </GetWordstatReportResponse>
  </soap:Body>
</soap:Envelope>"""

@resp_mock.activate
def test_collect_returns_keywords_with_volumes():
    resp_mock.add(resp_mock.POST,
        "https://api.wordstat.yandex.com/v2",
        body=FAKE_CREATE_RESPONSE, status=200,
        match_querystring=False)
    resp_mock.add(resp_mock.POST,
        "https://api.wordstat.yandex.com/v2",
        body=FAKE_GET_RESPONSE, status=200,
        match_querystring=False)

    collector = WordstatCollector(token=FAKE_TOKEN)
    result = collector.collect(["опросный лист продажи"], limit=50)

    assert isinstance(result, list)
    assert len(result) > 0
    assert "keyword" in result[0]
    assert "volume" in result[0]
    assert result[0]["volume"] > 0
```

**Step 2: Запустить тест, убедиться что падает**

```bash
pytest tests/test_wordstat.py -v
```

Ожидаемый вывод: `ImportError`

**Step 3: Написать `collectors/wordstat.py`**

```python
import time
import xml.etree.ElementTree as ET
import requests

WORDSTAT_API = "https://api.wordstat.yandex.com/v2"

CREATE_REPORT_TMPL = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetWordstatReportRequest>
      <login>{login}</login>
      <token>{token}</token>
      <phrases>
        {phrases}
      </phrases>
    </GetWordstatReportRequest>
  </soap:Body>
</soap:Envelope>"""

class WordstatCollector:
    def __init__(self, token: str, login: str = ""):
        self.token = token
        self.login = login
        self.headers = {
            "Authorization": f"OAuth {token}",
            "Content-Type": "text/xml; charset=utf-8",
        }

    def _soap_request(self, body: str) -> ET.Element:
        r = requests.post(WORDSTAT_API, data=body.encode("utf-8"), headers=self.headers)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}
        return root.find(".//soap:Body", ns)[0]

    def _create_report(self, keywords: list[str]) -> int:
        phrases_xml = "".join(f"<item><phrase>{kw}</phrase></item>" for kw in keywords)
        body = CREATE_REPORT_TMPL.format(
            login=self.login, token=self.token, phrases=phrases_xml
        )
        response = self._soap_request(body)
        return int(response.find("data").text)

    def _get_report(self, report_id: int) -> list[dict]:
        get_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetWordstatReportRequest>
      <login>{self.login}</login>
      <token>{self.token}</token>
      <reportID>{report_id}</reportID>
    </GetWordstatReportRequest>
  </soap:Body>
</soap:Envelope>"""
        response = self._soap_request(get_body)
        results = []
        for item in response.findall(".//phrases/item"):
            phrase = item.findtext("phrase", "")
            shows = int(item.findtext("shows", "0"))
            if phrase:
                results.append({"keyword": phrase, "volume": shows})
        return results

    def collect(self, seed_keywords: list[str], limit: int = 50) -> list[dict]:
        """Возвращает список {"keyword": str, "volume": int}."""
        results = []
        for keyword in seed_keywords:
            try:
                report_id = self._create_report([keyword])
                time.sleep(2)  # API требует паузу перед получением отчёта
                keywords = self._get_report(report_id)
                results.extend(keywords[:limit])
            except Exception as e:
                print(f"[wordstat] Ошибка для '{keyword}': {e}")
        # дедупликация
        seen = set()
        unique = []
        for item in results:
            if item["keyword"] not in seen:
                seen.add(item["keyword"])
                unique.append(item)
        return unique
```

**Step 4: Запустить тест**

```bash
pytest tests/test_wordstat.py -v
```

Ожидаемый вывод: `1 passed`

**Step 5: Commit**

```bash
git add collectors/wordstat.py tests/test_wordstat.py
git commit -m "feat(seo): add Wordstat collector"
```

---

### Task 4: PR-CY коллектор

**Files:**
- Create: `SEO/collectors/prcry.py`
- Test: `SEO/tests/test_prcry.py`

**Справка по API:**
PR-CY API: `https://api.pr-cy.ru/`
- `GET /domain/{domain}` — анализ домена (трафик, ключи)
- `GET /serp?query={keyword}&se=yandex` — топ выдачи по запросу

Заголовок: `X-Api-Key: <key>`

**Step 1: Написать failing test**

```python
# tests/test_prcry.py
import responses as resp_mock
import pytest
from collectors.prcry import PrcyCollector

FAKE_KEY = "fake_prcry_key"

FAKE_SERP = {
    "results": [
        {"url": "https://competitor1.ru/page", "domain": "competitor1.ru", "position": 1},
        {"url": "https://competitor2.ru/blog/form", "domain": "competitor2.ru", "position": 2},
        {"url": "https://unilist.ru", "domain": "unilist.ru", "position": 3},
    ]
}

FAKE_DOMAIN = {
    "domain": "competitor1.ru",
    "traffic": 15000,
    "keywords_count": 340,
    "top_pages": [
        {"url": "/oprosnik", "traffic": 4000, "keywords": ["опросный лист", "анкета клиента"]},
        {"url": "/crm-forma", "traffic": 2000, "keywords": ["форма для CRM"]},
    ]
}

@resp_mock.activate
def test_find_competitors_excludes_own_domain():
    resp_mock.add(resp_mock.GET,
        "https://api.pr-cy.ru/serp",
        json=FAKE_SERP, status=200)

    collector = PrcyCollector(api_key=FAKE_KEY, own_domain="unilist.ru")
    competitors = collector.find_competitors(["опросный лист продажи"])

    assert "unilist.ru" not in competitors
    assert "competitor1.ru" in competitors

@resp_mock.activate
def test_analyze_domain_returns_structured_data():
    resp_mock.add(resp_mock.GET,
        "https://api.pr-cy.ru/domain/competitor1.ru",
        json=FAKE_DOMAIN, status=200)

    collector = PrcyCollector(api_key=FAKE_KEY, own_domain="unilist.ru")
    result = collector.analyze_domain("competitor1.ru")

    assert result["domain"] == "competitor1.ru"
    assert result["traffic"] == 15000
    assert len(result["top_pages"]) == 2
```

**Step 2: Запустить тест, убедиться что падает**

```bash
pytest tests/test_prcry.py -v
```

**Step 3: Написать `collectors/prcry.py`**

```python
import requests

PRCRY_API = "https://api.pr-cy.ru"

class PrcyCollector:
    def __init__(self, api_key: str, own_domain: str):
        self.own_domain = own_domain
        self.headers = {"X-Api-Key": api_key}

    def _get(self, path: str, params: dict = None) -> dict:
        r = requests.get(f"{PRCRY_API}{path}", headers=self.headers, params=params or {})
        r.raise_for_status()
        return r.json()

    def find_competitors(self, keywords: list[str], limit: int = 10) -> list[str]:
        """Возвращает список доменов-конкурентов из выдачи по keywords."""
        domains = {}
        for keyword in keywords:
            try:
                data = self._get("/serp", {"query": keyword, "se": "yandex"})
                for result in data.get("results", []):
                    domain = result.get("domain", "")
                    if domain and domain != self.own_domain:
                        domains[domain] = domains.get(domain, 0) + 1
            except Exception as e:
                print(f"[prcry] SERP ошибка для '{keyword}': {e}")
        # сортируем по частоте появления в выдаче
        sorted_domains = sorted(domains, key=lambda d: domains[d], reverse=True)
        return sorted_domains[:limit]

    def analyze_domain(self, domain: str) -> dict:
        """Возвращает анализ домена: трафик, топ-страницы, ключевые слова."""
        try:
            data = self._get(f"/domain/{domain}")
            return {
                "domain": domain,
                "traffic": data.get("traffic", 0),
                "keywords_count": data.get("keywords_count", 0),
                "top_pages": data.get("top_pages", []),
            }
        except Exception as e:
            print(f"[prcry] Ошибка анализа {domain}: {e}")
            return {"domain": domain, "traffic": 0, "keywords_count": 0, "top_pages": []}

    def collect(self, keywords: list[str], max_competitors: int = 10) -> dict:
        """Возвращает {"competitors": [{"domain": ..., "traffic": ..., "top_pages": [...]}]}"""
        competitor_domains = self.find_competitors(keywords, limit=max_competitors)
        analyzed = [self.analyze_domain(d) for d in competitor_domains]
        return {"competitors": analyzed}
```

**Step 4: Запустить тест**

```bash
pytest tests/test_prcry.py -v
```

Ожидаемый вывод: `2 passed`

**Step 5: Commit**

```bash
git add collectors/prcry.py tests/test_prcry.py
git commit -m "feat(seo): add PR-CY collector"
```

---

### Task 5: Яндекс Вебмастер коллектор

**Files:**
- Create: `SEO/collectors/webmaster.py`
- Test: `SEO/tests/test_webmaster.py`

**Справка по API:**
Яндекс Вебмастер API v4: `https://api.webmaster.yandex.net/v4/`
- `GET /user/{user_id}/hosts/{host_id}/query-analytics/list` — позиции по запросам
- OAuth-токен в заголовке `Authorization: OAuth <token>`
- `host_id` — закодированный домен, например `https:unilist.ru:443`

**Step 1: Написать failing test**

```python
# tests/test_webmaster.py
import responses as resp_mock
import pytest
from collectors.webmaster import WebmasterCollector

FAKE_TOKEN = "fake_token"
FAKE_USER_ID = "12345"
FAKE_HOST_ID = "https:unilist.ru:443"

FAKE_QUERIES = {
    "queries": [
        {"query": "опросный лист продажи", "position": 7.2, "clicks": 45, "impressions": 320},
        {"query": "форма для клиента B2B", "position": 12.5, "clicks": 12, "impressions": 140},
    ]
}

@resp_mock.activate
def test_collect_returns_query_positions():
    url = f"https://api.webmaster.yandex.net/v4/user/{FAKE_USER_ID}/hosts/{FAKE_HOST_ID}/query-analytics/list"
    resp_mock.add(resp_mock.GET, url, json=FAKE_QUERIES, status=200)

    collector = WebmasterCollector(
        token=FAKE_TOKEN,
        user_id=FAKE_USER_ID,
        host_id=FAKE_HOST_ID,
    )
    result = collector.collect()

    assert isinstance(result, list)
    assert result[0]["query"] == "опросный лист продажи"
    assert result[0]["position"] == 7.2
    assert result[0]["clicks"] == 45
```

**Step 2: Запустить тест, убедиться что падает**

```bash
pytest tests/test_webmaster.py -v
```

**Step 3: Написать `collectors/webmaster.py`**

```python
import requests

WEBMASTER_API = "https://api.webmaster.yandex.net/v4"

class WebmasterCollector:
    def __init__(self, token: str, user_id: str, host_id: str):
        self.user_id = user_id
        self.host_id = host_id
        self.headers = {"Authorization": f"OAuth {token}"}

    def collect(self, limit: int = 500) -> list[dict]:
        """Возвращает список {"query": str, "position": float, "clicks": int, "impressions": int}."""
        url = (
            f"{WEBMASTER_API}/user/{self.user_id}"
            f"/hosts/{self.host_id}/query-analytics/list"
        )
        params = {"limit": limit, "offset": 0}
        try:
            r = requests.get(url, headers=self.headers, params=params)
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "query": q.get("query", ""),
                    "position": q.get("position", 0.0),
                    "clicks": q.get("clicks", 0),
                    "impressions": q.get("impressions", 0),
                }
                for q in data.get("queries", [])
            ]
        except Exception as e:
            print(f"[webmaster] Ошибка: {e}")
            return []
```

**Step 4: Запустить тест**

```bash
pytest tests/test_webmaster.py -v
```

Ожидаемый вывод: `1 passed`

**Step 5: Commit**

```bash
git add collectors/webmaster.py tests/test_webmaster.py
git commit -m "feat(seo): add Yandex Webmaster collector"
```

---

### Task 6: Claude Analyzer

**Files:**
- Create: `SEO/analyzers/claude_analyzer.py`
- Test: `SEO/tests/test_claude_analyzer.py`

**Step 1: Написать failing test**

```python
# tests/test_claude_analyzer.py
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
    with patch("anthropic.Anthropic") as mock_anthropic:
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
```

**Step 2: Запустить тест, убедиться что падает**

```bash
pytest tests/test_claude_analyzer.py -v
```

**Step 3: Написать `analyzers/claude_analyzer.py`**

```python
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
```

**Step 4: Запустить тест**

```bash
pytest tests/test_claude_analyzer.py -v
```

Ожидаемый вывод: `1 passed`

**Step 5: Commit**

```bash
git add analyzers/claude_analyzer.py tests/test_claude_analyzer.py
git commit -m "feat(seo): add Claude analyzer"
```

---

### Task 7: Оркестратор pipeline.py

**Files:**
- Create: `SEO/pipeline.py`
- Test: `SEO/tests/test_pipeline.py`

**Step 1: Написать failing test**

```python
# tests/test_pipeline.py
import os
import pytest
from unittest.mock import MagicMock, patch
from pipeline import run_pipeline

FAKE_CONFIG = {
    "seed_keywords": ["опросный лист продажи"],
    "your_domain": "unilist.ru",
    "apis": {
        "wordstat_token": "wt",
        "prcry_key": "pk",
        "webmaster_token": "wbt",
        "webmaster_user_id": "123",
        "claude_api_key": "ck",
    },
    "limits": {
        "wordstat_keywords_per_seed": 10,
        "prcry_competitors_to_analyze": 5,
        "max_pages_per_competitor": 5,
    },
}

def test_run_pipeline_creates_report_files(tmp_path):
    with patch("pipeline.load_config", return_value=FAKE_CONFIG), \
         patch("pipeline.WordstatCollector") as MockWordstat, \
         patch("pipeline.PrcyCollector") as MockPrcry, \
         patch("pipeline.WebmasterCollector") as MockWebmaster, \
         patch("pipeline.ClaudeAnalyzer") as MockClaude:

        MockWordstat.return_value.collect.return_value = [
            {"keyword": "опросный лист продажи", "volume": 4400}
        ]
        MockPrcry.return_value.collect.return_value = {
            "competitors": [{"domain": "competitor.ru", "traffic": 5000, "top_pages": []}]
        }
        MockWebmaster.return_value.collect.return_value = [
            {"query": "опросный лист продажи", "position": 0, "clicks": 0}
        ]
        MockClaude.return_value.analyze.return_value = "# Анализ\n## Приоритет 1\ntest"

        run_pipeline(config_path="config.yaml", reports_dir=str(tmp_path))

        date_dirs = list(tmp_path.iterdir())
        assert len(date_dirs) == 1
        report_dir = date_dirs[0]
        assert (report_dir / "keywords.md").exists()
        assert (report_dir / "competitors.md").exists()
        assert (report_dir / "action-plan.md").exists()
```

**Step 2: Запустить тест, убедиться что падает**

```bash
pytest tests/test_pipeline.py -v
```

**Step 3: Написать `pipeline.py`**

```python
import os
from datetime import date
from pathlib import Path

from config import load_config
from collectors.wordstat import WordstatCollector
from collectors.prcry import PrcyCollector
from collectors.webmaster import WebmasterCollector
from analyzers.claude_analyzer import ClaudeAnalyzer


def _keywords_to_markdown(keywords: list[dict]) -> str:
    lines = ["# Ключевые слова\n", "| Ключевое слово | Объём/мес |", "|---|---|"]
    for kw in sorted(keywords, key=lambda x: x["volume"], reverse=True):
        lines.append(f"| {kw['keyword']} | {kw['volume']} |")
    return "\n".join(lines)


def _competitors_to_markdown(competitors: list[dict]) -> str:
    lines = ["# Конкуренты\n"]
    for comp in competitors:
        lines.append(f"## {comp['domain']}")
        lines.append(f"- Трафик: {comp.get('traffic', '?')}/мес")
        lines.append(f"- Топ-страницы:")
        for page in comp.get("top_pages", [])[:5]:
            lines.append(f"  - {page.get('url', '')} ({page.get('traffic', '?')} визитов)")
        lines.append("")
    return "\n".join(lines)


def run_pipeline(config_path: str = "config.yaml", reports_dir: str = "reports"):
    config = load_config(config_path)
    apis = config["apis"]
    limits = config["limits"]
    seed_keywords = config["seed_keywords"]
    own_domain = config["your_domain"]

    print("[pipeline] Сбор ключевых слов через Вордстат...")
    wordstat = WordstatCollector(token=apis["wordstat_token"])
    keywords = wordstat.collect(seed_keywords, limit=limits["wordstat_keywords_per_seed"])

    print(f"[pipeline] Найдено {len(keywords)} ключевых слов. Ищем конкурентов через PR-CY...")
    prcry = PrcyCollector(api_key=apis["prcry_key"], own_domain=own_domain)
    keyword_list = [kw["keyword"] for kw in keywords[:10]]
    prcry_data = prcry.collect(keyword_list, max_competitors=limits["prcry_competitors_to_analyze"])

    print("[pipeline] Получаем свои позиции из Вебмастера...")
    webmaster_host_id = f"https:{own_domain}:443"
    webmaster = WebmasterCollector(
        token=apis["webmaster_token"],
        user_id=apis["webmaster_user_id"],
        host_id=webmaster_host_id,
    )
    own_positions = webmaster.collect()

    print("[pipeline] Анализируем через Claude...")
    analyzer = ClaudeAnalyzer(api_key=apis["claude_api_key"])
    analysis_data = {
        "keywords": keywords,
        "competitors": prcry_data["competitors"],
        "own_positions": own_positions,
        "own_domain": own_domain,
    }
    analysis_markdown = analyzer.analyze(analysis_data)

    today = date.today().isoformat()
    report_dir = Path(reports_dir) / today
    report_dir.mkdir(parents=True, exist_ok=True)

    (report_dir / "keywords.md").write_text(
        _keywords_to_markdown(keywords), encoding="utf-8"
    )
    (report_dir / "competitors.md").write_text(
        _competitors_to_markdown(prcry_data["competitors"]), encoding="utf-8"
    )
    (report_dir / "action-plan.md").write_text(analysis_markdown, encoding="utf-8")

    print(f"[pipeline] Готово! Отчёты в {report_dir}/")


if __name__ == "__main__":
    run_pipeline()
```

**Step 4: Запустить тест**

```bash
pytest tests/test_pipeline.py -v
```

Ожидаемый вывод: `1 passed`

**Step 5: Запустить все тесты**

```bash
pytest tests/ -v
```

Ожидаемый вывод: все тесты `passed`

**Step 6: Commit**

```bash
git add pipeline.py tests/test_pipeline.py
git commit -m "feat(seo): add pipeline orchestrator"
```

---

### Task 8: Cron-хук Claude Code

**Files:**
- Modify: `~/.claude/settings.json` (через `update-config` скилл)

**Step 1: Настроить еженедельный запуск через cron-хук**

Открыть новую сессию Claude Code и выполнить:
```
/update-config добавь cron: каждое воскресенье в 09:00 запускать python /Users/shuvaev/Продукты/unilist/saas-workspace/marketing/SEO/pipeline.py
```

**Step 2: Проверить что хук добавлен**

```bash
cat ~/.claude/settings.json | grep -A5 "cron"
```

**Step 3: Тестовый запуск pipeline вручную**

```bash
cd /Users/shuvaev/Продукты/unilist/saas-workspace/marketing/SEO
WORDSTAT_TOKEN=xxx PRCRY_API_KEY=yyy WEBMASTER_TOKEN=zzz WEBMASTER_USER_ID=123 ANTHROPIC_API_KEY=sk-... python pipeline.py
```

Ожидаемый вывод:
```
[pipeline] Сбор ключевых слов через Вордстат...
[pipeline] Найдено N ключевых слов. Ищем конкурентов через PR-CY...
[pipeline] Получаем свои позиции из Вебмастера...
[pipeline] Анализируем через Claude...
[pipeline] Готово! Отчёты в reports/2026-03-22/
```

**Step 4: Commit финальный**

```bash
git add .
git commit -m "feat(seo): complete SEO research pipeline v1"
```

---

## Переменные окружения (настроить перед запуском)

```bash
export WORDSTAT_TOKEN=        # OAuth-токен Яндекс (яндекс.паспорт → OAuth)
export PRCRY_API_KEY=         # Ключ из личного кабинета pr-cy.ru
export WEBMASTER_TOKEN=       # OAuth-токен Яндекс Вебмастер
export WEBMASTER_USER_ID=     # ID пользователя из Вебмастер API
export ANTHROPIC_API_KEY=     # API-ключ Anthropic
```

## Добавить keys.so (v2)

Когда появится ключ — создать `collectors/keysso.py` по образцу `prcry.py` и подключить в `pipeline.py`. Никаких других файлов менять не нужно.
