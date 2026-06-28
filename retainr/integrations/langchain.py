# retainr/integrations/langchain.py
from langchain.memory import BaseMemory
from retainr import Memory

class RetainrMemory(BaseMemory):

    def __init__(self, user_id: str = "default", **kwargs):
        self.mem = Memory(user_id=user_id)
        super().__init__(**kwargs)

    @property
    def memory_variables(self):
        return ["history"]

    def load_memory_variables(self, inputs):
        query = inputs.get("input", "")
        results = self.mem.recall(query, top_k=3)
        history = "\n".join(f"- {r['text']}" for r in results)
        return {"history": history}

    def save_context(self, inputs, outputs):
        self.mem.remember(inputs.get("input", ""), importance=0.7)
        self.mem.remember(outputs.get("output", ""), importance=0.5)

    def clear(self):
        self.mem.clear()