import asyncio
from .memory import Memory

class AsyncMemory:
    def __init__(self, user_id: str = "default", db_path: str = "memory.db"):
        self._mem = Memory(user_id=user_id, db_path=db_path)

    async def aremember(self, text: str, **kwargs) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._mem.remember(text, **kwargs))

    async def arecall(self, query: str, top_k: int = 5) -> list[dict]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._mem.recall(query, top_k))

    async def aforget(self, memory_id: str) -> bool:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._mem.forget(memory_id))

    async def aclear(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._mem.clear)