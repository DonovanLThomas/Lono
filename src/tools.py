from datetime import datetime
from zoneinfo import ZoneInfo


CURRENT_TIME_TOOL = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Current date and time. Timezone is fixed; call with no arguments.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}

TOOLS_REGISTRY = {
    "get_current_time": {
        "schema": CURRENT_TIME_TOOL,
        "handler" get_current_time,
    },
}



def get_current_time() -> str:
    """Return the current date and time in America/Los_Angeles as an ISO timestamp with a UTC offset. Takes no arguments."""
    now = datetime.now(ZoneInfo("America/Los_Angeles"))


    return now.isoformat()
