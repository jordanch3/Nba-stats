from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams as static_teams

from database import Base, SessionLocal, engine
from models import Game, Team

EAST = {"ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DET", "IND", "MIA", "MIL", "NYK", "ORL", "PHI", "TOR", "WAS"}

def ingest_teams(session):
    for t in static_teams.get_teams():
        session.merge(Team(
            id=t["id"],
            name=t["full_name"],
            abbreviation=t["abbreviation"],
            conference="East" if t["abbreviation"] in EAST else "West",
        ))
    session.commit()

def ingest_games(session, season = "2026-27"):
    df = leaguegamefinder.LeagueGameFinder(
        season_nullable=season,
        league_id_nullable="00",
        season_type_nullable="Regular Season",
        timeout=60,
    ).get_data_frames()[0].dropna(subset=["PTS"])

    games = {}
    for row in df.itertuples():
        g = games.setdefault(row.GAME_ID, {"date": row.GAME_DATE})
        if "vs. " in row.MATCHUP:
            g["home_team_id"] = row.TEAM_ID
            g["home_score"] = row.PTS
        else:
            g["away_team_id"] = row.TEAM_ID
            g["away_score"] = row.PTS

    for game_id, g in games.items():
        if len(g) < 5:
            continue
        session.merge(Game(
            id=game_id,
            date=g["date"],
            home_team_id=g["home_team_id"],
            away_team_id=g["away_team_id"],
            home_score=g["home_score"],
            away_score=g["away_score"],
        ))
    session.commit()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    ingest_teams(session)
    ingest_games(session, season="2026-27")