"""认证与公众号导入的 API 冒烟测试。"""
from app.core.config import settings


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_login_and_me(client, auth_headers):
    me = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["username"] == settings.default_admin_username
    assert me.json()["role"] == "admin"


def test_login_wrong_password(client):
    resp = client.post("/api/v1/auth/login", json={"username": "Admin", "password": "wrong"})
    assert resp.status_code == 401


def test_import_accounts_mock(client, auth_headers):
    resp = client.post("/api/v1/accounts/import", headers=auth_headers, json={
        "lines": ["华为数字能源", "华为智能光伏"],
        "tags": "自有账号",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] == 2
    assert all(i["ok"] for i in data["items"])

    lst = client.get("/api/v1/accounts", headers=auth_headers)
    assert lst.status_code == 200
    assert len(lst.json()) >= 2


def test_import_dedup(client, auth_headers):
    # 重复导入同名公众号 → 标记"已存在"
    resp = client.post("/api/v1/accounts/import", headers=auth_headers,
                       json={"lines": ["华为数字能源"]})
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["ok"] and "已存在" in (item["message"] or "")


def test_unauthorized(client):
    resp = client.get("/api/v1/accounts")
    assert resp.status_code == 401
