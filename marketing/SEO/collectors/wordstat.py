import time
import xml.etree.ElementTree as ET
import xml.sax.saxutils
import requests

WORDSTAT_API = "https://api.direct.yandex.ru/v4/"

MAX_POLL_ATTEMPTS = 30
POLL_INTERVAL = 3  # seconds


class WordstatCollector:
    def __init__(self, token: str):
        self.token = token
        self.base_headers = {
            "Authorization": f"OAuth {token}",
            "Content-Type": "text/xml; charset=utf-8",
        }

    def _soap_request(self, body: str, action: str) -> ET.Element:
        headers = {**self.base_headers, "SOAPAction": action}
        r = requests.post(WORDSTAT_API, data=body.encode("utf-8"), headers=headers, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        ns = {"soap": "http://schemas.xmlsoap.org/soap/envelope/"}
        return root.find(".//soap:Body", ns)[0]

    def _create_report(self, keywords: list[str]) -> int:
        phrases_xml = "".join(
            f"<Item>{xml.sax.saxutils.escape(kw)}</Item>"
            for kw in keywords
        )
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <CreateNewWordstatReportRequest>
      <Phrases>{phrases_xml}</Phrases>
    </CreateNewWordstatReportRequest>
  </soap:Body>
</soap:Envelope>"""
        response = self._soap_request(body, "CreateNewWordstatReport")
        return int(response.find("data").text)

    def _get_report(self, report_id: int) -> list[dict]:
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetWordstatReportRequest>
      <ReportID>{report_id}</ReportID>
    </GetWordstatReportRequest>
  </soap:Body>
</soap:Envelope>"""
        response = self._soap_request(body, "GetWordstatReport")
        results = []
        # API возвращает data=pending пока отчёт не готов
        data_el = response.find("data")
        if data_el is None or (data_el.text and data_el.text.strip() == "pending"):
            return []
        for item in response.findall(".//Phrases/Item"):
            phrase = item.findtext("Phrase", "")
            shows = int(item.findtext("Shows", "0"))
            if phrase:
                results.append({"keyword": phrase, "volume": shows})
        return results

    def collect(self, seed_keywords: list[str], limit: int = 50) -> list[dict]:
        """Возвращает список {"keyword": str, "volume": int}."""
        results = []
        for keyword in seed_keywords:
            try:
                report_id = self._create_report([keyword])
                for attempt in range(MAX_POLL_ATTEMPTS):
                    time.sleep(POLL_INTERVAL)
                    data = self._get_report(report_id)
                    if data:  # report is ready
                        results.extend(data[:limit])
                        break
                else:
                    print(f"[wordstat] Таймаут ожидания отчёта для '{keyword}'")
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
