import os

SCHEMA = {
    "type": "function",
    "function": {
        "name": "rename_file",
        "description": "Rename or move a file from old_path to new_path",
        "parameters": {
            "type": "object",
            "properties": {
                "old_path": {
                    "type": "string",
                    "description": "The current path of the file",
                },
                "new_path": {
                    "type": "string",
                    "description": "The new path or name for the file",
                }
            },
            "required": ["old_path", "new_path"],
        },
    }
}

async def execute(old_path: str, new_path: str) -> str:
    try:
        if not os.path.exists(old_path):
            return f"File not found: {old_path}"
        
        os.rename(old_path, new_path)
        return f"Successfully renamed {old_path} to {new_path}"
    except Exception as e:
        return f"Error renaming file: {str(e)}"