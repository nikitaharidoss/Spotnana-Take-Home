from datetime import datetime
from zoneinfo import ZoneInfo


def format_time(iso_time_str, timezone):
    """Format time for display (local time)"""
    dt = datetime.strptime(iso_time_str, '%Y-%m-%dT%H:%M:%S')
    tz = ZoneInfo(timezone)
    local_dt = dt.replace(tzinfo=tz)
    return local_dt.strftime('%H:%M')


def format_duration(minutes):
    """Format duration as HhMm"""
    hours = minutes // 60
    mins = minutes % 60
    if hours == 0:
        return f"{mins}m"
    elif mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}m"
