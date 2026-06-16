from fastapi import APIRouter
from tj_express.api.endpoints import stock, tax

from tj_express.config import COMPANIES

router = APIRouter(prefix="/api/v1")

@router.get("/")
@router.get("")
def api_root():
    """Returns the online status and the configured companies list."""
    return {"status": "online", "companies": list(COMPANIES.keys())}

router.include_router(stock.router, prefix="/stock", tags=["Stock"])
router.include_router(tax.router, prefix="/tax", tags=["Tax"])
