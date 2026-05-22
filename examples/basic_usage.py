from memoryos import Memory

mem = Memory(user_id="arjun")
mem.remember("I prefer dark mode and use VS Code")
mem.remember("Currently building memoryos, a local memory library")
mem.remember("I like concise answers over long explanations")

results = mem.recall("what is the user building?")
for r in results:
    print(f"[{r['score']:.3f}] {r['text']}")
    

from memoryos import Memory

mem = Memory(user_id="arjun", db_path=":memory:")
mid = mem.remember("Old info", decay_days=1)
mem.remember("User prefers Python", importance=0.9)
mem.remember("User said hi", importance=0.1)
mem.remember("Wants dark UI", tags=["ui", "preference"])

results = mem.recall("what does the user prefer?", top_k=3)
for r in results:
    print(f"[{r['score']:.3f}] {r['text']}")

mem.forget(mid)
print("After forget:", len(mem.recall("old info")), "results")
mem.clear()
print("After clear:", len(mem.recall("anything")), "results")