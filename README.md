# Data Quality Analyzer API

A REST API built with **Python, Flask, SQLAlchemy and Pandas** that lets you upload a CSV file and instantly get a data quality report: missing values, duplicate rows, outliers, and an overall 0-100 quality score. Reports are stored in a SQL database so datasets can be listed, filtered, and reviewed later.

## Features
- Upload CSV files and run automatic data validation
- Checks for missing values, duplicate rows, and numeric outliers (1.5 x IQR rule)
- Weighted quality score: completeness (50%), uniqueness (30%), validity (20%)
- Per-column profiling: data type, missing %, unique count, min / max / mean
- RESTful endpoints with pagination, score filtering, and JSON error responses
- Input validation: file type, empty files, malformed CSV, 5 MB upload limit
- SQLite by default; PostgreSQL via the `DATABASE_URL` environment variable
- Automated tests with Pytest (11 tests covering the API and quality logic)

## Tech Stack
Python, Flask, Flask-SQLAlchemy, Pandas, SQLite / PostgreSQL, Pytest, Git

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                    # runs at http://127.0.0.1:5000
```

Use PostgreSQL instead of SQLite:
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/dq
```

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/datasets` | Upload a CSV (form field `file`) and analyze it |
| GET | `/api/datasets` | List datasets (`page`, `per_page`, `min_score`) |
| GET | `/api/datasets/<id>` | Dataset summary |
| GET | `/api/datasets/<id>/report` | Full quality report |
| DELETE | `/api/datasets/<id>` | Delete a dataset |

## Example
```bash
curl -F "file=@sample_data/sample.csv" http://127.0.0.1:5000/api/datasets
```
Response:
```json
{"id": 1, "filename": "sample.csv", "rows": 10, "columns": 5, "quality_score": 93.62, "uploaded_at": "..."}
```
`GET /api/datasets/1/report` returns, among other fields:
```json
{
  "missing_cells": 2,
  "duplicate_rows": 1,
  "outlier_values": 2,
  "scores": {"completeness": 96.0, "uniqueness": 90.0, "validity": 93.1, "overall": 93.62},
  "issues": ["Column 'age' has 1 outlier(s)", "Column 'salary' has 1 outlier(s)", "1 duplicate row(s) found"]
}
```

## Run Tests
```bash
pytest -v
```

## Project Structure
```
app/
  __init__.py   # application factory, config, error handlers
  models.py     # SQLAlchemy Dataset model
  quality.py    # pandas data quality checks and scoring
  routes.py     # REST API endpoints
tests/          # pytest tests for API and quality logic
sample_data/    # example CSV
run.py
```

## Future Improvements
Authentication, Docker support, a Power BI or web dashboard on top of the stored reports, and scheduled re-checks.
