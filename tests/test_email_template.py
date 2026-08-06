from email_template import render_email


def test_render_email_contains_question():
    """Rendered email contains the question text."""
    html = render_email(
        question="What did you do today?",
        tip="This helps her reflect.",
        theme="courage",
        child_name="Alice",
        date_str="2026-08-06",
        theme_emoji="💪",
    )
    assert "What did you do today?" in html
    assert "Alice" in html
    assert "2026-08-06" in html


def test_render_email_contains_tip():
    """Rendered email contains the parent tip."""
    html = render_email(
        question="Q",
        tip="This is a custom tip.",
        theme="kindness",
        child_name="Bob",
        date_str="2026-08-06",
    )
    assert "This is a custom tip." in html


def test_render_email_contains_theme():
    """Rendered email contains the theme title."""
    html = render_email(
        question="Q",
        tip="T",
        theme="resilience",
        child_name="Carol",
        date_str="2026-08-06",
    )
    assert "Resilience" in html


def test_render_email_contains_generic_greeting():
    """Rendered email contains the generic greeting, not hardcoded names."""
    html = render_email(
        question="Q",
        tip="T",
        theme="courage",
        child_name="Dana",
        date_str="2026-08-06",
    )
    assert "Good evening!" in html
    assert "David" not in html
    assert "Brittnee" not in html


def test_render_email_has_no_style_blocks():
    """Email uses only inline styles, no <style> blocks (for email client compatibility)."""
    html = render_email(
        question="Q",
        tip="T",
        theme="courage",
        child_name="Eve",
        date_str="2026-08-06",
    )
    assert "<style>" not in html.lower()


def test_render_email_table_layout():
    """Email uses table-based layout for email compatibility."""
    html = render_email(
        question="Q",
        tip="T",
        theme="courage",
        child_name="Frank",
        date_str="2026-08-06",
    )
    assert "<table" in html
    assert "<tr>" in html
    assert "<td" in html


def test_render_email_custom_theme_emoji():
    """Renders the provided theme emoji."""
    html = render_email(
        question="Q",
        tip="T",
        theme="creativity",
        child_name="Grace",
        date_str="2026-08-06",
        theme_emoji="🎨",
    )
    assert "🎨" in html
