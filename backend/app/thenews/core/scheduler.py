# Scheduler utilities for background tasks
import asyncio
from typing import Callable, Any

class PeriodicTask:
    """Runs a coroutine periodically."""
    def __init__(self, interval_seconds: int, coro: Callable[..., Any], *args, **kwargs):
        self.interval = interval_seconds
        self.coro = coro
        self.args = args
        self.kwargs = kwargs
        self._task: asyncio.Task | None = None

    async def _run(self):
        while True:
            await self.coro(*self.args, **self.kwargs)
            await asyncio.sleep(self.interval)

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None