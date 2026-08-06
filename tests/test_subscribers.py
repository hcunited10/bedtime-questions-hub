from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

import subscribers


class TestFilterActive:
    """Test active subscriber filtering."""

    def test_filter_active_mixed_case(self):
        """Filter respects mixed-case TRUE."""
        subs = [
            {"parent_email": "a@ex.com", "active": "TRUE"},
            {"parent_email": "b@ex.com", "active": "true"},
            {"parent_email": "c@ex.com", "active": "False"},
            {"parent_email": "d@ex.com", "active": "FALSE"},
        ]
        result = subscribers.filter_active(subs)
        assert len(result) == 2
        assert result[0]["parent_email"] == "a@ex.com"
        assert result[1]["parent_email"] == "b@ex.com"

    def test_filter_active_missing_field(self):
        """Missing 'active' field is treated as false."""
        subs = [{"parent_email": "a@ex.com"}, {"parent_email": "b@ex.com", "active": "TRUE"}]
        result = subscribers.filter_active(subs)
        assert len(result) == 1
        assert result[0]["parent_email"] == "b@ex.com"


class TestLocalNow:
    """Test UTC -> local timezone conversion."""

    def test_local_now_denver(self):
        """Verify timezone conversion for America/Denver."""
        utc_dt = datetime(2026, 8, 6, 3, 0, 0, tzinfo=timezone.utc)  # 3:00 AM UTC
        sub = {"timezone": "America/Denver"}
        result = subscribers.local_now(sub, utc_dt)
        assert result.hour == 21  # 9:00 PM previous day MDT (UTC-6)

    def test_local_now_eastern(self):
        """Verify timezone conversion for America/New_York."""
        utc_dt = datetime(2026, 8, 6, 3, 0, 0, tzinfo=timezone.utc)
        sub = {"timezone": "America/New_York"}
        result = subscribers.local_now(sub, utc_dt)
        assert result.hour == 23  # 11:00 PM same day EDT (UTC-4)


class TestIsDue:
    """Test subscriber due-ness logic."""

    def test_is_due_exact_match(self):
        """Subscriber is due when time matches exactly."""
        # UTC 2:30 Aug 6 = 20:30 MDT Aug 5 (UTC-6)
        utc_dt = datetime(2026, 8, 6, 2, 30, 0, tzinfo=timezone.utc)
        sub = {
            "parent_email": "a@ex.com",
            "child_name": "Alice",
            "desired_time": "20:30",
            "timezone": "America/Denver",
            "last_sent_date": "2026-08-04",
            "active": "TRUE",
        }
        assert subscribers.is_due(sub, utc_dt, tolerance_minutes=8)

    def test_is_due_within_tolerance(self):
        """Subscriber is due when within tolerance."""
        # UTC 2:35 Aug 6 = 20:35 MDT Aug 5 (5 min after 20:30)
        utc_dt = datetime(2026, 8, 6, 2, 35, 0, tzinfo=timezone.utc)
        sub = {
            "parent_email": "a@ex.com",
            "desired_time": "20:30",
            "timezone": "America/Denver",
            "last_sent_date": "2026-08-04",
            "active": "TRUE",
        }
        assert subscribers.is_due(sub, utc_dt, tolerance_minutes=8)

    def test_is_due_outside_tolerance(self):
        """Subscriber is not due when outside tolerance."""
        utc_dt = datetime(2026, 8, 6, 2, 40, 0, tzinfo=timezone.utc)
        sub = {
            "parent_email": "a@ex.com",
            "desired_time": "20:30",
            "timezone": "America/Denver",
            "last_sent_date": "2026-08-05",
            "active": "TRUE",
        }
        assert not subscribers.is_due(sub, utc_dt, tolerance_minutes=8)

    def test_is_due_already_sent_today_blocks(self):
        """Already sent today (their local date) blocks send even if time matches."""
        utc_dt = datetime(2026, 8, 6, 2, 30, 0, tzinfo=timezone.utc)
        sub = {
            "parent_email": "a@ex.com",
            "desired_time": "20:30",
            "timezone": "America/Denver",
            "last_sent_date": "2026-08-05",
            "active": "TRUE",
        }
        local_dt = subscribers.local_now(sub, utc_dt)
        local_date = local_dt.strftime("%Y-%m-%d")

        sub_already_sent = sub.copy()
        sub_already_sent["last_sent_date"] = local_date
        assert not subscribers.is_due(sub_already_sent, utc_dt, tolerance_minutes=8)

    def test_is_due_midnight_wraparound(self):
        """Test midnight wraparound: desired_time 23:58, now 00:03 next day."""
        utc_dt = datetime(2026, 8, 6, 6, 3, 0, tzinfo=timezone.utc)  # 00:03 MDT on Aug 6
        sub = {
            "parent_email": "a@ex.com",
            "desired_time": "23:58",
            "timezone": "America/Denver",
            "last_sent_date": "2026-08-05",
            "active": "TRUE",
        }
        result = subscribers.is_due(sub, utc_dt, tolerance_minutes=8)
        assert result  # Should match (5-minute difference within 8-minute tolerance)

    def test_is_due_invalid_time_format(self):
        """Invalid desired_time format returns False."""
        utc_dt = datetime(2026, 8, 6, 2, 30, 0, tzinfo=timezone.utc)
        sub = {
            "parent_email": "a@ex.com",
            "desired_time": "invalid",
            "timezone": "America/Denver",
            "last_sent_date": "2026-08-05",
        }
        assert not subscribers.is_due(sub, utc_dt, tolerance_minutes=8)


class TestGetDueSubscribers:
    """Test composite due-subscriber filtering."""

    def test_get_due_subscribers_mixed_statuses(self):
        """Filter to active + due only."""
        # UTC 2:30 Aug 6 = 20:30 MDT Aug 5
        utc_dt = datetime(2026, 8, 6, 2, 30, 0, tzinfo=timezone.utc)
        subs = [
            {
                "parent_email": "a@ex.com",
                "desired_time": "20:30",
                "timezone": "America/Denver",
                "last_sent_date": "2026-08-04",
                "active": "TRUE",
            },
            {
                "parent_email": "b@ex.com",
                "desired_time": "20:30",
                "timezone": "America/Denver",
                "last_sent_date": "2026-08-04",
                "active": "FALSE",
            },
            {
                "parent_email": "c@ex.com",
                "desired_time": "18:00",
                "timezone": "America/Denver",
                "last_sent_date": "2026-08-04",
                "active": "TRUE",
            },
        ]
        result = subscribers.get_due_subscribers(subs, utc_dt, tolerance_minutes=8)
        assert len(result) == 1
        assert result[0]["parent_email"] == "a@ex.com"


class TestMarkSent:
    """Test worksheet update logic."""

    def test_mark_sent_valid(self):
        """Mark sent updates the correct cell."""
        mock_ws = MagicMock()
        mock_ws.row_values.return_value = ["timestamp", "parent_email", "child_name", "desired_time", "timezone", "active", "last_sent_date"]

        sub = {"parent_email": "a@ex.com", "_row": 2}
        subscribers.mark_sent(mock_ws, sub, "2026-08-06")

        mock_ws.update_cell.assert_called_once_with(2, 7, "2026-08-06")

    def test_mark_sent_missing_row_raises(self):
        """Missing _row field raises ValueError."""
        mock_ws = MagicMock()
        sub = {"parent_email": "a@ex.com"}
        with pytest.raises(ValueError, match="missing _row"):
            subscribers.mark_sent(mock_ws, sub, "2026-08-06")

    def test_mark_sent_missing_header_raises(self):
        """Missing last_sent_date column raises ValueError."""
        mock_ws = MagicMock()
        mock_ws.row_values.return_value = ["timestamp", "parent_email"]
        sub = {"parent_email": "a@ex.com", "_row": 2}
        with pytest.raises(ValueError, match="missing 'last_sent_date'"):
            subscribers.mark_sent(mock_ws, sub, "2026-08-06")
