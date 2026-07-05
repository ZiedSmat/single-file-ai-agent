# tools/list_files.py
import os
SCHEMA = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List all the files and directories in the specified path",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list (defaults to current directory)",
                }
            },
            "required": [],
        },
    }
}

async def execute(path: str = ".") -> str:
    try:
            if not os.path.exists(path):
                return f"Path not found: {path}"

            items = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"[DIR]  {item}/")
                else:
                    items.append(f"[FILE] {item}")

            if not items:
                return f"Empty directory: {path}"

            return f"Contents of {path}:\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing files: {str(e)}"