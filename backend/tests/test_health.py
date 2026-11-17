from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "env" in data
    assert "region" in data


def test_ec2_requires_auth():
    resp = client.get("/api/v1/ec2/instances")
    assert resp.status_code == 422  # missing X-API-Key header


def test_ec2_rejects_bad_key():
    resp = client.get("/api/v1/ec2/instances", headers={"X-API-Key": "wrong-key"})
    assert resp.status_code == 401
