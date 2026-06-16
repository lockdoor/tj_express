import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from tj_express.core.tax_report import generate_tax_report, export_tax_report_excel, THAI_MONTHS

from tj_express.config import EXPRESS_PATH, COMPANIES

router = APIRouter()

@router.get("/config")
def get_app_config():
    """Returns the list of configured companies and the base Express path."""
    return {
        "express_path": EXPRESS_PATH,
        "companies": COMPANIES
    }

@router.get("/report")
def get_tax_report(
    company_folder: str = Query(..., description="Company folder inside Express root (e.g. RINARA68)"),
    year_be: int = Query(..., description="Year in Buddhist Era (e.g. 2569)"),
    month: int = Query(..., description="Month number (1-12)", ge=1, le=12)
):
    """Generates and returns the sales tax report in JSON format."""
    year_ad = year_be - 543
    try:
        data = generate_tax_report(company_folder, year_ad, month)
        return data
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
def download_tax_report(
    company_folder: str = Query(..., description="Company folder inside Express root (e.g. RINARA68)"),
    year_be: int = Query(..., description="Year in Buddhist Era (e.g. 2569)"),
    month: int = Query(..., description="Month number (1-12)", ge=1, le=12)
):
    """Generates the sales tax report and downloads it as a formatted Excel spreadsheet."""
    year_ad = year_be - 543
    
    # Ensure outputs directory exists in project root
    project_root = Path(__file__).resolve().parent.parent.parent
    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    filename = f"sales_tax_{company_folder}_{year_be}_{month:02d}.xlsx"
    filepath = outputs_dir / filename
    
    try:
        export_tax_report_excel(company_folder, year_ad, month, str(filepath))
        
        # Determine a user-friendly Thai filename for download
        thai_month_name = THAI_MONTHS[month]
        download_filename = f"รายงานภาษีขาย_{company_folder}_{thai_month_name}_{year_be}.xlsx"
        
        # Return file response
        return FileResponse(
            path=filepath,
            filename=download_filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
