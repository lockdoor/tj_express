from fastapi import APIRouter
from tj_express.api.endpoints import stock, tax

router = APIRouter(prefix="/api/v1")

router.include_router(stock.router, prefix="/stock", tags=["Stock"])
router.include_router(tax.router, prefix="/tax", tags=["Tax"])
