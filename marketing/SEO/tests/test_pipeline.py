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
