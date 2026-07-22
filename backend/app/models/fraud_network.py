from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class NodeData(BaseModel):
    id: str = Field(..., description="Unique entity ID (e.g. Account Number, Device ID)")
    type: str = Field(..., description="Node classification: BANK_ACCOUNT, DEVICE_FINGERPRINT, PHONE_NUMBER, IP_ADDRESS")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary for this node")
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)

class EdgeData(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Relationship type: TRANSACTED_WITH, SHARED_DEVICE, LINKED_PHONE")
    weight: float = Field(default=1.0, description="Strength of relation/transaction amount proxy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FraudCluster(BaseModel):
    cluster_id: str
    nodes: List[NodeData]
    edges: List[EdgeData]
    average_risk_score: float
    mule_count: int
    scammer_infrastructure_count: int
    geographic_hotspots: List[str]

class EvidenceChainItem(BaseModel):
    step: int
    source_entity: str
    target_entity: str
    relation: str
    connecting_factor: str = Field(..., description="How they are linked, e.g. 'shared IMEI 35467... on 2026-07-18'")
    timestamp: datetime

class CourtAdmissibleEvidenceResponse(BaseModel):
    case_id: str
    suspect_ring_id: str
    generated_at: datetime
    evidence_chain: List[EvidenceChainItem]
    implicated_accounts: List[str]
    implicated_devices: List[str]
    implicated_phones: List[str]
    legal_memorandum_text: str = Field(..., description="Forensic narrative explaining the correlation and linkages for legal presentation")
    digital_signature: str = Field(..., description="SHA-256 cryptographic verification of evidence integrity")
