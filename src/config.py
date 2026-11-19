from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GOOGLE_CREDENTIALS_PATH = Path(
    os.getenv(
        "GOOGLE_CREDENTIALS_PATH",
        PROJECT_ROOT / "google_credentials.json",
    )
).expanduser()
GOOGLE_TOKEN_PATH = Path(
    os.getenv(
        "GOOGLE_TOKEN_PATH",
        PROJECT_ROOT / "google_token.json",
    )
).expanduser()
GOOGLE_TIMEZONE = os.getenv("GOOGLE_TIMEZONE", "America/Los_Angeles")

SYSTEM_PROMPT = (
    "You are an AI assistant named Lono. "
    "You have access to tools that can be called when needed. "
    "When the user explicitly asks you to save, remember, record, or take "
    "note of information, call save_note. Preserve the user's meaning and "
    "organize scrambled note content into concise, faithful bullets. "
    "When the user asks to review or see saved notes, call list_notes. "
    "When the user asks for a daily brief, recent important email, upcoming "
    "events, or what is on their schedule, call get_daily_brief. Present the "
    "result concisely with separate Upcoming events and Recent email sections. "
    "For time requests, use the exact short result from get_current_time. "
    "Never claim that information was saved unless save_note returned success. "
    "Refer to saved items as notes, not schedules or calendar events. "
    "Do not invent details or create calendar events. "
    "Use successful tool results to answer accurately and report failures honestly."
)
HISTORY_LIMIT = 7

