import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def load_history(path: str = "data/question_history.json") -> list[dict]:
    """Load question history from JSON file. Returns empty list if file doesn't exist or is empty."""
    file_path = Path(path)
    if not file_path.exists():
        return []
    try:
        with open(file_path) as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def recent_window(history: list[dict], days: int = 30) -> list[dict]:
    """Filter history to entries from the last N days."""
    if not history:
        return []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    return [e for e in history if e.get("date", "") >= cutoff]


def append_entry(history: list[dict], date: str, theme: str, question: str, tip: str) -> list[dict]:
    """Return a new list with the entry appended (pure function, doesn't modify the input)."""
    return history + [{"date": date, "theme": theme, "question": question, "tip": tip}]


def save_history(history: list[dict], path: str = "data/question_history.json") -> None:
    """Write history to JSON file."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(history, f, indent=2)
        f.write("\n")
