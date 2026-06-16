# tj_express ⚡

`tj_express` is a lightweight, high-performance FastAPI microservice designed to act as a bridge and report engine for the Express ERP database. It runs directly on the Express Windows Server, providing safe, read-only extraction of data from Express `.DBF` files.

This project solves two primary needs:
1. **Sales Tax Report Generator**: Generates custom sales tax reports (previewable in a modern web UI and downloadable as structured Excel spreadsheets) that handle online marketplace lump-sum vs. individual customer invoice rules.
2. **Stock Query Bridge**: Exposes stock balance information from `STLOC.DBF` and `STMAS.DBF` to be queried by other internal services like `tj_inventory`.

---

## 🚀 Key Features

* **Sleek Web Interface**: An interactive, glassmorphic single-page application (SPA) for accountants to select months/years, preview records, search on the fly, and download Excel reports.
* **Auto-override for Online Channels**: Automatically detects transactions from online platforms (`LAZADA`, `SHOPEE`, `TIKTOK`). If a customer requests a tax invoice, the program reads the custom client name (line #1) and Tax ID (line #2) from the Express invoice notes (`ARTRNRM.DBF`) and merges them into the report.
* **Read-Only Safety**: Data parsing is strictly read-only to guarantee zero risk of corrupting active Express DBF databases.
* **Plug-and-Play Company Profiles**: Automatically reads company details (name, tax ID, branch/HQ, address) directly from `ISINFO.DBF` for the selected database folder.

---

## 📂 Project Directory Structure

```text
tj_express/
├── pyproject.toml            # Package metadata and dependencies
├── README.md                 # Project documentation
├── .gitignore                # Git ignore configuration
├── secrets/                  # Private configuration folder (gitignored)
│   └── express.env           # Active environment variables
└── tj_express/               # Main application package
    ├── __init__.py
    ├── main.py               # FastAPI application setup
    ├── __main__.py             # Uvicorn package runner
    ├── config.py             # Environment configuration loader
    ├── core/                 # Business logic
    │   ├── dbf.py            # Read-only DBF parser
    │   └── tax_report.py     # Sales tax report engine & Excel writer
    ├── api/                  # FastAPI routers and endpoints
    │   ├── routes.py         # Version router (/api/v1)
    │   └── endpoints/
    │       ├── stock.py      # Stock balance endpoints
    │       └── tax.py        # Sales tax endpoints (JSON & download)
    └── ui/                   # Frontend SPA files
        ├── index.html        # Main HTML layout
        ├── style.css         # Glassmorphic dark UI styles
        └── app.js            # Fetch actions and DOM rendering
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
* Python 3.10+
* Virtual Environment setup

### 2. Install Dependencies
Set up the virtual environment and install the package in editable mode:
```bash
# Create and activate virtualenv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package and all dependencies
pip install -e .
```

### 3. Configuration (`express.env`)
Create a file named `express.env` under the `secrets/` directory (you can copy `secrets/express_example.env`):
```ini
EXPRESS_PATH='C:\ExpressI\Secure\'
COMPANIES='{"TJ":"TJ69","RINARA":"RINARA68"}'
PORT=8001
HOST=0.0.0.0
```
* `EXPRESS_PATH`: The root directory containing Express company folders.
* `COMPANIES`: A JSON mapping of friendly company IDs to their actual folders under `EXPRESS_PATH`.

---

## ⚡ Running the Application

* **Option A: Run as a Python module (Recommended)**
  ```bash
  python -m tj_express
  ```
  *(This launches uvicorn with hot-reload enabled by default on the port configured in `express.env`)*.

* **Option B: Run directly via Uvicorn**
  ```bash
  uvicorn tj_express.main:app --reload --port 8001
  ```

Once started, navigate to:
* **Dashboard UI**: `http://localhost:8001/` (Redirects to `/ui/index.html`)
* **Interactive API Docs (Swagger)**: `http://localhost:8001/docs`

---

## 📊 Express Database Table Reference

All database tables are accessed in a **read-only** manner:
* **`ARTRN.DBF`**: Sales Transactions (invoices `IV`, cash sales `HS`, returns `SR`).
* **`ARMAS.DBF`**: Customers master file.
* **`ARTRNRM.DBF`**: Transaction remarks (holding custom name and tax ID overrides for online sales).
* **`ISINFO.DBF`**: Company profile configuration.
* **`STLOC.DBF`**: Inventory location balances.
* **`STMAS.DBF`**: Stock items master list.

---

## 🔌 API Endpoints Reference

### 1. Configuration & Health
* **`GET /api/v1/tax/config`**: Returns base Express directory path and configured companies.

### 2. Custom Reports (Sales Tax)
* **`GET /api/v1/tax/report`**: Fetches the sales tax report for a specific company, Buddhist Era (BE) year, and month as JSON.
  * *Parameters*: `company_folder`, `year_be`, `month`
* **`GET /api/v1/tax/download`**: Generates and downloads a formatted Excel sheet version of the sales tax report matching the Thai Revenue Department layout.
  * *Parameters*: `company_folder`, `year_be`, `month`

### 3. Stock Counting Bridge
* **`GET /api/v1/stock/{company_id}`**: Reads stock balances in location `01` (Stock 1) and returns a list of items (`sku`, `name`, `unit`, `balance`).
