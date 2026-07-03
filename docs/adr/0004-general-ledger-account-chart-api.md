# ADR 0004: General Ledger Account Chart API Endpoint

## Status
Accepted

## Context
To support general ledger integrations and account mapping features in the frontend or external systems (like `tj_inventory`), we need an API endpoint to retrieve the list of accounts (chart of accounts) for a specific company.

In the Express ERP system, the General Ledger Account Chart is stored in the `GLACC.DBF` database file under each company's data directory. 

During initial testing, returning the raw Pandas DataFrame directly caused a serialization error in FastAPI (`TypeError: 'numpy.int64' object is not iterable`) because Uvicorn and FastAPI's native encoders cannot directly serialize a Pandas DataFrame object or its internal NumPy data types.

## Decision
1. **New Endpoint Module**: Create a new API router in [account.py](file:///Users/pitsanunamnil/Desktop/work/tj/tj_express/tj_express/api/endpoints/account.py) containing the `get_account_chart` function under the path `GET /api/v1/account/{company_id}/account-chart`.
2. **Read-Only DBF Access**: Read the `GLACC.DBF` file using the safe, read-only `read_dbf` helper defined in [dbf.py](file:///Users/pitsanunamnil/Desktop/work/tj/tj_express/tj_express/core/dbf.py).
3. **Proper JSON Serialization**: Explicitly convert the resulting Pandas DataFrame to a list of dictionaries using `data.to_dict(orient="records")`. This structures the records appropriately and allows FastAPI to correctly serialize the response to JSON without NumPy type compatibility errors.
4. **Router Registration**: Register the new router in [routes.py](file:///Users/pitsanunamnil/Desktop/work/tj/tj_express/tj_express/api/routes.py) under the `/account` prefix.

## Consequences
- **Expanded API Surface**: Consumer applications can now fetch structured General Ledger account charts.
- **Strict Read-Only Access**: Access is read-only, ensuring no risk of database corruption for Express.
- **Robust Serialization**: Converting to records via `.to_dict(orient="records")` ensures seamless JSON encoding by FastAPI.
