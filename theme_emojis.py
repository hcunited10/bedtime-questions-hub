THEME_EMOJIS = {
    "courage": "💪",
    "kindness": "💝",
    "resilience": "🌱",
    "curiosity": "🔍",
    "gratitude": "🙏",
    "teamwork": "🤝",
    "creativity": "🎨",
    "honesty": "💎",
    "perseverance": "🏔️",
    "empathy": "🌈",
    "confidence": "🌟",
    "growth": "🚀",
}


def get_theme_emoji(theme: str) -> str:
    return THEME_EMOJIS.get(theme, "✨")
