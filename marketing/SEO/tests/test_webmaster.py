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
