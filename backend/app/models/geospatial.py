from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class IncidentPoint(BaseModel):
    incident_id: str
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude of the crime incident")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude of the crime incident")
    crime_type: str = Field(..., description="E.g., counterfeit_circulation, mule_atm_withdrawal, scammer_den_call_center")
    district: str = Field(..., description="Police administrative district name")
    state: str = Field(..., description="Indian State, e.g. Haryana, Delhi, Karnataka")
    reported_timestamp: datetime
    financial_impact_inr: float = Field(default=0.0, ge=0.0)

class CrimeHotspot(BaseModel):
    hotspot_id: str
    latitude: float
    longitude: float
    cluster_radius_meters: float
    incident_count: int
    total_financial_loss_inr: float
    severity_score: float = Field(..., ge=0.0, le=10.0, description="Normalized score 0-10 based on incident volume and impact")
    inter_district_sharing_active: bool = Field(default=False)

class RouteWayPoint(BaseModel):
    sequence: int
    latitude: float
    longitude: float
    district: str
    action_item: str = Field(..., description="E.g., 'Patrol area', 'Verify suspicious ATM', 'Inspect shop'")

class PatrolRouteResponse(BaseModel):
    route_id: str
    start_latitude: float
    start_longitude: float
    waypoints: List[RouteWayPoint]
    total_distance_km: float
    estimated_duration_minutes: int
    covered_hotspots: List[str]
    alert_level: str = Field(..., description="Routine, High-Alert, Critical")
