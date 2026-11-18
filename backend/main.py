from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import SessionLocal
from models import Game, Team

app = FastAPI(title = "NBA Stats")

def get_db():
    with SessionLocal() as session:
        yield session

@app.get("/standings")
def get_standings(conference: str | None = None, db: Session = Depends(get_db)):
    teams = {t.id: t for t in db.scalars(select(Team))}
    record = {tid: {"wins": 0, "losses": 0} for tid in teams}

    for g in db.scalars(select(Game)):
        home_won = g.home_score > g.away_score
        record[g.home_team_id]["wins" if home_won else "losses"] += 1
        record[g.away_team_id]["losses" if home_won else "wins"] += 1

        rows = []
    for tid, r in record.items():
        team = teams[tid]
        played = r["wins"] + r["losses"]
        rows.append({
            "team_id": tid,
            "team": team.name,
            "abbreviation": team.abbreviation,
            "conference": team.conference,
            **r,
            "win_pct": round(r["wins"] / played, 3) if played else 0.0,
        })

    if conference:
        rows = [r for r in rows if r["conference"].lower() == conference.lower()]
    return sorted(rows, key=lambda r: (-r["win_pct"], -r["wins"]))