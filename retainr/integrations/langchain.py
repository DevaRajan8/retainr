
try:
    from langchain_core.memory import BaseMemory
except ImportError:
    try:
        from langchain.memory import BaseMemory
    except ImportError:
        try:
            from langchain.schema.memory import BaseMemory
        except ImportError:
  
            class BaseMemory:
                def load_memory_variables(self, inputs: dict) -> dict:
                    raise NotImplementedError
                def save_context(self, inputs: dict, outputs: dict) -> None:
                    raise NotImplementedError
                def clear(self) -> None:
                    raise NotImplementedError

from retainr import Memory


class RetainrMemory(BaseMemory):

    def __init__(self, user_id: str = "default", db_path: str = "memory.db", **kwargs):
        self.mem = Memory(user_id=user_id, db_path=db_path)
        try:
            super().__init__(**kwargs)
        except TypeError:
            pass 

    @property
    def memory_variables(self) -> list[str]:
        return ["history"]

    def load_memory_variables(self, inputs: dict) -> dict:

        query = inputs.get("input", inputs.get("human_input", ""))
        results = self.mem.recall(query, top_k=3)
        history = "\n".join(f"- {r['text']}" for r in results)
        return {"history": history}

    def save_context(self, inputs: dict, outputs: dict) -> None:
        user_msg = inputs.get("input", inputs.get("human_input", ""))
        bot_msg = outputs.get("output", outputs.get("response", ""))
        if user_msg:
            self.mem.remember(user_msg, importance=0.7)
        if bot_msg:
            self.mem.remember(bot_msg, importance=0.4)

    def clear(self) -> None:

        self.mem.clear()

    def __repr__(self) -> str:
        stats = self.mem.stats()
        total = stats["total"]
        user_id = self.mem.user_id
        return f"RetainrMemory(user_id={user_id!r}, total={total})"