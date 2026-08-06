import json
from datetime import datetime

import gspread
import pytz
from google.oauth2.service_account import Credentials

import config


def _open_worksheet() -> gspread.Worksheet:
    """
    Open the Subscribers worksheet via gspread + service-account credentials.
    Raises ValueError if GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SHEET_ID are not configured.
    """
    if not config.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not configured")
    if not config.GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID not configured")

    try:
        service_account_dict = json.loads(config.GOOGLE_SERVICE_ACCOUNT_JSON)
    except json.JSONDecodeError as e:
        raise ValueError(f"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {e}")

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(service_account_dict, scopes=scopes)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(config.GOOGLE_SHEET_ID)
    return sheet.worksheet(config.SUBSCRIBERS_SHEET_TAB)


def load_subscribers(worksheet: gspread.Worksheet | None = None) -> list[dict]:
    """
    Load active subscribers from the Sheet.
    Attaches a '_row' field to each dict (2-indexed row number) for later targeted updates via update_cell.
    """
    if worksheet is None:
        worksheet = _open_worksheet()

    all_records = worksheet.get_all_records()
    for i, record in enumerate(all_records, start=2):
        record["_row"] = i

    return all_records


def filter_active(subscribers: list[dict]) -> list[dict]:
    """Pure: filter to active=TRUE subscribers (case-insensitive)."""
    return [s for s in subscribers if s.get("active", "").upper() == "TRUE"]


def local_now(subscriber: dict, now_utc: datetime) -> datetime:
    """
    Pure: convert UTC to the subscriber's local timezone.
    """
    tz = pytz.timezone(subscriber["timezone"])
    return now_utc.astimezone(tz)


def is_due(subscriber: dict, now_utc: datetime, tolerance_minutes: int = 8) -> bool:
    """
    Pure: check if a subscriber is due for an email right now.

    Returns True if:
    1. Current local time is within tolerance_minutes of desired_time, AND
    2. The subscriber hasn't already received an email on their local calendar date today.
    """
    local_dt = local_now(subscriber, now_utc)
    local_date_str = local_dt.strftime("%Y-%m-%d")

    # Check if already sent today (their local date)
    last_sent = subscriber.get("last_sent_date", "")
    if last_sent == local_date_str:
        return False

    # Parse desired_time (HH:MM format)
    desired_time_str = subscriber.get("desired_time", "")
    try:
        desired_hour, desired_minute = map(int, desired_time_str.split(":"))
    except (ValueError, AttributeError):
        return False

    # Calculate time difference in minutes, handling midnight wraparound
    current_minutes = local_dt.hour * 60 + local_dt.minute
    desired_minutes = desired_hour * 60 + desired_minute
    diff = current_minutes - desired_minutes

    # Modular arithmetic: if diff is very negative (e.g., -1400 when crossing midnight),
    # add 24*60 to bring it into the positive wraparound range
    if diff < -(24 * 60 / 2):
        diff += 24 * 60

    return abs(diff) <= tolerance_minutes


def get_due_subscribers(
    subscribers: list[dict], now_utc: datetime, tolerance_minutes: int = 8
) -> list[dict]:
    """Pure composition: filter to active subscribers who are currently due."""
    active = filter_active(subscribers)
    return [s for s in active if is_due(s, now_utc, tolerance_minutes)]


def mark_sent(worksheet: gspread.Worksheet, subscriber: dict, local_date_str: str) -> None:
    """
    Impure: update the subscriber's last_sent_date in the Sheet.
    Uses the _row field attached by load_subscribers.
    """
    row = subscriber.get("_row")
    if not row:
        raise ValueError("Subscriber dict missing _row field (must be loaded via load_subscribers)")

    # Find the column index for last_sent_date by reading the header row
    headers = worksheet.row_values(1)
    try:
        col_index = headers.index("last_sent_date") + 1
    except ValueError:
        raise ValueError("Sheet header row missing 'last_sent_date' column")

    worksheet.update_cell(row, col_index, local_date_str)
