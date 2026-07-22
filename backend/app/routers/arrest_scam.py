from fastapi import APIRouter, HTTPException, Depends, status
from backend.app.models.arrest_scam import ArrestScamAnalysisRequest, ArrestScamAnalysisResponse
from backend.app.services.arrest_scam_service import arrest_scam_service
import logging

router = APIRouter(prefix="/arrest-scam", tags=["Digital Arrest Scam Detection"])
logger = logging.getLogger("defeatshield.routers.arrest_scam")

@router.post(
    "/analyze", 
    response_model=ArrestScamAnalysisResponse, 
    status_code=status.HTTP_200_OK,
    summary="Analyze Call Flow for Digital Arrest Scam Indicators",
    description="Processes call transcript text, audio features, and caller profiles to determine digital arrest scam probability and trigger Ministry of Home Affairs warnings."
)
async def analyze_call_session(payload: ArrestScamAnalysisRequest):
    try:
        response = await arrest_scam_service.analyze_scam_session(payload)
        return response
    except Exception as e:
        logger.error(f"Router error in call analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute scam session analysis: {str(e)}"
        )
