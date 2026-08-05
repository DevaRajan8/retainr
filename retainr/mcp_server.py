from fastmcp import FastMCP
from retainr import Memory

def start_server(db_path: str = "memory.db", user_id: str = "default"):
    # Initialize the MCP server
    mcp = FastMCP("retainr")
    
    # Connect to the existing retainr database
    mem = Memory(user_id=user_id, db_path=db_path)

    @mcp.tool(description="Store a memory entry with an optional importance score between 0.0 and 1.0.")
    def remember(text: str, importance: float = 0.5) -> str:
        """Store a memory entry with an optional importance score between 0.0 and 1.0."""

        mid = mem.remember(text, importance=importance)
        return f"Stored successfully. ID: {mid}"

    @mcp.tool(description="Retrieve the top matching memories for a query.")
    def recall(query: str, top_k: int = 5) -> list[dict]:
        """Retrieve the top matching memories for a query."""

        results = mem.recall(query, top_k=top_k)
        return [{"text": r["text"], "score": round(r["score"], 3), "id": r["id"]} for r in results]

    @mcp.tool(description="Delete a memory by its ID.")
    def forget(memory_id: str) -> str:
        """Delete a memory by its ID."""
  
        deleted = mem.forget(memory_id)
        return "Deleted successfully." if deleted else "Memory not found."

    @mcp.tool(description="Return memory statistics for the active user.")
    def stats() -> dict:
        """Return memory statistics for the active user."""
  
        return mem.stats()

    @mcp.tool(description="Delete all memories for the active user.")
    def clear_all() -> str:
        """Delete all memories for the active user."""

        mem.clear()
        return f"Cleared all memories for user '{user_id}'."

    # Start the server (uses stdio by default, which is what VS Code needs)
    mcp.run()