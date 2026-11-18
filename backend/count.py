from database import SessionLocal
from models import Game, Team

with SessionLocal() as session:
    print("teams:", session.query(Team).count())
    print("games:", session.query(Game).count())