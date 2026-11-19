from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import SessionLocal
from models import Game, Player, PlayerGame, Team

app = FastAPI(title = "NBA Stats")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
)

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

@app.get("/teams/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    games = db.scalars(
        select(Game)
        .where((Game.home_team_id == team_id) | (Game.away_team_id == team_id))
        .order_by(Game.date.desc())
    ).all()

    results = []
    for g in games:
        is_home = g.home_team_id == team_id
        score = g.home_score if is_home else g.away_score
        allowed = g.away_score if is_home else g.home_score
        results.append({
            "home": is_home,
            "won": score > allowed,
            "scored": score,
            "allowed": allowed,
        })

    def split(rs):
        wins = sum(r["won"] for r in rs)
        return {"wins": wins, "losses": len(rs) - wins}

    n = len(results)
    return {
        "team": team.name,
        "last 5": ["W" if r["won"] else "L" for r in results[:5]],
        "home": split([r for r in results if r["home"]]),
        "away": split([r for r in results if not r["home"]]),
        "avg scored": round(sum(r["scored"] for r in results) / n, 1) if n else 0.0,
        "avg allowed": round(sum(r["allowed"] for r in results) / n, 1) if n else 0.0,
    }

@app.get("/players")
def search_players(q: str, db: Session = Depends(get_db)):
    players = db.scalars(select(Player).where(Player.name.ilike(f"%{q}%")).limit(20))
    return [{"id": p.id, "name": p.name} for p in players]

@app.get("/players/{player_id}")
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    games = db.scalars(
        select(PlayerGame)
        .where(PlayerGame.player_id == player_id)
        .order_by(PlayerGame.date.desc())
    ).all()

    n = len(games)

    def pct(made, att):
        att = sum(getattr(g, att) for g in games)
        return round(sum(getattr(g, made) for g in games) / att, 3) if att else 0.0
    
    return {
        "name": player.name,
        "games_played": n,
        "averages": {
            "pts": avg("pts"),
            "reb": avg("reb"),
            "ast": avg("ast"),
            "minutes": avg("minutes"),
        },
        "shooting": {
            "fg_pct": pct("fgm", "fga"),
            "fg3_pct": pct("fg3m", "fg3a"),
            "ft_pct": pct("ftm", "fta"),
        },
        "last_10": [
            {"date": g.date, "pts": g.pts, "reb": g.reb, "ast": g.ast, "minutes": g.minutes}
            for g in games[:10]
        ],
    }
        