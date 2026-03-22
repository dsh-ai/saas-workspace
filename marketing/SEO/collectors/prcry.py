# collectors/prcry.py
import requests

PRCRY_API = "https://api.pr-cy.ru"

class PrcyCollector:
    def __init__(self, api_key: str, own_domain: str):
        self.own_domain = own_domain
        self.headers = {"X-Api-Key": api_key}

    def _get(self, path: str, params: dict = None) -> dict:
        r = requests.get(f"{PRCRY_API}{path}", headers=self.headers, params=params or {}, timeout=15)
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
