import time
from .embedder import Embedder
from .store import VectorStore

class Memory:
    def __init__(self, user_id: str = "default", db_path: str = "memory.db"):
        self.user_id = user_id
        self.embedder = Embedder()
        self.store = VectorStore(db_path)
        
    def import_from(self, filepath: str) -> int:

        import json
        with open(filepath, "r") as f:
            memories = json.load(f)
        count = 0
        for m in memories:
            self.remember(
                text=m["text"],
                tags=m.get("tags", []),
                importance=m.get("importance", 0.5),
            )
            count += 1
        return count
    
        
    def stats(self) -> dict:
        rows = self.store.conn.execute(
            "SELECT timestamp, importance FROM memories WHERE user_id = ?",
            (self.user_id,)
        ).fetchall()

        if not rows:
            return {"total": 0, "oldest": None, "newest": None, "avg_importance": None}

        timestamps = [r[0] for r in rows]
        importances = [r[1] for r in rows]
        return {
            "total": len(rows),
            "oldest": min(timestamps),
            "newest": max(timestamps),
            "avg_importance": round(sum(importances) / len(importances), 3),
            "user_id": self.user_id,
        }
        
        
    def summarize(self, llm_fn=None) -> str:
        results = self.store.search(
            self.user_id,
            self.embedder.encode(""),
            top_k=99999
        )

        if not results:
            return "No memories stored yet."

        bullets = "\n".join(f"- {r['text']}" for r in results)

        if llm_fn is None:
            return f"Memories for user '{self.user_id}':\n{bullets}"

        prompt = (
            f"Here are facts about a user:\n{bullets}\n\n"
            "Write a concise 2-3 sentence summary of what you know about this user. "
            "Be specific and natural, like you're briefing someone."
        )
        return llm_fn(prompt)
        
    def forget(self, memory_id: str) -> bool:
        return self.store.delete(memory_id)

    def clear(self):
        self.store.clear(self.user_id)

    def export(self, filepath: str):
        import json
        # Get all memories (high top_k to get everything)
        results = self.store.search(self.user_id,
                                    self.embedder.encode(""), top_k=99999)
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

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