import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

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
    try:
        config = load_config(config_path)
        apis = config["apis"]
        limits = config["limits"]
        seed_keywords = config["seed_keywords"]
        own_domain = config["your_domain"]

        print("[pipeline] Сбор ключевых слов через Вордстат...")
        wordstat = WordstatCollector(token=apis["wordstat_token"])
        keywords = wordstat.collect(seed_keywords, limit=limits["wordstat_keywords_per_seed"])

        if not keywords:
            print("[pipeline] ОШИБКА: Вордстат не вернул ключевых слов. Прерываем pipeline.")
            sys.exit(1)

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
    except SystemExit:
        raise
    except Exception as e:
        print(f"[pipeline] КРИТИЧЕСКАЯ ОШИБКА: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
