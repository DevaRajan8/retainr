import sys
import os
from pathlib import Path
from retainr import Memory, __version__

_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

def main():
    if len(sys.argv) < 2:
        print(f"retainr v{__version__} — local AI memory")
        print("Commands: remember <text> | recall <query> | clear | stats | serve-mcp")
        print("Usage: python -m retainr remember 'some text'")
        print("       python -m retainr serve-mcp --db my.db --user alice")
        return

    command = sys.argv[1].lower()
    
    # We only initialize the default memory if we aren't starting the MCP server
    if command != "serve-mcp":
        mem = Memory(user_id="cli_user", db_path="cli_memory.db")

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
        results = mem.recall(args, top_k=1)
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

    elif command == "serve-mcp":
        # Manually parse the --db and --user flags from sys.argv
        db_path = "memory.db"
        user_id = "default"
        
        if "--db" in sys.argv:
            try:
                db_path = sys.argv[sys.argv.index("--db") + 1]
            except IndexError:
                print("Error: Please provide a value after --db")
                return
                
        if "--user" in sys.argv:
            try:
                user_id = sys.argv[sys.argv.index("--user") + 1]
            except IndexError:
                print("Error: Please provide a value after --user")
                return

        try:
            from retainr.mcp_server import start_server
            start_server(db_path=db_path, user_id=user_id)
        except ImportError:
            print("Error: FastMCP not installed.")
            print("Please install with: pip install fastmcp")

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()