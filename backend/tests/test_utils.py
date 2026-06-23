from utils import format_duration, format_time


def test_format_time_returns_local_hour_and_minute():
    formatted = format_time("2024-03-15T08:30:00", "America/New_York")
    assert formatted == "08:30"


def test_format_duration_formats_minutes_only():
    assert format_duration(45) == "45m"


def test_format_duration_formats_exact_hours():
    assert format_duration(120) == "2h"


def test_format_duration_formats_hours_and_minutes():
    assert format_duration(185) == "3h 5m"
