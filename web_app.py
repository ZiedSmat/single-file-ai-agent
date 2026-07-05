import os
import asyncio
import gradio as gr
from dotenv import load_dotenv
from core.agent import AIAgent
from core.db import init_db

# Load environment variables
load_dotenv()

# Initialize the Agent
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY in .env file")

agent = AIAgent(api_key)

# Setup the database and agent memory before launching the web page
async def setup():
    print("Initializing database...")
    await init_db()
    await agent.initialize(session_id="web_user_1")

asyncio.run(setup())

# This function links Gradio's chat interface to your Agent
async def chat_function(message, history):
    # 'message' is what you type in the text box
    response = await agent.chat(message)
    return response

# Build the ChatGPT-like Web GUI
demo = gr.ChatInterface(
    fn=chat_function,
    title="AI Code Assistant",
    description="Your personal coding agent with file reading, editing, and deleting capabilities."
)

if __name__ == "__main__":
    # Launch the local web server
    demo.launch()