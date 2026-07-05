# main.py
import os
import sys
import argparse
import asyncio
from dotenv import load_dotenv
import logging

from core.agent import AIAgent
from core.db import init_db 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("agent.log")],
)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("--api-key", help="OpenAI API key")
    args = parser.parse_args()

    load_dotenv()
    
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: Please provide an API key")
        sys.exit(1)

    # 1. نحضرو قاعدة البيانات قبل كل شيء
    print("Initializing database...")
    await init_db()

    # 2. نصنعو الـ Agent ونعطيوه اسم مستعمل (Session ID)
    agent = AIAgent(api_key)
    await agent.initialize(session_id="user_123")

    print("AI Code Assistant (Database Memory Version)")
    print("================")
    print("Type 'exit' or 'quit' to end.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    asyncio.run(main())