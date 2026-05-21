from memoryos import Memory

def test_remember_and_recall():
    mem = Memory(user_id="test_user", db_path=":memory:")
    # ":memory:" = SQLite in RAM — auto-deleted after test, no file left behind

    mem.remember("I prefer dark mode")
    mem.remember("I use VS Code as my editor")
    mem.remember("My favourite language is Python")

    results = mem.recall("what editor does the user use?")
    assert len(results) > 0
    assert "VS Code" in results[0]["text"]

def test_empty_recall():
    mem = Memory(user_id="new_user", db_path=":memory:")
    assert mem.recall("anything") == []