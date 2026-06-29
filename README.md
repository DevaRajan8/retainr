# retainr

[![CI](https://github.com/Devarajan8/memoryos/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/Devarajan8/memoryos/actions)
[![PyPI version](https://badge.fury.io/py/retainr.svg)](https://pypi.org/project/retainr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> Persistent, semantic memory for any Python AI app — local or cloud, zero API cost.

---

## Install

```bash
pip install retainr
```

---

## Quick Start

```python
from retainr import Memory

mem = Memory(user_id="arjun")

mem.remember("I prefer dark mode and use VS Code")
mem.remember("Currently building a job application assistant")
mem.remember("I like concise answers over long explanations")

results = mem.recall("what tools does the user prefer?")
for r in results:
    print(f"[{r['score']:.3f}] {r['text']}")
```

```
[0.412] I prefer dark mode and use VS Code
[0.289] I like concise answers over long explanations
```

---

## Storage Backends

Choose where your data lives — same API every time.

### Local (default, zero setup)

```python
mem = Memory(user_id="arjun")                     # saves to memory.db
mem = Memory(user_id="arjun", db_path=":memory:") # RAM only (tests)
```

### Cloud — Supabase (no local files, multi-device)

```bash
pip install retainr supabase python-dotenv
```

```python
import os
from dotenv import load_dotenv
from retainr import Memory
from retainr.backends.supabase_backend import SupabaseBackend

load_dotenv()

backend = SupabaseBackend(
    url=os.environ["SUPABASE_URL"],
    key=os.environ["SUPABASE_KEY"]
)
mem = Memory(user_id="arjun", backend=backend)
```

> See [`docs/supabase_setup.sql`](docs/supabase_setup.sql) for one-click Supabase setup.

---

## Features

- **Semantic recall** — finds memories by meaning, not exact keywords
- **Memory decay** — scores fade over time using exponential half-life
- **Importance scoring** — weight memories by significance (0.0–1.0)
- **Tags** — organise memories into namespaces
- 🗑️ **Forget & clear** — GDPR-friendly deletion
- **Stats** — count, average importance, oldest/newest memory
- **Async support** — `AsyncMemory` for FastAPI and Discord bots
- **LangChain plugin** — drop-in persistent memory for any LangChain chain
- **Local or cloud** — SQLite locally, Supabase (pgvector) in the cloud
- **Zero cost** — no mandatory API keys, runs on your machine

---

## API Reference

### `Memory(user_id, db_path, backend)`

| Param     | Default       | Description                           |
| --------- | ------------- | ------------------------------------- |
| `user_id` | `"default"`   | Isolates memories per user            |
| `db_path` | `"memory.db"` | SQLite path. `":memory:"` for RAM     |
| `backend` | `None`        | Custom backend (e.g. SupabaseBackend) |

---

### `remember(text, tags, importance, decay_days)` → `str`

```python
mid = mem.remember(
    "Got promoted to SDE-2",
    tags=["career"],
    importance=0.9,   # 0.0–1.0, default 0.5
    decay_days=90,    # score halves every 90 days, 0 = no decay
)
```

---

### `recall(query, top_k)` → `list[dict]`

```python
results = mem.recall("job status?", top_k=3)
# [{"id": ..., "text": ..., "score": 0.87, "tags": [...], "importance": ...}]
```

---

### `forget(memory_id)` → `bool`

```python
mem.forget(mid)   # returns True if deleted, False if not found
```

---

### `clear()`

```python
mem.clear()   # wipes all memories for this user
```

---

### `stats()` → `dict`

```python
mem.stats()
# {"total": 12, "avg_importance": 0.65, "oldest": ..., "newest": ..., "user_id": "arjun"}
```

---

### `summarize(llm_fn)` → `str`

```python
mem.summarize()           # returns bullet list (no LLM)
mem.summarize(llm_fn=fn)  # pass any callable that takes a prompt string
```

---

### `export(filepath)`

```python
mem.export("backup.json")
```

---

## Async Support

For FastAPI, Discord bots, or any async app:

```python
from retainr import AsyncMemory
import asyncio

async def main():
    mem = AsyncMemory(user_id="arjun")
    await mem.aremember("I love async Python")
    results = await mem.arecall("what do I love?")
    print(results[0]["text"])

asyncio.run(main())
```

| Method        | Description    |
| ------------- | -------------- |
| `aremember()` | Async remember |
| `arecall()`   | Async recall   |
| `aforget()`   | Async forget   |
| `aclear()`    | Async clear    |

---

## LangChain Integration

Drop-in replacement for LangChain's built-in memory — persists across restarts:

```python
from retainr.integrations.langchain import RetainrMemory
from langchain.chains import ConversationChain

memory = RetainrMemory(user_id="alice", db_path="alice.db")
chain = ConversationChain(llm=llm, memory=memory)

# Session 1
chain.invoke({"input": "My name is Alice and I hate JavaScript"})

# Session 2 — new process, bot still remembers
chain.invoke({"input": "What languages do I dislike?"})
# → "You mentioned you hate JavaScript"
```

---

## CLI

```bash
python -m retainr remember "I love building Python libraries"
python -m retainr recall "what do I love?"
python -m retainr stats
python -m retainr clear
```

---

## How it works

1. **`remember()`** → text embedded locally via `sentence-transformers` (all-MiniLM-L6-v2) → vector stored in FAISS or pgvector, metadata in SQLite or Supabase
2. **`recall()`** → query embedded → nearest vectors found → original text returned
3. **Scoring** → `cosine_similarity × (0.7 + 0.3 × decayed_importance)`

---

---

## Stack

- [`sentence-transformers`](https://www.sbert.net/) — local embeddings
- [`faiss-cpu`](https://github.com/facebookresearch/faiss) — vector search
- `sqlite3` — local metadata (built into Python)
- [`supabase-py`](https://github.com/supabase-community/supabase-py) — cloud backend (optional)

---

## License

MIT © Devarajan S
