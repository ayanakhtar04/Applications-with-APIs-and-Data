# Simple Flask URL Shortener (Starter)

This is a minimal starting point for a URL shortener using Flask.

## Features Implemented
- Home route `/` returning a placeholder "Hello, world!" (will later host a form)
- POST `/shorten` to create a short code for a provided long URL
  - Accepts JSON `{ "url": "https://example.com" }` or form field `url`
  - Returns JSON with `code`, `short_url`, and `long_url`
- GET `/<code>` to redirect to the stored long URL
- In-memory dictionary `url_store` for mappings (non-persistent)
- Base62 short code generation using an incremental counter (thread-safe)

## Quick Start

Install dependencies and run the app:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then test:

```bash
curl -X POST http://127.0.0.1:5000/shorten -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'
```

Navigate to the returned `short_url` to verify the redirect.

## Next Steps
- Replace home route with an HTML form template
- Add validation and normalization of URLs
- Add persistence (e.g., SQLite) instead of in-memory dict
- Implement custom alias support
- Add rate limiting / analytics
