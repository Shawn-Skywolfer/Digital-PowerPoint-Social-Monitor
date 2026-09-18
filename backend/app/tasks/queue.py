"""进程内后台任务运行器：用 asyncio 任务执行抓取/分析，支持取消。"""
from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Optional

from ..core.logging import get_logger

logger = get_logger(__name__)

CancelEvent = asyncio.Event
JobCoro = Callable[[CancelEvent], Awaitable[None]]


class JobManager:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task] = {}
        self._cancels: dict[str, CancelEvent] = {}

    def start(self, job_key: str, coro: JobCoro) -> None:
        if job_key in self._tasks and not self._tasks[job_key].done():
            logger.warning("任务 %s 已在运行，忽略重复启动", job_key)
            return
        cancel = asyncio.Event()
        self._cancels[job_key] = cancel
        task = asyncio.create_task(self._run(job_key, coro, cancel))
        self._tasks[job_key] = task

    async def _run(self, job_key: str, coro: JobCoro, cancel: CancelEvent) -> None:
        try:
            await coro(cancel)
        except asyncio.CancelledError:
            logger.info("任务 %s 被取消", job_key)
        except Exception:  # noqa: BLE001
            logger.exception("任务 %s 执行异常", job_key)
        finally:
            self._cancels.pop(job_key, None)
            self._tasks.pop(job_key, None)

    def cancel(self, job_key: str) -> bool:
        ev = self._cancels.get(job_key)
        if ev:
            ev.set()
            return True
        return False

    def is_running(self, job_key: str) -> bool:
        t = self._tasks.get(job_key)
        return bool(t and not t.done())


manager = JobManager()
