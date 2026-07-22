import math
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from backend.app.config import settings
from backend.app.models.geospatial import (
    IncidentPoint,
    CrimeHotspot,
    RouteWayPoint,
    PatrolRouteResponse
)

logger = logging.getLogger("defeatshield.geospatial_service")

class GeospatialIntelligenceService:
    def __init__(self):
        # In-memory storage for active incidents
        self.incidents: List[IncidentPoint] = []
        
        # Populate with a realistic set of geo incidents (Delhi-NCR hotspot region)
        self._bootstrap_sample_incidents()

    def report_incident(self, incident: IncidentPoint) -> None:
        """
        Logs a new crime incident location (with spatial and financial telemetry).
        """
        self.incidents.append(incident)
        logger.info(f"Geospatial Incident Registered: {incident.incident_id} at ({incident.latitude}, {incident.longitude})")

    def analyze_hotspots(self) -> List[CrimeHotspot]:
        """
        Density-based spatial clustering using Haversine distance.
        Groups points within setting threshold, calculating aggregate loss, threat severity,
        and flagging cross-district boundaries for multi-jurisdictional action.
        """
        if not self.incidents:
            return []

        clusters: List[List[IncidentPoint]] = []
        visited = set()
        radius = settings.ai.GEOSPATIAL_HOTSPOT_RADIUS_METERS

        for idx, inc in enumerate(self.incidents):
            if inc.incident_id in visited:
                continue

            # Start a new cluster
            current_cluster = [inc]
            visited.add(inc.incident_id)

            # Find all nearby points
            for other_inc in self.incidents:
                if other_inc.incident_id in visited:
                    continue

                dist = self._haversine(
                    inc.latitude, inc.longitude, 
                    other_inc.latitude, other_inc.longitude
                )
                
                if dist <= radius:
                    current_cluster.append(other_inc)
                    visited.add(other_inc.incident_id)
            
            clusters.append(current_cluster)

        hotspots: List[CrimeHotspot] = []
        for c_idx, cluster in enumerate(clusters):
            # Centroid calculation
            avg_lat = sum(p.latitude for p in cluster) / len(cluster)
            avg_lon = sum(p.longitude for p in cluster) / len(cluster)
            
            total_loss = sum(p.financial_impact_inr for p in cluster)
            
            # Check if this cluster spans multiple districts (cross-district intelligence flag)
            districts = {p.district for p in cluster}
            cross_district = len(districts) > 1
            
            # Severity index: volume-based and loss-based (normalized 0-10)
            volume_factor = min(5.0, len(cluster) * 0.8)
            loss_factor = min(5.0, total_loss / 500000.0) # 5L threshold for max severity contribution
            severity = volume_factor + loss_factor

            hotspots.append(CrimeHotspot(
                hotspot_id=f"HOTSPOT-{c_idx + 1:03d}",
                latitude=round(avg_lat, 6),
                longitude=round(avg_lon, 6),
                cluster_radius_meters=radius,
                incident_count=len(cluster),
                total_financial_loss_inr=total_loss,
                severity_score=round(severity, 2),
                inter_district_sharing_active=cross_district
            ))

        # Sort hotspots by severity
        return sorted(hotspots, key=lambda x: x.severity_score, reverse=True)

    def optimize_patrol_vectors(
        self, 
        start_lat: float, 
        start_lng: float, 
        target_district: str
    ) -> PatrolRouteResponse:
        """
        Generates an optimized patrol vector visiting active crime hotspots in a district.
        Solves Traveling Salesperson Problem (TSP) using a greedy Nearest-Neighbor search strategy.
        """
        hotspots = self.analyze_hotspots()
        # Filter hotspots located in or close to the target district or overall region
        # For prototype simplicity, we optimize across the top hotspots
        active_hotspots = hotspots[:settings.ai.GEOSPATIAL_PATROL_VECTORS_LIMIT]

        if not active_hotspots:
            # Safe return of empty route
            return PatrolRouteResponse(
                route_id=f"PATROL-{uuid.uuid4().hex[:8].upper()}",
                start_latitude=start_lat,
                start_longitude=start_lng,
                waypoints=[],
                total_distance_km=0.0,
                estimated_duration_minutes=0,
                covered_hotspots=[],
                alert_level="Routine"
            )

        # Nearest neighbor traversal
        unvisited = list(active_hotspots)
        curr_lat, curr_lng = start_lat, start_lng
        route_points: List[RouteWayPoint] = []
        total_dist_meters = 0.0
        seq = 1

        while unvisited:
            # Find nearest hotspot
            nearest_idx = 0
            min_dist = float('inf')
            
            for i, hs in enumerate(unvisited):
                dist = self._haversine(curr_lat, curr_lng, hs.latitude, hs.longitude)
                if dist < min_dist:
                    min_dist = dist
                    nearest_idx = i
            
            # Visit nearest
            next_hs = unvisited.pop(nearest_idx)
            total_dist_meters += min_dist
            
            # Action logic based on crime type severity
            action = "Routine patrol scan."
            if next_hs.severity_score > 7.0:
                action = "Inspect ATM cashout hubs & check fraud ring device activity."
            elif next_hs.severity_score > 4.0:
                action = "Inspect local currency exchanges for counterfeit FICN bills."

            route_points.append(RouteWayPoint(
                sequence=seq,
                latitude=next_hs.latitude,
                longitude=next_hs.longitude,
                district=target_district,
                action_item=action
            ))
            
            # Update current coordinates
            curr_lat = next_hs.latitude
            curr_lng = next_hs.longitude
            seq += 1

        # Calculate estimated duration (assuming average patrol speed of 30 km/h = 500 meters/min)
        distance_km = total_dist_meters / 1000.0
        duration_mins = int(total_dist_meters / 500.0) + (len(route_points) * 10) # 10 mins inspect delay per waypoint

        max_severity = max(hs.severity_score for hs in active_hotspots) if active_hotspots else 0.0
        alert_lvl = "Critical" if max_severity > 7.0 else ("High-Alert" if max_severity > 4.0 else "Routine")

        return PatrolRouteResponse(
            route_id=f"PATROL-{uuid.uuid4().hex[:8].upper()}",
            start_latitude=start_lat,
            start_longitude=start_lng,
            waypoints=route_points,
            total_distance_km=round(distance_km, 2),
            estimated_duration_minutes=duration_mins,
            covered_hotspots=[hs.hotspot_id for hs in active_hotspots],
            alert_level=alert_lvl
        )

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Returns distance between two geographical coordinate pairs in meters.
        """
        R = 6371000.0  # Earth's radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def _bootstrap_sample_incidents(self):
        """
        Bootstraps initial incident dataset mapping Delhi-NCR and Haryana borders
        where digital scam and currency counterfeit clusters are historically reported.
        """
        now = datetime.utcnow()
        samples = [
            # Mewat/Nuh Cluster (Digital Scam Hotspots)
            IncidentPoint(incident_id="INC-001", latitude=28.1205, longitude=77.0125, crime_type="scammer_den_call_center", district="Nuh", state="Haryana", reported_timestamp=now - timedelta(hours=5), financial_impact_inr=150000.0),
            IncidentPoint(incident_id="INC-002", latitude=28.1250, longitude=77.0210, crime_type="mule_atm_withdrawal", district="Nuh", state="Haryana", reported_timestamp=now - timedelta(hours=10), financial_impact_inr=85000.0),
            IncidentPoint(incident_id="INC-003", latitude=28.1180, longitude=77.0090, crime_type="scammer_den_call_center", district="Nuh", state="Haryana", reported_timestamp=now - timedelta(hours=2), financial_impact_inr=320000.0),

            # Delhi Border / Gurugram Cluster (Laundering/Counterfeit Hotspots)
            IncidentPoint(incident_id="INC-004", latitude=28.4595, longitude=77.0266, crime_type="counterfeit_circulation", district="Gurugram", state="Haryana", reported_timestamp=now - timedelta(hours=12), financial_impact_inr=24000.0),
            IncidentPoint(incident_id="INC-005", latitude=28.4520, longitude=77.0310, crime_type="counterfeit_circulation", district="Gurugram", state="Haryana", reported_timestamp=now - timedelta(hours=24), financial_impact_inr=50000.0),
            
            # Cross-district borderline incidents (overlapping Mewat and Alwar, Rajasthan border)
            IncidentPoint(incident_id="INC-006", latitude=28.1050, longitude=76.9950, crime_type="mule_atm_withdrawal", district="Alwar", state="Rajasthan", reported_timestamp=now - timedelta(hours=3), financial_impact_inr=95000.0)
        ]
        self.incidents.extend(samples)

geospatial_service = GeospatialIntelligenceService()
