from fastapi import APIRouter, HTTPException, status
from backend.app.models.citizen_shield import CitizenRiskQuery, CitizenRiskResponse
from backend.app.services.citizen_shield_service import citizen_shield_service
import logging

router = APIRouter(prefix="/citizen-shield", tags=["Citizen Fraud Shield"])
logger = logging.getLogger("defeatshield.routers.citizen_shield")

@router.post(
    "/query", 
    response_model=CitizenRiskResponse, 
    status_code=status.HTTP_200_OK,
    summary="Assess Public Message/Contact Risk Level",
    description="Processes suspicious text calls/messages across 12 regional languages, outputs urgency risk rating, returns localized safety advisories, and formats pre-filled NCRB complaint scripts."
)
async def evaluate_risk(payload: CitizenRiskQuery):
    # Standardize language code format
    supported_langs = ["en", "hi", "ta", "te", "bn", "mr", "kn", "gu", "ml", "pa", "or", "as"]
    lang_code = payload.language_code.lower()
    
    if lang_code not in supported_langs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported Language Code: '{payload.language_code}'. The platform supports 12 regional language codes: {', '.join(supported_langs)}."
        )

    try:
        response = await citizen_shield_service.evaluate_risk(payload)
        return response
    except Exception as e:
        logger.error(f"Router error in citizen shield query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment pipeline failed: {str(e)}"
        )
