"""社媒监测洞察系统 · 一键配置程序。

用途：主程序安装完成后，双击运行本程序，自动完成：
  1. 在安装目录写入 .env（分发密钥、管理员、代理等参数）
  2. 向安装目录 data\\monitor.db 写入各类已加密 Key
     （dajiala 数据源 / DeepSeek 大模型 / Tavily 搜索 / LightPanda 浏览器）

Key 以密文形式内置于本程序（seed_data.py，由 prepare_seed.py 生成），
与写入 .env 的 SECRET_KEY 配套，本程序全程不接触明文。

GUI：双击即用（自动探测安装目录，可手动浏览更改）。
CLI：--cli [--path 安装目录]（静默配置，供打包后自测/运维使用；
      窗口版无控制台，日志同时写入 %TEMP%\\社媒监测一键配置.log，
      退出码 0=成功 1=失败 2=未找到安装目录）。
"""
from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import sys
import traceback
from datetime import datetime
from pathlib import Path

import seed_data  # 同目录，PyInstaller 会自动跟随打包

APP_EXE = "社媒监测洞察系统.exe"
APP_DIR = "社媒监测洞察系统"
LOG_FILE = Path(os.environ.get("TEMP", ".")) / "社媒监测一键配置.log"


# ---------------------------------------------------------------- 核心逻辑
def find_install_dir() -> Path | None:
    """按常见安装位置探测主程序目录（含 exe 才算命中）。"""
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / APP_DIR,
        Path(os.environ.get("PROGRAMFILES", "")) / APP_DIR,
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / APP_DIR,
        Path(sys.executable).resolve().parent,  # 配置程序与主程序同目录时
    ]
    for c in candidates:
        if (c / APP_EXE).is_file():
            return c
    return None


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def _write_env(install_dir: Path, log) -> None:
    env_path = install_dir / ".env"
    if env_path.is_file():
        old = env_path.read_text(encoding="utf-8", errors="replace")
        if old.strip() == seed_data.ENV_CONTENT.strip():
            log(".env 已是最新，跳过（不备份）")
            return
        bak = install_dir / f".env.bak-{datetime.now():%Y%m%d%H%M%S}"
        shutil.copy2(env_path, bak)
        log(f"已备份原 .env → {bak.name}")
    env_path.write_text(seed_data.ENV_CONTENT, encoding="utf-8")
    log("已写入 .env（密钥/管理员/代理/并发参数）")


def _seed_db(install_dir: Path, log) -> None:
    data_dir = install_dir / "data"
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "monitor.db"
    fresh = not db_path.exists()

    con = sqlite3.connect(str(db_path), timeout=15)
    try:
        con.execute("PRAGMA busy_timeout=15000;")
        # 库尚未初始化（主程序从未启动）时，先建配置相关表；
        # DDL 与应用 create_all 产物完全一致，其余表由主程序启动时自建。
        for ddl in seed_data.TABLE_DDL.values():
            con.execute(ddl.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1))
        if fresh:
            log("数据库不存在，已创建（其余表将在主程序首次启动时自动建立）")

        now = _now()

        # ---- dajiala Key（upsert by label）----
        for k in seed_data.DAJIALA_KEYS:
            row = con.execute(
                "SELECT id FROM dajiala_keys WHERE label=?", (k["label"],)).fetchone()
            if row:
                con.execute(
                    "UPDATE dajiala_keys SET key_enc=?, status='active', enabled=1,"
                    " is_default=1, used=0, updated_at=? WHERE id=?",
                    (k["key_enc"], now, row[0]))
            else:
                con.execute(
                    "INSERT INTO dajiala_keys (label, key_enc, owner_id, quota, used,"
                    " status, is_default, enabled, last_check, note,"
                    " created_at, updated_at)"
                    " VALUES (?,?,NULL,NULL,0,'active',1,1,NULL,?,?,?)",
                    (k["label"], k["key_enc"], "一键配置导入", now, now))
            log(f"  ✓ 数据源 Key（dajiala）：{k['label']}")

        # ---- LLM 配置（upsert by name）----
        for m in seed_data.LLM_CONFIGS:
            row = con.execute(
                "SELECT id FROM llm_configs WHERE name=?", (m["name"],)).fetchone()
            if row:
                con.execute(
                    "UPDATE llm_configs SET provider=?, base_url=?, api_key_enc=?,"
                    " model=?, enabled=1, updated_at=? WHERE id=?",
                    (m["provider"], m["base_url"], m["api_key_enc"],
                     m["model"], now, row[0]))
            else:
                con.execute(
                    "INSERT INTO llm_configs (name, provider, base_url, api_key_enc,"
                    " model, params, enabled, owner_id, created_at, updated_at)"
                    " VALUES (?,?,?,?,?,NULL,1,NULL,?,?)",
                    (m["name"], m["provider"], m["base_url"],
                     m["api_key_enc"], m["model"], now, now))
            log(f"  ✓ 大模型：{m['name']}（{m['base_url']} / {m['model']}）")

        # ---- 第三方服务（upsert by service+name）----
        for s in seed_data.SERVICE_CONFIGS:
            row = con.execute(
                "SELECT id FROM service_configs WHERE service=? AND name=?",
                (s["service"], s["name"])).fetchone()
            if row:
                con.execute(
                    "UPDATE service_configs SET base_url=?, api_key_enc=?,"
                    " enabled=1, updated_at=? WHERE id=?",
                    (s["base_url"], s["api_key_enc"], now, row[0]))
            else:
                con.execute(
                    "INSERT INTO service_configs (service, name, base_url,"
                    " api_key_enc, extra, enabled, owner_id, created_at, updated_at)"
                    " VALUES (?,?,?,?,NULL,1,NULL,?,?)",
                    (s["service"], s["name"], s["base_url"],
                     s["api_key_enc"], now, now))
            log(f"  ✓ 服务：{s['name']}")

        con.commit()

        n_keys = con.execute("SELECT COUNT(*) FROM dajiala_keys WHERE enabled=1").fetchone()[0]
        n_llm = con.execute("SELECT COUNT(*) FROM llm_configs WHERE enabled=1").fetchone()[0]
        n_svc = con.execute("SELECT COUNT(*) FROM service_configs WHERE enabled=1").fetchone()[0]
        log(f"数据库校验：数据源 Key ×{n_keys}，大模型 ×{n_llm}，服务 ×{n_svc}")
    finally:
        con.close()


def apply_config(install_dir: Path, log) -> None:
    """执行完整配置；log 为 callable(str)。出错抛异常由调用方展示。"""
    install_dir = install_dir.resolve()
    if not (install_dir / APP_EXE).is_file():
        raise FileNotFoundError(
            f"所选目录不是主程序安装目录（未找到 {APP_EXE}）：\n{install_dir}")
    log(f"安装目录：{install_dir}")
    _write_env(install_dir, log)
    log("写入加密配置到数据库 ...")
    _seed_db(install_dir, log)
    log("配置完成 ✔  请启动（或重启）「社媒监测洞察系统」生效。")


# ---------------------------------------------------------------- CLI
def run_cli(path_arg: str | None) -> int:
    lines = []

    def log(msg: str) -> None:
        line = f"[{datetime.now():%H:%M:%S}] {msg}"
        lines.append(line)
        try:
            print(line, flush=True)  # 窗口版 stdout 为 None，静默忽略
        except Exception:
            pass

    try:
        install_dir = Path(path_arg) if path_arg else find_install_dir()
        if not install_dir:
            log("未找到主程序安装目录，请先安装「社媒监测洞察系统」，"
                "或用 --path 指定目录。")
            return 2
        apply_config(install_dir, log)
        return 0
    except Exception:
        log("配置失败：\n" + traceback.format_exc())
        return 1
    finally:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} =====\n")
                f.write("\n".join(lines) + "\n")
        except Exception:
            pass


# ---------------------------------------------------------------- GUI
def run_gui() -> int:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext

    root = tk.Tk()
    root.title("社媒监测洞察系统 · 一键配置")
    root.geometry("620x560")
    root.minsize(560, 500)

    pad = {"padx": 14, "pady": 4}
    tk.Label(root, text="社媒监测洞察系统 · 一键配置",
             font=("Microsoft YaHei UI", 15, "bold")).pack(anchor="w", **pad)
    tk.Label(
        root,
        text="自动写入运行参数与各类 Key（数据源 / 大模型 / 搜索 / 云端浏览器），\n"
             "请在安装主程序之后运行本工具；若主程序正在运行，配置完成后请重启。",
        justify="left", fg="#555").pack(anchor="w", **pad)

    # 安装目录选择
    row = tk.Frame(root)
    row.pack(fill="x", **pad)
    tk.Label(row, text="安装目录：").pack(side="left")
    path_var = tk.StringVar(value=str(find_install_dir() or ""))
    entry = tk.Entry(row, textvariable=path_var)
    entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

    def browse():
        d = filedialog.askdirectory(title="请选择主程序安装目录")
        if d:
            path_var.set(d)

    tk.Button(row, text="浏览…", command=browse).pack(side="left")

    # 配置内容清单
    items = ["• 运行参数（.env：密钥 / 管理员 / 代理 / 并发）"]
    items += [f"• 数据源 Key（dajiala）：{k['label']}" for k in seed_data.DAJIALA_KEYS]
    items += [f"• 大模型：{m['name']}（{m['model']}）" for m in seed_data.LLM_CONFIGS]
    items += [f"• 服务：{s['name']}" for s in seed_data.SERVICE_CONFIGS]
    tk.Label(root, text="将写入以下配置：", font=("Microsoft YaHei UI", 10, "bold")
             ).pack(anchor="w", **pad)
    tk.Label(root, text="\n".join(items), justify="left", fg="#333"
             ).pack(anchor="w", padx=28)

    # 日志区
    log_box = scrolledtext.ScrolledText(root, height=11, state="disabled",
                                        font=("Consolas", 9))
    log_box.pack(fill="both", expand=True, **pad)

    def log(msg: str) -> None:
        log_box.configure(state="normal")
        log_box.insert("end", f"[{datetime.now():%H:%M:%S}] {msg}\n")
        log_box.see("end")
        log_box.configure(state="disabled")
        root.update_idletasks()

    def do_config():
        btn.config(state="disabled", text="配置中…")
        try:
            p = path_var.get().strip()
            if not p:
                messagebox.showwarning("提示", "请先选择主程序安装目录", parent=root)
                return
            apply_config(Path(p), log)
            messagebox.showinfo(
                "完成", "配置完成！\n\n请启动（或重启）「社媒监测洞察系统」。\n"
                "默认账号 Admin / Seek22626301，首次登录需改密。", parent=root)
        except Exception as e:
            log(traceback.format_exc())
            messagebox.showerror("配置失败", str(e), parent=root)
        finally:
            btn.config(state="normal", text="一键配置")

    btn = tk.Button(root, text="一键配置", command=do_config,
                    font=("Microsoft YaHei UI", 12, "bold"),
                    bg="#C7000B", fg="white", activebackground="#A50009",
                    relief="flat", height=1)
    btn.pack(fill="x", padx=14, pady=(2, 12))

    if not path_var.get():
        log("未自动找到安装目录，请点击「浏览…」选择主程序安装位置。")
    else:
        log("已自动定位安装目录，点击「一键配置」开始。")
    root.mainloop()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="社媒监测洞察系统 · 一键配置")
    ap.add_argument("--cli", action="store_true", help="命令行模式（不弹窗）")
    ap.add_argument("--path", default=None, help="主程序安装目录（可选）")
    args = ap.parse_args()
    if args.cli:
        return run_cli(args.path)
    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
