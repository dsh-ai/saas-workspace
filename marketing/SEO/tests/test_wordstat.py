import responses as resp_mock
import pytest
from unittest.mock import patch
from collectors.wordstat import WordstatCollector

FAKE_TOKEN = "fake_token"

FAKE_CREATE_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <CreateNewWordstatReportResponse>
      <data>12345</data>
    </CreateNewWordstatReportResponse>
  </soap:Body>
</soap:Envelope>"""

FAKE_GET_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetWordstatReportResponse>
      <data>
        <Phrases>
          <Item>
            <Phrase>опросный лист продажи</Phrase>
            <Shows>4400</Shows>
          </Item>
          <Item>
            <Phrase>опросник для клиента</Phrase>
            <Shows>1200</Shows>
          </Item>
        </Phrases>
      </data>
    </GetWordstatReportResponse>
  </soap:Body>
</soap:Envelope>"""

@resp_mock.activate
@patch("collectors.wordstat.time.sleep")  # skip real waits
def test_collect_returns_keywords_with_volumes(mock_sleep):
    # First POST: create report
    resp_mock.add(resp_mock.POST,
        "https://api.direct.yandex.ru/v4/",
        body=FAKE_CREATE_RESPONSE, status=200,
        match_querystring=False)
    # Second POST: get report — returns data immediately so loop breaks on first attempt
    resp_mock.add(resp_mock.POST,
        "https://api.direct.yandex.ru/v4/",
        body=FAKE_GET_RESPONSE, status=200,
        match_querystring=False)

    collector = WordstatCollector(token=FAKE_TOKEN)
    result = collector.collect(["опросный лист продажи"], limit=50)

    assert isinstance(result, list)
    assert len(result) > 0
    assert "keyword" in result[0]
    assert "volume" in result[0]
    assert result[0]["volume"] > 0
    # sleep must have been called at least once (polling loop ran)
    mock_sleep.assert_called()
