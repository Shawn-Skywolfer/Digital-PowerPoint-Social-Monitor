"""生成一键配置程序的种子数据（seed_data.py）。

从开发库 data/monitor.db 读出已配置的各类 Key（dajiala / LLM / Tavily /
LightPanda），用当前 .env 的 SECRET_KEY 解密，再用**新生成的分发密钥**
重新加密，连同建表 DDL 一起写入本目录的 seed_data.py。

安全性：seed_data.py 只含密文，不含明文 Key；明文仅在内存中短暂存在，
本脚本只打印脱敏摘要。seed_data.py 已加入 .gitignore，不应提交。

用法（在项目根）：
    .venv\\Scripts\\python.exe packaging\\configurator\\prepare_seed.py
"""
from __future__ import annotations

import base64
import hashlib
import pprint
import secrets
import sqlite3
import sys
from pathlib import Path

from cryptography.fernet import Fernet

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
DB_PATH = ROOT / "data" / "monitor.db"
OUT_PATH = Path(__file__).resolve().parent / "seed_data.py"


def _fernet(secret: str) -> Fernet:
    # 与 backend/app/core/security.py 相同的派生方式
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def _read_env_secret() -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("SECRET_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("未在 .env 中找到 SECRET_KEY")


def _mask(plain: str) -> str:
    return f"****{plain[-4:]}" if plain and len(plain) > 4 else "****"


def main() -> None:
    old_secret = _read_env_secret()
    new_secret = secrets.token_urlsafe(48)  # 分发密钥：每次重新生成
    dec, enc = _fernet(old_secret), _fernet(new_secret)

    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    # ---- 建表 DDL：原样取自 dev 库 sqlite_master（即应用 create_all 的产物）----
    tables = ["dajiala_keys", "llm_configs", "mcp_servers", "service_configs"]
    ddl = {}
    for t in tables:
        row = con.execute("SELECT sql FROM sqlite_master WHERE name=?", (t,)).fetchone()
        if not row:
            sys.exit(f"dev 库缺少表 {t}")
        ddl[t] = row[0]

    # ---- 读取并转加密 ----
    def reenc(token: str) -> str:
        plain = dec.decrypt(token.encode("utf-8")).decode("utf-8")
        return enc.encrypt(plain.encode("utf-8")).decode("utf-8")

    summary = []

    dajiala = []
    for r in con.execute("SELECT * FROM dajiala_keys WHERE enabled=1"):
        ct = reenc(r["key_enc"])
        dajiala.append({"label": r["label"], "key_enc": ct})
        plain = dec.decrypt(r["key_enc"].encode()).decode()
        summary.append(f"  dajiala Key 「{r['label']}」 {_mask(plain)}")

    llms = []
    for r in con.execute("SELECT * FROM llm_configs WHERE enabled=1"):
        ct = reenc(r["api_key_enc"])
        llms.append({
            "name": r["name"], "provider": r["provider"],
            "base_url": r["base_url"], "api_key_enc": ct, "model": r["model"],
        })
        plain = dec.decrypt(r["api_key_enc"].encode()).decode()
        summary.append(f"  LLM 「{r['name']}」 {r['base_url']} / {r['model']}  {_mask(plain)}")

    services = []
    for r in con.execute("SELECT * FROM service_configs WHERE enabled=1"):
        ct = reenc(r["api_key_enc"])
        services.append({
            "service": r["service"], "name": r["name"],
            "base_url": r["base_url"], "api_key_enc": ct,
        })
        plain = dec.decrypt(r["api_key_enc"].encode()).decode()
        summary.append(f"  服务 「{r['name']}」({r['service']})  {_mask(plain)}")

    con.close()

    if not dajiala and not llms and not services:
        sys.exit("dev 库里没有任何已配置的 Key，无种子可生成")

    # ---- .env 模板（随安装目录分发，与应用 config.py 的读取约定一致）----
    env_content = f"""# ===== 基本（由「社媒监测一键配置」生成）=====
APP_ENV=prod
# 用于 JWT 签名与 Key 加密；与已入库的加密 Key 配套，请勿修改
SECRET_KEY={new_secret}

# ===== 数据库（留空 = 安装目录 data\\\\monitor.db 的 SQLite）=====
DATABASE_URL=

# ===== 默认管理员（首次启动播种）=====
DEFAULT_ADMIN_USERNAME=Admin
DEFAULT_ADMIN_PASSWORD=Seek22626301
FORCE_CHANGE_DEFAULT_PASSWORD=true

# ===== CORS（桌面版无需改动）=====
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# ===== dajiala =====
DAJIALA_BASE_URL=https://www.dajiala.com
PROVIDER_MOCK=false

# ===== 出站 HTTP 代理（华为内网走代理 + 关 SSL 校验；直连外网则清空 PROXY 并置 true）=====
HTTP_PROXY=http://proxyjp.huawei.com:8080
HTTP_VERIFY_SSL=false

# ===== 抓取/分析调参 =====
FETCH_CONCURRENCY=3
ANALYSIS_CONCURRENCY=3
LLM_REQUEST_TIMEOUT=120
"""

    out = [
        '"""一键配置程序的种子数据 —— 由 prepare_seed.py 自动生成，请勿手改。',
        "",
        "只含 Fernet 密文（密钥见 SECRET_KEY，会写入目标机器 .env），不含明文 Key。",
        '"""',
        "",
        f"SECRET_KEY = {new_secret!r}",
        "",
        f"ENV_CONTENT = {env_content!r}",
        "",
        "# 建表 DDL（与应用 SQLAlchemy create_all 产物完全一致，取自 dev 库 sqlite_master）",
        f"TABLE_DDL = {pprint.pformat(ddl, width=100)}",
        "",
        f"DAJIALA_KEYS = {pprint.pformat(dajiala, width=100)}",
        "",
        f"LLM_CONFIGS = {pprint.pformat(llms, width=100)}",
        "",
        f"SERVICE_CONFIGS = {pprint.pformat(services, width=100)}",
        "",
    ]
    OUT_PATH.write_text("\n".join(out), encoding="utf-8")

    print(f"已生成 {OUT_PATH}（仅密文）")
    print("包含配置：")
    for s in summary:
        print(s)
    print(f"新分发 SECRET_KEY 已生成（{len(new_secret)} 字符，已写入 seed_data.py，不打印）")


if __name__ == "__main__":
    main()
