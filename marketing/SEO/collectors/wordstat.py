import time
import requests

DIRECT_API = "https://api.direct.yandex.com/json/v5/"

MAX_POLL_ATTEMPTS = 30
POLL_INTERVAL = 5  # seconds


class WordstatCollector:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Language": "ru",
        }

    def _post(self, service: str, method: str, params: dict) -> dict:
        body = {"method": method, "params": params}
        r = requests.post(
            DIRECT_API + service,
            json=body,
            headers=self.headers,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"Yandex API error: {data['error']}")
        return data.get("result", data)

    def _create_report(self, keywords: list[str]) -> int:
        result = self._post(
            "keywordsresearch",
            "createReport",
            {
                "Phrases": keywords,
                "GeoID": [225],  # Россия
            },
        )
        return result["ReportID"]

    def _get_report(self, report_id: int) -> list[dict]:
        result = self._post(
            "keywordsresearch",
            "getReport",
            {"ReportID": report_id},
        )
        # Пока не готов — возвращаем пустой список
        if result.get("Status") != "Done":
            return []
        items = []
        for row in result.get("SearchedWith", []):
            phrase = row.get("Phrase", "")
            shows = int(row.get("Shows", 0))
            if phrase:
                items.append({"keyword": phrase, "volume": shows})
        return items

    def collect(self, seed_keywords: list[str], limit: int = 50) -> list[dict]:
        """Возвращает список {"keyword": str, "volume": int}."""
        results = []
        for keyword in seed_keywords:
            try:
                report_id = self._create_report([keyword])
                for attempt in range(MAX_POLL_ATTEMPTS):
                    time.sleep(POLL_INTERVAL)
                    data = self._get_report(report_id)
                    if data:
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
