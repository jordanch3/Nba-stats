from sqlalchemy import func

from database import SessionLocal
from models import Game, Team, PlayerGame

with SessionLocal() as session:
    print("teams:", session.query(Team).count())
    print("games:", session.query(Game).count())
    print("games with player rows:", session.query(func.count(func.distinct(PlayerGame.game_id))).scalar())
    print("date range:", session.query(func.min(PlayerGame.date), func.max(PlayerGame.date)).one())