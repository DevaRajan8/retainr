import time
from .embedder import Embedder
from .store import VectorStore

class Memory:
    def __init__(self, user_id: str = "default", db_path: str = "memory.db"):
        self.user_id = user_id
        self.embedder = Embedder()
        self.store = VectorStore(db_path)

    def remember(self, text: str, tags: list[str] = [],
                 importance: float = 0.5, decay_days: int = 0) -> str:

        embedding = self.embedder.encode(text)
        return self.store.save(
            user_id=self.user_id, text=text, embedding=embedding,
            tags=tags, timestamp=time.time(),
            importance=importance, decay_days=decay_days,
        )

    def recall(self, query: str, top_k: int = 1) -> list[dict]:

        query_embedding = self.embedder.encode(query)
        return self.store.search(self.user_id, query_embedding, top_k)