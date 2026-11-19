from nba_api.stats.endpoints import leaguegamefinder

from database import SessionLocal
from models import Game, PlayerGame

with SessionLocal() as s:
    have = {g for (g,) in s.query(Game.id)}
    missing = {int(g) for (g,) in s.query(PlayerGame.game_id).distinct() if g not in have}

df = leaguegamefinder.LeagueGameFinder(
    season_nullable="2026-27",
    league_id_nullable="00",
    season_type_nullable="Regular Season",
    timeout=60,
).get_data_frames()[0]

df["gid"] = df["GAME_ID"].astype(int)
print("missing ids:", missing)
print(df[df["gid"].isin(missing)][["GAME_ID", "TEAM_ABBREVIATION", "MATCHUP", "PTS", "WL"]])