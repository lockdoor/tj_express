# ADR 0001: Use FastAPI for tj_express and Define Project Structure

## Status
Accepted

## Context
We need to develop a dedicated microservice, `tj_express`, that runs directly on the Express ERP server. 
1. **Core Responsibility**: Read-only extraction of data from Express DBF files to generate custom reports (e.g., sales tax reports) and serve utility endpoints (e.g., stock count query previously located in `tj_inventory`).
2. **Constraints**: All data access is strictly read-only to avoid corrupting the Express database.
3. **Deployment**: It will run on the Windows server hosting Express, making direct file system access fast and local.

Previously, some Express-related bridge code was embedded inside `tj_inventory`. We need to extract that context, move it to `tj_express`, and clean up the file structure to handle multiple reports, API endpoints, and a modern frontend UI.

## Decision
We will use **FastAPI** as the backend framework due to its high performance, native support for JSON/Pydantic validation, automatic OpenAPI docs generation, and ease of serving static frontend files.

We will structure the project using a modular layout:

```text
tj_express/
├── pyproject.toml            # Setuptools packaging and dependencies
├── README.md                 # Project README and usage instructions
├── .gitignore                # Git ignore patterns (ignores venv, secrets, asset_dev)
├── docs/                     # Documentation and ADRs
│   └── adr/
│       └── 0001-use-fastapi-and-project-structure.md
└── tj_express/               # Main application package
    ├── __init__.py
    ├── main.py               # FastAPI App startup and configurations
    ├── config.py             # Configuration settings (environment variables, paths)
    ├── core/                 # Business logic and DBF parsing
    │   ├── __init__.py
    │   ├── dbf.py            # DBF reader and custom field parsers (read-only)
    │   └── tax_report.py     # Sales tax report generation logic (Pandas processing)
    ├── api/                  # API endpoints
    │   ├── __init__.py
    │   ├── routes.py         # Main api router combining all versions and endpoints
    │   └── v1/
    │       ├── __init__.py
    │       ├── tax.py        # Sales tax report endpoints
    │       └── stock.py      # Stock count and STLOC endpoints (extracted from tj_inventory)
    └── ui/                   # Front-end user interface
        ├── index.html        # Main dashboard SPA
        ├── style.css         # Modern, premium user interface styling
        └── app.js            # Frontend logic and API requests
```

### Key Components

1. **`tj_express/core/dbf.py`**:
   - Wraps `dbfread` in a read-only manner.
   - Holds `SafeFieldParser` to safely parse dates and ignore corrupt formats.
2. **`tj_express/core/tax_report.py`**:
   - Encapsulates all Pandas/data-munging code needed to process `ARTRN.DBF`, `ARMAS.DBF`, and `ARTRNRM.DBF`.
3. **`tj_express/api/`**:
   - Restructures endpoints into submodules (`tax.py`, `stock.py`) rather than keeping them in a single bloated `main.py`.
4. **`tj_express/ui/`**:
   - An interactive single-page application (SPA) allowing accountants to easily select the Database, Year, and Month, preview the report table, and download generated Excel spreadsheets.

## Consequences
- **Decoupled Architecture**: `tj_inventory` will query this service over HTTP to get stock counts, making `tj_inventory` entirely independent of Express file paths.
- **Maintainability**: Adding new reports or tables only requires adding a new file in `core/` and exposing it in `api/`.
- **Robustness**: Safe parsing logic is isolated and reusable across all endpoints.
