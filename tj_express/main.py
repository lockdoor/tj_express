import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from tj_express.api.routes import router as api_router
from tj_express.config import PORT, HOST

app = FastAPI(
    title="tj_express", 
    description="Express ERP Bridge & Custom Report Engine",
    version="0.1.0"
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
def root_redirect():
    """Redirects the base URL to the dashboard UI."""
    return RedirectResponse(url="/ui/index.html")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server on {HOST}:{PORT}...")
    uvicorn.run(app, host=HOST, port=PORT)
