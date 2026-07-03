import os
from fastapi import APIRouter, HTTPException
from tj_express.core.dbf import read_dbf
from tj_express.config import EXPRESS_PATH

router = APIRouter()

@router.get("/{company_id}/account-chart")
def get_account_chart(company_id: str):
    """
    Return list of accounts from the given company, GLACC.DBF (Genaral Ledger Account Chart)
    """
    data_path = os.path.join(EXPRESS_PATH, company_id)       
    if not os.path.isdir(data_path):
        raise HTTPException(status_code=404, detail=f"Company directory '{company_id}' not found")
    dbf_path = os.path.join(data_path, "GLACC.DBF")
    
    try:
        data = read_dbf(dbf_path)   
        return data.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{dbf_path}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    