# Bedtime Questions Hub

A multi-family, self-service platform for sending personalized bedtime confidence-building questions to children via email. Parents sign up on a landing page, and each night receives a new AI-generated question at their chosen time in their local timezone.

## Features

- **Personalized per-child emails** — each child's name appears in the subject line and greeting
- **Shared daily question** — one AI-generated question for all subscribers, rotated through 12 confidence-building themes
- **Self-service signup** — parents collect their own email, child's name, preferred send time, and timezone via a landing page
- **Multi-timezone support** — each family gets their email at their chosen local time (±8 minute tolerance)
- **Smart send logic** — emails only send once per child per local calendar day, no duplicates on retries or delayed runs
- **Free to run** — uses GitHub Actions cron (15-min intervals across a 9-hour UTC band) and Google Sheets as the subscriber database

## Architecture

```
bedtime-questions-hub/
├── main.py                    # Orchestrator: load subscribers, find who's due, generate question, send, persist
├── config.py                  # Environment configuration
├── question_generator.py      # Anthropic API call (Haiku model)
├── email_template.py          # Pink/white responsive HTML email template
├── themes.py                  # 12-theme rotation logic
├── theme_emojis.py            # Theme -> emoji mapping
├── history.py                 # Shared question history I/O (JSON)
├── subscribers.py             # Gspread-backed subscriber management
├── lib/gmail_notifier.py      # SMTP Gmail sender (vendored, unmodified)
├── apps_script/Code.gs        # Google Apps Script backend for signup form
├── docs/                      # Static landing page (hosted via GitHub Pages)
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .github/workflows/
│   ├── ci.yml                 # Python tests + linting
│   └── send_questions.yml     # Cron job to send emails
└── tests/                     # Pytest suite
```

## Setup & Deployment

### 1. Prerequisites

- A GitHub account with the `hcunited10` organization (or personal account)
- A Google Cloud project with Sheets API enabled and a service account
- An Anthropic API key
- A Gmail account with an app password

### 2. Create the GitHub repository

```bash
gh repo create hcunited10/bedtime-questions-hub --public --source=. --remote=origin --push
```

(Must be `--public` so GitHub Pages can serve the landing page.)

### 3. Create the Google Sheet

1. Create a new Google Sheet
2. Name the first tab `Subscribers`
3. Add this header row (exactly, in row 1):
   ```
   timestamp | parent_email | child_name | desired_time | timezone | active | last_sent_date
   ```
4. Note the Sheet ID (from the URL: `docs.google.com/spreadsheets/d/{SHEET_ID}/...`)

### 4. Create a Google Cloud service account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Google Sheets API
4. Create a service account, generate a JSON key
5. Share the Subscribers Sheet with the service account's client email (Editor access)

### 5. Deploy Google Apps Script backend

1. Open the Subscribers Sheet
2. Extensions → Apps Script
3. Paste the contents of `apps_script/Code.gs`
4. Deploy → New deployment → Web app → Execute as "Me" → Access "Anyone"
5. Copy the Web App URL and save it

### 6. Set up GitHub secrets

```bash
gh secret set ANTHROPIC_API_KEY --repo hcunited10/bedtime-questions-hub
gh secret set GMAIL_SENDER --repo hcunited10/bedtime-questions-hub
gh secret set GMAIL_APP_PASSWORD --repo hcunited10/bedtime-questions-hub
gh secret set GOOGLE_SERVICE_ACCOUNT_JSON --repo hcunited10/bedtime-questions-hub
gh secret set GOOGLE_SHEET_ID --repo hcunited10/bedtime-questions-hub
```

(The service-account JSON should be passed as a single-line string, e.g. `'{"type":"service_account",...}'`.)

### 7. Enable GitHub Pages

```bash
gh api repos/hcunited10/bedtime-questions-hub/pages -X POST -f 'source[branch]=main' -f 'source[path]=/docs'
```

### 8. Update the signup page

Edit `docs/app.js` and replace `REPLACE_ME` with the Google Apps Script Web App URL from step 5:

```javascript
const APPS_SCRIPT_URL = 'https://script.google.com/macros/d/.../usercontent';
```

Push this change to `main`.

### 9. Test

Visit `https://hcunited10.github.io/bedtime-questions-hub/` (or your Pages URL) and submit a test signup.

Manually trigger the workflow to test sending:

```bash
gh workflow run send_questions.yml --repo hcunited10/bedtime-questions-hub
```

Watch it:

```bash
gh run watch --repo hcunited10/bedtime-questions-hub
```

## Development

### Local testing

```bash
# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Lint
ruff check .

# Test locally with a test subscriber in the Sheet
cp .env.example .env
# Fill in .env with your test credentials
python main.py
```

### Testing the signup form

Locally, you'll need to:
1. Update `docs/app.js` with the real Apps Script Web App URL
2. Open `docs/index.html` in a browser (or use a local HTTP server)
3. Submit a test signup and verify it appears in the Sheet

## Customization

### Change the cron cadence

Edit `.github/workflows/send_questions.yml`:

```yaml
cron: "*/15 21-23,0-5 * * *"  # Every 15 min, UTC 21:00-05:59
```

This band covers ~5-9pm across continental US timezones. Expand or narrow as needed based on your subscriber base.

### Adjust the tolerance window

In `config.py`:

```python
SEND_TOLERANCE_MINUTES = 8  # Allow ±8 minutes around desired_time
```

### Change the theme list

Edit `themes.py` and `theme_emojis.py` to customize the 12 themes.

### Update the timezone list

Edit both:
- `docs/index.html` → the `<select>` element
- `apps_script/Code.gs` → the `VALID_TIMEZONES` array

## Cost

- **GitHub Actions**: Free for public repos (unlimited minutes)
- **Google Sheets & Apps Script**: Free (no cost for this volume)
- **Anthropic API**: ~$0.01/day for Haiku model (1 question/day)
- **Gmail**: Free

**Total estimated cost: ~$0.30/month + any existing Gmail/GCP spending**

## Known Limitations

- The timezone list is manually synchronized between `docs/index.html`, `apps_script/Code.gs`, and the Python code. A mismatch will cause client-side validation to fail at the backend.
- No unsubscribe UI in the app — users must reply to an email or contact directly. (Recommend adding an unsubscribe link in a future iteration.)
- The shared question is always generated once per day max, but sending is per-subscriber based on their local time. If a question fails to generate, no one gets an email that day.

## Testing

Run the full pytest suite:

```bash
pytest tests/ -v --tb=short
```

All tests use mocks and fixtures; no real API/Sheet calls are made during testing.

## License

Private repo for family use.
