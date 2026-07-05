# tools/edit_file.py
import os

SCHEMA = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": "Edit a file by replacing old_text with new_text. Creates the file if it doesn't exist.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                            "type": "string",
                            "description": "The path to the file to edit",
                        },
                        "old_text": {
                            "type": "string",
                            "description": "The text to search for and replace (leave empty to create new file)",
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The text to replace old_text with",
                        },
            },
            "required": ["path", "new_text"],
        },
    }
}

async def execute(path: str, new_text: str, old_text: str = "") -> str:
    try:
            if os.path.exists(path) and old_text:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                if old_text not in content:
                    return f"Text not found in file: {old_text}"

                content = content.replace(old_text, new_text)

                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

                return f"Successfully edited {path}"
            else:
                # Only create directory if path contains subdirectories
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)

                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_text)

                return f"Successfully created {path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"