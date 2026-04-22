import json
import os

def get_knowledge_base():
    """Reads the local JSON file and returns the content as a string."""
    path = os.path.join("data", "knowledge_base.json")
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return json.dumps(data, indent=2)
    except FileNotFoundError:
        return "Knowledge base not found."