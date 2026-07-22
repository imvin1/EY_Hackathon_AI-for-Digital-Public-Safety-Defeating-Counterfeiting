from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class CallerProfile(BaseModel):
    phone_number: str = Field(..., description="The calling number or identifier")
    is_voip: bool = Field(default=False, description="Flag if number resolves to VoIP infrastructure")
    carrier_mismatch: bool = Field(default=False, description="Flag if caller ID doesn't match registration data")
    spoofing_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Probability of caller ID spoofing")

class MediaIndicators(BaseModel):
    fake_uniform_detected: bool = Field(default=False, description="CV flag for counterfeit police/customs uniforms")
    fake_backdrop_detected: bool = Field(default=False, description="CV flag for mock courtrooms or government offices")
    voice_synthetic_probability: float = Field(default=0.0, ge=0.0, le=1.0, description="Speech analysis probability of cloned/synthetic voice")

class ArrestScamAnalysisRequest(BaseModel):
    call_id: str = Field(..., description="Unique call session identifier")
    transcript: str = Field(..., description="Full text transcript of the call")
    caller: CallerProfile
    media: Optional[MediaIndicators] = None
    call_duration_seconds: int = Field(default=0, description="Duration of call sequence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MhaAlert(BaseModel):
    alert_id: str
    target_phone: str
    severity: str = Field(..., description="Low, Medium, High, Critical")
    reasons: List[str]
    alert_timestamp: datetime
    reported_by: str = "DefeatShield AI System"
    forwarded_to_telecom: bool = False
    forwarded_to_cyber_cell: bool = False

class ArrestScamAnalysisResponse(BaseModel):
    call_id: str
    scam_probability: float = Field(..., ge=0.0, le=1.0)
    coercion_score: float = Field(..., ge=0.0, le=1.0, description="Score measuring psychological coercion intensity")
    matched_script_templates: List[str] = Field(default_factory=list, description="IDs/names of standard scam scripts matched")
    spoofing_indicators_triggered: List[str] = Field(default_factory=list)
    mha_alert_generated: bool = False
    alert_details: Optional[MhaAlert] = None
    confidence_level: float = Field(..., ge=0.0, le=1.0)
