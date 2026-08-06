THEMES = [
    "courage",
    "kindness",
    "resilience",
    "curiosity",
    "gratitude",
    "teamwork",
    "creativity",
    "honesty",
    "perseverance",
    "empathy",
    "confidence",
    "growth",
]


def pick_todays_theme(history: list[dict]) -> str:
    """
    Pick today's theme deterministically based on history length.
    Ensures a stable rotation: every 12 questions cycles through all themes exactly once.
    """
    cycle_index = (len(history) // 12) % len(THEMES)
    return THEMES[cycle_index]
