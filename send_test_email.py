import argparse
from datetime import datetime, timezone

from dotenv import load_dotenv

import config
from email_template import render_email
from lib.gmail_notifier import is_configured, send_html_report
from question_generator import generate_question
from theme_emojis import get_theme_emoji
from themes import THEMES


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Send a design preview email.")
    parser.add_argument("--recipient", default="d.piazza10@gmail.com", help="Recipient email address")
    parser.add_argument("--child-name", default="David", help="Placeholder child name")
    parser.add_argument("--theme", default=THEMES[0], choices=THEMES, help="Theme to preview")
    args = parser.parse_args()

    sender = config.GMAIL_SENDER
    app_password = config.GMAIL_APP_PASSWORD
    if not is_configured(sender, app_password, args.recipient):
        raise RuntimeError("Gmail credentials not fully configured — check env vars.")

    print(f"Generating question for theme: {args.theme}...")
    question, tip = generate_question(theme=args.theme, recent_questions=[], max_retries=3)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    theme_emoji = get_theme_emoji(args.theme)

    html = render_email(
        question=question,
        tip=tip,
        theme=args.theme,
        child_name=args.child_name,
        date_str=date_str,
        theme_emoji=theme_emoji,
    )
    subject = f"🌙 [DESIGN PREVIEW] Tonight's Bedtime Question for {args.child_name} • {date_str}"

    print(f"Sending test email to {args.recipient}...")
    send_html_report(
        subject=subject,
        html_body=html,
        sender=sender,
        app_password=app_password,
        recipients=args.recipient,
    )
    print(f"✓ Test email sent to {args.recipient}")


if __name__ == "__main__":
    main()
