from database import SessionLocal
from models import Game, PlayerGame

with SessionLocal() as s:
    have = {g for (g,) in s.query(Game.id)}
    for gid, in s.query(PlayerGame.game_id).distinct():
        if gid not in have:
            rows = s.query(PlayerGame).filter_by(game_id=gid).all()
            print("missing game id:", gid, "date:", rows[0].date, "player rows:", len(rows))