from datetime import datetime
import pytz

def parse_datetime(date_str: str, timezone_str: str = "Europe/Amsterdam") -> datetime:
    try:
        dt = datetime.strptime(date_str.strip(), "%d.%m.%Y %H:%M")
        tz = pytz.timezone(timezone_str)
        return tz.localize(dt)
    except ValueError:
        return None

def get_current_time(timezone_str: str = "Europe/Amsterdam") -> datetime:
    tz = pytz.timezone(timezone_str)
    return datetime.now(tz)

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def get_example_times(timezone_str: str = "Europe/Amsterdam") -> str:
    now = get_current_time(timezone_str)
    
    from datetime import timedelta
    
    examples = []
    examples.append(f"{format_datetime(now + timedelta(minutes=10))} - через 10 минут")
    examples.append(f"{format_datetime(now + timedelta(hours=1))} - через час")
    examples.append(f"{format_datetime(now + timedelta(days=1))} - через день")
    examples.append(f"{format_datetime(now + timedelta(weeks=1))} - через неделю")
    
    return "\n".join(examples)