import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["JWT_SECRET"] = "test-secret-" + "x" * 40

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine, init_db
from app.main import app
from app.models import User
from app.security import hash_password


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    init_db()
    with SessionLocal() as db:
        db.add_all([User(username="aud", password_hash=hash_password("pwd-aud"), role="auditeur"),
                    User(username="resp", password_hash=hash_password("pwd-resp"), role="responsable")])
        db.commit()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def token(client, user, pwd):
    r = client.post("/token", data={"username": user, "password": pwd})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def aud(client):
    return token(client, "aud", "pwd-aud")


@pytest.fixture
def resp(client):
    return token(client, "resp", "pwd-resp")
