import os
import logging

SCHEMA = {
    "type": "function",
    "function": {
        "name": "delete_file",
        "description": "Delete a file safely. Requires 'path' and 'confirmed=True' to proceed.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to delete"},
                "confirmed": {
                    "type": "boolean",
                    "description": "Must be set to True to confirm deletion",
                },
            },
            "required": ["path", "confirmed"],
        },
    },
}


async def execute(path: str, confirmed: bool = False) -> str:
    # 1. Path Validation (Prevent directory traversal)
    base_dir = os.path.abspath(os.getcwd())
    file_path = os.path.abspath(path)

    if not file_path.startswith(base_dir):
        return "Security Error: Access denied. Cannot delete files outside the project directory."

    # 2. User Confirmation Check
    if not confirmed:
        return "Action required: Are you sure you want to delete this file? Please call this tool again with 'confirmed=True'."

    # 3. Execution & Logging
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {path}"

        os.remove(file_path)
        logging.info(f"File deleted successfully: {file_path}")
        return f"Successfully deleted {path}"

    except Exception as e:
        logging.error(f"Failed to delete {file_path}: {str(e)}")
        return f"Error: {str(e)}"
