# core/db.py
import os
import json
import asyncpg
import logging

async def init_db():
    # Create the table if it does not exist
    conn = await asyncpg.connect(os.environ.get("DATABASE_URL"))
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            messages JSONB
        )
    ''')
    await conn.close()
    logging.info("Database initialized.")

async def load_memory(session_id: str) -> list:
    # Fetch previous memory from the database
    conn = await asyncpg.connect(os.environ.get("DATABASE_URL"))
    row = await conn.fetchrow('SELECT messages FROM chat_sessions WHERE session_id = $1', session_id)
    await conn.close()
    
    if row and row['messages']:
        return json.loads(row['messages'])
    return []

async def save_memory(session_id: str, messages: list):
    # Save new memory and update if the session already exists
    conn = await asyncpg.connect(os.environ.get("DATABASE_URL"))
    messages_json = json.dumps(messages)
    
    await conn.execute('''
        INSERT INTO chat_sessions (session_id, messages) 
        VALUES ($1, $2)
        ON CONFLICT (session_id) DO UPDATE SET messages = EXCLUDED.messages
    ''', session_id, messages_json)
    await conn.close()