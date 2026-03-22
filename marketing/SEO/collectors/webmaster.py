# collectors/webmaster.py
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
            r = requests.get(url, headers=self.headers, params=params, timeout=15)
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
