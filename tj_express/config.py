import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
if os.getenv("IS_CONTAINER", "FALSE") == "FALSE":
    ENV_PATH = Path(__file__).resolve().parent.parent / "secrets" / "express.env"
    load_dotenv(ENV_PATH)

EXPRESS_PATH = os.getenv("EXPRESS_PATH", "")
PORT = int(os.getenv("PORT", 8001))
HOST = os.getenv("HOST", "0.0.0.0")

COMPANIES = ['RINARA', 'JINTAN', 'TJ']

def get_available_companies() -> list[str]:
    """Dynamically lists all subdirectories inside EXPRESS_PATH."""
    if not EXPRESS_PATH or not os.path.isdir(EXPRESS_PATH):
        return []
    try:
        return [
            d for d in os.listdir(EXPRESS_PATH)
            if os.path.isdir(os.path.join(EXPRESS_PATH, d)) and d.startswith(tuple(COMPANIES))
        ]
    except Exception:
        return []
