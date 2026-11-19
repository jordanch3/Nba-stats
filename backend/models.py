from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    abbreviation: Mapped[str]
    conference: Mapped[str]


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str]
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    home_score: Mapped[int]
    away_score: Mapped[int]

class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))

class PlayerGame(Base):
    __tablename__ = "player_games"

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), primary_key=True)
    date: Mapped[str]
    minutes: Mapped[int]
    pts: Mapped[int]
    reb: Mapped[int]
    ast: Mapped[int]
    fgm: Mapped[int]
    fga: Mapped[int]
    fg3m: Mapped[int]
    fg3a: Mapped[int]
    ftm: Mapped[int]
    fta: Mapped[int]