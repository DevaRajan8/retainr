
import os
from memoryos import Memory

from pathlib import Path

_env_file = Path(__file__).parent.parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

def get_memory_context(mem: Memory, user_message: str) -> str:

    results = mem.recall(user_message, top_k=1)
    if not results:
        return ""
    context = "\n".join(f"- {r['text']}" for r in results)
    return f"\nRelevant things I remember about you:\n{context}\n"


def chat_with_memory():
    mem = Memory(user_id="demo_user", db_path="chatbot_memory.db")
    print("Chatbot with memory (type 'quit' to exit, 'forget all' to clear)")
    print("\n")

    if HAS_GROQ:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    else:
        print("  Groq not installed — running in echo mode (no LLM)")
        print("   Install: pip install groq")
        print("   Get free API key: console.groq.com")
        print()

    conversation_history = []

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "forget all":
            mem.clear()
            print("Bot: Memory cleared.\n")
            continue
        
        def should_remember(user_input: str, client) -> bool:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": (
                        f"Does this message contain a personal fact, preference, or "
                        f"long-term information worth remembering about the user?\n\n"
                        f"Message: \"{user_input}\"\n\n"
                        f"Reply with only YES or NO."
                    )
                }],
                max_tokens=5,
                temperature=0,   
            )
            answer = response.choices[0].message.content.strip().upper()
            return answer.startswith("YES")
        
        
        if HAS_GROQ and should_remember(user_input, client):
            mem.remember(user_input, importance=0.8)
            print(" Stored in memory")

    
        memory_context = get_memory_context(mem, user_input)

        if HAS_GROQ:
            system_prompt = (
                "You are a helpful assistant with memory. "
                "Use the remembered context to personalise your responses."
                + memory_context
            )
            conversation_history.append({"role": "user", "content": user_input})
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}]
                         + conversation_history[-6:],  
            )
            reply = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": reply})
            print(f"Bot: {reply}\n")
        else:
            # Demo mode without LLM
            if memory_context:
                print(f"Bot: [Echo + Memory] {user_input}")
                print(f"     Context I have:{memory_context}")
            else:
                print(f"Bot: [Echo] {user_input}\n")


if __name__ == "__main__":
    chat_with_memory()