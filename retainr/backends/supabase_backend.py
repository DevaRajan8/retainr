import uuid
import numpy as np
from supabase import create_client, Client


class SupabaseBackend:


    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    def save(self, user_id: str, text: str, embedding: np.ndarray,
             tags: list, timestamp: float,
             importance: float = 0.5, decay_days: int = 0) -> str:

        if not text or not text.strip():
            raise ValueError("Cannot remember empty text.")
        if not 0.0 <= importance <= 1.0:
            raise ValueError(f"importance must be 0.0–1.0, got {importance}")

        memory_id = str(uuid.uuid4())

        self.client.table("memories").insert({
            "id": memory_id,
            "user_id": user_id,
            "text": text,
            "embedding": embedding.astype(np.float32).tolist(),
            "tags": tags,
            "importance": importance,
            "timestamp": timestamp,
            "decay_days": decay_days,
        }).execute()

        return memory_id

    def search(self, user_id: str, query_embedding: np.ndarray,
               top_k: int = 5) -> list[dict]:

        response = self.client.rpc("match_memories", {
            "query_embedding": query_embedding.astype(np.float32).tolist(),
            "match_user_id": user_id,
            "match_count": top_k,
        }).execute()

        results = []
        for row in response.data:
            results.append({
                "id": row["id"],
                "text": row["text"],
                "tags": row["tags"] if isinstance(row["tags"], list) else [],
                "importance": row["importance"],
                "score": float(row["similarity"]),
                "timestamp": row["timestamp"],
            })
        return results

    def delete(self, memory_id: str) -> bool:
        response = self.client.table("memories")\
            .delete()\
            .eq("id", memory_id)\
            .execute()
        return len(response.data) > 0

    def clear(self, user_id: str) -> None:
        self.client.table("memories")\
            .delete()\
            .eq("user_id", user_id)\
            .execute()