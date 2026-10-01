import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db
from app.models import User
from app.security import hash_password

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(engine)
    db = TestSessionLocal()
    db.add(User(username="auditeur", password_hash=hash_password("test1234"), role="auditeur"))
    db.add(User(username="responsable", password_hash=hash_password("test5678"), role="responsable"))
    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def token_auditeur(client):
    r = client.post("/token", data={"username": "auditeur", "password": "test1234"})
    return r.json()["access_token"]


@pytest.fixture()
def token_responsable(client):
    r = client.post("/token", data={"username": "responsable", "password": "test5678"})
    return r.json()["access_token"]