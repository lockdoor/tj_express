# ADR 0003: Memory Footprint Optimization for Production Containers

## Status
Accepted

## Context
When running within Docker, the `tj_express` FastAPI application initially consumed upwards of **160 MB of RAM** at idle. Compared to other services like the Django backend (`tj_inventory`) which runs at ~60 MB, this was unnecessarily high—especially given that `tj_express` is lightly used in the office environment.

We identified three primary drivers of this memory overhead:
1. **Uvicorn Reloader**: The server was hardcoded to run with `reload=True` inside Docker. This spawned a second watcher process to monitor file system changes, effectively doubling the baseline memory.
2. **Heavy Startup Imports**: Libraries like `pandas`, `openpyxl`, and `dbfread` were imported at the module level. Simply importing these modules on startup instantly inflated memory usage by ~70–80 MB.
3. **Built-in Docs (Swagger/Redoc)**: FastAPI automatically compiled OpenAPI schemas and hosted `/docs` and `/redoc` interfaces, which consumed additional memory and exposed internal endpoints unnecessarily in a production context.

## Decision
To bring the memory footprint down to a minimal level, we made the following changes when the application runs in a container environment (`IS_CONTAINER=TRUE`):

1. **Disable Hot-Reload and Limit Workers**: 
   Turn off `reload` and explicitly configure Uvicorn to run with exactly 1 worker process.
2. **Disable Documentation UIs**: 
   Pass `openapi_url=None`, `docs_url=None`, and `redoc_url=None` to FastAPI to prevent schema compilation and disable the documentation routes.
3. **Lazy-Load Heavy Dependencies**: 
   Move the imports of `pandas`, `openpyxl`, and `dbfread` from the module level to the inside of individual functions (e.g. `read_dbf`, `generate_tax_report`, `get_stock`). This defers loading these libraries into RAM until a request actually invokes them.

## Consequences
- **Memory Footprint Reduced by 78%**: Idle memory usage dropped from **160+ MB** to **34 MB**.
- **Minimal Process Count**: The container runs with a single PID (PID 1) instead of multiple processes.
- **Instantaneous Startup**: The application boots up almost instantly because it doesn't load heavy analytical packages or compile API docs at launch.
- **Lazy-Load Overhead**: The very first API request that reads a DBF or generates a tax report will experience a small, one-time delay (less than 1 second) as `pandas` or `openpyxl` are loaded into memory. Memory usage will rise to ~60–80 MB after this first request and stay loaded, which is comparable to a standard Django process.
