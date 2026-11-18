import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app, get_db
from models import Team, Game

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine)

def override_get_db():
    with TestingSession() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def seed():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSession() as s:
        s.add_all([
            Team(id=1, name="Team A", abbreviation="A", conference="East"),
            Team(id=2, name="Team B", abbreviation="B", conference="West"),
            Game(id=1, date="2026-11-01", home_team_id=1, away_team_id=2, home_score=100, away_score=90),
            Game(id=2, date="2026-11-02", home_team_id=2, away_team_id=1, home_score=95, away_score=105),
            Game(id=3, date="2026-11-03", home_team_id=1, away_team_id=2, home_score=90, away_score=100),
        ])
        s.commit()

def test_standings_records_and_order():
    rows = client.get("/standings").json()
    assert [r["team"] for r in rows] == ["Team A", "Team B"]
    assert (rows[0]["wins"], rows[0]["losses"], rows[0]["win_pct"]) == (2, 1, 0.667)

def test_standings_filter_by_conference():
    rows = client.get("/standings?conference=East").json()
    assert [r["team"] for r in rows] == ["Team A"]

def test_team_page_stats():
    data = client.get("/teams/1").json()
    assert data["last 5"] == ["L", "W", "W"]
    assert data["home"] == {"wins" : 1, "losses" : 1}
    assert data["away"] == {"wins" : 1, "losses" : 0}
    assert data["avg scored"] == 98.3
    assert data["avg allowed"] == 95.0

def test_unknown_team_returns_404():
    assert client.get("/teams/999").status_code == 404


