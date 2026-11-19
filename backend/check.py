from nba_api.stats.endpoints import leaguegamelog

df = leaguegamelog.LeagueGameLog(
    season="2026-27",
    player_or_team_abbreviation="P",
    season_type_all_star="Regular Season",
    timeout=60,
).get_data_frames()[0]

print("rows:", len(df))
print("unique players:", df["PLAYER_ID"].nunique())
print("unique games:", df["GAME_ID"].nunique())
print(df[["PLAYER_NAME", "GAME_DATE", "MATCHUP", "PTS"]].head())