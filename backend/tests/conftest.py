"""pytest 夹具：独立测试库 + mock 数据源 + 已认证客户端。"""
import os
import tempfile

# 必须在导入 app 之前设置环境变量
_tmp_db = tempfile.mktemp(suffix=".db", prefix="monitor_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db}"
os.environ["PROVIDER_MOCK"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-0123456789abcdef"
os.environ["FORCE_CHANGE_DEFAULT_PASSWORD"] = "false"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User, UserRole


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token(client):
    resp = client.post("/api/v1/auth/login", json={
        "username": settings.default_admin_username,
        "password": settings.default_admin_password,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
