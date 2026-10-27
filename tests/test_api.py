import io
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    return app.test_client()


def upload(client, content, name="data.csv"):
    return client.post(
        "/api/datasets",
        data={"file": (io.BytesIO(content.encode()), name)},
        content_type="multipart/form-data",
    )


CSV = "a,b\n1,x\n2,y\n3,z\n4,w\n"


def test_health(client):
    assert client.get("/api/health").json == {"status": "ok"}


def test_upload_and_fetch_report(client):
    resp = upload(client, CSV)
    assert resp.status_code == 201
    ds_id = resp.json["id"]
    report = client.get(f"/api/datasets/{ds_id}/report")
    assert report.status_code == 200
    assert report.json["report"]["rows"] == 4


def test_rejects_non_csv(client):
    assert upload(client, CSV, name="data.txt").status_code == 400


def test_rejects_missing_file(client):
    assert client.post("/api/datasets").status_code == 400


def test_rejects_empty_csv(client):
    assert upload(client, "").status_code == 400


def test_list_and_filter(client):
    upload(client, CSV)
    upload(client, "a,b\n1,x\n1,x\n,y\n")
    assert client.get("/api/datasets").json["total"] == 2
    assert client.get("/api/datasets?min_score=99").json["total"] == 1


def test_delete(client):
    ds_id = upload(client, CSV).json["id"]
    assert client.delete(f"/api/datasets/{ds_id}").status_code == 204
    assert client.get(f"/api/datasets/{ds_id}").status_code == 404
