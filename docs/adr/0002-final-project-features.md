# ADR 0002: Final Feature Specification for tj_express

## Status
Accepted

## Context
Following the successful refactoring of the project from a script/CLI structure into a modular FastAPI application, we need to document the finalized architecture, rules, and implemented features for the `tj_express` service.

This document serves as the single source of truth for the capabilities of `tj_express` and how it interacts with the Express ERP database.

---

## Implemented Features

### 1. Multi-Company & Database Configuration
* **Exposed Config Endpoint (`GET /api/v1/tax/config`)**: Exposes the base path (`EXPRESS_PATH`) and the configured company mapping defined in `secrets/express.env` (e.g. `{"TJ": "TJ68", "THAIJINTAN": "JINTAN68"}`). This allows the frontend dashboard to populate company selector dropdowns dynamically.
* **Auto Company Profile Loader**: When generating reports, the app dynamically reads `ISINFO.DBF` inside the targeted database directory to extract the company's official Thai name, 13-digit Tax ID, address, and HQ/branch organization code. This ensures reports are dynamic and self-configuring.

### 2. Custom Sales Tax Report Engine (`GET /api/v1/tax/report`)
* **PE-to-AD Year Conversion**: Accepts Thai Buddhist Era (BE) years in the parameters (e.g., `2569`) and automatically converts them to Gregorian (AD) years (`2026`) for querying the DBF files.
* **Document Filtering Rules**:
  * **Included**: Invoices (`IV`), Cash Sales (`HS`), and Credit Notes / Sales Returns (`SR`).
  * **Excluded**: General Receipts (`RE`).
  * **Cancelled Invoices**: Automatically handles zero-total or cancelled invoices by reporting them with `0.00` values.
* **Sign Adjustment**: Sales returns (`SR` documents) have their amounts and VAT values multiplied by `-1` to represent a reduction in tax liability.
* **Online Marketplace Overrides**:
  * For transactions belonging to online platform customer codes (`LAZADA`, `SHOPEE`, `TIKTOK`), the engine checks for corresponding notes in `ARTRNRM.DBF`.
  * If notes exist, the line marked `@1` is used as the customer's custom name, and the line marked `@2` is used as their custom Tax ID.
  * If no overrides exist, the engine defaults to the standard platform customer profile from `ARMAS.DBF`.

### 3. High-Fidelity Excel Export Engine (`GET /api/v1/tax/download`)
* **Thai Accounting Format**: Writes `.xlsx` files styled in `Angsana New` font with tailored double-border underlines for totals and specific column widths matching official Thai Revenue Department guidelines.
* **Dynamic Page Splitting**: Spits data items into chunks of a maximum of **33 items per page**.
* **Page Summary Rows (`รวมแต่ละหน้า`)**: Inserts a summary row after each 33-item page that sums the goods values and VAT for that page using dynamic formulas (e.g., `=SUM(H9:H41)`).
* **Print Titles repeating**: Configures `ws.print_title_rows = '1:8'`. When printed or saved as PDF, the title metadata (company details) and the column headers repeat at the top of every printed page.
* **Page Breaks**: Inserts explicit print page breaks (`Break`) after each page's summary row, ensuring clean page divisions when printing.
* **Grand Total Row (`รวมทั้งหมด`)**: Sums the page summaries directly (e.g., `=H42+H68`) to ensure accurate totals without double-counting data.

### 4. Stock Count Bridge (`GET /api/v1/stock/{company_id}`)
* **Decoupled Inventory Checking**: Queries `STLOC.DBF` and `STMAS.DBF` locally on the Express server and returns current stock balances for location `01` (Stock 1) in JSON format.
* **Independence**: Allows the external NAS-hosted `tj_inventory` application to fetch stock numbers via HTTP, completely removing its dependency on mounting local file paths.

### 5. Interactive Frontend Dashboard
* **Modern Interface**: Single-page application served directly from the FastAPI root `/` url (redirecting to `/ui/index.html`).
* **Glassmorphic Dark Mode**: Designed on premium UX principles with sleek dark slate backdrops, custom Outfit/Inter typography, and hover micro-animations.
* **Search Filters**: Allows accountants to search and filter through hundreds of rows in the preview table instantaneously without fetching from the server again.
* **Download Trigger**: Dynamic buttons let users review the report on-screen first, then download the exact Excel equivalent with one click.

---

## Consequences
* **Decoupling**: Express table reading is entirely localized to `tj_express`, minimizing network latency and security access points.
* **Extensibility**: The core parsing engine in `tj_express/core/dbf.py` can be reused to read any other Express DBF tables (e.g. Purchases, AP, GL) should additional custom reporting or bridges be needed in the future.
