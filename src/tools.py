from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_time() -> str:
    now = datetime.now(ZoneInfo("America/Los_Angeles"))


    return now.isoformat()
