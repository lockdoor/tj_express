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

try:
    COMPANIES = json.loads(os.getenv("COMPANIES", "{}"))
except Exception:
    COMPANIES = {}
