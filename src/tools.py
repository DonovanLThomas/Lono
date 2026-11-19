from datetime import datetime
from zoneinfo import ZoneInfo
import json

from .config import GOOGLE_TIMEZONE
from .google_services import get_recent_emails, get_upcoming_events
from .storage import insert_note, list_notes


def get_current_time() -> str:
    """Return a short current-time sentence in the configured timezone."""
    now = datetime.now(ZoneInfo(GOOGLE_TIMEZONE))
    display_time = now.strftime("%I:%M %p").lstrip("0")
    return f"The time is {display_time}."


def validate_task_title(title: str) -> str:
    if not isinstance(title, str):
        raise ValueError(
            f"{title} is not a string"
        )

    title = title.strip()

    if title == "":
        raise ValueError(
            f"Empty Title"
        )
    return title


def save_note(raw_text: str, bullets: list[str] | None = None) -> str:
    if not bullets:
        bullets = [raw_text]

    note_id = insert_note(raw_text, bullets)

    return json.dumps(
        {
            "status": "saved",
            "note_id": note_id,
        }
    )


def get_saved_notes() -> str:
    notes = list_notes()

    return json.dumps(
        {
            "status": "success",
            "notes": notes,
        }
    )


def get_daily_brief() -> str:
    try:
        emails = get_recent_emails(hours=24, limit=10)
        events = get_upcoming_events(hours=48, limit=20)
    except RuntimeError as error:
        return json.dumps(
            {
                "status": "error",
                "message": str(error),
            }
        )

    return json.dumps(
        {
            "status": "success",
            "timezone": GOOGLE_TIMEZONE,
            "window": {
                "email_hours": 24,
                "calendar_hours": 48,
            },
            "emails": emails,
            "calendar_events": events,
        }
    )


CURRENT_TIME_TOOL = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": (
            "Return only a short current-time sentence in the user's configured "
            "timezone. Call with no arguments."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}

DAILY_BRIEF_TOOL = {
    "type": "function",
    "function": {
        "name": "get_daily_brief",
        "description": (
            "Read recent Gmail inbox metadata and upcoming Google Calendar events "
            "to prepare a concise schedule briefing. Use when the user asks what "
            "is coming up, what is on their schedule, for a daily brief, or to "
            "review recent email alongside calendar events. This tool is read-only."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}

LIST_NOTES_TOOL = {
    "type": "function",
    "function": {
        "name": "list_notes",
        "description": (
            "Retrieve the user's saved notes when they ask what they "
            "have saved, ask to review their notes, or request their notes."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}

SAVE_NOTE_TOOL = {
    "type": "function",
    "function": {
        "name": "save_note",
        "description": (
            "Save a note when the user explicitly asks to remember, "
            "record, or take note of something. Preserve the meaning and "
            "wording of the content requested for storage in raw_text, "
            "excluding command phrases such as 'save this note', and organize it "
            "into concise, faithful bullet points. Do not invent facts."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "raw_text": {
                    "type": "string",
                    "description": (
                        "The content the user asked to save, with all relevant "
                        "information preserved."
                    ),
                },
                "bullets": {
                    "type": "array",
                    "description": (
                        "The note reorganized into concise bullet items."
                    ),
                    "items": {
                        "type": "string",
                    },
                    "minItems": 1,
                },
            },
            "required": ["raw_text"],
            "additionalProperties": False,
        },
    },
}

TOOLS_REGISTRY = {
    "get_current_time": {
        "schema": CURRENT_TIME_TOOL,
        "handler": get_current_time,
        "direct_return": True,
    },
    "save_note": {
        "schema": SAVE_NOTE_TOOL,
        "handler": save_note,
    },
    "list_notes": {
        "schema": LIST_NOTES_TOOL,
        "handler": get_saved_notes,
    },
    "get_daily_brief": {
        "schema": DAILY_BRIEF_TOOL,
        "handler": get_daily_brief,
    },
}
