from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from backend.app.models.geospatial import (
    IncidentPoint,
    CrimeHotspot,
    PatrolRouteResponse
)
from backend.app.services.geospatial_service import geospatial_service
import logging

router = APIRouter(prefix="/geospatial", tags=["Geospatial Crime Pattern Intelligence"])
logger = logging.getLogger("defeatshield.routers.geospatial")

@router.post(
    "/incidents", 
    status_code=status.HTTP_201_CREATED,
    summary="Log New Spatial Crime Incident",
    description="Registers an incident coordinates and metadata (crime type, financial impact, administrative district) into the spatial analyzer."
)
async def log_incident(incident: IncidentPoint):
    try:
        geospatial_service.report_incident(incident)
        return {"status": "success", "message": f"Spatial incident '{incident.incident_id}' successfully mapped."}
    except Exception as e:
        logger.error(f"Failed to log spatial incident: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Geospatial write error: {str(e)}"
        )

@router.get(
    "/hotspots", 
    response_model=List[CrimeHotspot], 
    status_code=status.HTTP_200_OK,
    summary="Retrieve Calculated Crime Hotspots",
    description="Executes density-based Haversine spatial clustering on active crime inputs to identify high-density locations, total economic losses, and multi-district overlap states."
)
async def get_hotspots():
    try:
        hotspots = geospatial_service.analyze_hotspots()
        return hotspots
    except Exception as e:
        logger.error(f"Failed to calculate hotspots: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spatial clustering algorithm execution failed: {str(e)}"
        )

@router.get(
    "/patrol-route", 
    response_model=PatrolRouteResponse, 
    status_code=status.HTTP_200_OK,
    summary="Generate Optimized Police Patrol Vector",
    description="Calculates a Traveling Salesperson optimized route starting from defined coordinate to patrol top active severity hotspots in a district."
)
async def get_patrol_route(
    start_latitude: float = Query(..., description="Latitude of dispatch police station"),
    start_longitude: float = Query(..., description="Longitude of dispatch police station"),
    district: str = Query(..., description="Target police district for patrol assignment")
):
    try:
        route = geospatial_service.optimize_patrol_vectors(
            start_lat=start_latitude,
            start_lng=start_longitude,
            target_district=district
        )
        return route
    except Exception as e:
        logger.error(f"Failed to calculate optimized patrol vector: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Patrol route TSP optimizer calculation failed: {str(e)}"
        )
