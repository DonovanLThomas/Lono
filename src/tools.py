from datetime import datetime
from zoneinfo import ZoneInfo
import json

from .storage import insert_note, list_notes


def get_current_time() -> str:
    """Return the current date and time in America/Los_Angeles as an ISO timestamp with a UTC offset. Takes no arguments."""
    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    return now.isoformat()


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
    },
    "save_note": {
        "schema": SAVE_NOTE_TOOL,
        "handler": save_note,
    },
    "list_notes": {
        "schema": LIST_NOTES_TOOL,
        "handler": get_saved_notes,
    },
}
