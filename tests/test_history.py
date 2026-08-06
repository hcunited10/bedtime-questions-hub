import json
from datetime import datetime, timedelta, timezone

from history import append_entry, load_history, recent_window, save_history


def test_load_history_missing_file():
    """Missing file returns empty list."""
    result = load_history("/nonexistent/path.json")
    assert result == []


def test_load_history_empty_file(tmp_path):
    """Empty file returns empty list."""
    path = tmp_path / "empty.json"
    path.write_text("[]")
    result = load_history(str(path))
    assert result == []


def test_load_history_valid_file(tmp_path):
    """Valid JSON file is loaded."""
    path = tmp_path / "history.json"
    data = [
        {"date": "2026-08-01", "theme": "courage", "question": "Q1", "tip": "T1"},
        {"date": "2026-08-02", "theme": "kindness", "question": "Q2", "tip": "T2"},
    ]
    path.write_text(json.dumps(data))
    result = load_history(str(path))
    assert len(result) == 2
    assert result[0]["question"] == "Q1"


def test_load_history_corrupted_json_returns_empty(tmp_path):
    """Corrupted JSON returns empty list."""
    path = tmp_path / "corrupted.json"
    path.write_text("{not valid json}")
    result = load_history(str(path))
    assert result == []


def test_recent_window_all_within_range(tmp_path):
    """All entries within range are returned."""
    path = tmp_path / "history.json"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    data = [
        {"date": yesterday, "theme": "courage", "question": "Q1", "tip": "T1"},
        {"date": today, "theme": "kindness", "question": "Q2", "tip": "T2"},
    ]
    path.write_text(json.dumps(data))
    result = recent_window(load_history(str(path)), days=30)
    assert len(result) == 2


def test_recent_window_excludes_old_entries(tmp_path):
    """Old entries outside the window are excluded."""
    path = tmp_path / "history.json"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    old_date = (datetime.now(timezone.utc) - timedelta(days=40)).strftime("%Y-%m-%d")
    data = [
        {"date": old_date, "theme": "courage", "question": "Q1", "tip": "T1"},
        {"date": today, "theme": "kindness", "question": "Q2", "tip": "T2"},
    ]
    path.write_text(json.dumps(data))
    result = recent_window(load_history(str(path)), days=30)
    assert len(result) == 1
    assert result[0]["date"] == today


def test_recent_window_empty_history(tmp_path):
    """Empty history returns empty list."""
    path = tmp_path / "history.json"
    path.write_text("[]")
    result = recent_window(load_history(str(path)), days=30)
    assert result == []


def test_append_entry_is_pure():
    """append_entry doesn't modify the input list."""
    original = [{"date": "2026-08-01", "theme": "courage", "question": "Q1", "tip": "T1"}]
    original_copy = original.copy()
    result = append_entry(original, "2026-08-02", "kindness", "Q2", "T2")
    assert original == original_copy
    assert len(result) == 2
    assert result[1]["date"] == "2026-08-02"


def test_save_history_creates_directory(tmp_path):
    """save_history creates parent directories."""
    path = tmp_path / "nested" / "deep" / "history.json"
    save_history([{"date": "2026-08-01", "theme": "courage", "question": "Q", "tip": "T"}], str(path))
    assert path.exists()


def test_save_history_valid_json(tmp_path):
    """save_history writes valid JSON with trailing newline."""
    path = tmp_path / "history.json"
    data = [{"date": "2026-08-01", "theme": "courage", "question": "Q", "tip": "T"}]
    save_history(data, str(path))
    content = path.read_text()
    assert content.endswith("\n")
    loaded = json.loads(content.rstrip())
    assert loaded == data


def test_save_and_load_roundtrip(tmp_path):
    """Save and load preserves data exactly."""
    path = tmp_path / "history.json"
    original = [
        {"date": "2026-08-01", "theme": "courage", "question": "Q1", "tip": "T1"},
        {"date": "2026-08-02", "theme": "kindness", "question": "Q2", "tip": "T2"},
    ]
    save_history(original, str(path))
    loaded = load_history(str(path))
    assert loaded == original
