from memoryos import Memory

mem = Memory(user_id="arjun")
mem.remember("I prefer dark mode and use VS Code")
mem.remember("Currently building memoryos, a local memory library")
mem.remember("I like concise answers over long explanations")

results = mem.recall("what is the user building?")
for r in results:
    print(f"[{r['score']:.3f}] {r['text']}")