import jwt


def test_login_ok(client):
    r = client.post("/token", data={"username": "aud", "password": "pwd-aud"})
    assert r.status_code == 200 and r.json()["token_type"] == "bearer"


def test_login_bad_password_same_message_as_unknown_user(client):
    a = client.post("/token", data={"username": "aud", "password": "nope"})
    b = client.post("/token", data={"username": "ghost", "password": "nope"})
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()


def test_no_token_401(client):
    r = client.post("/imports", files={"file": ("a.csv", b"x", "text/csv")})
    assert r.status_code == 401 and r.json()["error"] == "unauthorized"


def test_forged_token_401(client):
    fake = jwt.encode({"sub": "1", "role": "auditeur", "exp": 9999999999}, "wrong-secret", algorithm="HS256")
    r = client.post("/imports", headers={"Authorization": f"Bearer {fake}"},
                    files={"file": ("a.csv", b"x", "text/csv")})
    assert r.status_code == 401


def test_alg_none_rejected(client):
    fake = jwt.encode({"sub": "1", "exp": 9999999999}, None, algorithm="none")
    r = client.post("/imports", headers={"Authorization": f"Bearer {fake}"},
                    files={"file": ("a.csv", b"x", "text/csv")})
    assert r.status_code == 401


def test_responsable_cannot_import_403(client, resp):
    r = client.post("/imports", headers=resp, files={"file": ("a.csv", b"ref\n", "text/csv")})
    assert r.status_code == 403 and r.json()["error"] == "forbidden"
