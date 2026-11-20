from datetime import datetime, timedelta, timezone
from email.utils import parseaddr
from zoneinfo import ZoneInfo

from .config import (
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_TIMEZONE,
    GOOGLE_TOKEN_PATH,
)


GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def _load_google_dependencies():
    try:
        from google.auth.exceptions import GoogleAuthError
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError as error:
        raise RuntimeError(
            "Google support is not installed. Install the project dependencies "
            "before using get_daily_brief."
        ) from error

    return GoogleAuthError, Request, Credentials, InstalledAppFlow, build, HttpError


def _load_credentials():
    _, Request, Credentials, InstalledAppFlow, _, _ = _load_google_dependencies()
    credentials = None

    if GOOGLE_TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(
            GOOGLE_TOKEN_PATH,
            GOOGLE_SCOPES,
        )

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        if not GOOGLE_CREDENTIALS_PATH.exists():
            raise RuntimeError(
                "Google OAuth is not configured. Download a desktop OAuth client "
                f"file to {GOOGLE_CREDENTIALS_PATH}."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            GOOGLE_CREDENTIALS_PATH,
            GOOGLE_SCOPES,
        )
        credentials = flow.run_local_server(
            port=0,
            open_browser=False,
            authorization_prompt_message=(
                "\nOpen this URL in a browser to authorize Lono:\n{url}\n"
            ),
            success_message=(
                "Lono authorization is complete. You may close this tab."
            ),
        )

    GOOGLE_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    GOOGLE_TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")
    GOOGLE_TOKEN_PATH.chmod(0o600)
    return credentials


def _build_service(api_name: str, version: str):
    GoogleAuthError, _, _, _, build, HttpError = _load_google_dependencies()

    try:
        return build(
            api_name,
            version,
            credentials=_load_credentials(),
            cache_discovery=False,
        )
    except (GoogleAuthError, HttpError, OSError) as error:
        raise RuntimeError(f"Google API setup failed: {error}") from error


def _message_headers(message: dict) -> dict[str, str]:
    headers = message.get("payload", {}).get("headers", [])
    return {
        header.get("name", "").lower(): header.get("value", "")
        for header in headers
    }


def get_recent_emails(hours: int = 24, limit: int = 10) -> list[dict]:
    service = _build_service("gmail", "v1")
    _, _, _, _, _, HttpError = _load_google_dependencies()
    days = max(1, (hours + 23) // 24)
    query = f"in:inbox newer_than:{days}d -in:spam -in:trash"

    try:
        response = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=limit,
        ).execute()

        emails = []
        for reference in response.get("messages", []):
            message = service.users().messages().get(
                userId="me",
                id=reference["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            ).execute()
            headers = _message_headers(message)
            sender_name, sender_email = parseaddr(headers.get("from", ""))
            internal_date = message.get("internalDate")
            received_at = None

            if internal_date:
                received_at = datetime.fromtimestamp(
                    int(internal_date) / 1000,
                    tz=timezone.utc,
                ).astimezone(ZoneInfo(GOOGLE_TIMEZONE)).isoformat()

            emails.append(
                {
                    "id": message.get("id"),
                    "from": sender_name or sender_email or headers.get("from", ""),
                    "from_email": sender_email or None,
                    "subject": headers.get("subject") or "(no subject)",
                    "received_at": received_at,
                    "unread": "UNREAD" in message.get("labelIds", []),
                    "snippet": message.get("snippet", ""),
                }
            )

        return emails
    except HttpError as error:
        raise RuntimeError(f"Gmail request failed: {error}") from error


def get_upcoming_events(hours: int = 48, limit: int = 20) -> list[dict]:
    service = _build_service("calendar", "v3")
    _, _, _, _, _, HttpError = _load_google_dependencies()
    now = datetime.now(timezone.utc)
    end = now + timedelta(hours=hours)

    try:
        response = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
            timeZone=GOOGLE_TIMEZONE,
        ).execute()

        return [
            {
                "id": event.get("id"),
                "title": event.get("summary") or "(untitled event)",
                "start": event.get("start", {}).get("dateTime")
                or event.get("start", {}).get("date"),
                "end": event.get("end", {}).get("dateTime")
                or event.get("end", {}).get("date"),
                "location": event.get("location"),
                "status": event.get("status"),
            }
            for event in response.get("items", [])
        ]
    except HttpError as error:
        raise RuntimeError(f"Calendar request failed: {error}") from error
