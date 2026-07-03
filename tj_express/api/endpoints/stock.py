import os
from fastapi import APIRouter, HTTPException
from tj_express.core.dbf import read_dbf
from tj_express.config import EXPRESS_PATH

router = APIRouter()

@router.get("/{company_id}")
def get_stock(company_id: str):
    import pandas as pd
    """
    Reads STLOC.DBF and STMAS.DBF for the given company and returns SKU -> Balance for Stock 1 (01).
    """
    data_path = os.path.join(EXPRESS_PATH, company_id)
    if not os.path.isdir(data_path):
        raise HTTPException(status_code=404, detail=f"Company directory '{company_id}' not found")
    
    stmas_path = os.path.join(data_path, 'STMAS.DBF')
    stloc_path = os.path.join(data_path, 'STLOC.DBF')
    
    if not os.path.exists(stmas_path) or not os.path.exists(stloc_path):
        raise HTTPException(status_code=404, detail="Stock data file not found")

    try:
        stmas_df = read_dbf(stmas_path)
        stloc_df = read_dbf(stloc_path)
            
        merge_df = pd.merge(stmas_df, stloc_df, how='left', on='STKCOD')
        selected_columns = ['STKCOD', 'STKDES', 'STKDES2', 'LOCBAL', 'QUCOD', 'LOCCOD']
        selected_df = merge_df[selected_columns]
        selected_df = selected_df[selected_df['LOCCOD'] == '01']
        
        # Clean up any NaN values before converting to dict
        selected_df = selected_df.fillna(0)

        # Change column names
        selected_df = selected_df.rename(columns={
            'STKCOD': 'sku', 
            'LOCBAL': 'balance',
            'STKDES': 'name',
            'STKDES2': 'name2',
            'QUCOD': 'unit'
        })

        # Remove LOCCOD column
        selected_df = selected_df.drop(columns=['LOCCOD'])
        
        return selected_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
