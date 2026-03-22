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
