from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from backend.app.models.counterfeit import CurrencyValidationResponse
from backend.app.services.counterfeit_service import counterfeit_service
import logging

router = APIRouter(prefix="/counterfeit", tags=["Counterfeit Currency Identification"])
logger = logging.getLogger("defeatshield.routers.counterfeit")

@router.post(
    "/validate", 
    response_model=CurrencyValidationResponse, 
    status_code=status.HTTP_200_OK,
    summary="Validate Banknote Authenticity using Computer Vision",
    description="Accepts an image file of a banknote along with its denomination and runs CV thread continuity, microprint sharpness, and serial OCR validations."
)
async def validate_banknote(
    denomination: int = Form(..., description="INR Denomination: 10, 20, 50, 100, 200, 500, 2000"),
    file: UploadFile = File(..., description="Banknote high-resolution image file (PNG/JPG)")
):
    # Enforce supported INR denominations
    if denomination not in [10, 20, 50, 100, 200, 500, 2000]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported INR Denomination: {denomination}. Platform only supports standard active RBI notes (10, 20, 50, 100, 200, 500, 2000)."
        )
        
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file uploaded."
            )
            
        result = await counterfeit_service.validate_banknote(file_bytes, denomination)
        return result
    except Exception as e:
        logger.error(f"Router error in banknote validation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Currency validation pipeline failed: {str(e)}"
        )
