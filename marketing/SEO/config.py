import os
import re
import yaml

def _expand_env_vars(value):
    """Заменяет ${VAR} на значение переменной окружения."""
    if not isinstance(value, str):
        return value
    pattern = re.compile(r'\$\{([^}]+)\}')
    def replacer(match):
        return os.environ.get(match.group(1), match.group(0))
    return pattern.sub(replacer, value)

def _expand_recursive(obj):
    if isinstance(obj, dict):
        return {k: _expand_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_recursive(i) for i in obj]
    return _expand_env_vars(obj)

def _find_unexpanded(obj, path=""):
    """Returns list of paths where env vars were not expanded."""
    unexpanded = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            unexpanded.extend(_find_unexpanded(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            unexpanded.extend(_find_unexpanded(v, f"{path}[{i}]"))
    elif isinstance(obj, str) and re.search(r'\$\{[^}]+\}', obj):
        unexpanded.append(path)
    return unexpanded

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    config = _expand_recursive(raw)
    unexpanded = _find_unexpanded(config)
    if unexpanded:
        print(f"[config] ПРЕДУПРЕЖДЕНИЕ: переменные окружения не установлены: {', '.join(unexpanded)}")
    return config
