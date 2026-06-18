from datetime import datetime
import pytz

def local_to_utc(local_time_str, timezone):
    """Convert local time string to UTC datetime"""
    dt = datetime.strptime(local_time_str, '%Y-%m-%dT%H:%M:%S')
    tz = pytz.timezone(timezone)
    local_dt = tz.localize(dt)
    return local_dt.astimezone(pytz.utc)

def utc_to_local(utc_dt, timezone):
    """Convert UTC datetime to local timezone"""
    tz = pytz.timezone(timezone)
    return utc_dt.astimezone(tz)

def get_date_in_timezone(date_str, timezone):
    """Get date in specific timezone"""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    tz = pytz.timezone(timezone)
    local_dt = tz.localize(dt)
    return local_dt.strftime('%Y-%m-%d')

def minutes_between(from_dt, to_dt):
    """Calculate minutes between two datetimes"""
    delta = to_dt - from_dt
    return int(delta.total_seconds() / 60)

def format_time(iso_time_str, timezone):
    """Format time for display (local time)"""
    dt = datetime.strptime(iso_time_str, '%Y-%m-%dT%H:%M:%S')
    tz = pytz.timezone(timezone)
    local_dt = tz.localize(dt)
    return local_dt.strftime('%H:%M')

def format_date(iso_date_str):
    """Format date for display"""
    dt = datetime.strptime(iso_date_str, '%Y-%m-%d')
    return dt.strftime('%b %d, %Y')

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
