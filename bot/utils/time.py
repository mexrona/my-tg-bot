from datetime import datetime


def format_time(dt: datetime | None = None) -> str:
    """Return local time as HH:MM."""
    moment = dt or datetime.now()
    return moment.strftime("%H:%M")
