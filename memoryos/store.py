import sqlite3
import json
import uuid
import time
import numpy as np
import faiss

class VectorStore:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.dimension = 384  # all-MiniLM-L6-v2 output size


        self.index = faiss.IndexFlatIP(self.dimension)


        self.id_map: list[str] = []

        self._init_db()
        self._load_from_db() 

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id          TEXT PRIMARY KEY,
                user_id     TEXT NOT NULL,
                text        TEXT NOT NULL,
                embedding   BLOB NOT NULL,
                tags        TEXT DEFAULT '[]',
                importance  REAL DEFAULT 0.5,
                timestamp   REAL NOT NULL,
                decay_days  INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def _load_from_db(self):

        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            "SELECT id, embedding FROM memories ORDER BY rowid"
        ).fetchall()
        conn.close()
        for memory_id, emb_bytes in rows:
            embedding = np.frombuffer(emb_bytes, dtype=np.float32)
            self.index.add(embedding.reshape(1, -1))
            self.id_map.append(memory_id)

    def save(self, user_id: str, text: str, embedding: np.ndarray,
             tags: list, timestamp: float, importance: float = 0.5,
             decay_days: int = 0) -> str:
        memory_id = str(uuid.uuid4())
        self.index.add(embedding.astype(np.float32).reshape(1, -1))
        self.id_map.append(memory_id)

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO memories
            (id, user_id, text, embedding, tags, importance, timestamp, decay_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (memory_id, user_id, text,
              embedding.astype(np.float32).tobytes(),
              json.dumps(tags), importance, timestamp, decay_days))
        conn.commit()
        conn.close()
        return memory_id

    def search(self, user_id: str, query_embedding: np.ndarray,
               top_k: int = 5) -> list[dict]:
        if self.index.ntotal == 0:
            return []

        scores, indices = self.index.search(
            query_embedding.astype(np.float32).reshape(1, -1),
            min(top_k * 2, self.index.ntotal)
        )
        results = []
        conn = sqlite3.connect(self.db_path)
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            memory_id = self.id_map[idx]
            row = conn.execute(
                "SELECT * FROM memories WHERE id = ? AND user_id = ?",
                (memory_id, user_id)
            ).fetchone()
            if row:
                results.append({
                    "id": row[0], "text": row[2],
                    "tags": json.loads(row[4]),
                    "importance": row[5], "score": float(score),
                    "timestamp": row[6],
                })
            if len(results) >= top_k:
                break
        conn.close()
        return results