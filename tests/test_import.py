from sqlalchemy import select

from app.db import SessionLocal
from app.models import Finding

H = "ref,asset,title,severity,detected_on\n"


def up(client, headers, content: str | bytes, name="f.csv"):
    data = content.encode("utf-8") if isinstance(content, str) else content
    return client.post("/imports", headers=headers, files={"file": (name, data, "text/csv")})


def refs():
    with SessionLocal() as db:
        return sorted(db.scalars(select(Finding.ref)))


def test_valid_file(client, aud):
    r = up(client, aud, H + "A1,srv,t1,forte,2026-09-01\nA2,srv,t2,faible,2026-09-02\n")
    assert r.status_code == 200
    assert r.json()["inserted"] == 2 and r.json()["rejected_count"] == 0
    assert refs() == ["A1", "A2"]


def test_missing_column_rejects_whole_file_no_write(client, aud):
    r = up(client, aud, "ref,asset,title,detected_on\nA1,srv,t,2026-09-01\n")
    assert r.status_code == 422
    assert r.json()["error"] == "missing_columns" and r.json()["missing_columns"] == ["severity"]
    assert refs() == []


def test_extra_columns_and_order_ignored(client, aud):
    r = up(client, aud, "comment,detected_on,severity,title,asset,ref\nx,2026-09-01,moyenne,t,srv,A1\n")
    assert r.json()["inserted"] == 1


def test_mixed_lines_example_from_spec(client, aud):
    up(client, aud, H + "AUD-001,srv-web-01,Port SSH,forte,2026-09-01\n")
    csv = (H.strip() + ",comment\n"
           "AUD-001,srv-web-01,Port SSH exposé,forte,2026-09-01,x\n"
           "AUD-010,srv-app-03,XSS réfléchi,forte,2026-09-03,y\n"
           "AUD-011,,Header manquant,faible,2026-09-03,z\n"
           "AUD-012,srv-app-03,CSRF,critique,2026-09-04,\n"
           "AUD-013,srv-mail,SPF absent,moyenne,2026-13-01,\n"
           "AUD-010,srv-app-03,XSS doublon,faible,2026-09-05,\n")
    j = up(client, aud, csv).json()
    assert j["total_lines"] == 6
    assert j["inserted"] == 1
    assert j["duplicates_existing"] == 1
    assert j["duplicates_in_file"] == 1
    assert [x["line"] for x in j["rejected"]] == [4, 5, 6]


def test_first_valid_wins(client, aud):
    j = up(client, aud, H + "X,srv,t,critique,2026-09-01\nX,srv,bon,forte,2026-09-01\n").json()
    assert j["inserted"] == 1 and j["rejected_count"] == 1 and j["duplicates_in_file"] == 0
    with SessionLocal() as db:
        assert db.scalar(select(Finding.title).where(Finding.ref == "X")) == "bon"


def test_reimport_does_not_modify_existing(client, aud):
    up(client, aud, H + "A1,srv,original,forte,2026-09-01\n")
    with SessionLocal() as db:
        f = db.scalar(select(Finding).where(Finding.ref == "A1"))
        f.status = "corrige"
        db.commit()
    j = up(client, aud, H + "A1,autre,modifié,faible,2026-01-01\n").json()
    assert j["inserted"] == 0 and j["duplicates_existing"] == 1
    with SessionLocal() as db:
        f = db.scalar(select(Finding).where(Finding.ref == "A1"))
        assert (f.title, f.status, f.severity) == ("original", "corrige", "forte")


def test_invalid_dates(client, aud):
    bad = ["2026-02-30", "2026-9-1", "01/09/2026", "demain", ""]
    body = H + "".join(f"D{i},srv,t,forte,{d}\n" for i, d in enumerate(bad))
    j = up(client, aud, body).json()
    assert j["rejected_count"] == len(bad) and j["inserted"] == 0


def test_multiple_errors_on_one_line(client, aud):
    j = up(client, aud, H + ",,,x,nope\n").json()
    assert len(j["rejected"][0]["errors"]) == 5


def test_wrong_column_count(client, aud):
    j = up(client, aud, H + "A1,srv,t,forte\nA2,srv,t,forte,2026-09-01,extra\n").json()
    assert j["rejected_count"] == 2


def test_bom(client, aud):
    r = up(client, aud, b"\xef\xbb\xbf" + (H + "A1,srv,t,forte,2026-09-01\n").encode())
    assert r.json()["inserted"] == 1


def test_header_only(client, aud):
    j = up(client, aud, H).json()
    assert j["inserted"] == 0 and j["total_lines"] == 0


def test_not_utf8(client, aud):
    r = up(client, aud, (H + "A1,srv,très,forte,2026-09-01\n").encode("latin-1"))
    assert r.status_code == 422 and r.json()["error"] == "invalid_encoding"


def test_wrong_extension(client, aud):
    assert up(client, aud, H, name="f.txt").status_code == 415


def test_too_large(client, aud, monkeypatch):
    import app.routers.imports as m
    monkeypatch.setattr(m, "MAX_UPLOAD_BYTES", 100)
    assert up(client, aud, H + "A1,srv,t,forte,2026-09-01\n" * 10).status_code == 413


def test_csv_formula_stored_as_text(client, aud):
    up(client, aud, H + 'A1,srv,"=HYPERLINK(""http://x"")",forte,2026-09-01\n')
    with SessionLocal() as db:
        assert db.scalar(select(Finding.title)).startswith("=HYPERLINK")


def test_cli_same_report_as_api(client, aud, tmp_path, capsys):
    import json
    from app.cli import main
    p = tmp_path / "f.csv"
    p.write_text(H + "C1,srv,t,forte,2026-09-01\nC2,,t,forte,2026-09-01\n", encoding="utf-8")
    assert main([str(p)]) == 0
    cli = json.loads(capsys.readouterr().out)
    api = up(client, aud, p.read_text(encoding="utf-8")).json()   # 2e passage : doublon
    assert cli["inserted"] == 1 and cli["rejected_count"] == 1
    assert api["duplicates_existing"] == 1 and api["rejected"] == cli["rejected"]


def test_cli_rejected_exit_code(tmp_path, capsys):
    from app.cli import main
    p = tmp_path / "f.csv"
    p.write_text("ref,asset\n", encoding="utf-8")
    assert main([str(p)]) == 1
