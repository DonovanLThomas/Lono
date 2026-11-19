import sqlite3
from pathlib import Path
from datetime import datetime, timezone


DB_PATH = Path(__file__).resolve().parent.parent / "lono.db"

def initialize_database() -> None:
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                raw_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS note_items (
                id INTEGER PRIMARY KEY,
                note_id INTEGER NOT NULL,
                position INTEGER NOT NULL CHECK (position >= 0),
                body TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
                UNIQUE (note_id, position)
            )
            """
        )
        connection.commit()

        
    finally:
        connection.close()

    
def insert_task(title: str) -> int:
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )
        connection.commit()
        task_id = cursor.lastrowid

        if task_id is None:
            raise RuntimeError("SQLite did not return a task ID")
        
        return task_id
    finally:
        connection.close()

def _validate_note_input(raw_text, bullets):
    if isinstance(raw_text, str) == False:
        raise ValueError("Raw note must be a string")
    
    clean_raw_text = raw_text.strip()

    if clean_raw_text == "":
        raise ValueError("Raw note cannot be empty")

    if not isinstance(bullets, list):
        raise ValueError("Bullets must be a list")

    if len(bullets) == 0:
        raise ValueError("A note must contain at least one bullet")

    clean_bullets = []

    for bullet in bullets:
        if not isinstance(bullet, str):
            raise ValueError("Each bullet point must be string")

        cleaned_bullet = bullet.strip()

        if cleaned_bullet == "":
            raise ValueError("Bullet cannot be empty")

        clean_bullets.append(cleaned_bullet)
    
    return (clean_raw_text, clean_bullets)

def insert_note(raw_text: str, bullets: list[str]) -> int:

    clean_raw_text, clean_bullets = _validate_note_input(
        raw_text,
        bullets,
    )

    created_at = datetime.now(timezone.utc).isoformat()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute(
            """
            INSERT INTO notes (raw_text, created_at)
            VALUES (?, ?)
            """,
            (clean_raw_text, created_at),
        )

        note_id = cursor.lastrowid

        if note_id is None:
            raise RuntimeError("SQLite did not return a note ID")

        for position, body in enumerate(clean_bullets):
            connection.execute(
                """
                INSERT INTO note_items (note_id, position, body)
                VALUES (?, ?, ?)
                """,
                (note_id, position, body),
            )

        connection.commit()
        return note_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_note(note_id: int) -> dict | None:
    connection = sqlite3.connect(DB_PATH)

    try:
        note_row = connection.execute(
            """
            SELECT id, raw_text, created_at
            FROM notes
            WHERE id = ?
            """,
            (note_id,),
        ).fetchone()

        if note_row is None:
            return None

        item_rows = connection.execute(
            """
            SELECT body
            FROM note_items
            WHERE note_id = ?
            ORDER BY position
            """,
            (note_id,),
        ).fetchall()

        bullets = []

        for item_row in item_rows:
            bullets.append(item_row[0])

        return {
            "id": note_row[0],
            "raw_text": note_row[1],
            "created_at": note_row[2],
            "bullets": bullets,
        }

    finally:
        connection.close()

def list_notes() -> list[dict]:
    connection = sqlite3.connect(DB_PATH)

    try:
        note_rows = connection.execute(
            """
            SELECT id, raw_text, created_at
            FROM notes
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

        item_rows = connection.execute(
            """
            SELECT note_id, body
            FROM note_items
            ORDER BY note_id, position
            """
        ).fetchall()

        bullets_by_note = {}

        for note_id, body in item_rows:
            if note_id not in bullets_by_note:
                bullets_by_note[note_id] = []

            bullets_by_note[note_id].append(body)

        notes = []

        for note_id, raw_text, created_at in note_rows:
            notes.append(
                {
                    "id": note_id,
                    "raw_text": raw_text,
                    "created_at": created_at,
                    "bullets": bullets_by_note.get(note_id, []),
                }
            )

        return notes

    finally:
        connection.close()
