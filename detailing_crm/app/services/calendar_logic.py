"""Bay calendar logic: duration + buffer overlap check (pure functions).

Replaces the first draft's exact-start-time-only check. One bay is the
default for a solo shop; BAY_COUNT is configurable when a second bay/tech
is added. Buffer (default 30 min) prevents back-to-back impossible days --
a feature every serious detailing CRM advertises.
"""
from datetime import datetime, timedelta
BAY_COUNT = 1
BUFFER_MINUTES = 30

def slot_window(start: datetime, duration_hours: float, buffer_minutes: int = BUFFER_MINUTES):
    end = start + timedelta(hours=duration_hours)
    return start, end + timedelta(minutes=buffer_minutes)

def overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end

def is_slot_available(existing, new_start: datetime, duration_hours: float, bay_count: int = BAY_COUNT) -> bool:
    """existing: iterable of (start_datetime, duration_hours) for scheduled/in_bay jobs."""
    n_start, n_end = slot_window(new_start, duration_hours)
    conflicts = 0
    for s, d in existing:
        e_start, e_end = slot_window(s, d)
        if overlaps(n_start, n_end, e_start, e_end):
            conflicts += 1
            if conflicts >= bay_count:
                return False
    return True
