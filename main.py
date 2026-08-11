from datetime import datetime, timezone

from dotenv import load_dotenv

import config
import subscribers
from email_template import render_email
from history import append_entry, load_history, recent_window, save_history
from lib.gmail_notifier import is_configured, send_html_report
from question_generator import generate_question
from theme_emojis import get_theme_emoji
from themes import pick_todays_theme


def main() -> None:
    load_dotenv()

    now_utc = datetime.now(timezone.utc)

    try:
        worksheet = subscribers._open_worksheet()
        all_subscribers = subscribers.load_subscribers(worksheet)
    except (ValueError, RuntimeError) as e:
        print(f"Failed to load subscribers: {e}")
        return

    due = subscribers.get_due_subscribers(all_subscribers, now_utc, config.SEND_TOLERANCE_MINUTES)

    if not due:
        print("No subscribers due at this time, skipping question generation.")
        return

    print(f"Found {len(due)} subscriber(s) due for email.")

    history = load_history()
    recent = recent_window(history, days=30)
    recent_questions = [e["question"] for e in recent]

    theme = pick_todays_theme(history)
    question, tip = generate_question(theme=theme, recent_questions=recent_questions, max_retries=3)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    theme_emoji = get_theme_emoji(theme)

    sender = config.GMAIL_SENDER
    app_password = config.GMAIL_APP_PASSWORD

    if not is_configured(sender, app_password, "dummy"):
        raise RuntimeError("Gmail credentials not fully configured — check env vars.")

    sent_count = 0
    failures = []

    for subscriber in due:
        try:
            sub_local_dt = subscribers.local_now(subscriber, now_utc)
            sub_local_date = sub_local_dt.strftime("%Y-%m-%d")

            html = render_email(
                question=question,
                tip=tip,
                theme=theme,
                child_name=subscriber["child_name"],
                date_str=sub_local_date,
                theme_emoji=theme_emoji,
            )

            subject = f"🌙 Tonight's Bedtime Question for {subscriber['child_name']} • {sub_local_date}"

            send_html_report(
                subject=subject,
                html_body=html,
                sender=sender,
                app_password=app_password,
                recipients=subscriber["parent_email"],
            )

            sent_count += 1
            print(f"✓ Sent to {subscriber['parent_email']} ({subscriber['child_name']})")

            subscribers.mark_sent(worksheet, subscriber, sub_local_date)
        except (ValueError, RuntimeError) as e:
            failures.append((subscriber["parent_email"], str(e)))
            print(f"✗ Failed to send to {subscriber['parent_email']}: {e}")

    if sent_count > 0:
        updated = append_entry(history, date=date_str, theme=theme, question=question, tip=tip)
        save_history(updated)
        print(f"✓ Persisted shared question history ({sent_count} email(s) sent)")
    else:
        print("No emails sent successfully, skipping history update.")

    if failures:
        print(f"\n{len(failures)} failure(s):")
        for email, error in failures:
            print(f"  - {email}: {error}")


if __name__ == "__main__":
    main()
