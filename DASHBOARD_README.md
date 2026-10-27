# Data Quality Dashboard

This dashboard is added to the existing Flask application without changing the `/api` endpoints or database configuration.

## Run locally

From the inner `data-quality-api` project directory, activate your existing virtual environment and run:

```powershell
python run.py
```

Open http://127.0.0.1:5000/

## Files added/changed

- `app/__init__.py`: adds a `/` route while preserving existing config, database setup, blueprint registration, and error handlers.
- `app/templates/index.html`: dashboard markup.
- `app/static/css/style.css`: responsive styling.
- `app/static/js/dashboard.js`: connects to existing API endpoints.

CSV upload limit remains 5 MB, matching the backend.
