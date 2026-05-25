import time
import pytest
from memoryos import Memory


# ─── Basic functionality ──────────────────────────────────────────────────────

def test_remember_and_recall():
    mem = Memory(user_id="test_user", db_path=":memory:")
    mem.remember("I prefer dark mode")
    mem.remember("I use VS Code as my editor")
    mem.remember("My favourite language is Python")

    results = mem.recall("what editor does the user use?")
    assert len(results) > 0
    assert "VS Code" in results[0]["text"]


def test_empty_recall():
    mem = Memory(user_id="new_user", db_path=":memory:")
    assert mem.recall("anything") == []


# ─── Forget ───────────────────────────────────────────────────────────────────

def test_forget_removes_memory():
    mem = Memory(user_id="u1", db_path=":memory:")
    mid = mem.remember("This should be deleted")
    mem.remember("This should stay")

    deleted = mem.forget(mid)
    assert deleted is True

    results = mem.recall("deleted", top_k=5)
    texts = [r["text"] for r in results]
    assert "This should be deleted" not in texts


def test_forget_nonexistent_returns_false():
    mem = Memory(user_id="u2", db_path=":memory:")
    result = mem.forget("nonexistent-id-12345")
    assert result is False


# ─── Clear ────────────────────────────────────────────────────────────────────

def test_clear_wipes_all_memories():
    mem = Memory(user_id="u3", db_path=":memory:")
    mem.remember("Memory one")
    mem.remember("Memory two")
    mem.clear()
    assert mem.recall("memory", top_k=5) == []


# ─── Importance + Tags ────────────────────────────────────────────────────────

def test_importance_stored():
    mem = Memory(user_id="u4", db_path=":memory:")
    mem.remember("Very important fact", importance=0.9)
    results = mem.recall("important fact", top_k=1)
    assert results[0]["importance"] == 0.9


def test_tags_stored():
    mem = Memory(user_id="u5", db_path=":memory:")
    mem.remember("Prefers dark mode", tags=["ui", "preference"])
    results = mem.recall("dark mode", top_k=1)
    assert "ui" in results[0]["tags"]
    assert "preference" in results[0]["tags"]


# ─── User isolation ───────────────────────────────────────────────────────────

def test_users_are_isolated():
    """Memories from user A should not appear in user B's recall."""
    mem_a = Memory(user_id="alice", db_path=":memory:")
    mem_b = Memory(user_id="bob",   db_path=":memory:")

    mem_a.remember("Alice likes cats")
    # Bob has no memories — should return empty
    results = mem_b.recall("cats", top_k=5)
    # Bob's store is separate, so "Alice likes cats" won't appear
    texts = [r["text"] for r in results]
    assert "Alice likes cats" not in texts