# Google read-only setup

Lono's `get_daily_brief` tool reads recent Gmail inbox metadata and upcoming
events from the primary Google Calendar. It uses only these OAuth scopes:

- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/calendar.readonly`

It cannot send email or modify calendar events.

## Configure Google Cloud

1. Create or select a Google Cloud project.
2. Enable the Gmail API and Google Calendar API.
3. Configure the Google Auth consent screen.
4. Create an OAuth client with application type **Desktop app**.
5. Download the client JSON to the repository root as
   `google_credentials.json`.

The first `get_daily_brief` call prints a Google consent URL in the terminal.
Open that URL in a browser, choose the account, and approve read-only access.
The browser may then report that `localhost` refused to connect. This is
expected when the browser and Lono run in different environments. Copy the
complete `localhost` URL from the browser address bar and paste it at Lono's
terminal prompt. Lono exchanges the authorization code and stores the result as
`google_token.json`. Both files are ignored by Git. The token file is written
with owner-only permissions.

The paths can be overridden in `.env`:

```text
GOOGLE_CREDENTIALS_PATH=/absolute/path/to/google_credentials.json
GOOGLE_TOKEN_PATH=/absolute/path/to/google_token.json
GOOGLE_TIMEZONE=America/Los_Angeles
```

If OAuth scopes change, delete `google_token.json` and authorize again.
