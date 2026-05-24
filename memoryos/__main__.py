
import sys
from memoryos import Memory, __version__

import os
from pathlib import Path


_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main():
    print(f"memoryos v{__version__} — local AI memory")
    print("Commands: remember <text> | recall <query> | clear | stats")
    print()

    mem = Memory(user_id="cli_user", db_path="cli_memory.db")

    if len(sys.argv) < 2:
        print("Usage: python -m memoryos remember 'some text'")
        print("       python -m memoryos recall 'your query'")
        print("       python -m memoryos clear")
        print("       python -m memoryos stats")
        return

    command = sys.argv[1].lower()
    args = " ".join(sys.argv[2:])

    if command == "remember":
        if not args:
            print("Error: provide text to remember")
            return
        mid = mem.remember(args)
        print(f"Remembered (id: {mid[:8]}...)")

    elif command == "recall":
        if not args:
            print("Error: provide a query")
            return
        results = mem.recall(args, top_k=3)
        if not results:
            print("No memories found.")
        for r in results:
            print(f"[{r['score']:.3f}] {r['text']}")

    elif command == "clear":
        mem.clear()
        print("  All memories cleared.")

    elif command == "stats":
        results = mem.recall("", top_k=99999)
        print(f"Total memories: {len(results)}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()