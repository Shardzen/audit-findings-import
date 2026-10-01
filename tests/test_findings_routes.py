def test_get_findings_sans_token(client):
    r = client.get("/findings")
    assert r.status_code == 401


def test_get_findings_avec_token(client, token_auditeur):
    r = client.get("/findings", headers={"Authorization": f"Bearer {token_auditeur}"})
    assert r.status_code == 200
    body = r.json()
    assert "items" in body and "page" in body and "total" in body


def test_get_findings_per_page_trop_grand(client, token_auditeur):
    r = client.get(
        "/findings?per_page=1000",
        headers={"Authorization": f"Bearer {token_auditeur}"},
    )
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        assert r.json()["per_page"] <= 100


def test_get_findings_severity_invalide(client, token_auditeur):
    r = client.get(
        "/findings?severity=critique",
        headers={"Authorization": f"Bearer {token_auditeur}"},
    )
    assert r.status_code == 422


def test_get_finding_inexistant(client, token_auditeur):
    r = client.get("/findings/999999", headers={"Authorization": f"Bearer {token_auditeur}"})
    assert r.status_code == 404


def test_resolve_par_auditeur_refuse(client, token_auditeur):
    r = client.patch(
        "/findings/1/resolve",
        headers={"Authorization": f"Bearer {token_auditeur}"},
    )
    assert r.status_code in (403, 404)


def test_resolve_id_inexistant(client, token_responsable):
    r = client.patch(
        "/findings/999999/resolve",
        headers={"Authorization": f"Bearer {token_responsable}"},
    )
    assert r.status_code == 404