# ADR 0005: Remove Hardcoded COMPANIES Mapping and Use Dynamic Directory Scanning

## Status
Accepted

## Context
Previously, the `tj_express` service relied on a hardcoded `COMPANIES` environment variable mapping (e.g., `{"TJ":"TJ69","THAIJINTAN":"JINTAN68"}`) to map short identifiers to physical folders in the filesystem.

This configuration approach had several drawbacks:
1. **High Maintenance**: Adding new company folders or changing folder names required updating environment files (like `express.env`) or Docker environments and restarting the service.
2. **Fragility**: File path resolution relied on config synchronization. If a folder on disk was renamed but the config was not updated, endpoints would crash with unhandled filesystem errors.
3. **Redundant Mapping**: The frontend had to map between display values and folder names back and forth.

We needed a system that dynamically scans available data directories and strictly validates their physical existence on disk.

## Decision
1. **Remove env-based COMPANIES Mapping**: Delete the `COMPANIES` JSON parser from the config module [config.py](file:///Users/pitsanunamnil/Desktop/work/tj/tj_express/tj_express/config.py).
2. **Implement Dynamic Scanning**: Introduce a utility function `get_available_companies()` that dynamically reads `EXPRESS_PATH` at runtime, returning only active directories.
3. **Direct Directory Routing**: Update `/stock/{company_id}` and `/account/{company_id}/account-chart` routes to treat the path parameter as the folder name directly.
4. **Strict Directory Validation**: Add validation checks using `os.path.isdir` inside all API endpoint handlers (`stock.py`, `account.py`, `tax.py`). If the requested directory does not exist, throw a `404 Not Found` HTTP exception.
5. **Array-based UI Integration**: Refactor [app.js](file:///Users/pitsanunamnil/Desktop/work/tj/tj_express/tj_express/ui/app.js) to consume the company list as a list of strings, populating dropdowns with the direct directory names.

## Consequences
- **Zero Config Maintenance**: Newly added folders inside the Express root directory are discovered and available immediately without server restarts or configuration updates.
- **Fail-Fast Error Handling**: Invalid or non-existent directories passed via paths or queries are rejected with clean `404` errors before any parsing/reading starts.
- **Decoupled Environment**: Reduced configuration complexity since only `EXPRESS_PATH` is required to run the service.
