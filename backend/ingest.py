import time
from datetime import date, timedelta

from nba_api.stats.endpoints import leaguegamefinder,leaguegamelog
from nba_api.stats.static import teams as static_teams

from database import Base, SessionLocal, engine
from models import Game, Player, PlayerGame, Team

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
        if " @ " in row.MATCHUP:
            home_abbr = row.MATCHUP.split(" @ ")[1]
        else:
            home_abbr = row.MATCHUP.split(" vs. ")[0]

        g = games.setdefault(row.GAME_ID, {"date": row.GAME_DATE})
        if row.TEAM_ABBREVIATION == home_abbr:
            g["home_team_id"], g["home_score"] = int(row.TEAM_ID), int(row.PTS)
        else:
            g["away_team_id"], g["away_score"] = int(row.TEAM_ID), int(row.PTS)

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

def ingest_players(session, season="2026-27", start=date(2026, 10, 1)):
    day = start
    today = date.today()
    while day <= today:
        end = min(day + timedelta(days=6), today)
        df = leaguegamelog.LeagueGameLog(
            season=season,
            player_or_team_abbreviation="P",
            season_type_all_star="Regular Season",
            timeout=60,
        ).get_data_frames()[0].fillna(0)

        for row in df.itertuples():
            session.merge(Player(
                id=int(row.PLAYER_ID),
                name=row.PLAYER_NAME,
                team_id=int(row.TEAM_ID),
            ))
            session.merge(PlayerGame(
                player_id=int(row.PLAYER_ID),
                game_id=int(row.GAME_ID),
                date=row.GAME_DATE,
                minutes=float(row.MIN),
                pts=int(row.PTS),
                reb=int(row.REB),
                ast=int(row.AST),
                fgm=int(row.FGM),
                fga=int(row.FGA),
                fg3m=int(row.FG3M),
                fg3a=int(row.FG3A),
                ftm=int(row.FTM),
                fta=int(row.FTA),
            ))
        session.commit()
        day = end + timedelta(days=1)
        time.sleep(1)  # avoid rate limiting

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        ingest_teams(session)
        ingest_games(session, season="2026-27")
        ingest_players(session, season="2026-27")
        print("teams:", session.query(Team).count())
        print("games:", session.query(Game).count())
        print("players:", session.query(Player).count())
        print("player games:", session.query(PlayerGame).count())