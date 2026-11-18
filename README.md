# NBA Stats

A REST API and dashboard for NBA standings and team stats, built with FastAPI, SQLAlchemy and React.

## Features
- Idempotent ingestion of teams and games from NBA.com (via `nba_api`) into SQLite
- `GET /standings` with an optional `?conference=East|West` filter
- `GET /teams/{id}` with last-5 form, home/away splits and scoring averages
- Pytest suite and GitHub Actions CI

## Setup
```bash
git clone https://github.com/jordanch3/nba-stats.git
cd nba-stats/backend
python -m venv .venv
source .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python ingest.py
uvicorn main:app --reload
```
API docs at http://127.0.0.1:8000/docs

## Design decisions
- Data is stored locally instead of calling the API per request, to avoid rate limits and slow responses.
- Ingestion upserts by the API's own IDs, so re-running it never creates duplicates.
- Standings are derived from stored games rather than stored as separate columns, so they can't drift out of sync.

## Roadmap
- React frontend
- Player stats and trend charts
