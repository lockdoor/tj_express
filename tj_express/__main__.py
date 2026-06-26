import os
import uvicorn
from tj_express.config import HOST, PORT

def main():
    is_container = os.getenv("IS_CONTAINER", "FALSE") == "TRUE"
    # Launch uvicorn programmatically, loading the app from tj_express.main
    # Disable reload inside containers to avoid spawning a watcher process.
    # Run with exactly 1 worker for the lowest possible RAM usage.
    uvicorn.run(
        "tj_express.main:app", 
        host=HOST, 
        port=PORT, 
        reload=not is_container,
        workers=1 if is_container else None
    )

if __name__ == "__main__":
    main()