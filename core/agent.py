# core/agent.py
import json
import logging
import importlib
import pkgutil
from typing import List, Dict, Any
from openai import AsyncOpenAI
import tools
from core.db import load_memory, save_memory  # Added DB imports


class AIAgent:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

        self.system_prompt = """
        You are an expert AI coding assistant. You are proficient in Python, SQL and data engineering tools.
        Your goal is to help the user with coding tasks, file management, and data analysis.
        - Always analyze the context before making changes.
        - Write clean, efficient, and well-documented code.
        - If the user asks you to write code, always include necessary imports.
        - If you make an edit, ensure it is correct and follows best practices.
        - You have access to tools; use them autonomously to resolve the user's request.
        """

        self.messages = [{"role": "system", "content": self.system_prompt}]

        self.messages: List[Dict[str, Any]] = []
        self.tools_schema = []
        self.tool_functions = {}
        self._setup_tools()

    # Async initialize method to handle DB loading
    async def initialize(self, session_id: str = "default_user"):
        self.session_id = session_id
        # Fetch previous memory from the database
        self.messages = await load_memory(self.session_id)
        logging.info(f"Loaded {len(self.messages)} messages for session {session_id}")

    def _setup_tools(self):
        """
        Dynamically load all tools from the 'tools' directory.
        """
        for _, module_name, _ in pkgutil.iter_modules(tools.__path__):
            full_module_name = f"tools.{module_name}"
            module = importlib.import_module(full_module_name)

            if hasattr(module, "SCHEMA") and hasattr(module, "execute"):
                self.tools_schema.append(module.SCHEMA)
                tool_name = module.SCHEMA["function"]["name"]
                self.tool_functions[tool_name] = module.execute
                logging.info(f"Loaded tool: {tool_name}")

    async def chat(self, user_input: str) -> str:
        logging.info(f"User input: {user_input}")
        self.messages.append({"role": "user", "content": user_input})

        # Save memory directly after user input
        await save_memory(self.session_id, self.messages)

        while True:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.messages,
                    tools=self.tools_schema,
                )

                message = response.choices[0].message
                assistant_message = {"role": "assistant", "content": message.content}

                if message.tool_calls:
                    assistant_message["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ]
                self.messages.append(assistant_message)

                if message.tool_calls:
                    for tc in message.tool_calls:
                        tool_name = tc.function.name
                        tool_input = json.loads(tc.function.arguments)

                        if tool_name in self.tool_functions:
                            result = await self.tool_functions[tool_name](**tool_input)
                        else:
                            result = f"Unknown tool: {tool_name}"

                        logging.info(f"Tool result: {str(result)[:500]}...")
                        self.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": str(result),
                            }
                        )
                else:
                    # Save memory directly after final AI response
                    await save_memory(self.session_id, self.messages)
                    return message.content or ""

            except Exception as e:
                logging.error(f"Error in chat loop: {str(e)}")
                return f"Error: {str(e)}"
