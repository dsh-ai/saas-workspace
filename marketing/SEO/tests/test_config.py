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
