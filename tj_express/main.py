import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from tj_express.api.routes import router as api_router
from tj_express.config import PORT, HOST, COMPANIES

is_container = os.getenv("IS_CONTAINER", "FALSE") == "TRUE"

app = FastAPI(
    title="tj_express", 
    description="Express ERP Bridge & Custom Report Engine",
    version="0.1.0",
    openapi_url=None if is_container else "/openapi.json",
    docs_url=None if is_container else "/docs",
    redoc_url=None if is_container else "/redoc",
)

# CORS middleware for local development/external queries
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount Static UI Folder
ui_path = Path(__file__).resolve().parent / "ui"
# Ensure the directory exists so FastAPI doesn't crash on mount
ui_path.mkdir(exist_ok=True)
app.mount("/ui", StaticFiles(directory=str(ui_path)), name="ui")

@app.get("/")
def read_root(request: Request):
    """
    Returns the online status and the configured companies list if requested by API,
    otherwise redirects to the dashboard UI for browser users.
    """
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/ui/index.html")
    return {"status": "online", "companies": list(COMPANIES.keys())}

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on {HOST}:{PORT}...")
    uvicorn.run(app, host=HOST, port=PORT)
