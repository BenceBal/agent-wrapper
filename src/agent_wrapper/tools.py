from langchain_core.tools import tool
import os

@tool
def write_file(path: str, content: str):
    """
    Writes content to a file at the given path.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def read_file(path: str):
    """
    Reads content from a file.
    """
    if not os.path.exists(path):
        return "File not found."
    with open(path, "r") as f:
        return f.read()

@tool
def list_files(directory: str = "."):
    """
    Lists files in a directory.
    """
    return str(os.listdir(directory))

# Define the toolset for Anthropic
TOOLS = [write_file, read_file, list_files]
